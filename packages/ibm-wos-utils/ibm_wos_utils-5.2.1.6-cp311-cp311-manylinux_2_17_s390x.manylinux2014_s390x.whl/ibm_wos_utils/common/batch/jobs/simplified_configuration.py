# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2022
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------
import json
import tarfile
from io import BytesIO

from ibm_wos_utils.common.batch.utils.configuration_generator import ConfigurationGenerator

from ibm_wos_utils.joblib.jobs.aios_spark_job import AIOSBaseJob
from ibm_wos_utils.joblib.utils.constants import *
from ibm_wos_utils.joblib.utils.db_utils import DbUtils
from ibm_wos_utils.joblib.utils.param_utils import get


class SimplifiedConfiguration(AIOSBaseJob):
    """Common Configuration job which generates the required artifacts based on the monitor configuration flags"""

    def run_job(self):
        try:
            self.logger.info("Started Configuration Job")

            self.output_file_path = get(self.arguments, "output_file_path")
            self.save_status("STARTED")

            self.__validate_and_set_params()

            spark_df = DbUtils.get_table_as_dataframe(
                self.spark,
                self.location_type,
                self.database,
                self.table,
                schema_name=self.schema,
                columns_to_map=self.columns,
                columns_to_filter=self.columns_to_filter,
                connection_properties=self.jdbc_connection_properties,
                probability_column=self.probability_column,
                partition_column=self.partition_column,
                num_partitions=self.num_partitions)

            max_constraints_per_column = 1000000 if self.storage_type == StorageType.HIVE.value else 32000

            config_generator = ConfigurationGenerator(
                self.arguments, spark_df, log_function=self.save_status)
            config_obj = config_generator.generate_configuration(
                generate_archive=False, spark_version=self.spark.version, max_constraints_per_column=max_constraints_per_column)

            self.__create_archive(config_obj)
            self.save_status("FINISHED")
        except Exception as ex:
            self.logger.exception(str(ex))
            self.save_exception_trace(str(ex))
            self.save_status("FAILED", additional_info={"exception": str(ex)})
            raise ex
        finally:
            pass

    def __validate_and_set_params(self):
        self.model_type = get(self.arguments, "problem_type")
        if self.model_type is None:
            self.model_type = get(self.arguments, "model_type")

        self.enable_drift = get(
            self.arguments, "enable_drift", False)
        self.enable_model_drift = False if not self.enable_drift else get(
            self.arguments, "drift_parameters.model_drift.enable", True)
        self.enable_data_drift = False if not self.enable_drift else get(
            self.arguments, "drift_parameters.data_drift.enable", True)

        if self.model_type == "regression":
            self.enable_model_drift = False

        # if enable_drift is True and both drift_parameters.model_drift.enable
        # and drift_parameters.data_drift.enable are False, set enable_drift to False
        if not self.enable_model_drift and not self.enable_data_drift:
            self.enable_drift = False

        self.enable_explainability = get(
            self.arguments, "enable_explainability", False)

        self.enable_fairness = get(self.arguments, "enable_fairness", False)

        self.logger.info("Configuration flags are enable_model_drift:{0}, enable_data_drift:{1}, enable_explainability:{2}, enable_fairness:{3}".format(
            self.enable_model_drift, self.enable_data_drift, self.enable_explainability, self.enable_fairness))

        # Validate training table
        tables = get(self.arguments, "tables", [])
        training_table = next((table for table in tables if get(
            table, "type", "") == "training"), None)
        if not training_table:
            raise Exception(
                "The database and/or table for reading training data is missing.")
        self.database = get(training_table, "database")
        self.table = get(training_table, "table")
        self.schema = get(training_table, "schema")

        # Partition Information
        self.partition_column = get(
            training_table, "parameters.partition_column")
        self.num_partitions = get(
            training_table, "parameters.num_partitions", 1)

        if not self.database or not self.table:
            raise Exception(
                "The database and/or table for reading training data is missing.")

        self.feature_columns = get(self.arguments, "feature_columns", [])
        self.categorical_columns = get(
            self.arguments, "categorical_columns", [])

        if not self.feature_columns:
            raise Exception("No feature columns are added.")

        self.prediction_column = get(
            self.arguments, "prediction")
        self.probability_column = get(
            self.arguments, "probability")

        if not self.prediction_column:
            raise Exception(
                "The prediction column is missing from arguments.")
        if self.model_type != "regression" and not self.probability_column:
            raise Exception(
                "The probability column is missing from arguments.")

        self.label_column = get(
            self.arguments, "label_column")
        if not self.label_column:
            raise Exception("No label column is supplied.")

        self.record_timestamp_column = get(
            self.arguments, "record_timestamp")

        self.columns = self.feature_columns.copy()
        self.columns.append(self.prediction_column)
        # self.columns.append(self.record_id_column)
        self.columns.append(self.label_column)
        if self.probability_column is not None:
            self.columns.append(self.probability_column)
        if self.record_timestamp_column is not None:
            self.columns.append(self.record_timestamp_column)
        # If protected attributes are specified, adding them to the list of columns_to_map to handle case sensitivity
        protected_attributes = get(self.arguments, "protected_attributes")
        if protected_attributes:
            for protected_attr in protected_attributes:
                self.columns.append(protected_attr)

        self.columns_to_filter = [self.prediction_column]

    def __add_json_file(self, name, some_dict):
        some_json = BytesIO(json.dumps(some_dict, indent=4).encode("utf-8"))
        tarinfo = tarfile.TarInfo(name)
        tarinfo.size = len(some_json.getvalue())
        return {
            "tarinfo": tarinfo,
            "fileobj": some_json
        }

    def __add_archive_file(self, name, archive):
        # data = base64.b64encode(data).encode("utf-8")
        tarinfo = tarfile.TarInfo(name)
        tarinfo.size = len(archive.getvalue())
        archive.seek(0)
        return {
            "tarinfo": tarinfo,
            "fileobj": archive
        }

    def __create_archive(self, config_obj):

        if self.enable_drift:
            self.__create_drift_archive(
                config_obj.drift_model, config_obj.ddm_properties, config_obj.constraint_set, config_obj.drifted_transactions_schema)

        # Final configuration archive
        configuration_archive_name = BytesIO()
        with tarfile.open(fileobj=configuration_archive_name, mode="w:gz") as configuration_tar:

            # remove the scoring function from common configuration
            if 'score_function' in config_obj.common_configuration:
                del config_obj.common_configuration['score_function']

            configuration = self.__remove_unneccesary_attributes(
                config_obj.common_configuration)
            if config_obj.common_configuration:
                configuration_tar.addfile(
                    **self.__add_json_file("common_configuration.json", configuration))

            if self.enable_fairness and config_obj.fairness_configuration:
                configuration_tar.addfile(
                    **self.__add_json_file("fairness_statistics.json", config_obj.fairness_configuration))

            if self.enable_explainability and config_obj.explainability_configuration:
                configuration_tar.addfile(**self.__add_json_file(
                    "explainability_statistics.json", config_obj.explainability_configuration))

        configuration_archive_path = self.output_file_path + "/configuration_archive.tar.gz"
        self.spark.sparkContext.parallelize([configuration_archive_name.getvalue()]).map(lambda x: (None, x)).coalesce(
            1).saveAsSequenceFile(configuration_archive_path)

        configuration_archive_name.close()

        return configuration_archive_path

    def __create_drift_archive(self, drift_model, ddm_properties, constraint_set, drifted_transactions_schema):
        archive = BytesIO()

        with tarfile.open(fileobj=archive, mode="w:gz") as tar:
            # Add schema json to tar
            tar.addfile(
                **self.__add_json_file("drifted_transactions_schema.json", drifted_transactions_schema.to_json()))

            if self.enable_model_drift:
                if drift_model is not None:
                    model_path = self.output_file_path + "/drift_detection_model"
                    drift_model.save(model_path)
                    ddm_properties["drift_model_path"] = model_path

                    self.logger.info(
                        "drift_detection_model path: {}".format(model_path))

                # Add ddm properties to tar
                tar.addfile(
                    **self.__add_json_file("ddm_properties.json", ddm_properties))

            if self.enable_data_drift:
                # Add constraints to tar
                tar.addfile(
                    **self.__add_json_file("data_drift_constraints.json", constraint_set.to_json()))

        # Write the whole tar.gz as a sequence file to HDFS
        drift_archive_path = self.output_file_path + "/drift_archive.tar.gz"
        self.spark.sparkContext.parallelize([archive.getvalue()]).map(lambda x: (None, x)).coalesce(
            1).saveAsSequenceFile(drift_archive_path)
        archive.close()

        return drift_archive_path

    def __remove_unneccesary_attributes(self, common_configuration):
        attributes = ["storage", "tables", "spark_settings", "output_file_path",
                      "data_file_path", "param_file_name", "score_function"]
        for attrib in attributes:
            if attrib in common_configuration["common_configuration"]:
                del common_configuration["common_configuration"][attrib]

        if "explainability_configuration" in common_configuration:
            del common_configuration["explainability_configuration"]

        return common_configuration
