# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2020, 2021
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

import logging
import re
try:
    import pyspark.sql.functions as F
except ImportError as iex:
    pass

from ibm_wos_utils.joblib.exceptions.client_errors import *
from ibm_wos_utils.joblib.utils.constants import *


logger = logging.getLogger(__name__)


class JDBCUtils:
    """
    Utility class for database interaction using JDBC
    """

    @classmethod
    def get_table_as_dataframe(
            cls,
            spark,
            database_name: str,
            table_name: str,
            schema_name: str,
            connection_properties: dict,
            sql_query: str = None,
            probability_column: str = None,
            columns_to_map: list = None,
            partition_column=None,
            lower_bound=None,
            upper_bound=None,
            num_partitions=None):
        """
        Get database table as dataframe using JDBC
        Arguments:
            spark {SparkSession} -- Spark Session to use
            database_name {str} -- Name of Database
            table_name {str} -- Name of table in the database
            schema_name {str} -- Schema name
            connection_properties {dict} -- Dictionary of JDBC connection details like url, user, password, driver
            partition_column {str} -- Name of the column used for partition
            lower_bound --  The minimum value of partition column, used to decide partition stride
            upper_bound -- the maximum value of partition column, used to decide partition stride
            num_partitions -- the number of partitions

        Keyword Arguments:
            sql_query {str} -- SQL query
            probability_column {str} -- Probability column
        """
        # Get instance of JDBC util based on the database type
        util = cls.get_util_instance(spark, database_name, table_name,
                                     schema_name, connection_properties, sql_query, probability_column)
        spark_df = None
        try:
            spark_df = util.read_data(columns_to_map=columns_to_map,
                                      partition_column=partition_column,
                                      lower_bound=lower_bound,
                                      upper_bound=upper_bound,
                                      num_partitions=num_partitions)
        except Exception as e:
            error_message = "Error while reading from database with JDBC. Error: {}".format(
                str(e))
            # If specified driver does not exist, raise error with proper message.
            if "java.lang.ClassNotFoundException" in str(e):
                driver = connection_properties.get("driver")
                error_message = "Specified JDBC driver '{}' could not be found.".format(
                    driver)
            raise DatabaseError(error_message)
        return spark_df

    @classmethod
    def write_dataframe_to_table(
            cls,
            spark_df,
            mode,
            database_name: str,
            table_name: str,
            schema_name: str,
            connection_properties: dict,
            probability_column: str = None,
            spark=None,
            create_table_column_types: str=None):

        # Get instance of JDBC util based on the database type
        util = cls.get_util_instance(spark, database_name, table_name,
                                     schema_name, connection_properties, probability_column=probability_column)
        try:
            # Check if table exists in database before writing the data
            if spark is not None:
                table_exists = util.check_if_table_exists()
                if not table_exists:
                    raise DatabaseError("Table {}.{} could not be found in the database.".format(
                        schema_name, table_name))
            util.write_data(spark_df, mode, create_table_column_types)
        except Exception as e:
            error_message = "Error while writing to database with JDBC. Error: {}".format(
                str(e))
            # If specified driver does not exist, raise error with proper message.
            if "java.lang.ClassNotFoundException" in str(e):
                driver = connection_properties.get("driver")
                error_message = "Specified JDBC driver '{}' could not be found.".format(
                    driver)
            raise DatabaseError(error_message)

    @classmethod
    def list_columns(
            cls,
            spark,
            database_name: str,
            table_name: str,
            schema_name: str,
            connection_properties: dict,
            probability_column: str = None,
            columns_to_map: list = None):

        # Get instance of JDBC util based on the database type
        util = cls.get_util_instance(spark, database_name, table_name,
                                     schema_name, connection_properties, probability_column=probability_column)
        columns = []
        try:
            dtypes_dict = util.get_column_types(columns_to_map=columns_to_map)
            from collections import namedtuple
            Column = namedtuple(
                "Column", "name dataType")
            for field in dtypes_dict:
                columns.append(Column(
                    name=field,
                    dataType=dtypes_dict[field]))
        except Exception as e:
            error_message = "Error while fetching database column types with JDBC. Error: {}".format(
                str(e))
            raise DatabaseError(error_message)
        return columns

    @classmethod
    def get_db_type(cls, jdbc_url: str):
        if jdbc_url is None or jdbc_url.strip() == "":
            raise ValueError("JDBC URL is not specified or is empty.")
        jdbc_url = jdbc_url.lower()
        if jdbc_url.startswith("jdbc:db2"):
            return JDBCDatabaseType.DB2.value
        elif jdbc_url.startswith("jdbc:hive"):
            return JDBCDatabaseType.HIVE.value
        elif jdbc_url.startswith("jdbc:postgresql"):
            return JDBCDatabaseType.POSTGRESQL.value
        else:
            raise ValueError(
                "JDBC URL is incorrect or the specified database is not supported.")

    @classmethod
    def get_util_instance(
            cls,
            spark,
            database_name: str,
            table_name: str,
            schema_name: str,
            connection_properties: dict,
            sql_query: str = None,
            probability_column: str = None):
        
        url = connection_properties.get("url")
        # Get modified jdbc_url by appending given database_name if it does not exist. WI #26127
        if url is not None and not url.endswith(database_name):
            url = cls.append_dbname_to_jdbc_url(url, database_name)
            connection_properties["url"] = url
        # Get the database type from JDBC URL
        database_type = cls.get_db_type(url)
        if database_type == JDBCDatabaseType.DB2.value:
            return DB2JDBCUtil(spark, database_name, table_name, schema_name, connection_properties, sql_query=sql_query, probability_column=probability_column)
        elif database_type == JDBCDatabaseType.HIVE.value:
            return HiveJDBCUtil(spark, database_name, table_name, schema_name, connection_properties, sql_query=sql_query, probability_column=probability_column)
        elif database_type == JDBCDatabaseType.POSTGRESQL.value:
            return PostgresJDBCUtil(spark, database_name, table_name, schema_name, connection_properties, sql_query=sql_query, probability_column=probability_column)

    @classmethod
    def append_dbname_to_jdbc_url(cls, jdbc_url: str, database_name: str):
        # This method adds database_name to jdbc_url if it does not contain it
        # If the jdbc_url already contains some database_name, it is overridden with given database name
        # Ex. 
        # 1. append_dbname_to_jdbc_url("jdbc:db2://<host>:50000", "SAMPLE") will return jdbc:db2://<host>:50000/SAMPLE
        # 2. append_dbname_to_jdbc_url("jdbc:db2://<host>:50000/BLUDB", "SAMPLE") will return jdbc:db2://<host>:50000/SAMPLE
        
        # Regex to fetch jdbc:db2://<host>:<port> part from the url
        url_regex = "^jdbc:\w+://+[\w.*_-]+:?\d*"
        match_str = re.search(url_regex, jdbc_url)
        if match_str:
            jdbc_url = match_str.group().strip()
            # Append given database name to the jdbc_url
            if database_name:
                jdbc_url = "{}/{}".format(jdbc_url, database_name)
        return jdbc_url



class BaseJDBCUtil:
    """
    Base class for different JDBC database types
    """

    def __init__(self, spark, database_name: str, table_name: str, schema_name: str, connection_properties: dict, sql_query: str = None, probability_column: str = None):
        self.spark = spark
        self.database_name = database_name
        self.table_name = table_name
        self.schema_name = schema_name
        self.connection_properties = connection_properties
        self.sql_query = sql_query
        self.probability_column = probability_column
        self.url = connection_properties.get("url")

    def is_dtype_conversion_needed(self, dtypes_dict, column_name, expected_dtype):
        dtype_conversion_needed = False
        for col in dtypes_dict:
            # Column names can be in the form of "table_name.column_name" so pick only column name
            col_name = col
            if "." in col:
                col_name = col.split(".")[1]
            if col_name.lower() == column_name.lower():
                col_dtype = dtypes_dict.get(col)
                if col_dtype != expected_dtype:
                    dtype_conversion_needed = True
                break
        return dtype_conversion_needed

    def get_col_names_in_expected_case(self, spark_df, columns_to_map):
        if columns_to_map:
            logger.info("Converting column names to expected case.")
            lowercase_cols = list(
                map(lambda col: col.lower(), columns_to_map))
            expected_cols = list(
                map(lambda col: columns_to_map[lowercase_cols.index(
                    col.lower())] if col.lower() in lowercase_cols else col, spark_df.columns))
            spark_df = spark_df.toDF(*expected_cols)
        return spark_df


class DB2JDBCUtil(BaseJDBCUtil):
    """
    Class for interaction with DB2 using JDBC
    """

    def __init__(self, spark, database_name, table_name, schema_name, connection_properties, sql_query=None, probability_column=None):
        super().__init__(spark, database_name, table_name, schema_name,
                         connection_properties, sql_query=sql_query, probability_column=probability_column)
        self.db_table = "\"{}\".\"{}\"".format(
            self.schema_name, self.table_name)

    def read_data(self, columns_to_map=None, partition_column=None, lower_bound=None, upper_bound=None, num_partitions=None):
        logger.info("Reading data from DB2 data source.")
        if self.sql_query is None:
            self.sql_query = "(select * from {})".format(self.db_table)
        if not (self.sql_query.startswith("(") and self.sql_query.endswith(")")):
            self.sql_query = "({})".format(self.sql_query)

        spark_df = self._read(self.sql_query, columns_to_map=columns_to_map, partition_column=partition_column,
                              lower_bound=lower_bound, upper_bound=upper_bound, num_partitions=num_partitions)
        return spark_df

    def write_data(self, spark_df, mode, create_table_column_types=None):
        logger.info("Writing spark dataframe to DB2 data source.")
        self._write(spark_df, self.db_table, mode, create_table_column_types)

    def get_column_types(self, columns_to_map=None):
        logger.info("Fetching column types from DB2 data source.")
        spark_df = self._read(self.db_table, columns_to_map=columns_to_map)
        dtypes_dict = dict(spark_df.dtypes)
        return dtypes_dict

    def check_if_table_exists(self):
        logger.info(
            "Checking if table {} exists in DB2 to write the data.".format(self.db_table))
        table_exists = False
        try:
            spark_df = self._read(self.db_table)
            if spark_df is not None:
                table_exists = True
        except Exception as e:
            if "SQLCODE=-204, SQLSTATE=42704" in str(e):
                logger.warning(
                    "Table {} could not be found.".format(self.db_table))
            else:
                raise DatabaseError("Error while checking if table {} exists in database. Error: {}".format(
                    self.db_table, str(e)))
        return table_exists

    def _read(self, query, columns_to_map=None, partition_column=None, lower_bound=None, upper_bound=None, num_partitions=None):
        read_jdbc = self.spark.read.format("jdbc").option(
            "url", self.url).option("dbtable", query)

        if partition_column is not None and lower_bound is not None and upper_bound is not None and num_partitions is not None:
            logger.info("Partition options: partition column {}, lower bound {}, upper bound {}, number of partitions {}".format(
                partition_column, lower_bound, upper_bound, num_partitions))
            read_jdbc.option("partitionColumn", partition_column).option(
                "lowerBound", lower_bound).option("upperBound", upper_bound).option("numPartitions", num_partitions)

        for k, v in self.connection_properties.items():
            if v:
                read_jdbc.option(k, v)

        # If some column contains special characters like space or $, reading with spark-JDBC fails with pyspark.sql.utils.ParseException. WI #28110
        # To fix this, disabling predicate pushdown.
        special_chars = [" ", "$"]
        if columns_to_map is None or len(columns_to_map) == 0 or any(char in column for column in columns_to_map for char in special_chars):
            read_jdbc.option("pushDownPredicate", "false")

        spark_df = read_jdbc.load()

        dtypes_dict = dict(spark_df.dtypes)
        if self.probability_column is not None:
            # Check if probability column needs to be converted to array
            if self.is_dtype_conversion_needed(dtypes_dict, self.probability_column, "array"):
                spark_df = self._get_probability_as_array(spark_df)
        # If column names in expected case are provided, then convert column names from spark_df to expected case
        if columns_to_map:
            spark_df = self.get_col_names_in_expected_case(
                spark_df, columns_to_map)
        return spark_df

    def _write(self, spark_df, dbtable, mode, create_table_column_types=None):


        # Convert column types if needed to match the database schema
        # Check if probability column needs to be converted back to string as it was converted to array while reading
        if self.probability_column is not None:
            dtypes_dict = dict(spark_df.dtypes)
            if self.is_dtype_conversion_needed(dtypes_dict, self.probability_column, "string"):
                spark_df = self._get_probability_as_string(spark_df)

        if create_table_column_types:
            # remove all None values from connection properties before sending to jdbc
            connection_properties_non_null = {k: v for k, v in self.connection_properties.items() if v is not None}
            
            spark_df.write.option("createTableColumnTypes", create_table_column_types) \
                .jdbc(self.url, dbtable, mode=mode, properties=connection_properties_non_null)
        else:
            spark_df.write.jdbc(self.url, dbtable, mode=mode, properties=self.connection_properties)
        
    def _get_probability_as_array(self, spark_df):
        logger.info("Converting probability column to array.")
        # Get the first row to check format in which probability value is stored. It can be in one of [a, b] or a|b.
        first_row_df = spark_df.filter(
            F.col(self.probability_column).isNotNull()).limit(1)
        first_row = first_row_df.select(
            self.probability_column).limit(1).collect()
        if first_row is None or len(first_row) == 0:
            # This is empty data case. Returning existing dataframe. #WI 21508
            try:
                spark_df = spark_df.withColumn(
                    self.probability_column,
                    F.split(
                        F.col(self.probability_column), ",\s*").cast("array<double>"))
            except Exception as e:
                logger.warning(
                    "Error while converting probability column to array in table {}. Error: {}".format(self.db_table, str(e)))
            return spark_df

        prob_val = str(first_row[0][0])
        if prob_val.startswith("[") and prob_val.endswith("]"):
            spark_df = spark_df.withColumn(
                self.probability_column, F.from_json(F.col(self.probability_column), "array<double>"))
        elif "|" in prob_val:
            delimeter = '\|'
            spark_df = spark_df.withColumn(
                self.probability_column,
                F.split(
                    F.col(self.probability_column), delimeter).cast("array<double>"))
        return spark_df

    def _get_probability_as_string(self, spark_df, delimeter='|'):
        logger.info("Converting probability column to string.")
        spark_df = spark_df.withColumn(
            self.probability_column,
            F.concat_ws(
                delimeter, F.col(self.probability_column)))
        return spark_df


class HiveJDBCUtil(BaseJDBCUtil):
    """
    Class for interaction with DB2 using JDBC
    """

    def read_data(self, partition_column=None, lower_bound=None, upper_bound=None, num_partitions=None):
        logger.info("Reading data from Hive data source.")
        dbtable = "{}.{}".format(self.database_name, self.table_name)
        if self.sql_query is None:
            self.sql_query = "(select * from {}) as {}".format(dbtable,
                                                               self.table_name)
        if not (self.sql_query.startswith("(") and self.sql_query.endswith(")")):
            self.sql_query = "({})".format(self.sql_query)

        spark_df = self._read(self.sql_query, partition_column=partition_column,
                              lower_bound=lower_bound, upper_bound=upper_bound, num_partitions=num_partitions)
        return spark_df

    def get_column_types(self):
        logger.info("Fetching column types from Hive data source.")
        dbtable = "{}.{}".format(self.database_name, self.table_name)
        spark_df = self._read(dbtable)
        dtypes_dict = dict(spark_df.dtypes)
        return dtypes_dict

    def _read(self, query, partition_column=None, lower_bound=None, upper_bound=None, num_partitions=None):
        # Register hive dialect
        self._register_dialect()

        read_jdbc = self.spark.read.format("jdbc").option(
            "url", self.url).option("dbtable", query)

        if partition_column is not None and lower_bound is not None and upper_bound is not None and num_partitions is not None:
            read_jdbc.option("partitionColumn", partition_column).option(
                "lowerBound", lower_bound).option("upperBound", upper_bound).option("numPartitions", num_partitions)

        for k, v in self.connection_properties.items():
            if v:
                read_jdbc.option(k, v)

        spark_df = read_jdbc.load()

        # Rename all the columns by removing whitespaces and the table_name prefix
        new_column_name_list = list(map(lambda x: x.split(
            ".")[1].replace('\s*', ''), spark_df.columns))
        spark_df = spark_df.toDF(*new_column_name_list)

        if self.probability_column is not None:
            # In case of hive, the probability column will be read as string with the dialect so converting it.
            spark_df = self._get_probability_as_array(spark_df)
        return spark_df

    def _get_probability_as_array(self, spark_df):
        logger.info("Converting probability column to array.")
        spark_df = spark_df.withColumn(
            self.probability_column, F.from_json(F.col(self.probability_column), "array<double>"))
        return spark_df

    def _register_dialect(self):
        from ibm_wos_utils.joblib.utils.dialect_utils import DialectUtils
        # Register hive dialect
        DialectUtils.register_hive_dialect(self.spark)

class PostgresJDBCUtil(BaseJDBCUtil):
    """
    Class for interaction with Postgres using JDBC
    """

    def __init__(self, spark, database_name, table_name, schema_name, connection_properties, sql_query=None, probability_column=None):
        super().__init__(spark, database_name, table_name, schema_name,
                         connection_properties, sql_query=sql_query, probability_column=probability_column)
        self.db_table = "\"{}\".\"{}\"".format(
            self.schema_name, self.table_name)

    def read_data(self, columns_to_map=None, partition_column=None, lower_bound=None, upper_bound=None, num_partitions=None):
        logger.info("Reading data from Postgres data source.")
        if self.sql_query is None:
            self.sql_query = "(select * from {})".format(self.db_table)
        if not (self.sql_query.startswith("(") and self.sql_query.endswith(")")):
            self.sql_query = "({})".format(self.sql_query)
        # Postgres requires to define the in brackets select statement by AS. Defined by table name 
        self.sql_query += " AS {}".format(self.table_name)
        
        spark_df = self._read(self.sql_query, columns_to_map=columns_to_map, partition_column=partition_column,
                              lower_bound=lower_bound, upper_bound=upper_bound, num_partitions=num_partitions)
        return spark_df

    def write_data(self, spark_df, mode, create_table_column_types=None):
        logger.info("Writing spark dataframe to Postgres data source.")
        self._write(spark_df, self.db_table, mode, create_table_column_types)

    def get_column_types(self, columns_to_map=None):
        logger.info("Fetching column types from Postgres data source.")
        spark_df = self._read(self.db_table, columns_to_map=columns_to_map)
        dtypes_dict = dict(spark_df.dtypes)
        return dtypes_dict

    def check_if_table_exists(self):
        logger.info(
            "Checking if table {} exists in Postgres to write the data.".format(self.db_table))
        table_exists = False
        try:
            spark_df = self._read(self.db_table)
            if spark_df is not None:
                table_exists = True
        except Exception as e:
            if "does not exist" in str(e):
                logger.warning(
                    "Table {} could not be found.".format(self.db_table))
            else:
                raise DatabaseError("Error while checking if table {} exists in postgres database. Error: {}".format(
                    self.db_table, str(e)))
        return table_exists

    def _read(self, query, columns_to_map=None, partition_column=None, lower_bound=None, upper_bound=None, num_partitions=None):
        read_jdbc = self.spark.read.format("jdbc").option(
            "url", self.url).option("dbtable", query)

        if partition_column is not None and lower_bound is not None and upper_bound is not None and num_partitions is not None:
            logger.info("Partition options: partition column {}, lower bound {}, upper bound {}, number of partitions {}".format(
                partition_column, lower_bound, upper_bound, num_partitions))
            read_jdbc.option("partitionColumn", partition_column).option(
                "lowerBound", lower_bound).option("upperBound", upper_bound).option("numPartitions", num_partitions)

        for k, v in self.connection_properties.items():
            if v:
                read_jdbc.option(k, v)

        # If some column contains special characters like space or $, reading with spark-JDBC fails with pyspark.sql.utils.ParseException. WI #28110
        # To fix this, disabling predicate pushdown.
        special_chars = [" ", "$"]
        if columns_to_map is None or len(columns_to_map) == 0 or any(char in column for column in columns_to_map for char in special_chars):
            read_jdbc.option("pushDownPredicate", "false")

        spark_df = read_jdbc.load()

        # If column names in expected case are provided, then convert column names from spark_df to expected case
        if columns_to_map:
            spark_df = self.get_col_names_in_expected_case(
                spark_df, columns_to_map)
        return spark_df

    def _write(self, spark_df, dbtable, mode, create_table_column_types=None):
        # remove all None values from connection properties before sending to jdbc
        connection_properties_non_null = {k: v for k, v in self.connection_properties.items() if v is not None}
        spark_df.write.jdbc(self.url, dbtable, mode=mode, properties=connection_properties_non_null)
