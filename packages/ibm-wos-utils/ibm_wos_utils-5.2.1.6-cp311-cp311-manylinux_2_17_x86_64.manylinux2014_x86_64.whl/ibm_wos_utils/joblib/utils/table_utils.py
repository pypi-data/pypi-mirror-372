# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2021
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------
import json
import logging
from ibm_wos_utils.joblib.utils.constants import *
from ibm_wos_utils.joblib.utils import ddl_utils
from ibm_wos_utils.joblib.utils.jdbc_utils import JDBCUtils
from ibm_wos_utils.joblib.utils.joblib_utils import JoblibUtils
from ibm_wos_utils.joblib.utils.param_utils import get
from ibm_wos_utils.joblib.utils.validate_table_utils import ValidateTableUtils
try:
    from pyspark.sql import SQLContext
except ImportError as e:
    pass
logger = logging.getLogger(__name__)

class TableUtils:

    def __init__(self, spark, sql_context, arguments, storage_type, 
                location_type=None, jdbc_connection_properties=None, 
                location_type_map={}, jdbc_connection_properties_map={}):
        self.spark = spark
        self.sql_context = sql_context
        self.arguments = arguments
        self.storage_type = storage_type
        self.location_type_map = location_type_map
        self.location_type = location_type
        self.credentials_set = False
        self.jdbc_connection_properties = jdbc_connection_properties
        self.jdbc_connection_properties_map = jdbc_connection_properties_map

    def __get_partition_column_field(self, partition_column):
        partition_field = {
            "name": partition_column,
            "type": "long",
            "nullable": False,
            "metadata": {
                "modeling_role": "partition-column"
            }
        }
        return partition_field     

    def create_table(self):
        error_json = {
                "error": []
            }
        error_msg = None
        tables = get(self.arguments, "tables")
        tables_status = []
        table_info_details = []
        table_info_json = {}
        self.jdbc_connection_details = {}

        for table in tables:
            table_status = {
                "table_name": get(table, "table_name")
            }
            try:
                failure = None
                database_name = get(table, "database_name")
                schema_name = get(table, "schema_name")
                table_name = get(table, "table_name")

                schema = get(table, "schema")
                auto_create = get(table, "auto_create")
                table_parameters = get(table, "parameters")
                table_type = get(table, "type")
                if get(table, "storage.type"):
                    self.storage_type = get(table, "storage.type")
                    if self.location_type_map:
                        self.location_type = get(self.location_type_map, table_type)
                    if self.jdbc_connection_properties_map:
                        self.jdbc_connection_properties = get(self.jdbc_connection_properties_map, table_type)
                if not table_parameters:
                    table_parameters = {}
                partition_column = get(table_parameters, "partition_column") \
                        if self.storage_type == StorageType.JDBC.value else None

                if auto_create:
                    if self.storage_type == StorageType.HIVE.value:
                        self.create_hive_table(database_name, table_name, schema, table_parameters)

                    elif self.storage_type == StorageType.JDBC.value or (
                        self.location_type is not None and self.location_type == LocationType.JDBC.value):

                        if "postgresql" in str(self.jdbc_connection_properties):
                            table_info_json = self.create_postgres_table(database_name, table_name, schema_name, schema, table_parameters)
                        else:
                            table_info_json = self.create_db2_table(database_name, table_name, schema_name, schema, table_parameters)
                else:
                    logger.info("Auto create is set to False for the table {}. Hence, validating the table.".format(table_name))
                    ValidateTableUtils.validate_table(database_name, table_name, schema_name, table, self.spark, self.location_type, \
                            self.jdbc_connection_properties, partition_column)
                table_status["state"] = "active"
            except Exception as e:
                error_json["error"].append(str(e))
                failure = {
                            "errors": [
                                {
                                    "message": str(e)
                                }
                            ]
                        }
                table_status["failure"] = json.dumps(failure)
                table_status["state"] = "error"
                error_msg = f"Create Table(s) job failed. Reason: {error_json}"
                logger.exception("An error occured while creating table. Reason: {}".format(str(e)))
            finally:
                tables_status.append(table_status)
                if table_info_json:
                    table_info_details.append(table_info_json)

                self.credentials_set = False
        logger.info(
                "Completed table creation job")
        table_info_json = {}
        if table_info_details:
            table_info_json["table_info_details"] = json.dumps(table_info_details)
        if self.jdbc_connection_details:
            table_info_json["jdbc_connection_details"] = self.jdbc_connection_details
                
        logger.info("table info json {}".format(table_info_json))
        logger.info("error msg {}".format(error_msg))
        return tables_status, table_info_json, error_msg

    def create_hive_table(self, database_name, table_name, schema, table_parameters):
        sql_context = SQLContext(self.sql_context)
        table_properties = []
        if table_name in sql_context.tableNames(database_name):
            msg = "Autocreate is set to True. However, a table with the name {} already exists in the database {}.".format(
                    table_name, database_name)
            raise Exception(msg)
                            
        hive_storage_format = "csv"
        if table_parameters:
            hive_storage_format = get(table_parameters, "hive_storage_format") or "csv"
            table_properties = get(table_parameters, "table_properties")
            table_properties_arr = []
            if table_properties:
                for property in table_properties:
                    property_split_arr = property.split("=")
                    table_properties_arr.append("'{}'='{}'".format(property_split_arr[0], property_split_arr[1]))
        
        table_format = hive_storage_format.lower()

        create_table_ddl = ddl_utils.generate_table_ddl_batch_simplification(
            schema=schema,
            database_name=database_name,
            table_name=table_name,
            stored_as=table_format)

        if table_properties:
            create_table_ddl = create_table_ddl.rstrip(";")
            create_table_ddl += " TBLPROPERTIES ({})".format(
                                    ",".join(table_properties_arr))
        logger.info("Creating table with DDL: {}".format(create_table_ddl.rstrip(";")))
        self.spark.sql(create_table_ddl.rstrip(";"))

    def create_db2_table(self, database_name, table_name, schema_name, schema, table_parameters):
        probability_column = JoblibUtils.get_column_by_modeling_role(
                                        schema, 'probability')

        util_instance = JDBCUtils.get_util_instance(
                spark=self.spark,
                database_name=database_name,
                table_name=table_name,
                schema_name=schema_name,
                connection_properties=self.jdbc_connection_properties,
                sql_query=None,
                probability_column=probability_column)

        if util_instance.check_if_table_exists():
            msg = "Autocreate is set to True. However, a table with the name {} already exists in the database {}.".format(
                table_name, database_name)
            raise Exception(msg)

        partition_column = get(table_parameters, "partition_column")
        index_columns = get(table_parameters, "index_columns") or []
        primary_keys = get(table_parameters, "primary_keys") or []
        max_length_categories = get(table_parameters, "max_length_categories") or {}

        create_table_column_types, \
            table_info_json, \
                partition_column_in_schema = ValidateTableUtils.convert_data_types(
                    schema=schema,
                    schema_name=schema_name,
                    table_name=table_name,
                    partition_column=partition_column,
                    max_length_categories=max_length_categories,
                    index_columns=index_columns,
                    primary_keys=primary_keys,
                    connection_properties=self.jdbc_connection_properties)

        # add this only if user has specified a partition column and its not part of schema
        # skip in case user has either not specified partition column or 
        # has specified it, but its part of schema.
        if partition_column and not partition_column_in_schema:
            # If partition column is not already present in the schema, 
            # add it to the schema as a non-nullable field
            partition_field = self.__get_partition_column_field(partition_column)
            schema["fields"].append(partition_field)

        if not self.credentials_set:
            self.jdbc_connection_details = self.jdbc_connection_properties
            self.jdbc_connection_details["certificate"] = get(self.arguments, "storage.connection.certificate")
            self.credentials_set = True

        emptyRDD = self.sql_context.emptyRDD()
                        
        from pyspark.sql.types import StructType
        # Restore schema from json:
        new_schema = StructType.fromJson(schema)
        logger.info("schema after converting to db2 types {}".format(new_schema))

        spark_df = emptyRDD.toDF(new_schema)
        JDBCUtils.write_dataframe_to_table(
            spark_df=spark_df,
            mode="overwrite",
            database_name=database_name,
            table_name=table_name,
            schema_name=schema_name,
            connection_properties=self.jdbc_connection_properties,
            probability_column=probability_column,
            create_table_column_types=create_table_column_types)

        logger.info("created table {}.{} in db2".format(schema_name, table_name))
        return table_info_json

    def create_postgres_table(self, database_name, table_name, schema_name, schema, table_parameters):
        probability_column = JoblibUtils.get_column_by_modeling_role(
            schema, 'probability')

        util_instance = JDBCUtils.get_util_instance(
            spark=self.spark,
            database_name=database_name,
            table_name=table_name,
            schema_name=schema_name,
            connection_properties=self.jdbc_connection_properties,
            sql_query=None,
            probability_column=probability_column)

        if util_instance.check_if_table_exists():
            msg = "Autocreate is set to True. However, a table with the name {} already exists in the database {}.".format(
                table_name, database_name)
            raise Exception(msg)

        partition_column = get(table_parameters, "partition_column")
        index_columns = get(table_parameters, "index_columns") or []
        primary_keys = get(table_parameters, "primary_keys") or []

        table_info_json, \
            partition_column_in_schema = ValidateTableUtils.convert_postgres_data_types(
            schema=schema,
            schema_name=schema_name,
            table_name=table_name,
            partition_column=partition_column,
            index_columns=index_columns,
            primary_keys=primary_keys,
            connection_properties=self.jdbc_connection_properties)

        # add this only if user has specified a partition column and its not part of schema
        # skip in case user has either not specified partition column or
        # has specified it, but its part of schema.
        if partition_column and not partition_column_in_schema:
            # If partition column is not already present in the schema,
            # add it to the schema as a non-nullable field
            partition_field = self.__get_partition_column_field(partition_column)
            schema["fields"].append(partition_field)

        if not self.credentials_set:
            self.jdbc_connection_details = self.jdbc_connection_properties
            self.jdbc_connection_details["certificate"] = get(self.arguments, "storage.connection.certificate")
            self.credentials_set = True

        emptyRDD = self.sql_context.emptyRDD()

        from pyspark.sql.types import StructType
        # Restore schema from json:
        new_schema = StructType.fromJson(schema)
        logger.info("schema after converting to postgres types {}".format(new_schema))

        spark_df = emptyRDD.toDF(new_schema)
        JDBCUtils.write_dataframe_to_table(
            spark_df=spark_df,
            mode="overwrite",
            database_name=database_name,
            table_name=table_name,
            schema_name=schema_name,
            connection_properties=self.jdbc_connection_properties,
            probability_column=probability_column)

        logger.info("created table {}.{} in postgres".format(schema_name, table_name))
        return table_info_json