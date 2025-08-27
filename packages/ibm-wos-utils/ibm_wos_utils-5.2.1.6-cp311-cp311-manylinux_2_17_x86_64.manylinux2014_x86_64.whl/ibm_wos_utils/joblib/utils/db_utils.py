# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2020, 2021
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

import base64
import tempfile
import logging
import re
import ssl
from datetime import datetime

try:
    from pyspark.sql.types import *
    import pyspark.sql.functions as F
except ImportError as iex:
    pass

from ibm_wos_utils.joblib.utils.constants import *
from ibm_wos_utils.joblib.utils.date_util import DateUtil
from ibm_wos_utils.joblib.exceptions.client_errors import *
from ibm_wos_utils.joblib.utils import hive_utils
from ibm_wos_utils.joblib.utils.jdbc_utils import JDBCUtils
from ibm_wos_utils.joblib.utils.joblib_utils import JoblibUtils
from ibm_wos_utils.joblib.utils.param_utils import get, get_boolean_value

logger = logging.getLogger(__name__)


class DbUtils:
    """
    Utility class for database interaction
    """

    @classmethod
    def get_table_as_dataframe(
            cls,
            spark,
            location_type: str,
            database_name: str,
            table_name: str,
            schema_name: str = None,
            connection_properties: dict = None,
            sql_query: str = None,
            columns_to_map: list = [],
            columns_to_filter: list = [],
            record_timestamp_column: str = None,
            start_time: str = None,
            end_time: str = None,
            probability_column: str = None,
            order_by_timestamp_desc: bool = False,
            limit: int = None,
            partition_column=None,
            lower_bound=None,
            upper_bound=None,
            num_partitions=None,
            is_partition_col_timestamp=False):
        """Get database table as dataframe.

        Additionally, it does:
        - Converts any column of boolean type to string type
        - Filter out header row based on columns_to_filter. Only uses the first column found in the table.
        - If provided, fetches records based on the timestamps

        It does NOT do any validation.

        Arguments:
            spark {SparkSession} -- Spark Session to use
            location_type {str} -- The location type of data source. It can be one of ['metastore', 'jdbc']
            database_name {str} -- Name of Database
            table_name {str} -- Name of table in the database

        Keyword Arguments:
            schema_name {str} -- Name of schema
            connection_properties {dict} -- Dictionary of JDBC connection details like url, user, password, driver
            sql_query {str} -- SQL query
            columns_to_map {list} -- List of columns to map from lowercase to correct case
            columns_to_filter {list} -- List of columns to filter out header row. Uses the first column found in table (default: {[]})
            record_timestamp_column {str} -- Name of the column with modeling role record-timestamp (default: {None})
            start_time {str} -- Start Time in ISO format `%Y-%m-%dT%H:%M:%S.%f` (default: {None})
            end_time {str} -- End Time in ISO format `%Y-%m-%dT%H:%M:%S.%f` (default: {None})
            probability_column {str} - Probability column
            order_by_timestamp_desc {bool} - To apply order by on the timestamp column in descending order (latest first).
            limit {int} - Limit on number of records to be read.
            partition_column {str} -- Name of the column used for partition. Used when location type is jdbc.
            lower_bound --  The minimum value of partition column, used to decide partition stride. Used when location type is jdbc.
            upper_bound -- the maximum value of partition column, used to decide partition stride. Used when location type is jdbc.
            num_partitions -- the number of partitions. Used when location type is jdbc.
            is_partition_col_timestamp -- whether the partition column is timestamp or not. Need to be provided when the partition_column is not same as record_timestamp_column.
        Returns:
            pyspark Dataframe

        """
        logger.info("Reading data as spark dataframe from the database.")
        start_ts = DateUtil.get_current_datetime()
        # Defaulting to hive metastore
        if location_type is None or location_type in [LocationType.HIVE_METASTORE.value, StorageType.HIVE.value]:
            spark_df = hive_utils.get_table_as_dataframe(spark,
                                                         database_name,
                                                         table_name,
                                                         columns_to_map,
                                                         columns_to_filter=columns_to_filter,
                                                         record_timestamp_column=record_timestamp_column,
                                                         start_time=start_time,
                                                         end_time=end_time,
                                                         order_by_timestamp_desc=order_by_timestamp_desc,
                                                         limit=limit,
                                                         sql_query=sql_query)
            return spark_df
        elif location_type == LocationType.JDBC.value:
            if num_partitions:
                partition_column, lower_bound, upper_bound = DbUtils.get_partition_column_details(
                    spark=spark,
                    database_name=database_name, table_name=table_name, schema_name=schema_name,
                    connection_properties=connection_properties,
                    record_timestamp_column=record_timestamp_column,
                    start_time=start_time, end_time=end_time,
                    partition_column=partition_column,
                    lower_bound=lower_bound,
                    upper_bound=upper_bound,
                    is_partition_col_timestamp=is_partition_col_timestamp)
            spark_df = JDBCUtils.get_table_as_dataframe(spark,
                                                        database_name,
                                                        table_name,
                                                        schema_name,
                                                        connection_properties,
                                                        sql_query=sql_query,
                                                        probability_column=probability_column,
                                                        columns_to_map=columns_to_map,
                                                        partition_column=partition_column,
                                                        lower_bound=lower_bound,
                                                        upper_bound=upper_bound,
                                                        num_partitions=num_partitions)
        else:
            raise Exception(
                "Unsupported storage location type: {}. Only supported storage location types are {}.".format(
                    location_type, [LocationType.HIVE_METASTORE.value, LocationType.JDBC.value]))

        logger.info(spark_df.printSchema())
        logger.info(
            "******* Number of Partitions: {} ********".format(spark_df.rdd.getNumPartitions()))

        # Convert boolean columns to string
        spark_df_dtypes = dict(spark_df.dtypes)
        logger.info(spark_df_dtypes)
        for col in spark_df.columns:
            if spark_df_dtypes[col] == "boolean":
                spark_df = spark_df.withColumn(
                    col, spark_df[col].cast("string"))
                logger.info(
                    " - Changed column {} of type boolean to type string.".format(col))

        if record_timestamp_column is not None and record_timestamp_column in spark_df.columns:
            # assumptions: start_time and end_time are in isoformat
            # %Y-%m-%dT%H:%M:%S.%fZ
            if start_time is not None:
                start_time = datetime.strptime(start_time, TIMESTAMP_FORMAT)
                spark_df = spark_df.where(
                    F.col(record_timestamp_column) >= start_time)

            if end_time is not None:
                end_time = datetime.strptime(end_time, TIMESTAMP_FORMAT)
                spark_df = spark_df.where(
                    F.col(record_timestamp_column) <= end_time)

            if order_by_timestamp_desc:
                # Sorting the rows on timestamp column in descending order
                spark_df = spark_df.orderBy(
                    record_timestamp_column, ascending=False)

        # Applying limit if given
        spark_df = spark_df.limit(limit) if limit else spark_df

        logger.info(spark_df.explain())
        logger.info(spark_df.printSchema())
        logger.info("Total time to read data from the database: {} seconds".format(
            DateUtil.get_time_diff_in_seconds(start_ts)))
        return spark_df

    @classmethod
    def get_partition_column_details(cls, spark,
                                     database_name,
                                     table_name,
                                     schema_name,
                                     connection_properties,
                                     record_timestamp_column,
                                     start_time,
                                     end_time,
                                     partition_column,
                                     lower_bound,
                                     upper_bound,
                                     is_partition_col_timestamp):

        if partition_column and lower_bound and upper_bound:
            return partition_column, lower_bound, upper_bound

        if not partition_column:
            if not record_timestamp_column:
                return None, None, None
            partition_column = record_timestamp_column

        if partition_column == record_timestamp_column:
            is_partition_col_timestamp = True

        st_time = DateUtil.get_current_datetime()
        # truncate extra quotes in partition column name
        partition_column = partition_column.replace("\"", "")
        sql_query = "SELECT MIN(\"{0}\") PMIN, MAX(\"{1}\") PMAX from \"{2}\".\"{3}\"".format(
            partition_column, partition_column, schema_name, table_name)
        
        if record_timestamp_column is not None:
            where_clauses = []
            if start_time is not None:
                start_time = datetime.strptime(start_time, TIMESTAMP_FORMAT)
                where_clauses.append("\"{}\" >= '{}'".format(record_timestamp_column, start_time))
            if end_time is not None:
                end_time = datetime.strptime(end_time, TIMESTAMP_FORMAT)
                where_clauses.append("\"{}\" <= '{}'".format(record_timestamp_column, end_time))
            
            if where_clauses:
                where_clauses = " AND ".join(where_clauses)
                sql_query += " WHERE {}".format(where_clauses)
            
        logger.info("Executing query {}".format(sql_query))
        spark_df = JDBCUtils.get_table_as_dataframe(spark,
                                                    database_name,
                                                    table_name,
                                                    schema_name,
                                                    connection_properties,
                                                    sql_query=sql_query)

        response = spark_df.collect()[0]
        # Sometimes in postgres the columns converted to be in small case.
        p_min = response["PMIN"] if "PMIN" in response else response["pmin"]
        p_max = response["PMAX"] if "PMAX" in response else response["pmax"]

        if (p_min is None) or (p_max is None):
            logger.info("One of lower bound '{}' or upper bound '{}' for the partition column '{}' is None. Returning.".format(p_min, p_max, partition_column))
            return None, None, None

        if is_partition_col_timestamp:
            p_min = p_min.strftime("%Y-%m-%d %H:%M:%S.%f")
            p_max = p_max.strftime("%Y-%m-%d %H:%M:%S.%f")

        logger.info("Got the lower bound {} and upper bound {} values for the partition column {} in {} seconds".format(
            p_min, p_max, partition_column, DateUtil.get_time_diff_in_seconds(st_time)))

        return partition_column, p_min, p_max

    @classmethod
    def write_dataframe_to_table(
            cls,
            spark_df,
            location_type: str,
            database_name: str,
            table_name: str,
            schema_name: str = None,
            mode: str = WriteMode.APPEND.value,
            connection_properties: dict = None,
            probability_column: str = None,
            spark=None
    ):
        """
        Writes a spark dataframe to database table
        Arguments:
            spark_df {SparkDataFrame} -- Spark dataframe to be written to the database
            location_type {str} -- The location type of data source. It can be one of ['metastore', 'jdbc']
            database_name {str} -- Name of Database
            table_name {str} -- Name of table in the database

        Keyword Arguments:
            schema_name {str} -- Name of schema
            mode {str} -- Mode of writing. Default is append mode.
            connection_properties {dict} -- Dictionary of JDBC connection details like url, user, password, driver
            probability_column {str} - Probability column
            spark {SparkSession} -- Spark Session to use
        """

        logger.info("Writing data to the database in {} mode".format(mode))
        start_ts = DateUtil.get_current_datetime()
        # Checking location_type, defaulting to hive metastore
        if location_type is None or location_type in [LocationType.HIVE_METASTORE.value, StorageType.HIVE.value]:
            hive_utils.write_dataframe_to_table(
                spark_df,
                mode,
                database_name,
                table_name,
                schema_name=schema_name
            )

        elif location_type == LocationType.JDBC.value:
            spark_df = JDBCUtils.write_dataframe_to_table(
                spark_df,
                mode,
                database_name,
                table_name,
                schema_name,
                connection_properties,
                probability_column=probability_column,
                spark=spark
            )
        else:
            raise Exception(
                "Unsupported storage location type: {}. Only supported storage location types are {}.".format(
                    location_type, [LocationType.HIVE_METASTORE.value, LocationType.JDBC.value]))

        logger.info("Total time to write data to the database: {} seconds".format(
            DateUtil.get_time_diff_in_seconds(start_ts)))

    @classmethod
    def get_connection_properties(
            cls,
            user: str,
            password: str,
            url: str,
            driver: str = None,
            use_ssl=None,
            ssl_certificate=None,
            ssl_cert_location=None):
        """
        Construct dictionary of connection parameters
        Arguments:
            user {str} -- Username
            password {str} -- Password
            url {str} -- JDBC URL

        Keyword Arguments:
            driver {str} -- Name of the JDBC driver
            ssl_certificate -- The SSL certificate
            ssl_cert_location -- Location of SSL certificate file, if uploaded in volume or hdfs
        """

        connection_properties = dict()
        if user is not None:
            connection_properties["user"] = user
        if password is not None:
            connection_properties["password"] = password
        connection_properties["url"] = url
        if driver is not None and driver.strip() != "":
            connection_properties["driver"] = driver
        if use_ssl is not None and get_boolean_value(use_ssl) is True:
            if "sslconnection=true" not in url.lower():
                connection_properties["sslConnection"] = "true"
            # Add location of certificate file.
            # If location of file uploaded in volume or hdfs is provided then use it otherwise create certificate file only if certificate text is provided. #21139
            if ssl_cert_location:
                connection_properties["sslCertLocation"] = ssl_cert_location
            elif ssl_certificate:
                f = cls.create_certificate_file(ssl_certificate)
                connection_properties["sslCertLocation"] = f
        # Add connection timeout
        connection_properties["connectionTimeout"] = str(
            DEFAULT_CONNECTION_TIMEOUT)
        connection_properties["fetchSize"] = str(DEFAULT_FETCH_SIZE)
        return connection_properties

    @classmethod
    def create_certificate_file(cls, certificate_base64):
        certificate = None
        cert_file = None
        if certificate_base64:
            # if certificate already set in the connection_details
            if 'BEGIN CERTIFICATE' not in certificate_base64:
                # If 'BEGIN CERTIFICATE' is not present, assuming that it will be a base64 encoded.
                certificate = base64.b64decode(
                    certificate_base64.strip()).decode()
            else:
                certificate = certificate_base64.strip()

        with tempfile.NamedTemporaryFile(mode="w", prefix="db2ssl_", suffix="_cert.arm", delete=False) as f:
            cert_file = f.name
            f.write(certificate)
        return cert_file

    @classmethod
    def check_and_create_ssl_cert_file(cls, arguments):
        certificate_file = None
        connection = get(arguments, "storage.connection")
        if connection:
            use_ssl = connection.get("use_ssl")
            certificate = connection.get("certificate")
            if use_ssl is not None and get_boolean_value(use_ssl) is True and certificate:
                certificate_file = cls.create_certificate_file(certificate)
        return certificate_file

    @classmethod
    def get_certificate_from_host(cls, url):
        host = None
        port = None
        certificate = None
        host_str = re.search("//(.*)/", url)
        if host_str:
            host_str = host_str.group(1)
            if ":" in host_str:
                arr = host_str.split(":")
                host = arr[0]
                port = arr[1]
        certificate = ssl.get_server_certificate(
            (host, port))
        return certificate

    @classmethod
    def delete_certificate_file(cls, cert_file=None, connection_properties=None, spark=None, base_path=None):
        # If file name is specified, use it otherwise get it from connection_properties
        if cert_file is None and connection_properties is not None:
            cert_file = connection_properties.get("sslCertLocation")
        if cert_file:
            # Check type of SSL certificate file to determine whether to delete from volume/hdfs or local
            ssl_cert_file_type = None
            if connection_properties:
                ssl_cert_file_type = connection_properties.get(
                    "ssl_cert_file_type")
            if ssl_cert_file_type is not None and ssl_cert_file_type == "remote":
                # In case of HDFS, file location will not contain base path as file exists in working directory of each executor.
                # The file in each executor is deleted once job finishes. To delete file from HDFS, prefixing the file name with base_path.
                if base_path and (base_path not in cert_file):
                    cert_file = "{}/{}".format(base_path, cert_file)
                JoblibUtils.delete_file_from_hdfs(spark, cert_file)
            else:
                JoblibUtils.delete_local_file(cert_file)

    @classmethod
    def list_columns(
            cls,
            spark,
            location_type: str,
            database_name: str,
            table_name: str,
            schema_name: str = None,
            connection_properties: dict = None,
            probability_column: str = None,
            columns_to_map: list = None
    ):

        columns = None
        logger.info("Fetching column types of the table from the database.")
        start_ts = DateUtil.get_current_datetime()
        # Defaulting to hive metastore
        if location_type is None or location_type in [LocationType.HIVE_METASTORE.value, StorageType.HIVE.value]:
            columns = spark.catalog.listColumns(
                tableName=table_name, dbName=database_name)
        elif location_type == LocationType.JDBC.value:
            columns = JDBCUtils.list_columns(
                spark, database_name,
                table_name, schema_name,
                connection_properties, probability_column=probability_column, columns_to_map=columns_to_map)
        else:
            raise Exception(
                "Unsupported storage location type: {}. Only supported storage location types are {}.".format(
                    location_type, [LocationType.HIVE_METASTORE.value, LocationType.JDBC.value]))
        logger.info("Total time to fetch column types of the table from the database: {} seconds".format(
            DateUtil.get_time_diff_in_seconds(start_ts)))
        return columns
