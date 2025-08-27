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
import time
import pickle
import os
import io

import logging
import logging.config

from ibm_wos_utils.drift.batch.constraints.manager import DataConstraintMgr
from ibm_wos_utils.drift.batch.drift_detection_model import DriftDetectionModel
from ibm_wos_utils.drift.batch.util.constants import (
    CATEGORICAL_UNIQUE_THRESHOLD, MAX_DISTINCT_CATEGORIES)
from ibm_wos_utils.explainability.utils.training_data_stats import \
    TrainingDataStats
from ibm_wos_utils.fairness.batch.utils.config_distribution_builder import \
    FairnessConfigDistributionBuilder
from ibm_wos_utils.explainability.utils.perturbations import Perturbations

from ibm_wos_utils.joblib.utils.constants import *
from ibm_wos_utils.joblib.utils.param_utils import get
from ibm_wos_utils.joblib.utils.notebook_utils import generate_schemas


class ConfigurationGenerator():
    """Common Configuration class which generates the required artifacts based on the monitor configuration flags"""

    def __init__(self, configuration_params, spark_df, logger=None, log_function=None):
        try:

            self.logger = logger
            if self.logger == None:
                self.logger = logging.getLogger(__name__)

            self.log_function = log_function
            if log_function == None:
                self.log_function = self.__log_function

            self.__validate_config_info(configuration_params)

            self.arguments = configuration_params
            self.spark_df = spark_df
            self.config_obj = ConfigurationArchiveObj()

        except Exception as ex:
            self.logger.exception(str(ex))
            # self.save_exception_trace(str(ex))
            self.log_function("FAILED", additional_info={"exception": str(ex)})
            raise ex
        finally:
            pass

    def generate_configuration(self, **kwargs):

        self.logger.info("Started simplified Configuration Job")
        self.log_function("STARTED - Generate configuration")

        self.logger.info("Total Rows to use {}".format(self.spark_df.count()))

        self.__set_config_flags()

        # self.__validate_spark_df(self.spark_df)

        common_configuration = generate_schemas(self.spark_df, self.arguments)

        self.arguments['common_configuration'] = common_configuration

        self.log_function("Schema generated successfully")

        self.__validate_and_set_params()

        start_time = time.time()
        drifted_transactions_schema, ddm_properties, constraint_set, drift_model = self.__generate_drift_config(
            self.spark_df, kwargs.get('max_constraints_per_column', 32000))
        if ddm_properties is not None and kwargs.get('spark_version') is not None:
            ddm_properties["drift_model_version"] = "spark-{}".format(
                kwargs.get('spark_version'))
        self.logger.info(" Time taken to generate drift config {}".format(
            time.time() - start_time))

        start_time = time.time()
        explainability_configuration = self.__generate_explainability_config(
            self.spark_df, constraint_set, common_configuration)
        self.logger.info(" Time taken to generate explain config {}".format(
            time.time() - start_time))

        start_time = time.time()
        fairness_configuration = self.__generate_fairness_config(
            self.spark_df, common_configuration)
        self.logger.info(" Time taken to generate fairness config {}".format(
            time.time() - start_time))

        self.log_function("FINISHED - Generate configuration")
        self.logger.info("Finished simplified Configuration Job")

        common_conf = {}
        common_conf['common_configuration'] = common_configuration
        common_conf['fairness_configuration'] = fairness_configuration
        common_conf['explainability_configuration'] = explainability_configuration

        self.config_obj.common_configuration = common_conf
        self.config_obj.fairness_configuration = fairness_configuration
        self.config_obj.explainability_configuration = explainability_configuration
        self.config_obj.constraint_set = constraint_set
        self.config_obj.ddm_properties = ddm_properties
        self.config_obj.drift_model = drift_model
        self.config_obj.drifted_transactions_schema = drifted_transactions_schema

        if 'generate_archive' in kwargs:
            if kwargs['generate_archive'] == True:
                self.__create_archive(self.config_obj)

        return self.config_obj

    def __log_function(self, status: str = None):
        print(status)

    def __validate_config_info(self, configuration_params):
        model_type = configuration_params.get("problem_type")
        if model_type is None:
            model_type = configuration_params.get("model_type")
        missing_details = []
        if configuration_params.get("label_column") is None:
            missing_details.append("label_column")

        if configuration_params.get("prediction") is None:
            missing_details.append("prediction")

        if model_type != "regression" and configuration_params.get("probability") is None:
            missing_details.append("probability")

        if len(missing_details) > 0:
            raise Exception(
                "Missing information in config_info. Details:{}".format(missing_details))

    def __set_config_flags(self):
        self.enable_model_drift = get(
            self.arguments, "drift_parameters.model_drift.enable", False)
        self.enable_data_drift = get(
            self.arguments, "drift_parameters.data_drift.enable", False)
        self.enable_explainability = get(
            self.arguments, "enable_explainability", False)
        self.enable_drift = get(
            self.arguments, "enable_drift", False)

        self.enable_fairness = get(self.arguments, "enable_fairness", False)

        self.logger.info("Configuration flags are enable_model_drift:{0}, enable_data_drift:{1}, enable_explainability:{2}, enable_fairness:{3}".format(
            self.enable_model_drift, self.enable_data_drift, self.enable_explainability, self.enable_fairness))

    def __validate_and_set_params(self):

        self.feature_columns = get(
            self.arguments, "common_configuration.feature_columns", [])

        self.categorical_columns = get(
            self.arguments, "common_configuration.categorical_columns", [])

        # Validate model type
        self.model_type = get(
            self.arguments, "common_configuration.problem_type")
        if self.model_type is None:
            self.model_type = get(
                self.arguments, "common_configuration.model_type")

        if self.model_type == "regression" and self.enable_model_drift:
            self.logger.warning(
                "The model type specified is regression. Disabling model drift.")
            self.enable_model_drift = False

        # Validate prediction and probability columns
        self.prediction_column = get(
            self.arguments, "common_configuration.prediction")
        self.probability_column = get(
            self.arguments, "common_configuration.probability")

        self.record_id_column = get(
            self.arguments, "common_configuration.record_id")
        if not self.record_id_column:
            raise Exception(
                "The record id column is missing from arguments.")

        self.label_column = get(
            self.arguments, "common_configuration.label_column")

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

        self.columns_to_filter = []
        if self.model_type != "regression":
            self.columns_to_filter.append(self.prediction_column)

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
        self.log_function("Model Drift Configuration STARTED")
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
            # "drift_model_version": "spark-{}".format(self.spark.version),
            # "drift_model_version": "spark-{}".format("3.0.2"), #TODO Do we really need this attribute
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
        self.log_function("Model Drift Configuration COMPLETED")
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
            "Drift detection model training quality check completed")
        self.log_function("Model Drift Configuration COMPLETED")
        return ddm.ddm_model, ddm_properties

    def __generate_constraints(self, spark_df):
        self.logger.info("Started data drift constraints generation.")
        self.log_function("Data Drift Configuration STARTED")
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
                callback=self.log_function,
                **drift_options)
        else:
            constraint_set = DataConstraintMgr.learn_constraints_v2(
                training_data=spark_df,
                feature_columns=self.feature_columns,
                categorical_columns=self.categorical_columns,
                callback=self.log_function,
                **drift_options)

        self.logger.info("Completed data drift constraints generation.")
        self.log_function("Data Drift Configuration COMPLETED")
        return constraint_set

    # TODO rename the mdethod
    def __generate_drifted_txns_schema(self, constraint_set, max_constraints_per_column):

        schema = DataConstraintMgr.generate_schema(
            record_id_column=self.record_id_column,
            record_timestamp_column=self.record_timestamp_column,
            model_drift_enabled=self.enable_model_drift,
            data_drift_enabled=self.enable_data_drift,
            constraint_set=constraint_set,
            max_constraints_per_column=max_constraints_per_column)

        return schema

    def __add_json_file(self, name, some_dict):
        some_json = BytesIO(json.dumps(some_dict, indent=4).encode("utf-8"))
        tarinfo = tarfile.TarInfo(name)
        tarinfo.size = len(some_json.getvalue())
        return {
            "tarinfo": tarinfo,
            "fileobj": some_json
        }

    def __generate_drift_config(self, spark_df, max_constraints_per_column):
        drift_model = None
        ddm_properties = {}
        constraint_set = None
        drifted_transactions_schema = None
        ddm_properties = None

        if self.enable_drift:
            if self.enable_model_drift:
                drift_model, ddm_properties = self.__generate_ddm(spark_df)

            if self.enable_data_drift:
                constraint_set = self.__generate_constraints(spark_df)

            if self.enable_model_drift or self.enable_data_drift:
                drifted_transactions_schema = self.__generate_drifted_txns_schema(
                    constraint_set, max_constraints_per_column)

        return drifted_transactions_schema, ddm_properties, constraint_set, drift_model

    def __generate_explainability_config(self, spark_df, constraint_set, configuration):
        explainability_configuration = None
        if self.enable_explainability:
            self.log_function("Explainability Configuration STARTED")
            explainability_configuration = TrainingDataStats(
                problem_type=configuration.get("problem_type"),
                feature_columns=self.feature_columns,
                categorical_columns=self.categorical_columns,
                label_column=self.label_column,
                spark_df=spark_df,
                prediction_column=configuration.get("prediction"),
                probability_column=configuration.get("probability"),
                constraint_set=constraint_set,
                class_labels=configuration.get("class_labels")).generate_explain_stats()
            # Note: actual scoring and generation of purtubation of job will be done after the archives are generated

            self.log_function("Explainability Configuration COMPLETED")

        return explainability_configuration

    def __generate_fairness_config(self, spark_df, configuration):
        fairness_configuration = None
        if self.enable_fairness:
            self.log_function("Fairness Configuration STARTED")

            # Getting the fairness parameters
            fairness_parameters = get(self.arguments, "fairness_parameters")

            # Getting the common configuration
            common_configuration = get(self.arguments, "common_configuration")

            # Generating the training data distribution for the fairness attributes
            fairness_configuration = FairnessConfigDistributionBuilder(
                common_configuration, fairness_parameters, spark_df).build()

            self.log_function("Fairness Configuration COMPLETED")

        return fairness_configuration

    def __create_archive(self, config_obj):

        # Build Drift tar
        if self.enable_drift:
            drift_archive_filename = "drift_archive.tar.gz"
            self.__create_drift_model_archive(drift_archive_filename, config_obj.drift_model,
                                              config_obj.ddm_properties, config_obj.constraint_set, config_obj.drifted_transactions_schema)

        # Final configuration archive
        configuration_archive_name = "configuration_archive.tar.gz"
        with tarfile.open(configuration_archive_name, mode="w:gz") as configuration_tar:

            # remove the scoring function from common configuration
            if 'score_function' in config_obj.common_configuration:
                del config_obj.common_configuration['score_function']

            if config_obj.common_configuration:
                common_configuration_json = io.BytesIO(json.dumps(
                    config_obj.common_configuration, indent=4).encode('utf8'))
                tarinfo = tarfile.TarInfo("common_configuration.json")
                tarinfo.size = len(common_configuration_json.getvalue())
                configuration_tar.addfile(
                    tarinfo=tarinfo, fileobj=common_configuration_json)

            if self.enable_fairness:
                fairness_configuration_json = io.BytesIO(json.dumps(
                    config_obj.fairness_configuration, indent=4).encode('utf8'))
                tarinfo = tarfile.TarInfo("fairness_statistics.json")
                tarinfo.size = len(fairness_configuration_json.getvalue())
                configuration_tar.addfile(
                    tarinfo=tarinfo, fileobj=fairness_configuration_json)

            if self.enable_explainability:
                explainability_configuration_json = io.BytesIO(json.dumps(
                    config_obj.explainability_configuration, indent=4).encode('utf8'))
                tarinfo = tarfile.TarInfo("explainability_statistics.json")
                tarinfo.size = len(
                    explainability_configuration_json.getvalue())
                configuration_tar.addfile(
                    tarinfo=tarinfo, fileobj=explainability_configuration_json)
                
            if self.enable_drift:
                configuration_tar.add(drift_archive_filename)

        if self.enable_drift:
            os.remove(drift_archive_filename)

    def __create_drift_model_archive(self, file_name, drift_detection_model, ddm_properties, constraints, drifted_transactions_schema):
        """Creates a tar file with the drift detection model and constraints

        Arguments:
            drift_detection_model {DriftDetectionModel} -- the drift detection model to save
            constraints - column constraints
            ddm_properties - ddm properties to be referred in case of exceptions/warnings

        Keyword Arguments:
            path_prefix {str} -- path of the directory to save the file (default: {"."})
            file_name {str} -- name of the tar file (default: {"drift_detection_model.tar.gz"})

        Raises:
            Exception: If there is an issue while creating directory, pickling the model or creating the tar file
        """
        path_prefix = "."
        try:
            os.makedirs(path_prefix, exist_ok=True)

            drift_detection_model_filename = "drift_detection_model"
            if drift_detection_model:
                drift_detection_model.write().overwrite().save(drift_detection_model_filename)
                with tarfile.open(drift_detection_model_filename + '.tar.gz', mode='w:gz') as archive:
                    archive.add(drift_detection_model_filename)

            with tarfile.open(file_name, mode="w:gz") as model_tar:

                '''
                model_pkl = io.BytesIO(pickle.dumps(drift_detection_model))
                if model_pkl:
                    tarinfo = tarfile.TarInfo("drift_detection_model.pkl")
                    tarinfo.size = len(model_pkl.getvalue())
                    model_tar.addfile(tarinfo=tarinfo, fileobj=model_pkl)
                '''
                if drift_detection_model:
                    model_tar.add(drift_detection_model_filename)

                if ddm_properties is None:
                    ddm_properties = {}
                # ddm_properties["drift_model_version"] = "scikit-learn-{}".format(sklearn.__version__)

                ddm_properties_json = io.BytesIO(json.dumps(
                    ddm_properties, indent=4).encode('utf8'))
                tarinfo = tarfile.TarInfo("ddm_properties.json")
                tarinfo.size = len(ddm_properties_json.getvalue())
                model_tar.addfile(
                    tarinfo=tarinfo, fileobj=ddm_properties_json)

                if constraints:
                    constraints_json = io.BytesIO(json.dumps(
                        constraints.to_json(), indent=4).encode('utf8'))
                    tarinfo = tarfile.TarInfo("data_drift_constraints.json")
                    tarinfo.size = len(constraints_json.getvalue())
                    model_tar.addfile(
                        tarinfo=tarinfo, fileobj=constraints_json)

                if drifted_transactions_schema:
                    drifted_transactions_schema_json = io.BytesIO(json.dumps(
                        drifted_transactions_schema.to_json(), indent=4).encode('utf8'))
                    tarinfo = tarfile.TarInfo(
                        "drifted_transactions_schema.json")
                    tarinfo.size = len(
                        drifted_transactions_schema_json.getvalue())
                    model_tar.addfile(
                        tarinfo=tarinfo, fileobj=drifted_transactions_schema_json)

            os.remove(drift_detection_model_filename + '.tar.gz')
            import shutil
            shutil.rmtree(drift_detection_model_filename)

        except (OSError, pickle.PickleError, tarfile.TarError):
            raise Exception(
                "There was a problem creating tar file for drift detection model.")


class ConfigurationArchiveObj():

    def __init__(self):

        self.common_configuration = None
        self.fairness_configuration = None
        self.explainability_configuration = None
        self.explain_perturbation_df = None
        self.constraint_set = None
        self.ddm_properties = None
        self.drift_model = None
        self.drifted_transactions_schema = None
