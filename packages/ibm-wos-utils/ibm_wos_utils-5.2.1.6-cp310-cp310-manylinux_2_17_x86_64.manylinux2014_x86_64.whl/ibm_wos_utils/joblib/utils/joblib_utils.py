# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2020, 2021
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

import os
import logging
import re

from ibm_wos_utils.joblib.exceptions.client_errors import UnsupportedOperationError
from ibm_wos_utils.joblib.utils import constants
from ibm_wos_utils.joblib.utils.environment import Environment
from ibm_wos_utils.joblib.utils.python_utils import get

logger = logging.getLogger(__name__)

environment = Environment()

class JoblibUtils:

    @classmethod
    def get_spark_instance_details(cls, credentials):
        spark_instance_details = dict()
        connection = credentials.get("connection")
        spark_credentials = credentials.get("credentials")
        if spark_credentials is None:  # This is for backward compatibility
            spark_credentials = credentials.get("spark_credentials")
        if connection is not None:
            endpoint = connection.get("endpoint")
            location_type = connection.get("location_type")
            spark_instance_details["location_type"] = location_type
            if location_type is not None and location_type == constants.SparkType.IAE_SPARK.value:
                # Get spark instance name and volume for IAE
                spark_instance_details["instance_id"] = connection.get(
                    "instance_id")
                spark_instance_details["display_name"] = connection.get(
                    "display_name")
                spark_instance_details["volume"] = connection.get("volume")
                # If cluster url is provided in connection details, then use it otherwise fetch the cluster url from job url
                if connection.get("url"):
                    endpoint = connection.get("url")
                # In case of IAE, endpoint will be jobs endpoint. So just fetching host part from the endpoint
                elif endpoint is not None:
                    match_obj = re.search("(.+?)://(.+?)/", endpoint)
                    if match_obj:
                        endpoint = endpoint[match_obj.start(): match_obj.end()-1]
        else:
            endpoint = spark_credentials.get("url")
        spark_instance_details["endpoint"] = endpoint
        spark_instance_details["username"] = spark_credentials.get("username")
        if "password" in spark_credentials:
            spark_instance_details["password"] = spark_credentials.get(
                "password")
        if "apikey" in spark_credentials:
            spark_instance_details["apikey"] = spark_credentials.get("apikey")
        return spark_instance_details

    @classmethod
    def get_spark_instance_id_from_url(cls, url: str) -> str:
        spark_instance_id = None
        if url:
            # Check if it is v3 or v4 jobs enpoint
            if "/v4/analytics_engines/" in url:
                pattern = "(.+?)/v4/analytics_engines/(.+?)/spark_applications"
            elif "/v3/instances/" in url:
                pattern = "(.+?)/v3/instances/(.+?)/spark/applications"
            else:
                pattern = "(.+?)/spark/v2/(.+?)/v2/jobs"
            match_obj = re.search(pattern, url)
            if match_obj:
                spark_instance_id = match_obj.groups()[1]
        return spark_instance_id

    @classmethod
    def is_default_volume_used(cls, job_payload, instance_volume):
        default_volume_used = False
        volumes = get(job_payload, "volumes")
        volume_name_key = "name"
        # For V3, the volumes will be at top level in the payload. If it is not found means it is V2 payload, try to fetch it from engine
        if volumes is None or len(volumes) == 0:
            volumes = get(job_payload, "engine.volumes")
            volume_name_key = "volume_name"
        if volumes is not None and len(volumes) > 0:
            volume_name = volumes[0].get(volume_name_key)
            if instance_volume == volume_name:
                default_volume_used = True
        return default_volume_used

    @classmethod
    def update_spark_parameters(cls, spark_parameters):
        if "max_num_executors" not in spark_parameters and "max_executors" in spark_parameters:
            spark_parameters["max_num_executors"] = spark_parameters.get(
                "max_executors")
        if "min_num_executors" not in spark_parameters and "min_executors" in spark_parameters:
            spark_parameters["min_num_executors"] = spark_parameters.get(
                "min_executors")
        if "executor_cores" not in spark_parameters and "max_executor_cores" in spark_parameters:
            spark_parameters["executor_cores"] = spark_parameters.get(
                "max_executor_cores")
        if "driver_cores" not in spark_parameters and "max_driver_cores" in spark_parameters:
            spark_parameters["driver_cores"] = spark_parameters.get(
                "max_driver_cores")

    @classmethod
    def get_column_by_modeling_role(cls, schema, modeling_role):
        for column in schema.get("fields"):
            col_modeling_role = get(column, "metadata.modeling_role")
            is_deleted_column = get(column, "metadata.deleted")
            if col_modeling_role is not None and col_modeling_role == modeling_role and not is_deleted_column:
                return column.get("name")
        return None
    
    @classmethod
    def get_columns_with_modeling_role(cls, schema: dict, modeling_role: str) -> list:
        """
        Returns the list of columns with the given modeling role from the given schema.
        :schema: The schema from the subscription JSON.
        :modeling_role: The modeling role for which the columns are to be returned.

        :returns: The list of columns with the given modeling role.
        """
        columns_with_modeling_role = list()

        for field_obj in schema.get("fields"):
            column_name = field_obj.get("name")
            column_modeling_role = get(field_obj, "metadata.modeling_role")
            is_deleted_column = get(field_obj, "metadata.deleted")
            if column_modeling_role is not None and column_modeling_role == modeling_role and not is_deleted_column:
                columns_with_modeling_role.append(column_name)

        return columns_with_modeling_role

    @classmethod
    def delete_local_file(cls, file_path: str):
        try:
            if file_path is not None and os.path.exists(file_path) and os.path.isfile(file_path):
                os.remove(file_path)
                logger.info('Deleted file {}'.format(file_path))
        except Exception as e:
            logger.warning(
                "Failed to delete file {}. Error: {}".format(file_path, str(e)))

    @classmethod
    def delete_file_from_hdfs(cls, spark, file_path: str):
        try:
            sc = spark.sparkContext
            fs = sc._jvm.org.apache.hadoop.fs.FileSystem.get(
                sc._jsc.hadoopConfiguration())
            if file_path:
                fs_file_path = sc._jvm.org.apache.hadoop.fs.Path(file_path)
                if fs.exists(fs_file_path) and fs.isFile(fs_file_path):
                    fs.delete(fs_file_path, True)
                    logger.info('Deleted file {}'.format(file_path))
        except Exception as e:
            logger.warning(
                "Failed to delete file {}. Error: {}".format(file_path, str(e)))

    @classmethod
    def does_dict_contain_req_details(cls, parameters_dict: dict, key_list: list):
        """
        Method to check if dictionary contains all the required details
        """
        if parameters_dict and all(parameters_dict.get(key) for key in key_list):
            return True
        return False

    @classmethod
    def get_job_payload_in_v3_format(cls, payload_dict: dict, job_params: dict):
        """
        Construct job payload for IAE V3 API
        Sample payload:
        {
            "application_details": {
                "application": "/openscale/job/main_job.py",
                "application_arguments": ["sample_job", "ibm_wos_utils.sample.batch.jobs.sample_spark_job.SampleJob", "{\"data_file_path\": \"/openscale/sample_job/75535645-6316-46f8-99cb-7383b66d9052/data\", \"output_file_path\": \"/openscale/sample_job/75535645-6316-46f8-99cb-7383b66d9052/output/fairness_run\", \"param_file_name\": \"tmph5crmfe5\", \"storage_type\": \"hive\"}"],
                "conf": {
                    "spark.app.name": "Sample Spark job with v3",
                    "spark.eventLog.enabled": "true"
                },
                "env": {
                    "PYTHONPATH": "/openscale/py_packages/wos_env/lib/python3.7/site-packages:/openscale/py_packages/wos_env/lib/python3.8/site-packages:/openscale/py_packages/wos_env/lib/python3.9/site-packages"
                },
                "driver-memory": "1G",
                "driver-cores": 1,
                "executor-memory": "1G",
                "executor-cores": 1,
                "num-executors": 1
            },
            "volumes": [{
                "name": "iae-wos-volume",
                "mount_path": "/openscale"
            }]
        }
        """
        # Construct the spark job details
        application_details = {
            "application": payload_dict.get("full_job_file"),
            "application_arguments": payload_dict.get("parameter_list"),
            "conf": payload_dict.get("conf"),
            "driver-memory": "{}G".format(payload_dict.get("driver_memory")),
            "driver-cores": payload_dict.get("driver_cores"),
            "executor-memory": "{}G".format(payload_dict.get("executor_memory")),
            "executor-cores": payload_dict.get("executor_cores"),
            "num-executors": payload_dict.get("max_num_executors")
        }
        env = job_params.get("env")
        if env is None:
            env = dict()
        if "PYTHONPATH" not in env:
            env["PYTHONPATH"] = environment.get_wos_env_location().replace("$mount_path", payload_dict.get("mount_path"))

        # Adding LD_LIBRARY_PATH to env. WI #31346
        if "LD_LIBRARY_PATH" not in env:
            env["LD_LIBRARY_PATH"] = environment.get_ld_library_path()

        # Setting python version to 3.11
        env["RUNTIME_PYTHON_ENV"] = "python311"

        application_details["env"] = env

        # Construct the volume details where job related data is stored
        volumes = [{
            "name": payload_dict.get("volume_name"),
            "mount_path": payload_dict.get("mount_path"),
            "source_sub_path": ""
        }]

        # Construct the payload
        job_payload = {
            "application_details": application_details,
            "volumes": volumes
        }

        # If IAE jobs queuing is enabled, add the corresponding flag to the job payload. WI #26109
        if environment.is_iae_jobs_queuing_enabled():
            job_payload["queuing_enabled"] = True
            logger.info("Queuing of IAE spark jobs is enabled")

        return job_payload

    @classmethod
    def get_yarn_principal(cls, hive_kerb_principal: str):
        """
        Get yarn principal from hive kerberos principal
        The hive_kerb_principal will be of the form user/host@REALM, replace the user with yarn
        """
        if "/" in hive_kerb_principal:
            user = hive_kerb_principal.split("/")[0]
        else:
            user = "hive"
        yarn_principal = hive_kerb_principal.replace(user, "yarn")
        return yarn_principal

    @classmethod
    def get_storage_types_from_data_sources(cls, job_args: dict):
        """
        Fetches storage type from each data source
        Arguments:
            job_args:  The job arguments containing data source details
        Returns:
            storage types map
        """
        storage_type_map = {}
        data_sources = job_args.get("tables", [])
        hive_metastores = set()

        for data_source in data_sources:
            data_source_type = data_source.get("type")
            # Check if storage details exist for the data source. If not found, get it from common storage location. WI #29075
            storage_details = data_source.get("storage") if data_source.get("storage") else job_args.get("storage")
            # Store storage details at data source level which is required during job execution
            data_source["storage"] = storage_details
            storage_type = storage_details.get("type")

            # Check if different hive databases are configured. If yes, then return an error as spark sessions with shared sparkContext can not connect to different metastores at the same time.
            if storage_type is not None and storage_type == constants.StorageType.HIVE.value:
                metastore_url = get(
                    storage_details, "connection.metastore_url")
                if metastore_url:
                    hive_metastores.add(metastore_url)
                    if len(hive_metastores) > 1:
                        raise UnsupportedOperationError(message="The spark job can not access data from different hive metastores.")

            storage_type_map[data_source_type] = storage_type
        return storage_type_map
