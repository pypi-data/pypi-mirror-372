# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2021, 2023
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

from collections.abc import Mapping
import json

try:
    from pyspark.sql import SQLContext
except ImportError as e:
    pass

from ibm_wos_utils.drift.batch.constraints.manager import DataConstraintMgr
from ibm_wos_utils.drift.batch.util.constants import (
    CATEGORICAL_UNIQUE_THRESHOLD, MAX_DISTINCT_CATEGORIES)

from ibm_wos_utils.joblib.jobs.aios_spark_job import AIOSBaseJob
from ibm_wos_utils.joblib.utils import ddl_utils
from ibm_wos_utils.joblib.utils.constants import *
from ibm_wos_utils.joblib.utils.db_utils import DbUtils
from ibm_wos_utils.joblib.utils.joblib_utils import JoblibUtils
from ibm_wos_utils.joblib.utils.param_utils import get
from ibm_wos_utils.joblib.utils.jdbc_utils import JDBCUtils

import re

class DriftConfigurationJob(AIOSBaseJob):
    """Spark job to train drift model, learn data constraints and create drift tables"""

    def run_job(self):
        self.logger.info("Starting drift configuration job")
        self.logger.info(self.arguments)

        self.output_file_path = get(self.arguments, "output_file_path")
        self.schema = None
        self.table_schema = None
        
        train_drift_model = get(self.arguments, "train_drift_model")
        if train_drift_model:
            training_table = next((table for table in get(self.arguments, "tables") if get(
                table, "type", "") == "training"), None)
            if not training_table:
                raise Exception(
                    "Training data table details are missing.")

            self.__generate_drift_artifacts(training_table=training_table)
        
        configure_drift_table = get(self.arguments, "configure_drift_table")
        if configure_drift_table:
            drift_table = next((table for table in get(self.arguments, "tables") if get(
                table, "type", "") == "drift"), None)
            if not drift_table:
                raise Exception(
                    "Drift Table details are missing.")

            self.__create_or_validate_drift_table(table=drift_table)

    def __create_or_validate_drift_table(self, table):
        is_error = False
        error_json = {
            "error": []
        }

        # table details
        database_name = get(table, "database_name")
        schema_name = get(table, "schema_name")
        table_name = get(table, "table_name")

        schema = get(table, "schema")
        if not schema:
            schema = self.table_schema
            table["schema"] = schema
        if not schema:
            raise Exception("Drift Table schema missing.")
        
        auto_create = get(table, "auto_create")

        table_parameters = get(table, "parameters")
        if not table_parameters:
            table_parameters = {}

        partition_column = get(table_parameters, "partition_column") \
            if self.storage_type == StorageType.JDBC.value else None

        table_info_json = None
        jdbc_connection_details = {}

        table_status = {
            "table_name": get(table, "table_name")
        }
        try:
            if auto_create and self.storage_type == StorageType.HIVE.value:
                self.__create_table_in_hive(
                    database_name=database_name,
                    table_name=table_name,
                    table_parameters=table_parameters,
                    table_schema=schema)

            if auto_create and (self.storage_type == StorageType.JDBC.value or (
                self.location_type is not None and self.location_type == LocationType.JDBC.value)):
                table_info_json, jdbc_connection_details = self.__create_table_in_db2(
                    database_name=database_name,
                    schema_name=schema_name,
                    table_name=table_name,
                    table_parameters=table_parameters,
                    table_schema=schema)

            if not auto_create:
                self.logger.info("Auto create is set to False for the table {}. Hence, validating the table.".format(table_name))
                self.__validate_table(
                    database_name=database_name,
                    table_name=table_name,
                    schema_name=schema_name,
                    table=table,
                    partition_column=partition_column)
            table_status["state"] = "active"
        except Exception as ex:
            is_error = True
            error_json["error"].append(str(ex))
            failure = {
                        "errors": [
                            {
                                "message": str(ex)
                            }
                        ]
                    }
            table_status["failure"] = json.dumps(failure)
            table_status["state"] = "error"
            self.logger.exception("An error occured while creating table. Reason: {}".format(str(ex)))

        try:
            if is_error:
                raise Exception("Create Table(s) job failed. Reason: {}".format(error_json))
            self.logger.info("Completed table creation job")
        except Exception as ex:
            self.logger.exception(str(ex))
            super().save_exception_trace(str(ex))
            raise ex
        finally:
            self.save_data(
                "{}/tables_status.json".format(self.arguments.get("output_file_path")),
                {
                    "tables_status": [table_status]
                })

            table_details_json = {}
            if table_info_json:
                table_details_json["table_info_details"] = json.dumps([table_info_json])
            if jdbc_connection_details:
                table_details_json["jdbc_connection_details"] = jdbc_connection_details
                    
            self.logger.info("table details json {}".format(table_details_json))
            if table_details_json:
                self.save_data(
                    "{}/table_info.json".format(self.arguments.get("output_file_path")),
                    table_details_json)

    def __create_table_in_hive(self, database_name, table_name, table_parameters, table_schema):
        sql_context = SQLContext(self.sc)

        if table_name in sql_context.tableNames(database_name):
            msg = "Autocreate is set to True. However, a table with the name {} already exists in the database {}.".format(
                    table_name, database_name)
            raise Exception(msg)
        
        hive_storage_format = "csv"
        if table_parameters:
            hive_storage_format = get(table_parameters, "hive_storage_format") or "csv"
        table_format = hive_storage_format.lower()

        create_table_ddl = ddl_utils.generate_table_ddl_batch_simplification(
            schema=table_schema,
            database_name=database_name,
            table_name=table_name,
            stored_as=table_format)
        self.logger.info("Creating table with DDL: {}".format(create_table_ddl.rstrip(";")))
        self.spark.sql(create_table_ddl.rstrip(";"))

    def __create_table_in_db2(self, database_name, schema_name, table_name, table_parameters, table_schema):
        probability_column = JoblibUtils.get_column_by_modeling_role(
            schema=table_schema,
            modeling_role='probability')

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
                partition_column_in_schema = self.__convert_data_types(
                    schema=table_schema,
                    schema_name=schema_name,
                    table_name=table_name,
                    partition_column=partition_column,
                    max_length_categories=max_length_categories,
                    index_columns=index_columns,
                    primary_keys=primary_keys)

        # add this only if user has specified a partition column and its not part of schema
        # skip in case user has either not specified partition column or 
        # has specified it, but its part of schema.
        if partition_column and not partition_column_in_schema:
            # If partition column is not already present in the schema, 
            # add it to the schema as a non-nullable field
            partition_field = self.__get_partition_column_field(partition_column)
            table_schema["fields"].append(partition_field)

        jdbc_connection_details = self.jdbc_connection_properties
        jdbc_connection_details["certificate"] = get(self.arguments, "storage.connection.certificate")

        emptyRDD = self.sc.emptyRDD()
    
        from pyspark.sql.types import StructType
        # Restore schema from json:
        new_schema = StructType.fromJson(table_schema)
        self.logger.info("schema after converting to db2 types {}".format(new_schema))

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

        self.logger.info("created table {}.{} in db2".format(schema_name, table_name))

        return table_info_json, jdbc_connection_details

    def __convert_data_types(
        self, schema, schema_name, table_name, partition_column,
        max_length_categories, index_columns, primary_keys):

        spark_to_db2_map = {
            "boolean": "boolean",
            "byte": "bigint",
            "short": "bigint",
            "integer": "bigint",
            "long": "bigint",
            "float": "double",
            "double": "double",
            "timestamp": "timestamp",
            "string": "varchar",
            "binary": "blob"
        }

        column_string = ""
        table_info_json = {}
        partition_column_in_schema = False
        primary_key = None
        index_column = None

        get_varchar_length = lambda x: max(64, get(max_length_categories, x, 32)*2)
        ddl_fields = schema.get("fields").copy()
        for field in ddl_fields:
            feature_name = get(field, "name")
            feature_type = get(field, "type")

            if isinstance(feature_type, dict):
                feature_type = "varchar"
            else:
                db2_element_type = spark_to_db2_map.get(feature_type)
                if db2_element_type is not None:
                    feature_type = db2_element_type

            if feature_type == "blob":
                continue

            if feature_type == "varchar":
                if get(field, "metadata.modeling_role") == "probability":
                    feature_type += "(32000)"
                else:
                    # check if field has length
                    feature_length = get(field, "length")
                    if not feature_length:
                        # fall back
                        feature_length = get(field, "metadata.columnInfo.columnLength")

                    if not feature_length:
                        # default option
                        feature_length = get_varchar_length(feature_name)
                    feature_type += "({})".format(feature_length) 

            if get(field, "metadata.modeling_role") == "record-id":
                primary_key = feature_name
            
            if get(field, "metadata.modeling_role") == "record-timestamp":
                index_column = feature_name

            # If the partition column is already present in the schema 
            # validate it to be a numeric or time stamp column and do 
            # not alter the db2 table with the partition column
            if feature_name == partition_column:
                partition_column_in_schema = True
                if feature_type not in ["bigint", "timestamp", "double"]:
                    raise Exception("partition column should either be a numeric or timestamp column.")

            column_string += "`{}` {}, ".format(feature_name, feature_type.upper())
        column_string = column_string.rstrip()
        
        table_info_json = self.__get_table_info_json(
            schema_name=schema_name,
            table_name=table_name,
            partition_column=partition_column,
            primary_key=primary_key,
            index_column=index_column, 
            partition_column_in_schema=partition_column_in_schema,
            additional_index_columns=index_columns,
            additional_primary_keys=primary_keys)
            
        self.logger.info("column string {}".format(column_string.rstrip(",")))
        return column_string.rstrip(","), table_info_json, partition_column_in_schema

    def __get_table_info_json(
        self, schema_name, table_name,
        partition_column, primary_key, index_column,
        partition_column_in_schema,
        additional_index_columns, additional_primary_keys):
        
        table_info_json = {}
        table_info_json["schema_name"] = schema_name
        table_info_json["table_name"] = table_name
        
        if partition_column and not partition_column_in_schema:
            table_info_json["partition_column"] = partition_column
        
        if primary_key:
            table_info_json["primary_key"] = primary_key
        
        if index_column:
            table_info_json["index_column"] = index_column
        
        if additional_index_columns:
            table_info_json["additional_index_columns"] = additional_index_columns

        if additional_primary_keys:
            table_info_json["additional_primary_keys"] = additional_primary_keys
        
        return table_info_json

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

    def __validate_table(self, database_name, table_name, schema_name, table, partition_column=None):

        map_data_types = True
        # Mapping between Hive and Spark data types. Datatypes like "map", "array" which are present in both
        # Hive and Spark are not part of the mapping below. Hive data type is used in that case.
        # Reference:
        # https://docs.cloudera.com/HDPDocuments/HDP3/HDP-3.1.4/integrating-hive/content/hive_hivewarehouseconnector_supported_types.html
        hive_to_spark_map = {
            "tinyint": "byte",
            "smallint": "short",
            "integer": "integer",
            "int": "integer",
            "bigint": "long",
            "float": "float",
            "double": "double",
            "decimal": "decimal",
            "string": "string",
            "varchar": "string",
            "binary": "binary",
            "boolean": "boolean",
            "interval": "calendarinterval"
        
        }
        probability_column = JoblibUtils.get_column_by_modeling_role(
                    get(table, "schema"), 'probability')
        columns = DbUtils.list_columns(
                    self.spark, self.location_type,
                    database_name, table_name,
                    schema_name=schema_name, connection_properties=self.jdbc_connection_properties,
                    probability_column=probability_column)

        actual_schema = {}

        is_error_local = False
        is_error = False
        error_json = {
                "error": []
            }

        try:
            for column in columns:
                if map_data_types:
                    data_type = get(
                            hive_to_spark_map, column.dataType.lower())
                    if data_type is None:
                        data_type = column.dataType.lower()

                        # For hive datatype of format like: array<int>, fetch the inner datatype and convert it
                        # Complex datatypes like array, map are present in
                        # both hive and spark
                        type_split = data_type.split("<")
                        if len(type_split) > 1:
                            type_split_0 = type_split[0]
                            type_split_1 = type_split[1][:-1]
                            spark_sub_type = get(
                                hive_to_spark_map, type_split_1)
                            if spark_sub_type is not None:
                                data_type = "{}<{}>".format(
                                    type_split_0, spark_sub_type)

                    actual_schema[column.name.lower()] = data_type
                else:
                    actual_schema[column.name.lower(
                    )] = column.dataType.lower()

            # validate table schema
            # iterate through expected column names and verify they exist in target table
            # we are verifying expected list, its okay for target table to
            # have a lot more columns than expectation
            self.logger.info("Validating schema...")
            expected_columns = get(table, "schema")
            self.logger.info(
                "Expected columns : {}".format(expected_columns))
            self.logger.info("Actual Schema: {}".format(actual_schema))

            columns_not_found = []
            expected_val_not_present = []
            data_type_mismatch = []

            for column in get(expected_columns, "fields"):
                if get(column, "metadata.deleted") is True:
                    # skip validation if this column has metadata with deleted set to true
                    continue

                key = get(column, "name")
                value = get(column, "type")

                # column name validation
                if not key or key.lower() not in actual_schema.keys():
                    is_error = True
                    is_error_local = True
                    columns_not_found.append(key)
                    continue

                if value is None:
                    # Unlikely to happen
                    is_error = True
                    is_error_local = True
                    expected_val_not_present.append(key)
                    continue

                valid_values = []
                integrals = ["short", "integer", "long"]
                fractions = ["float", "double", "decimal", "float4", "float8"]
                # Postgres is adding a precision and scale by default for "decimal"
                # adding this line to match any precision and scale comes with "decimal" type
                decimal_pattern = re.compile(r"decimal\(\d+,\d+\)")

                if isinstance(value, Mapping):
                    # for columns with the type stored in a dictionary,
                    # prepare column type as a string
                    data_type = value.get("type").lower()
                    element_type = value.get("elementType").lower()
                    if element_type.lower() in integrals:
                        valid_values = list(
                            map(lambda t: "{}<{}>".format(data_type, t), integrals))
                    elif element_type.lower() in fractions or decimal_pattern.match(element_type.lower()):
                        valid_values = list(
                            map(lambda t: "{}<{}>".format(data_type, t), fractions))
                    else:
                        valid_values = [
                            "{}<{}>".format(
                                data_type, element_type)]
                elif value.lower() in integrals:
                    valid_values = integrals
                elif value.lower() in fractions:
                    valid_values = fractions
                else:
                    valid_values = [value.lower()]

                data_type_dict = dict()
                # column name found, validate column datatype
                if str(actual_schema[key.lower()]) not in valid_values:
                    is_error = True
                    is_error_local = True
                    data_type_dict["column_name"] = key
                    data_type_dict["expected_type"] = valid_values
                    data_type_dict["actual_type"] = actual_schema.get(
                        key.lower())
                    data_type_mismatch.append(data_type_dict)

            # partition column name validation
            if partition_column and partition_column not in actual_schema.keys():
                is_error = True
                is_error_local = True
                columns_not_found.append(partition_column)

            # Prepare error_json
            error_string = "database_name: `{}`, table_name: `{}`;".format(
                database_name, table_name)
            if len(columns_not_found) != 0:
                error_string += " Column(s) not found: {};".format(
                    columns_not_found)
            if len(expected_val_not_present) != 0:
                error_string += " No expected value present for column(s): {};".format(
                    expected_val_not_present)
            if len(data_type_mismatch) != 0:
                error_string += " Datatype mismatch for column(s): {}".format(
                    data_type_mismatch)

            if is_error_local:
                error_json["error"].append({
                    "database": database_name,
                    "table": table_name,
                    "error": error_string
                })

            if is_error:
                raise Exception(
                    "Table(s) validation failed : {}.".format(error_json))
            self.logger.info("Table schema successfully validated!")

        except Exception as ex:
            self.logger.exception(str(ex))
            super().save_exception_trace(str(ex))
            raise ex            

    def __generate_drift_artifacts(self, training_table):

        database = get(training_table, "database_name")
        table = get(training_table, "table_name")
        schema = get(training_table, "schema_name")

        # Partition Information
        partition_column = get(training_table, "parameters.partition_column")
        num_partitions = get(training_table, "parameters.num_partitions", 1)

        if not database or not table:
            raise Exception(
                "The database and/or table for reading training data is missing.")

        model_type, feature_columns, categorical_columns, \
            label_column, prediction_column, probability_column, \
                record_id_column, record_timestamp_column, \
                    enable_data_drift, enable_model_drift = self.__validate_and_get_params()

        columns = feature_columns.copy()
        columns.append(prediction_column)
        columns.append(record_id_column)
        columns.append(label_column)
        if probability_column is not None:
            columns.append(probability_column)
        if record_timestamp_column is not None:
            columns.append(record_timestamp_column)

        columns_to_filter = []
        if model_type != "regression":
            columns_to_filter.append(prediction_column)

        # get handle to training data as a spark dataframe
        spark_df = DbUtils.get_table_as_dataframe(
                spark=self.spark,
                location_type=self.location_type,
                database_name=database,
                table_name=table,
                schema_name=schema,
                columns_to_map=columns,
                columns_to_filter=columns_to_filter,
                connection_properties=self.jdbc_connection_properties,
                probability_column=probability_column,
                partition_column=partition_column,
                num_partitions=num_partitions)

        # basic validation of spark dataframe
        self.__validate_spark_df(
            spark_df=spark_df,
            feature_columns=feature_columns,
            label_column=label_column,
            prediction_column=prediction_column,
            probability_column=probability_column,
            model_type=model_type)

        # generate and save drift artefacts - drift model and data constraints
        self.__generate_drift_config(
            spark_df=spark_df,
            enable_data_drift=enable_data_drift,
            enable_model_drift=enable_model_drift,
            model_type=model_type,
            feature_columns=feature_columns,
            categorical_columns=categorical_columns,
            label_column=label_column,
            prediction_column=prediction_column,
            probability_column=probability_column,
            record_id_column=record_id_column,
            record_timestamp_column=record_timestamp_column)

    def __validate_and_get_params(self):
        # Validate feature columns
        feature_columns = get(
            self.arguments, "common_configuration.feature_columns", [])
        categorical_columns = get(
            self.arguments, "common_configuration.categorical_columns", [])

        if not feature_columns:
            raise Exception("No feature columns are added.")

        # Validate model type
        model_type = get(
            self.arguments, "common_configuration.problem_type")
        if not model_type:
            raise Exception("No model type is specified.")

        enable_model_drift = get(
            self.arguments, "enable_model_drift", True)
        enable_data_drift = get(
            self.arguments, "enable_data_drift", True)

        if model_type == "regression" and enable_model_drift:
            self.logger.warning(
                "The model type specified is regression. Disabling model drift.")
            enable_model_drift = False

        if not enable_data_drift and not enable_model_drift:
            raise Exception("One of model or data drift must be enabled.")

        # Validate prediction and probability columns
        prediction_column = get(
            self.arguments, "common_configuration.prediction")
        probability_column = get(
            self.arguments, "common_configuration.probability")

        if not prediction_column:
            raise Exception(
                "The prediction column is missing from arguments.")
        if model_type != "regression" and not probability_column:
            raise Exception(
                "The probability column is missing from arguments.")

        label_column = get(
            self.arguments, "common_configuration.label_column")
        if not label_column:
            raise Exception("No label column is supplied.")

        record_id_column = get(
            self.arguments, "common_configuration.record_id")
        if not record_id_column:
            raise Exception(
                "The record id column is missing from arguments.")

        record_timestamp_column = get(
            self.arguments, "common_configuration.record_timestamp")

        return model_type, feature_columns, categorical_columns, \
            label_column, prediction_column, probability_column, \
                record_id_column, record_timestamp_column, \
                    enable_data_drift, enable_model_drift

    def __validate_spark_df(
        self, spark_df, feature_columns, label_column, prediction_column, 
        probability_column, model_type):

        # Validate feature columns
        missing_columns = list(
            set(feature_columns) - set(spark_df.columns))
        if len(missing_columns) > 0:
            raise Exception(
                "The feature columns {} are not present in the training data.".format(missing_columns))
        self.logger.info("******** Feature Columns [{}]: {} ********".format(
            len(feature_columns), feature_columns))

        # Validate label column
        if label_column not in spark_df.columns:
            raise Exception("The label column {} is not present in the training data.".format(
                label_column))

        # Validate probability and prediction columns
        if prediction_column not in spark_df.columns:
            raise Exception("The prediction column '{}' is missing from the training data.".format(
                prediction_column))

        if model_type != "regression" and probability_column not in spark_df.columns:
            raise Exception("The probability column '{}' is missing from the training data.".format(
                probability_column))

    def __generate_drift_config(
        self, spark_df, enable_data_drift, enable_model_drift, model_type,
        feature_columns, categorical_columns, label_column, prediction_column, 
        probability_column, record_id_column, record_timestamp_column):

        drift_model = None
        ddm_properties = {}
        constraint_set = None

        if enable_model_drift:
            drift_model, ddm_properties = self.__generate_ddm(
                spark_df=spark_df,
                model_type=model_type,
                feature_columns=feature_columns,
                categorical_columns=categorical_columns,
                label_column=label_column,
                prediction_column=prediction_column,
                probability_column=probability_column)

        if enable_data_drift:
            constraint_set = self.__generate_constraints(
                spark_df=spark_df,
                feature_columns=feature_columns,
                categorical_columns=categorical_columns)

        if enable_model_drift or enable_data_drift:
            self.__persist_drift_artefacts(
                enable_data_drift=enable_data_drift,
                enable_model_drift=enable_model_drift,
                drift_model=drift_model,
                ddm_properties=ddm_properties,
                constraint_set=constraint_set,
                record_id_column=record_id_column,
                record_timestamp_column=record_timestamp_column)

    def __generate_ddm(
        self, spark_df, model_type, feature_columns, categorical_columns,
        label_column, prediction_column, probability_column):

        self.logger.info("Started drift detection model generation.")
        self.save_status("Model Drift Configuration STARTED")

        # Get inputs
        ddm_inputs = {
            "model_type": model_type,
            "feature_columns": feature_columns,
            "categorical_columns": categorical_columns,
            "label_column": label_column,
            "prediction": prediction_column,
            "probability": probability_column,
            "enable_tuning": get(
                self.arguments,
                "drift_parameters.model_drift.enable_drift_model_tuning",
                False),
            "max_bins": get(
                self.arguments,
                "drift_parameters.model_drift.max_bins", -1),
            "check_ddm_training_quality": get(
                self.arguments,
                "drift_parameters.model_drift.check_ddm_training_quality", True),
            "ddm_training_quality_check_threshold": get(
                self.arguments,
                "drift_parameters.model_drift.ddm_training_quality_check_threshold", 0.3)
        }
        from ibm_wos_utils.drift.batch.drift_detection_model import DriftDetectionModel
        ddm = DriftDetectionModel(
            spark_df, ddm_inputs)
        ddm.generate_drift_detection_model()

        # Save the properties
        ddm_properties = {
            "build_id": ddm.build_id,
            "drift_model_version": "spark-{}".format(self.spark.version),
            "feature_columns": ddm.feature_columns,
            "categorical_columns": ddm.categorical_columns,
            "class_labels": ddm.class_labels,
            "prediction": ddm.prediction,
            "predicted_labels": ddm.predicted_labels,
            "probability": ddm.probability,
            "ddm_features": ddm.ddm_features,
            "ddm_prediction": ddm.ddm_prediction_col,
            "ddm_probability_difference": ddm.ddm_probability_diff_col,
            "base_model_accuracy": ddm.base_model_accuracy,
            "base_predicted_accuracy": ddm.base_predicted_accuracy
        }

        if ddm_inputs.get("check_ddm_training_quality"):
            return self.__check_ddm_training_quality(
                ddm=ddm,
                ddm_properties=ddm_properties,
                enable_tuning=ddm_inputs.get("enable_tuning"),
                ddm_training_check_threshold=ddm_inputs.get(
                    "ddm_training_quality_check_threshold"))

        self.logger.info(
            "Completed drift detection model generation.")
        self.save_status("Model Drift Configuration COMPLETED")

        return ddm.ddm_model, ddm_properties

    def __check_ddm_training_quality(
        self, ddm, ddm_properties,
        enable_tuning=False, ddm_training_check_threshold=0.3):

        # Check for ddm model quality and return ddm properties accordingly
        self.logger.info(
            "===Drift detection model training quality check started====")

        if abs(ddm.base_model_accuracy - ddm.base_predicted_accuracy) > ddm_training_check_threshold:
            new_ddm_properties = {}
            new_ddm_properties["model_drift_enabled"] = "false"
            new_ddm_properties["base_model_accuracy"] = ddm.base_model_accuracy
            new_ddm_properties["base_predicted_accuracy"] = ddm.base_predicted_accuracy
            if enable_tuning:
                new_ddm_properties["message"] = \
                    "The trained drift detection model did not meet quality standards. \
                        Drop in accuracy cannot be detected."
            else:
                new_ddm_properties["message"] = \
                    "The trained drift detection model did not meet quality standards. \
                        Drop in accuracy cannot be detected. To try again, enable tuning."

            ddm_properties = new_ddm_properties
            ddm.ddm_model = None

        self.logger.info(
            "===Drift detection model training quality check completed===")
        self.save_status("Model Drift Configuration COMPLETED")

        return ddm.ddm_model, ddm_properties

    def __generate_constraints(self, spark_df, feature_columns, categorical_columns):
        self.logger.info("Started data drift constraints generation.")
        self.save_status("Data Drift Configuration STARTED")
        self.logger.info(
            "******* Number of Partitions: {} ********".format(spark_df.rdd.getNumPartitions()))

        drift_options = {
            "enable_two_col_learner": get(
                self.arguments,
                "drift_parameters.data_drift.enable_two_col_learner",
                True),
            "categorical_unique_threshold": get(
                self.arguments,
                "drift_parameters.data_drift.categorical_unique_threshold",
                CATEGORICAL_UNIQUE_THRESHOLD),
            "max_distinct_categories": get(
                self.arguments,
                "drift_parameters.data_drift.max_distinct_categories",
                MAX_DISTINCT_CATEGORIES),
            "user_overrides": get(
                self.arguments,
                "drift_parameters.data_drift.user_overrides",
                [])}

        use_alt_learner = get(
            self.arguments, "drift_parameters.data_drift.use_alt_learner", False)

        if not use_alt_learner:
            constraint_set = DataConstraintMgr.learn_constraints(
                training_data=spark_df,
                feature_columns=feature_columns,
                categorical_columns=categorical_columns,
                callback=self.save_status,
                **drift_options)
        else:
            constraint_set = DataConstraintMgr.learn_constraints_v2(
                training_data=spark_df,
                feature_columns=feature_columns,
                categorical_columns=categorical_columns,
                callback=self.save_status,
                **drift_options)

        self.logger.info("Completed data drift constraints generation.")
        self.save_status("Data Drift Configuration COMPLETED")

        return constraint_set

    def __persist_drift_artefacts(self, enable_data_drift, enable_model_drift, drift_model, ddm_properties, constraint_set, record_id_column, record_timestamp_column):
        max_constraints_per_column = 1000000 if self.storage_type == StorageType.HIVE.value else 32000

        self.schema = DataConstraintMgr.generate_schema(
            record_id_column=record_id_column,
            record_timestamp_column=record_timestamp_column,
            model_drift_enabled=enable_model_drift,
            data_drift_enabled=enable_data_drift,
            constraint_set=constraint_set,
            max_constraints_per_column=max_constraints_per_column).to_json()

        schema_columns = get(self.schema, "columns")
        fields = []
        for key, value in schema_columns.items():
            fields.append({
                "name": key,
                "type": get(value, "type"),
                "length": get(value, "length"),
                "nullable": not(get(value, "not_null")),
                "unique": get(value, "unique"),
                "metadata": {}
            })

        self.table_schema = {
            "fields": fields,
            "type": "struct"
        }

        # OLD SCHEME: spark job generates archive in hdfs containing jsons
        # archive = BytesIO()

        # with tarfile.open(fileobj=archive, mode="w:gz") as tar:
        #     # Add schema json to tar
        #     tar.addfile(
        #         **self.__add_json_file("drifted_transactions_schema.json", schema.to_json()))

        #     if enable_model_drift:
        #         if drift_model is not None:
        #             model_path = self.output_file_path + "/drift_detection_model"
        #             drift_model.save(model_path)
        #             ddm_properties["drift_model_path"] = model_path

        #         # Add ddm properties to tar
        #         tar.addfile(
        #             **self.__add_json_file("ddm_properties.json", ddm_properties))

        #     if enable_data_drift:
        #         # Add constraints to tar
        #         tar.addfile(
        #             **self.__add_json_file("data_drift_constraints.json", constraint_set.to_json()))

        # # Write the whole tar.gz as a sequence file to HDFS
        # self.spark.sparkContext.parallelize([archive.getvalue()]).map(lambda x: (None, x)).coalesce(
        #     1).saveAsSequenceFile(self.output_file_path + "/drift_configuration")
        # archive.close()

        # NEW SCHEME: spark job generates json files in hdfs
        # output location for json files
        path = "{}/drift_configuration".format(self.output_file_path)

        # save drifted transactions schema json
        df = self.spark.createDataFrame([{"drifted_transactions_schema": json.dumps(self.schema)}])
        df.coalesce(1).write.json("{}/drifted_transactions_schema.json".format(path), mode="overwrite")

        # save drift model
        if enable_model_drift:
            if drift_model is not None:
                model_path = "{}/drift_detection_model".format(self.output_file_path)
                drift_model.save(model_path)
                ddm_properties["drift_model_path"] = model_path

            # save ddm properties
            df = self.spark.createDataFrame([{"ddm_properties": json.dumps(ddm_properties)}])
            df.coalesce(1).write.json("{}/ddm_properties.json".format(path), mode="overwrite")

        # save data drift constraints json
        if enable_data_drift:
            df = self.spark.createDataFrame([{"data_drift_constraints": json.dumps(constraint_set.to_json())}])
            df.coalesce(1).write.json("{}/data_drift_constraints.json".format(path), mode="overwrite")

    # def __add_json_file(self, name, some_dict):
    #     some_json = BytesIO(json.dumps(some_dict, indent=4).encode("utf-8"))
    #     tarinfo = tarfile.TarInfo(name)
    #     tarinfo.size = len(some_json.getvalue())
    #     return {
    #         "tarinfo": tarinfo,
    #         "fileobj": some_json
    #     }
