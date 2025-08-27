# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2023
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S. Copyright Office.
# ----------------------------------------------------------------------------------------------------

import json
import time

from ibm_wos_utils.data_health.batch.metrics.metrics_manager import MetricsManager
from ibm_wos_utils.data_health.batch.utils.batch_utils import BatchUtils
from ibm_wos_utils.data_health.batch.utils.constants import DATA_HEALTH, FEEDBACK, Metrics, PAYLOAD, PROBABILITY_MODELING_ROLE, RECORD_TIMESTAMP_MODELING_ROLE
from ibm_wos_utils.fairness.batch.utils.batch_utils import BatchUtils as FairnessBatchUtils
from ibm_wos_utils.fairness.batch.utils.python_util import get
from ibm_wos_utils.joblib.jobs.aios_spark_job import AIOSBaseJob
from ibm_wos_utils.joblib.utils.db_utils import DbUtils


class DataHealthRunJob(AIOSBaseJob):

    def __init__(self, arguments: dict, job_name: str):
        """
        Constructor for the job class.
        :arguments: The arguments to the Spark job.
        :job_name: The name of the job.
        """
        super().__init__(arguments)
        self.name = job_name
    
    def run_job(self) -> None:
        """
        The entry point method for the Spark job.
        """
        self.logger.info("Started the data health metrics computation job run.")
        start_time = time.time()

        try:
            # Reading the inputs from the argument list
            subscription = get(self.arguments, "subscription")
            monitor_instance = get(self.arguments, "monitor_instance")
            monitoring_run_id = get(self.arguments, "monitoring_run_id")
            top_features_limit = get(self.arguments, "top_features_limit")
            tables = get(self.arguments, "tables")
            output_file_path = get(self.arguments, "output_file_path")

            # Reading the data to be considered
            pl_data, fb_data = self._read_data(subscription, monitor_instance, tables)
            
            # Computing the metrics on the data
            metric_values = MetricsManager.calculate_metrics(
                subscription,
                monitor_instance,
                pl_data=pl_data,
                fb_data=fb_data,
                top_features_limit=top_features_limit
            )

            if metric_values is not None:
                # Writing records marked by certain metrics to the `data_health` data source table
                self._write_marked_records(tables, metric_values, monitoring_run_id)
            
            # Storing the metrics results in the intermediate persistence layer between Spark and WOS
            output_json = {
                "job_output": metric_values
            }
            
            # Converting the value of outermost value as string because of #19045
            output_json["job_output"] = json.dumps(output_json["job_output"])
            self.logger.info("Job Output {}.".format(output_json["job_output"]))  
            
            # Write to HDFS
            output_file_name = "{}.json".format(self.name)
            output_path = "{}/{}".format(output_file_path, output_file_name)
            self.save_data(path=output_path, data_json=output_json)
            self.logger.info("The output file successfully stored in HDFS at {}.".format(output_path))
        except Exception as ex:
            error_message = str(ex)
            self.save_exception_trace(error_message)
            raise ex

        self.logger.info("Completed the data health metrics computation job run in {} seconds.".format(time.time() - start_time))

        return
    
    def _write_marked_records(self, tables: list, metric_values: dict, monitoring_run_id: str) -> None:
        """
        Writes the record-ids for the metrics that marked the records.
        :tables: The tables list.
        :metric_values: The `metric_values` object.
        :monitoring_run_id: The monitoring run ID.

        :returns: None.
        """

        for metric_id in metric_values["metrics"]:
            if metric_id == Metrics.CLASS_CONFUSION.value:
                # Getting the record-ids
                record_ids = get(metric_values, "metrics.{}.payload.scoring_ids".format(metric_id))
                if record_ids is not None and len(record_ids) > 0:
                    # Building the data-frame to write
                    record_id_df = self.spark.createDataFrame(
                        [
                            [monitoring_run_id, metric_id, x] for x in record_ids
                        ],
                        ["monitoring_run_id", "metric_id", "record-id"]
                    )
                    
                    # Getting the `data_health` table details
                    data_source_type = "{}_{}".format(DATA_HEALTH, PAYLOAD)
                    data_health_table = BatchUtils.get_table_details(tables, data_source_type)
                    database_name = get(data_health_table, "database")
                    schema_name = get(data_health_table, "schema")
                    table_name = get(data_health_table, "table")
                    
                    # Writing the record-ids to the table
                    DbUtils.write_dataframe_to_table(
                        spark_df=record_id_df,
                        location_type=self.location_type_map.get(data_source_type),
                        database_name=database_name,
                        table_name=table_name,
                        schema_name=schema_name,
                        connection_properties=self.jdbc_connection_properties_map.get(data_source_type),
                        spark=self.spark
                    )
        
        return
    
    def _read_data(self, subscription: dict, monitor_instance: dict, tables: list):
        """
        Reads the payload logging and the feedback data for the given subscription given their availability.
        :subscription: The subscription object.
        :monitor_instance: The `data_health` monitor instance object.
        :tables: The list of table details sent as Spark job arguments.

        :returns: The payload and feedback data.
        """
        pl_data = fb_data = None

        # Getting the last processed time
        last_processed_timestamp = get(monitor_instance, "entity.parameters.last_processed_timestamp")

        # Getting the output data schema
        output_data_schema = get(subscription, "entity.asset_properties.output_data_schema")

        # Getting the timestamp column name
        timestamp_column = FairnessBatchUtils.get_name_with_modeling_role(RECORD_TIMESTAMP_MODELING_ROLE, output_data_schema)

        # Checking presence of `payload` table
        pl_table = BatchUtils.get_table_details(tables, PAYLOAD)
        if pl_table is not None:
            # Getting the payload table details
            pl_db_name = get(pl_table, "database")
            pl_table_name = get(pl_table, "table")
            pl_schema_name = get(pl_table, "schema")
            pl_partition_column = get(pl_table, "parameters.partition_column")
            pl_num_partitions = get(pl_table, "parameters.num_partitions")
            
            # Getting the probability column (Would be None in case of regression models)
            probability_column = FairnessBatchUtils.get_name_with_modeling_role(PROBABILITY_MODELING_ROLE, output_data_schema)

            # Generating columns to map and filter
            columns_to_map = BatchUtils.get_all_names_from_schema(output_data_schema)
            columns_to_filter = [probability_column]

            # Reading the payload data
            pl_data = DbUtils.get_table_as_dataframe(
                self.spark,
                self.location_type_map.get(PAYLOAD),
                pl_db_name,
                pl_table_name,
                schema_name=pl_schema_name,
                connection_properties=self.jdbc_connection_properties_map[PAYLOAD],
                columns_to_map=columns_to_map,
                columns_to_filter=columns_to_filter,
                probability_column=probability_column,
                record_timestamp_column=timestamp_column,
                start_time=last_processed_timestamp,
                partition_column=pl_partition_column,
                num_partitions=pl_num_partitions
            )
        
        # Checking presence of `feedback` table
        fb_table = BatchUtils.get_table_details(tables, FEEDBACK)
        if fb_table is not None:
            # Getting the feedback table details
            fb_db_name = get(fb_table, "database")
            fb_table_name = get(fb_table, "table")
            fb_schema_name = get(fb_table, "schema")
            fb_partition_column = get(fb_table, "parameters.partition_column")
            fb_num_partitions = get(fb_table, "parameters.num_partitions")

            # Generating columns to map and filter
            columns_to_map = BatchUtils.get_feedback_table_columns(subscription)
            columns_to_filter = []

            # Reading the feedback data
            fb_data = DbUtils.get_table_as_dataframe(
                self.spark,
                self.location_type_map.get(FEEDBACK),
                fb_db_name,
                fb_table_name,
                schema_name=fb_schema_name,
                connection_properties=self.jdbc_connection_properties_map[FEEDBACK],
                columns_to_map=columns_to_map,
                columns_to_filter=columns_to_filter,
                probability_column=probability_column,
                record_timestamp_column=timestamp_column,
                start_time=last_processed_timestamp,
                partition_column=fb_partition_column,
                num_partitions=fb_num_partitions
            )

        return pl_data, fb_data