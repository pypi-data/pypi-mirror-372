
# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2020, 2021
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

import time
import sys
import json
from ibm_wos_utils.feedback.batch.utils.data_reader import DataReader
from ibm_wos_utils.feedback.batch.utils.metrics_utils import MetricsUtils
from ibm_wos_utils.feedback.batch.utils.time_window_utils import TimeWindowUtils
from ibm_wos_utils.feedback.batch.utils import constants
from ibm_wos_utils.joblib.jobs.aios_spark_job import AIOSBaseJob


class QualityJob(AIOSBaseJob):

    def run_job(self):
        """
        CLI Arguments:
            model_type - Type of the deployed model
            label_col - Label column name
            prediction_col - Prediction column name
            probability_col - Prediction column name
            timestamp_col - timestamp column name
            last_updated_timestamp - last run updated timestamp
            min_sample_records - minimum sample records to consider for the job execution
            storage_type - Database storage type
            storage_url =  Database storage url 
            table_name =  Table name in the database
            db_name =  Name of the database

        """
        json_data_output = dict()
        quality_metrics_list = list()
        try:
            log_start_time = time.time()
            params = self.arguments
            model_type = params.get("model_type")
            label_col = params.get("label_col")
            prediction_col = params.get("prediction_col")
            probability_col = params.get("probability_col")
            scoring_id_col = params.get("scoring_id_col")
            timestamp_col = None
            last_updated_timestamp = None
            if 'timestamp_col' in params:
                timestamp_col = params.get("timestamp_col")
            if 'last_updated_timestamp' in params:
                last_updated_timestamp = params.get("last_updated_timestamp")
            min_sample_records = params.get("min_sample_records")
            connection_props = params.get("storage")
            hdfs_path = params.get("output_file_path")
            spark_settings= params.get("spark_settings")

            is_history_run = False
            if 'history_runs_payload' in params:
                is_history_run = True
            output_path = "{}/{}.{}".format(
                hdfs_path, constants.JOB_OUTPUT_FILE_NAME, constants.JOB_OUTPUT_FILE_FORMAT)
            
            time_window_utils = TimeWindowUtils(self.logger)
            # Calculates the time windows for the given start date and end date in the history runs payload
            # and computes the metrics for each time window for the history runs option and there will be a
            # single time window for regulat batch flow which will compute the metrics based on the last processed time. 
            
            time_windows = time_window_utils.get_time_windows(is_history_run, params, last_updated_timestamp)
            time_window_len = len(time_windows)
            run_successful = False
            for idx, time_window in enumerate(time_windows):
                start_time = time_window[0]
                end_time = time_window[1]
                self.logger.info("Computing the metrics for the time window start_time {} and end_time {}".format(start_time, end_time))
                try:
                    spark_df, counts = DataReader(self.logger, is_history_run).read_data(
                        self.spark, scoring_id_col, label_col, prediction_col,
                        connection_props, spark_settings, timestamp_col, start_time,
                        min_sample_records, probability_column=probability_col, end_time = end_time)

                    quality_metrics = MetricsUtils(self.logger, self.spark.version).compute_quality_metrics(
                        self.sc, spark_df, model_type, label_col, prediction_col, probability_col, counts)
                    if end_time is not None:
                        quality_metrics["end_time"] = end_time

                    quality_metrics_list.append(quality_metrics)
                    run_successful = True
                    self.logger.info("Finished metrics computation for the time window start_time {} and end_time {}".format(start_time, end_time))
                except Exception as ex:
                    exc_message = str(ex)
                    if not is_history_run:
                        raise ex
                    else:
                        #log the error and continue for other time windows until the last time window is reached for history runs
                        self.logger.error("Error occurred while running for the time window start_time {} and end_time {}. \
                                    Error: {}".format(start_time, end_time, exc_message))
                        # Throw the error when the run evaluation is not successful for single time window
                        if idx == time_window_len-1 and not run_successful:
                            raise ex

            self.logger.info(
                "Saving the output to the hdfs location: {}".format(output_path))
            json_data_output["metrics"] = json.dumps(quality_metrics_list)
            self.save_data(output_path, data_json = json_data_output)

            log_end_time = time.time()
            self.logger.info("Time to complete the  quality spark metrics {}".format(
                log_end_time-log_start_time))
        except Exception as ex:
            exc_message = str(ex)
            if constants.COPY_METRICS_MESSAGE in exc_message:
                metrics_copy_msg = dict()
                metrics_copy_msg["copy_metrics"] = "true"
                quality_metrics_list.append(metrics_copy_msg)
                json_data_output["metrics"] = json.dumps(quality_metrics_list)
                self.logger.info(
                    "Saving the copy metrics output to the hdfs location: {}".format(output_path))
                self.save_data(output_path, data_json = json_data_output)

            else:
                if 'error_code' in exc_message:
                    error_code = None
                    error_params = None
                    error_msg = None
                    (args_dict,) = ex.args
                    if args_dict and isinstance(args_dict, dict):
                        error_msg = args_dict.get("error_msg")
                        error_code = args_dict.get("error_code")
                        error_params = args_dict.get("parameters")

                    self.logger.error(error_msg)
                    super().save_exception(error_msg=error_msg,
                        error_code=error_code,
                        parameters=error_params
                    )
                else:
                    self.logger.error(exc_message)
                    super().save_exception_trace(exc_message)
                raise ex
