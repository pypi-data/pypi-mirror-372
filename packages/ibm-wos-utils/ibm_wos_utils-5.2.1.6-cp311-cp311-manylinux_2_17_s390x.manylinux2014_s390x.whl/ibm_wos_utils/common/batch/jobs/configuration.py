# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2021
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------
import json
import tarfile
from io import BytesIO

from ibm_wos_utils.drift.batch.constraints.manager import DataConstraintMgr
from ibm_wos_utils.drift.batch.drift_detection_model import DriftDetectionModel
from ibm_wos_utils.drift.batch.util.constants import (
    CATEGORICAL_UNIQUE_THRESHOLD, MAX_DISTINCT_CATEGORIES)
from ibm_wos_utils.explainability.utils.training_data_stats import \
    TrainingDataStats
from ibm_wos_utils.fairness.batch.utils.config_distribution_builder import \
    FairnessConfigDistributionBuilder
from ibm_wos_utils.joblib.jobs.aios_spark_job import AIOSBaseJob
from ibm_wos_utils.joblib.utils.constants import *
from ibm_wos_utils.joblib.utils.db_utils import DbUtils
from ibm_wos_utils.joblib.utils.param_utils import get


class Configuration(AIOSBaseJob):
    """Common Configuration job which generates the required artifacts based on the monitor configuration flags"""

    def run_job(self):
        try:
            self.logger.info("Started Configuration Job")
            self.output_file_path = get(self.arguments, "output_file_path")
            self.save_status("STARTED")

            self.__set_config_flags()

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

            self.__validate_spark_df(spark_df)

            configuration = {}

            constraint_set = self.__generate_drift_config(
                spark_df)
            self.__generate_explainability_config(
                spark_df, constraint_set, configuration)
            self.__generate_fairness_config(spark_df, configuration)
            self.__add_class_labels_to_prediction_field(spark_df=spark_df)

            self.__save_configuration(configuration)
            self.save_status("FINISHED")
        except Exception as ex:
            self.logger.exception(str(ex))
            self.save_exception_trace(str(ex))
            self.save_status("FAILED", additional_info={"exception": str(ex)})
            raise ex
        finally:
            pass

    def __set_config_flags(self):
        self.enable_model_drift = get(
            self.arguments, "enable_model_drift", False)
        self.enable_data_drift = get(
            self.arguments, "enable_data_drift", False)
        self.enable_explainability = get(
            self.arguments, "enable_explainability", False)
        self.enable_fairness = get(self.arguments, "enable_fairness", False)

        self.logger.info("Configuration flags are enable_model_drift:{0}, enable_data_drift:{1}, enable_explainability:{2}, enable_fairness:{3}".format(
            self.enable_model_drift, self.enable_data_drift, self.enable_explainability, self.enable_fairness))

    def __validate_and_set_params(self):
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

        # Validate feature columns
        self.feature_columns = get(
            self.arguments, "common_configuration.feature_columns", [])
        self.categorical_columns = get(
            self.arguments, "common_configuration.categorical_columns", [])

        if not self.feature_columns:
            raise Exception("No feature columns are added.")

        # Validate model type
        self.model_type = get(
            self.arguments, "common_configuration.problem_type")

        if not self.model_type:
            raise Exception("No model type is specified.")
        if self.model_type == "regression" and self.enable_model_drift:
            self.logger.warning(
                "The model type specified is regression. Disabling model drift.")
            self.enable_model_drift = False

        # Validate prediction and probability columns
        self.prediction_column = get(
            self.arguments, "common_configuration.prediction")
        self.probability_column = get(
            self.arguments, "common_configuration.probability")

        if not self.prediction_column:
            raise Exception(
                "The prediction column is missing from arguments.")
        if self.model_type != "regression" and not self.probability_column:
            raise Exception(
                "The probability column is missing from arguments.")

        self.record_id_column = get(
            self.arguments, "common_configuration.record_id")
        if not self.record_id_column:
            raise Exception(
                "The record id column is missing from arguments.")

        self.label_column = get(
            self.arguments, "common_configuration.label_column")
        if not self.label_column:
            raise Exception("No label column is supplied.")

        self.record_timestamp_column = get(
            self.arguments, "common_configuration.record_timestamp")

        self.columns = self.feature_columns.copy()
        self.columns.append(self.prediction_column)
        self.columns.append(self.record_id_column)
        self.columns.append(self.label_column)
        if self.probability_column is not None:
            self.columns.append(self.probability_column)
        if self.record_timestamp_column is not None:
            self.columns.append(self.record_timestamp_column)

        self.columns_to_filter = [self.prediction_column]

    def __validate_spark_df(self, spark_df):
        # Validate feature columns
        missing_columns = list(
            set(self.feature_columns) - set(spark_df.columns))
        if len(missing_columns) > 0:
            raise Exception(
                "The feature columns {} are not present in the training data.".format(missing_columns))
        self.logger.info("******** Feature Columns [{}]: {} ********".format(
            len(self.feature_columns), self.feature_columns))

        # Validate label column
        if self.label_column not in spark_df.columns:
            raise Exception("The label column {} is not present in the training data.".format(
                self.label_column))

        # Validate probability and prediction columns
        if self.prediction_column not in spark_df.columns:
            raise Exception("The prediction column '{}' is missing from the training data.".format(
                self.prediction_column))

        if self.model_type != "regression" and self.probability_column not in spark_df.columns:
            raise Exception("The probability column '{}' is missing from the training data.".format(
                self.probability_column))

    def __generate_ddm(self, spark_df):
        self.logger.info("Started drift detection model generation.")
        self.save_status("Model Drift Configuration STARTED")
        # Get inputs
        ddm_inputs = {
            "model_type": self.model_type,
            "feature_columns": self.feature_columns,
            "categorical_columns": self.categorical_columns,
            "label_column": self.label_column,
            "prediction": self.prediction_column,
            "probability": self.probability_column,
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
            return self.check_ddm_training_quality(
                ddm, ddm_properties, ddm_inputs.get("enable_tuning"), ddm_inputs.get("ddm_training_quality_check_threshold"))

        self.logger.info(
            "Completed drift detection model generation.")
        self.save_status("Model Drift Configuration COMPLETED")
        return ddm.ddm_model, ddm_properties

    def check_ddm_training_quality(self, ddm: DriftDetectionModel, ddm_properties, enable_tuning=False, ddm_training_check_threshold=0.3):
        # Check for ddm model quality and return ddm properties accordingly
        self.logger.info(
            "===Drift detection model training quality check started====")
        if abs(ddm.base_model_accuracy - ddm.base_predicted_accuracy) > ddm_training_check_threshold:
            new_ddm_properties = {}
            new_ddm_properties["model_drift_enabled"] = "false"
            new_ddm_properties["base_model_accuracy"] = ddm.base_model_accuracy
            new_ddm_properties["base_predicted_accuracy"] = ddm.base_predicted_accuracy
            if enable_tuning:
                new_ddm_properties["message"] = "The trained drift detection model did not meet quality standards . Drop in accuracy cannot be detected."
            else:
                new_ddm_properties["message"] = "The trained drift detection model did not meet quality standards . Drop in accuracy cannot be detected. To try again, enable tuning."

            ddm_properties = new_ddm_properties
            ddm.ddm_model = None
        self.logger.info(
            "===Drift detection model training quality check completed===")
        self.save_status("Model Drift Configuration COMPLETED")
        return ddm.ddm_model, ddm_properties

    def __generate_constraints(self, spark_df):
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
                feature_columns=self.feature_columns,
                categorical_columns=self.categorical_columns,
                callback=self.save_status,
                **drift_options)
        else:
            constraint_set = DataConstraintMgr.learn_constraints_v2(
                training_data=spark_df,
                feature_columns=self.feature_columns,
                categorical_columns=self.categorical_columns,
                callback=self.save_status,
                **drift_options)

        self.logger.info("Completed data drift constraints generation.")
        self.save_status("Data Drift Configuration COMPLETED")
        return constraint_set

    def __create_drift_archive(self, drift_model, ddm_properties, constraint_set):
        max_constraints_per_column = 1000000 if self.storage_type == StorageType.HIVE.value else 32000

        schema = DataConstraintMgr.generate_schema(
            record_id_column=self.record_id_column,
            record_timestamp_column=self.record_timestamp_column,
            model_drift_enabled=self.enable_model_drift,
            data_drift_enabled=self.enable_data_drift,
            constraint_set=constraint_set,
            max_constraints_per_column=max_constraints_per_column)

        archive = BytesIO()

        with tarfile.open(fileobj=archive, mode="w:gz") as tar:
            # Add schema json to tar
            tar.addfile(
                **self.__add_json_file("drifted_transactions_schema.json", schema.to_json()))

            if self.enable_model_drift:
                if drift_model is not None:
                    model_path = self.output_file_path + "/drift_detection_model"
                    drift_model.save(model_path)
                    ddm_properties["drift_model_path"] = model_path

                # Add ddm properties to tar
                tar.addfile(
                    **self.__add_json_file("ddm_properties.json", ddm_properties))

            if self.enable_data_drift:
                # Add constraints to tar
                tar.addfile(
                    **self.__add_json_file("data_drift_constraints.json", constraint_set.to_json()))

        # Write the whole tar.gz as a sequence file to HDFS
        self.spark.sparkContext.parallelize([archive.getvalue()]).map(lambda x: (None, x)).coalesce(
            1).saveAsSequenceFile(self.output_file_path + "/drift_configuration")
        archive.close()

    def __add_json_file(self, name, some_dict):
        some_json = BytesIO(json.dumps(some_dict, indent=4).encode("utf-8"))
        tarinfo = tarfile.TarInfo(name)
        tarinfo.size = len(some_json.getvalue())
        return {
            "tarinfo": tarinfo,
            "fileobj": some_json
        }

    def __save_configuration(self, configuration):
        configuration["batch_notebook_version"] = get(
            self.arguments, "batch_notebook_version")
        configuration["common_configuration"] = get(
            self.arguments, "common_configuration")
        conf = {"configuration": json.dumps(configuration)}
        self.logger.info("Configuration: " + str(conf))
        self.spark.createDataFrame([conf]).coalesce(1).write.json(
            self.output_file_path + "/configuration.json", mode="overwrite")

    def __generate_drift_config(self, spark_df):
        drift_model = None
        ddm_properties = {}
        constraint_set = None
        if self.enable_model_drift:
            drift_model, ddm_properties = self.__generate_ddm(spark_df)

        if self.enable_data_drift:
            constraint_set = self.__generate_constraints(spark_df)

        if self.enable_model_drift or self.enable_data_drift:
            self.__create_drift_archive(
                drift_model, ddm_properties, constraint_set)

        return constraint_set

    def __generate_explainability_config(self, spark_df, constraint_set, configuration):
        if self.enable_explainability:
            self.save_status("Explainability Configuration STARTED")
            explainability_configuration = TrainingDataStats(problem_type=self.model_type,
                                                             feature_columns=self.feature_columns,
                                                             categorical_columns=self.categorical_columns,
                                                             label_column=self.label_column,
                                                             spark_df=spark_df,
                                                             prediction_column=self.prediction_column,
                                                             probability_column=self.probability_column,
                                                             constraint_set=constraint_set).generate_explain_stats()

            configuration["explainability_configuration"] = explainability_configuration
            self.save_status("Explainability Configuration COMPLETED")

    def __generate_fairness_config(self, spark_df, configuration):
        if self.enable_fairness:
            self.save_status("Fairness Configuration STARTED")

            # Getting the fairness parameters
            fairness_parameters = get(self.arguments, "fairness_parameters")

            # Getting the common configuration
            common_configuration = get(self.arguments, "common_configuration")

            # Generating the training data distribution for the fairness attributes
            fairness_configuration = FairnessConfigDistributionBuilder(
                common_configuration, fairness_parameters, spark_df).build()

            configuration["fairness_configuration"] = fairness_configuration

            self.save_status("Fairness Configuration COMPLETED")

    def __add_class_labels_to_prediction_field(self, spark_df):
        if self.model_type == "regression":
            return

        class_labels = [x[self.label_column]
                        for x in spark_df.select(self.label_column).distinct().collect()]

        updated_fields = []
        for field in get(self.arguments, "common_configuration.output_data_schema.fields"):
            if get(field, "metadata.modeling_role") == "prediction":
                field["metadata"]["class_labels"] = class_labels

            updated_fields.append(field)

        self.arguments["common_configuration"]["output_data_schema"]["fields"] = updated_fields
