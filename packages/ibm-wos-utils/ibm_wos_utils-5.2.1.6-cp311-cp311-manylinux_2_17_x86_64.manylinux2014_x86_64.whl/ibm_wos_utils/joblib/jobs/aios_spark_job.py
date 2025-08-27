# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2020, 2021
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

import json
import copy
import logging
import logging.config
import pathlib
import traceback
import os
from abc import ABC

from ibm_wos_utils.joblib.utils.constants import *
from ibm_wos_utils.joblib.utils.db_utils import DbUtils
from ibm_wos_utils.joblib.utils.joblib_utils import JoblibUtils
from ibm_wos_utils.joblib.utils.log_formatter import SensitiveDataFormatter
from ibm_wos_utils.joblib.utils.param_utils import get


class AIOSBaseJob(ABC):

    def __init__(self, arguments, job_name: str = "Base Job"):

        print("*********** Dumping a list of packages and versions ********************")
        import pkg_resources
        packages_of_interest = ["pyspark", "numpy", "pandas", "ibm-wos-utils", "ibm-metrics-plugin"]
        installed_packages_list = sorted(["{}=={}".format(
            i.key, i.version) for i in pkg_resources.working_set if i.key in packages_of_interest])
        print("Packages of Interest: {}".format(packages_of_interest))
        print("Installed packages of interest with version: {}".format(
            installed_packages_list))
        print("************************************************************************")

        spark_module = None
        try:
            spark_module = __import__("pyspark.sql", fromlist=["SparkSession"])
        except Exception as e:
            msg = "Unable to find pyspark library ro run AI OpenScale Job " + job_name
            raise Exception(msg)

        sparkSession = getattr(spark_module, "SparkSession")
        sparkApp = sparkSession.builder.appName(job_name)

        # Getting the storage type to decide whether to enable hive support when initiating spark session
        self.storage_type_map = get(arguments, "storage_type_map")
        # If there is only single storage type, setting the storage_type in base job. This is to ensure that jobs that use only single data source continue to work without any modifications.
        self.storage_type = get(arguments, "storage_type")

        if self.storage_type and self.storage_type == StorageType.HIVE.value:
            sparkApp = sparkApp.enableHiveSupport()
        elif self.storage_type_map:
            storage_types = list(self.storage_type_map.values())
            if len(set(storage_types)) == 1:
                self.storage_type = storage_types[0]
            if StorageType.HIVE.value in storage_types:
                sparkApp = sparkApp.enableHiveSupport()

        self.spark = sparkApp.getOrCreate()
        print("****** Using Spark - {} ******".format(self.spark.version))

        output_file_path = arguments["output_file_path"]
        data_file_path = arguments["data_file_path"]
        argument_file_name = arguments["param_file_name"]

        # Getting the spark type
        self.spark_type = get(arguments, "spark_type")

        param_df = self.spark.read.text(
            data_file_path + "/" + argument_file_name)
        val = param_df.select("value").collect()[0][0]
        # Since we are reading argument file as text file, replace single quote and boolean values.
        # Truncate extra double quotes
        # Reading file as json is throwing back the corrupted exception

        argument_json = json.loads(val)

        # Set the path in the read json
        argument_json["output_file_path"] = output_file_path
        argument_json["data_file_path"] = data_file_path
        argument_json["param_file_name"] = argument_file_name

        self.arguments = argument_json
        self.show_progress = get(self.arguments, "show_progress", True)
        self.logger = self.__get_logger()

        self.sc = self.spark.sparkContext

        argument_json_copy = copy.deepcopy(argument_json)
        # do not log training statistics
        if get(argument_json_copy, "metric_configuration.configuration.explainability.training_statistics"):
            del argument_json_copy["metric_configuration"]["configuration"]["explainability"]["training_statistics"]

        self.logger.info(
            "AIOSBaseJob instantiated with parameters {}".format(argument_json_copy))
        
        print("===== Start - Spark Properties ")
        print(self.sc.getConf().getAll())
        print("===== End - Spark Properties ")

        """
            conf.set("spark.dynamicAllocation.enabled",True)
            conf.set("spark.shuffle.service.enabled",True)
            conf.set("spark.dynamicAllocation.shuffleTracking.enabled",True)
            conf.set("spark.dynamicAllocation.minExecutors", "5");
            conf.set("spark.dynamicAllocation.maxExecutors", "30");
            conf.set("spark.dynamicAllocation.initialExecutors", "10");
            spark.sql.execution.arrow.enabled
            spark.sql.execution.arrow.fallback.enabled
        """

        # Process data sources to generate jdbc connection properties, add metastore_url to sparkContext etc.
        data_sources = self.arguments.get("tables", [])
        self.location_type_map = {}
        self.jdbc_connection_properties_map = {}
        # If there is only single location type, setting the location_type and connection properties in base job
        self.location_type = None
        self.jdbc_connection_properties = None

        # If the storage is common for all tables, get details from the common storage. Otherwise get details from each table's storage separately. WI #29635
        if self.arguments.get("storage"):
            self.location_type, self.jdbc_connection_properties = self.__get_storage_details(self.arguments, self.storage_type, sparkApp)
            if self.jdbc_connection_properties:
                self.arguments["storage"]["jdbc_connection_properties"] = self.jdbc_connection_properties
        else:
            for data_source in data_sources:
                data_source_type = data_source.get("type")
                storage_type = self.storage_type_map.get(data_source_type)

                location_type, jdbc_connection_properties = self.__get_storage_details(data_source, storage_type, sparkApp)
                self.location_type_map[data_source_type] = location_type
                self.jdbc_connection_properties_map[data_source_type] = jdbc_connection_properties

            # If there is a single location type, setting location type in base job.
            location_types = list(self.location_type_map.values())
            if len(set(location_types)) == 1:
                self.location_type = location_types[0]

            # If there is a single jdbc data source, setting connection properties in base job.
            if self.jdbc_connection_properties_map and len(self.jdbc_connection_properties_map) == 1 :
                self.jdbc_connection_properties = list(self.jdbc_connection_properties_map.values())[0]
                # If storage is specified at common location(for jobs using single table), updating connection properties in storage.
                if "storage" in self.arguments:
                    self.arguments["storage"]["jdbc_connection_properties"] = self.jdbc_connection_properties

        # Set the following configuration to skip generating _SUCCESS file
        # while saving dataframe as files in HDFS
        self.sc._jsc.hadoopConfiguration().set(
            "mapreduce.fileoutputcommitter.marksuccessfuljobs", "false")

    def save_data(
            self,
            path: str,
            data_json: dict,
            mode: str = "overwrite",
            compression: str = None):
        
        data_json = { key: value for key, value in data_json.items() if value is not None }
        df = self.spark.createDataFrame([data_json])
        try:
            if compression is None:
                df.coalesce(1).write.json(path, mode=mode)
            else:
                df.coalesce(1).write.json(
                    path, mode=mode, compression=compression)
        except Exception as e:
            # In case of hive-jdbc, the hive-exec jar is required to read the data. But this jar contains its own implementation of some functions which are also part of commons-lang3 jar.
            # The method implementation in hive-exec does not support default timestamp format which results in `java.lang.IllegalArgumentException: Illegal pattern component: XXX`
            # A workaround for this is to specify timestampFormat as option while writing the dataframe to json file. # 20706
            timestamp_error_msg = "Illegal pattern component: XXX"
            if timestamp_error_msg.lower() in str(e).lower():
                df.coalesce(1).write \
                    .option('timestampFormat', WRITE_TO_JSON_TIMESTAMP_FORMAT) \
                    .json(path, mode=mode, compression=compression)
            else:
                raise e

    def save_exception_trace(self, error_msg: str):
        tr = traceback.format_exc()
        output_path = self.arguments.get("output_file_path")
        path = output_path + "/exception.json"
        exception = {
            "error_msg": error_msg,
            "stacktrace": tr
        }
        self.save_data(path=path, data_json=exception)

    def save_exception(self, error_msg: str, error_code: str = None, parameters: [] = None):
        tr = traceback.format_exc()
        output_path = self.arguments.get("output_file_path")
        path = output_path + "/exception.json"
        exception = {
            "error_msg": error_msg,
            "stacktrace": tr,
            "code": error_code,
            "parameters": parameters
        }
        self.save_data(path=path, data_json=exception)

    def save_log_file(self, mode: str = "overwrite"):

        f = open("openscale_job.log", "r")
        d = [(str(f.read()))]
        strType = __import__("pyspark.sql.types", fromlist=["StringType"])
        df = self.spark.createDataFrame(d, getattr(strType, "StringType")())
        df.coalesce(1).write.mode(mode).text(
            self.arguments.get("output_file_path") + "/job.log")

    def __get_logger(self):
        clients_dir = pathlib.Path(__file__).parent.absolute()
        with open(str(clients_dir) + "/../jobs/logging.json", "r") as f:
            log_config = json.load(f)
        logging.config.dictConfig(log_config)
        # Add formatter to each handler to mask sensitive information. WI# 21541
        for h in logging.root.handlers:
            h.setFormatter(SensitiveDataFormatter(
                h.formatter))
        return logging.getLogger(__name__)

    def finish_job(self):
        self.save_log_file()

        # Delete temp argument file
        fs = (self.sc._jvm.org.apache.hadoop.fs.FileSystem.get(
            self.sc._jsc.hadoopConfiguration()))
        path = self.arguments.get("data_file_path") + \
            "/" + self.arguments.get("param_file_name")
        fs.delete(self.sc._jvm.org.apache.hadoop.fs.Path(path), True)

        # In case of jdbc connection type, delete SSL certificate file, if created
        if self.jdbc_connection_properties or self.jdbc_connection_properties_map:
            data_file_path = self.arguments.get("data_file_path")
            # If map of connection properties exist, delete the certificate file for each jdbc connection, otherwise delete file created for the common connection.
            if self.jdbc_connection_properties_map:
                for jdbc_connection_properties in list(self.jdbc_connection_properties_map.values()):
                    DbUtils.delete_certificate_file(
                        connection_properties=jdbc_connection_properties, spark=self.spark, base_path=data_file_path)        
            else:
                DbUtils.delete_certificate_file(
                    connection_properties=self.jdbc_connection_properties, spark=self.spark, base_path=data_file_path)

        if self.spark is not None:
            self.spark.stop()

    def save_status(self, status: str, additional_info: dict = {}):
        if self.show_progress:
            status_json = {"status": status}
            if len(additional_info):
                status_json.update(additional_info)
            self.save_data(self.arguments.get("output_file_path") +
                           "/status.json", status_json)

    def get_jdbc_connection_properties(self, data_source: dict):
        connection = get(
            data_source, "storage.connection")
        credentials = get(
            data_source, "storage.credentials")
        jdbc_connection_properties = None
        if connection is not None and credentials is not None:
            # If name of the ssl certificate file which is uploaded to volume/hdfs exists in parameters, fetch it to set location in connection properties
            ssl_cert_file_name = connection.get("ssl_cert_file_name")
            ssl_cert_location = None
            ssl_cert_file_type = None
            if ssl_cert_file_name:
                data_file_path = self.arguments.get("data_file_path")
                # In case of HDFS, the certificate file is available in working directory of each executor so file location will be file_name itself.
                if str(data_file_path).startswith("hdfs://"):
                    ssl_cert_location = ssl_cert_file_name
                else:
                    ssl_cert_location = "{}/{}".format(
                        data_file_path, ssl_cert_file_name)
                ssl_cert_file_type = "remote"
            else:
                ssl_cert_file_type = "local"
            jdbc_connection_properties = DbUtils.get_connection_properties(
                credentials.get("username"), credentials.get("password"),
                connection.get('jdbc_url'), connection.get('jdbc_driver'),
                connection.get('use_ssl'), connection.get('certificate'), ssl_cert_location=ssl_cert_location)

            # Add certificate file type(local or remote) which is required while deleting certificate file
            jdbc_connection_properties["ssl_cert_file_type"] = ssl_cert_file_type

        return jdbc_connection_properties

    def __get_location_type(self, data_source: dict):
        """
        Method to check location type and return default location type based on storage type if not specified in the arguments
        """
        location_type = get(
            data_source, "storage.connection.location_type")
        if location_type is None or str(location_type).strip() == "":
            # Get default location type based on storage type
            # For hive, it is metastore and for jdbc, it is jdbc
            if self.storage_type == StorageType.HIVE.value:
                return LocationType.HIVE_METASTORE.value
            elif self.storage_type == StorageType.JDBC.value:
                return LocationType.JDBC.value
        return location_type

    def __update_yarn_principal_in_conf(self, sparkApp, data_source: dict):
        """
        For Kerberized Hive, add yarn principal to spark conf. WI #26625
        - Get current conf properties from sparkContext
        - Set yarn principal in the conf
        - Stop the current sparkSession and 
        - Create new sparkSession with updated conf
        """
        kerberos_principal = get(
            data_source, "storage.credentials.kerberos_principal")
        if kerberos_principal:
            spark_conf = self.sc.getConf()
            yarn_principal = JoblibUtils.get_yarn_principal(kerberos_principal)
            spark_conf.set("spark.hadoop.yarn.resourcemanager.principal", yarn_principal)

            # Restart the spark session with updated config
            if self.spark is not None:
                self.spark.stop()
            self.spark = sparkApp.config(conf=spark_conf).getOrCreate()
            self.sc = self.spark.sparkContext
            self.logger.info(
                "Updated yarn principal in the spark configuration.")
            self.logger.info(
                "Updated spark configuration: {}".format(self.sc.getConf().getAll()))

    def __get_storage_details(self, data_source: dict, storage_type: str, sparkApp):
        """
        Fetches storage details based on storage type
        - For Hive metastore, sets metastore_url in sparkContext
        - For JDBC, constructs connection properties in format required by spark-jdbc
        Arguments:
            storage: The data source details passed in job arguments
            storage_type: The storage type- one of 'hive' or 'jdbc'
            sparkApp: The sparkApp
        Returns:
            location_type, jdbc_connection_properties
        """
        location_type = self.__get_location_type(data_source)
        jdbc_connection_properties = None

        # For hive metastore, setting metastore_url in sparkContext and for JDBC, generating connection properties
        if storage_type == StorageType.HIVE.value and (location_type is None or location_type == LocationType.HIVE_METASTORE.value):
            metastore_url = get(
                data_source, "storage.connection.metastore_url")
            if metastore_url:
                self.sc.setSystemProperty(
                    "hive.metastore.uris", metastore_url)
            # For kerberized hive in IAE, add spark.hadoop.yarn.resourcemanager.principal to the conf parameters
            kerberos_enabled = get(
                data_source, "storage.connection.kerberos_enabled")
            if kerberos_enabled is not None and str(kerberos_enabled).lower() == "true" and self.spark_type is not None and self.spark_type == SparkType.IAE_SPARK.value:
                self.__update_yarn_principal_in_conf(sparkApp, data_source)

        elif storage_type == StorageType.JDBC.value or (location_type is not None and location_type == LocationType.JDBC.value):
            # If one of storage type or location type is JDBC, generate connection properties
            jdbc_connection_properties = self.get_jdbc_connection_properties(data_source)

        return location_type, jdbc_connection_properties
