# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2022
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------
import base64
import json
import logging
import logging.config
import os
import tarfile

import numpy as np
from ibm_wos_utils.common.batch.jobs.simplified_configuration import \
    SimplifiedConfiguration
from ibm_wos_utils.joblib.clients.engine_client import EngineClient
from ibm_wos_utils.joblib.utils.notebook_utils import JobStatus, validate_config_info
from ibm_wos_utils.joblib.utils.param_utils import get


class ConfigurationUtility():
    """Common Configuration job which generates the required artifacts based on the monitor configuration flags"""

    def __init__(self, common_config, training_data_connection, spark_connection_settings, spark_df=None, logger=None, log_function=None):
        try:

            self.logger = logger
            if self.logger == None:
                self.logger = logging.getLogger(__name__)

            self.training_data_connection = training_data_connection
            self.spark_connection_settings = spark_connection_settings
            self.common_config = common_config

            self.enabled_explainability = get(
                self.common_config, "enable_explainability", False)
            self.enabled_fairness = get(
                self.common_config, "enable_fairness", False)

            self.enabled_drift = get(self.common_config, "enable_drift", False)
            self.enabled_model_drift = False if not self.enabled_drift else get(
                self.common_config, "drift_parameters.model_drift.enable", True)
            self.enabled_data_drift = False if not self.enabled_drift else get(
                self.common_config, "drift_parameters.data_drift.enable", True)

            if get(self.common_config, "model_type") == "regression":
                self.enabled_model_drift = False

            # if enable_drift is True and both drift_parameters.model_drift.enable
            # and drift_parameters.data_drift.enable are False, set enable_drift to False
            if not self.enabled_model_drift and not self.enabled_data_drift:
                self.enabled_drift = False

            self.spark_df = spark_df

            self.run_as_job = True

            validate_config_info(config_info=common_config)

            # Need to validate score function since other validations are done as part of configuration_generator class
            self.score_function = get(
                self.common_config, "score_function", None)
            if self.enabled_explainability:
                if self.score_function == None:
                    raise Exception(
                        "Missing information in config_info. Details:{}".format("score_function is required for explainability"))

            self.score_batch_size = get(
                self.common_config, "score_batch_size", 1000)
        except Exception as ex:
            self.logger.exception(str(ex))
            raise ex

    def generate_configuration(self, **kwargs):
        # TODO add logic to check whether we want to run as job.
        self.run_as_job = True
        if self.run_as_job:
            try:
                common_config = self.common_config
                common_config["storage"] = get(
                    self.training_data_connection, "storage_details", None)
                common_config["tables"] = get(
                    self.training_data_connection, "tables", None)

                problem_type = get(common_config, "problem_type", None)
                if problem_type is None:
                    common_config["problem_type"] = get(
                        common_config, "model_type")

                del common_config["score_function"]

                spark_settings = get(
                    self.spark_connection_settings, "spark_settings", None)

                configuration_params = {
                    "arguments": common_config,
                    "spark_settings": spark_settings,
                    "dependency_zip": [],
                    "conf": get(spark_settings, "conf", None)
                }

                self.job_params = configuration_params

                job_name = "Simplified_Configuration_Job"
                client = EngineClient(
                    credentials=self.spark_connection_settings["credentials"])
                job_response = client.engine.run_job(job_name=job_name, job_class=SimplifiedConfiguration,
                                                     job_args=self.job_params, background=True)
                JobStatus(client, job_response).print_status()

                self.__make_single_archive(job_response.get(
                    "output_file_path"), client.engine)
            except Exception as ex:
                self.logger.exception(str(ex))
                raise ex

    def __make_single_archive(self, output_path, client_engine):
        # Step 1: Build the tar files from binary content
        # Step 2: Extract the tar files
        # Step 3: Add the appropriate files to tar files
        try:
            spark_module = __import__("pyspark.sql", fromlist=["SparkSession"])
        except Exception as e:
            msg = "Unable to find pyspark library to compute metrics. Please install it "
            raise Exception(msg)

        spark_session = getattr(spark_module, "SparkSession")
        spark = spark_session.builder.appName(
            "Simplified Common Configuration Generation").getOrCreate()

        configuration_archive = client_engine.get_file(
            output_path + "/configuration_archive.tar.gz")
        if self.enabled_drift:
            drift_archive = client_engine.get_file(
                output_path + "/drift_archive.tar.gz")

        archive_directory = "./archives"
        if not os.path.exists(archive_directory):
            os.mkdir(archive_directory)

        # with NamedTemporaryFile() as binary_file:
        with open("configuration_archive.tar.gz", mode="wb") as binary_file:
            binary_file.write(configuration_archive)
            binary_file.flush()
            configuration_archive_tar = spark.sparkContext.sequenceFile(
                binary_file.name).collect()[0][1]

            with open(archive_directory + "/configuration_package.tar.gz", "wb") as binary_file:
                binary_file.write(configuration_archive_tar)

        os.remove("configuration_archive.tar.gz")

        if self.enabled_drift:
            # with NamedTemporaryFile() as binary_file:
            with open("drift.tar.gz", mode="wb") as binary_file:
                binary_file.write(drift_archive)
                binary_file.flush()
                drift_archive_tar = spark.sparkContext.sequenceFile(
                    binary_file.name).collect()[0][1]

            with open(archive_directory + "/drift_archive.tar.gz", "wb") as binary_file:
                binary_file.write(drift_archive_tar)

            os.remove("drift.tar.gz")

        with tarfile.open(archive_directory + "/configuration_package.tar.gz", "r:gz") as f:
            f.extractall(archive_directory)

        common_config = None
        with open(archive_directory + "/common_configuration.json") as f:
            common_config = json.load(f)

        # update as per class probabilities if any
        class_probabilities = self.common_config.get(
            "class_probabilities") if self.common_config.get("model_type") != "regression" else None
        if not class_probabilities:
            # explicitly set it to None to avoid it being empty
            class_probabilities = None

        if class_probabilities is not None:
            # clean up any class probability columns already added
            updated_output_data_schema_fields = []
            for field in get(common_config, "common_configuration.output_data_schema.fields"):
                if get(field, "metadata.modeling_role") == "class_probability":
                    continue

                updated_output_data_schema_fields.append(field)

            # add class probabilities to output_data_schema
            for class_probability in class_probabilities:
                updated_output_data_schema_fields.append({
                    "name": class_probability,
                    "type": "double",
                    "nullable": True,
                    "metadata": {
                        "modeling_role": "class_probability"
                    }
                })

            common_config["common_configuration"]["output_data_schema"]["fields"] = updated_output_data_schema_fields
            common_config["common_configuration"]["probability_fields"] = class_probabilities

            with open(archive_directory + "/common_configuration.json", "w") as f:
                json.dump(common_config, f)

        common_config = common_config.get("common_configuration")
        if self.enabled_explainability:
            from ibm_wos_utils.explainability.utils.perturbations import \
                Perturbations
            with open(archive_directory + "/explainability_statistics.json") as stats_file:
                model_type = self.common_config["model_type"]
                explainability_configuration = json.load(stats_file)
                perturbations = Perturbations(training_stats=explainability_configuration,
                                              problem_type=model_type,
                                              output_data_schema=common_config.get("output_data_schema"))
                perturbs_df = perturbations.generate_perturbations()

                predict_probabilities = []
                for i in range(0, len(perturbs_df), self.score_batch_size):
                    predict_probabilities.append(
                        self.score_function(perturbs_df.iloc[i:i+self.score_batch_size, :]))

                # scoring function returns in order: array_of_probabilities, array_of_predictions
                # for regression model, we expect return: array_of_predictions
                if model_type == "regression":
                    scored_perturbations = {
                        "predictions": np.concatenate(predict_probabilities).tolist()
                    }
                else:
                    scored_perturbations = {
                        "probabilities": np.concatenate([p[0] for p in predict_probabilities]).tolist(),
                        "predictions": np.concatenate([p[1] for p in predict_probabilities]).tolist()
                    }

                with open(archive_directory + "/lime_scored_perturbations.json", "w") as f:
                    f.write(json.dumps(scored_perturbations))

                with open(archive_directory + "/training_statistics.json", "w") as f:
                    f.write(json.dumps(
                        {"training_statistics": explainability_configuration}))

                with tarfile.open(archive_directory + "/explainability.tar.gz", "w:gz") as f:
                    f.add(archive_directory + "/lime_scored_perturbations.json",
                          arcname="lime_scored_perturbations.json")
                    f.add(archive_directory + "/training_statistics.json",
                          arcname="training_statistics.json")

        # Step 2
        if self.enabled_drift:
            with tarfile.open(archive_directory + "/drift_archive.tar.gz", "r:gz") as f:
                f.extractall(archive_directory)

            #drift_detection_model = None
            if os.path.exists(archive_directory + "/ddm_properties.json"):
                with open(archive_directory + "/ddm_properties.json") as ddm_file:
                    ddm_properties = json.load(ddm_file)
                    ddm_path = ddm_properties["drift_model_path"]
                    drift_detection_model = client_engine.download_directory(
                        ddm_path)
                    if drift_detection_model is not None:
                        with open(archive_directory + "/model.tar.gz", "wb") as binary_file:
                            binary_file.write(drift_detection_model)
            with tarfile.open(archive_directory + "/drift_archive.tar.gz", "w:gz") as f:
                f.add(archive_directory + "/drifted_transactions_schema.json",
                      arcname="drifted_transactions_schema.json")
                if self.enabled_data_drift:
                    f.add(archive_directory + "/data_drift_constraints.json",
                          arcname="data_drift_constraints.json")

                if self.enabled_model_drift:
                    f.add(archive_directory + "/ddm_properties.json",
                          arcname="ddm_properties.json")
                    f.add(archive_directory + "/model.tar.gz",
                          arcname="model.tar.gz")

        # Step 3
        with tarfile.open(archive_directory + "/configuration_archive.tar.gz", "w:gz") as f:
            f.add(archive_directory + "/common_configuration.json",
                  arcname="common_configuration.json")
            if self.enabled_fairness:
                f.add(archive_directory + "/fairness_statistics.json",
                      arcname="fairness_statistics.json")
            if self.enabled_drift:
                f.add(archive_directory + "/drift_archive.tar.gz",
                      arcname="drift_archive.tar.gz")
            if self.enabled_explainability:
                f.add(archive_directory + "/explainability.tar.gz",
                      arcname="explainability.tar.gz")

        self.__delete_file(archive_directory + "/common_configuration.json")
        self.__delete_file(archive_directory + "/configuration_package.tar.gz")

        self.__delete_file(archive_directory + "/data_drift_constraints.json")
        self.__delete_file(archive_directory +
                           "/drifted_transactions_schema.json")
        self.__delete_file(archive_directory + "/ddm_properties.json")
        self.__delete_file(archive_directory + "/drift_archive.tar.gz")
        self.__delete_file(archive_directory + "/model.tar.gz")

        self.__delete_file(archive_directory + "/training_statistics.json")
        self.__delete_file(archive_directory +
                           "/lime_scored_perturbations.json")
        self.__delete_file(archive_directory + "/explainability.tar.gz")
        self.__delete_file(archive_directory +
                           "/explainability_statistics.json")

        self.__delete_file(archive_directory + "/fairness_statistics.json")

    def create_download_link(self, data, filename="configuration_archive.tar.gz"):
        format_args = {
            "payload": base64.b64encode(data).decode(),
            "title": "Download Configuration Archive",
            "filename": filename
        }

        from IPython.display import HTML
        html = '<a download="{filename}" href="data:text/json;base64,{payload}" target="_blank">{title}</a>'
        return HTML(html.format(**format_args))

    def __delete_file(self, filename):
        if os.path.exists(filename):
            os.remove(filename)