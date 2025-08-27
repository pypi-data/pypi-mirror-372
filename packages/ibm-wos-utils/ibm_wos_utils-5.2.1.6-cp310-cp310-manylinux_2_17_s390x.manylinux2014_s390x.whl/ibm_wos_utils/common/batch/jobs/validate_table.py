# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2020, 2021
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

import collections
import logging

from ibm_wos_utils.joblib.jobs.aios_spark_job import AIOSBaseJob
from ibm_wos_utils.joblib.utils.constants import *
from ibm_wos_utils.joblib.utils.db_utils import DbUtils
from ibm_wos_utils.joblib.utils.joblib_utils import JoblibUtils
from ibm_wos_utils.joblib.utils.param_utils import get


class ValidateTable(AIOSBaseJob):

    def run_job(self):

        self.logger.info("===================== This is table schema validation job from wos utils package executed by entrypoint job (job/main_job.py) =================")
        self.logger.info(self.arguments)
        try:
            # example
            # {"monitoring_run_id": "drift_config", "map_data_types": false, "storage": {"type": "hive", "connection": {"metastore_url": "thrift://localhost:9083", "jdbc_url": None, "jdbc_driver": None}}, "tables": [{"database": "subscription_d1642521", "schema": None, "table": "payload_data", "columns": {"fields": [{"metadata": {}, "name": "scoring_id", "nullable": False, "type": "string", "unique": True, "length": None}, {"metadata": {}, "name": "sepal_length", "nullable": False, "type": "float", "unique": False, "length": None}, {"metadata": {}, "name": "sepal_width", "nullable": False, "type": "float", "unique": False, "length": None}, {"metadata": {}, "name": "petal_length", "nullable": False, "type": "float", "unique": False, "length": None}, {"metadata": {}, "name": "petal_width", "nullable": False, "type": "float", "unique": False, "length": None}, {"metadata": {}, "name": "prediction", "nullable": False, "type": "string", "unique": False, "length": None}, {"metadata": {}, "name": "probability", "nullable": False, "type": "float", "unique": False, "length": None}], "type": "struct"}}, {"database": "subscription_d1642521", "schema": None, "table": "drifted_transactions", "columns": {"fields": [{"metadata": {}, "name": "scoring_id", "nullable": False, "type": "string", "unique": True, "length": None}, {"metadata": {}, "name": "constraints_generation_id", "nullable": False, "type": "string", "unique": False, "length": None}, {"metadata": {}, "name": "is_model_drift", "nullable": False, "type": "boolean", "unique": False, "length": None}, {"metadata": {}, "name": "drift_model_confidence", "nullable": False, "type": "float", "unique": False, "length": None}, {"metadata": {}, "name": "is_data_drift", "nullable": False, "type": "boolean", "unique": False, "length": None}, {"metadata": {}, "name": "categorical_constraints", "nullable": False, "type": "string", "unique": False, "length": None}, {"metadata": {}, "name": "numerical_range_constraints", "nullable": False, "type": "string", "unique": False, "length": None}, {"metadata": {}, "name": "catcat_constraints", "nullable": False, "type": "float", "unique": False, "length": None}, {"metadata": {}, "name": "catnum_range_constraints", "nullable": False, "type": "float", "unique": False, "length": None}], "type": "struct"}}], "data_file_path": "hdfs://localhost:9000/testing_data/common/cd862105-8760-4d0e-8697-f45b86037379/data", "output_file_path": "hdfs://localhost:9000/testing_data/common/cd862105-8760-4d0e-8697-f45b86037379/output/drift_config"}

            allowed_storage_types = [
                StorageType.HIVE.value, StorageType.JDBC.value]
            if self.storage_type not in allowed_storage_types:
                raise Exception("Unsupported storage type provided. Only supported storage types are {}.".format(
                    str(allowed_storage_types)))

            is_error = False
            error_json = {
                "error": []
            }

            tables_to_be_validated = get(self.arguments, "tables")

            # Set map_data_types property to True if not present in the payload
            map_data_types = get(self.arguments, "map_data_types")
            if map_data_types is not None:
                if not map_data_types or map_data_types.lower() == "false":
                    map_data_types = False
                else:
                    map_data_types = True
            else:
                map_data_types = True

            for table in tables_to_be_validated:
                table_name = get(table, "table")
                database_name = get(table, "database")
                schema_name = get(table, "schema")
                self.logger.info(
                    "Retrieving columns of table {}:{}".format(
                        database_name, table_name))
                # In case of Db2, the probability column is stored as string. Passing the column name here for type casting
                probability_column = JoblibUtils.get_column_by_modeling_role(
                    get(table, "columns"), 'probability')
                columns = DbUtils.list_columns(
                    self.spark, self.location_type,
                    database_name, table_name,
                    schema_name=schema_name, connection_properties=self.jdbc_connection_properties,
                    probability_column=probability_column)

                actual_schema = {}

                is_error_local = False

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
                expected_columns = get(table, "columns")
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
                    fractions = ["float", "double", "decimal"]

                    if isinstance(value, collections.Mapping):
                        # for columns with the type stored in a dictionary,
                        # prepare column type as a string
                        data_type = value.get("type").lower()
                        element_type = value.get("elementType").lower()
                        if element_type.lower() in integrals:
                            valid_values = list(
                                map(lambda t: "{}<{}>".format(data_type, t), integrals))
                        elif element_type.lower() in fractions:
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
