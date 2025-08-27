# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2021
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

import copy
import json
import time

from ibm_wos_utils.fairness.batch.utils.batch_utils import BatchUtils
from ibm_wos_utils.fairness.batch.utils.config_distribution_builder import FairnessConfigDistributionBuilder
from ibm_wos_utils.fairness.batch.utils.python_util import get
from ibm_wos_utils.joblib.jobs.aios_spark_job import AIOSBaseJob
from ibm_wos_utils.joblib.utils.db_utils import DbUtils


class TrainingStatsComputationJob(AIOSBaseJob):

    def __init__(self, arguments, job_name):
        """
        Constructor for the job class.
        :arguments: The arguments to the Spark job.
        """
        super().__init__(arguments)
        self.name = job_name

    def run_job(self) -> None:
        """
        The entry point method for the Spark job.
        """
        self.logger.info("Started the training stats computation job run.")

        try:
            training_stats_start_time = time.time()
            # Reading the inputs from the argument list
            subscription = get(self.arguments, "subscription")
            monitor_instance = get(self.arguments, "monitor_instance")
            output_file_path = get(self.arguments, "output_file_path")

            distribution_counts = None
            # Checking for training data source in subscription
            training_data_source = BatchUtils.get_data_source_from_subscription(subscription, "training")

            if training_data_source is None:
                self.logger.info("Could not generate training data distribution (training stats) as training data source is not present in the subscription.")
            else:
                # Getting the training data table details
                database_name = get(training_data_source, "database_name")
                table_name = get(training_data_source, "table_name")
                schema_name = get(training_data_source, "schema_name")
                training_data_schema = get(subscription, "entity.asset_properties.training_data_schema")
                columns_to_map = [field["name"] for field in get(training_data_schema, "fields")]
                partition_column = get(training_data_source, "parameters.partition_column")
                num_partitions = get(training_data_source, "parameters.num_partitions")
                if num_partitions is None and partition_column is not None:
                    spark_settings = self.arguments.get("spark_settings", BatchUtils.get_spark_settings_from_subscription(subscription))
                    if spark_settings is not None:
                        num_partitions = int(spark_settings.get("max_num_executors", 1)) * int(spark_settings.get("executor_cores", 1))
                    else:
                        num_partitions = 1
                
                # Reading the data
                training_df = DbUtils.get_table_as_dataframe(
                    spark=self.spark,
                    location_type=self.location_type,
                    database_name=database_name,
                    table_name=table_name,
                    schema_name=schema_name,
                    connection_properties=self.jdbc_connection_properties,
                    columns_to_map=columns_to_map,
                    partition_column=partition_column,
                    num_partitions=num_partitions
                )

                # Getting the configuration parameters
                common_configuration = get(subscription, "entity.asset_properties")
                training_fairness_parameters = copy.deepcopy(get(monitor_instance, "entity.parameters"))

                # Updating the `class_label` based on training data, i.e., label column
                training_fairness_parameters["class_label"] = get(subscription, "entity.asset_properties.label_column")

                # Generating the distributions
                fairness_configuration_with_training_stats = FairnessConfigDistributionBuilder(
                    common_configuration=common_configuration,
                    fairness_parameters=training_fairness_parameters,
                    training_df=training_df
                ).build()

                # Getting the training stats
                distribution_counts = {
                    "training_data_distributions": get(fairness_configuration_with_training_stats, "parameters.training_data_distributions"),
                    "training_data_records_count": get(fairness_configuration_with_training_stats, "parameters.training_data_records_count"),
                    "training_data_class_label": get(fairness_configuration_with_training_stats, "parameters.training_data_class_label"),
                    "training_data_last_processed_time": get(fairness_configuration_with_training_stats, "parameters.training_data_last_processed_time"),
                    "training_data_measurements_computed": get(fairness_configuration_with_training_stats, "parameters.training_data_measurements_computed")
                }
                training_stats_time_taken = time.time() - training_stats_start_time
                output_json = {
                    "job_output": [
                        {
                            "data_name": "training",
                            "counts": distribution_counts,
                            "time_taken": training_stats_time_taken
                        }
                    ]
                }
                
                # Converting the value of outermost value as string because of #19045
                output_json["job_output"] = json.dumps(output_json["job_output"])

                # Write to HDFS
                output_file_name = "{}.json".format(self.name)
                output_path = "{}/{}".format(output_file_path, output_file_name)
                self.save_data(path=output_path, data_json=output_json)
                self.logger.info("The output file successfully stored in HDFS at {}.".format(output_path))
        except Exception as ex:
            self.save_exception_trace(str(ex))
            raise ex
        
        return