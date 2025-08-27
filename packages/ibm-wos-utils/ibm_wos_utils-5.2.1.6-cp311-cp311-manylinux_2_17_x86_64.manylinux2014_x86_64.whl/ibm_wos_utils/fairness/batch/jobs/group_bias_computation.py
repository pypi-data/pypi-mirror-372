# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2021, 2023
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

import copy
import json
import time
try:
    from pyspark.sql.dataframe import DataFrame
except ImportError as ie:
    pass

from ibm_wos_utils.fairness.batch.utils.constants import CLASS_PROBABILITY_MODELING_ROLE, FEATURE_MODELING_ROLE, META_FIELD_MODELING_ROLE, PREDICTION_MODELING_ROLE, PROBABILITY_MODELING_ROLE, RECORD_ID_MODELING_ROLE, REGRESSION_MODEL_TYPE, SUPPORTED_STORAGE_TYPES, TIMESTAMP_MODELING_ROLE, PAYLOAD, FEEDBACK, NUMERICAL_DATA_TYPES
from ibm_wos_utils.fairness.batch.utils.batch_utils import BatchUtils
from ibm_wos_utils.fairness.batch.utils.perturbation_utils import PerturbationUtils
from ibm_wos_utils.fairness.batch.utils.python_util import get
from ibm_wos_utils.fairness.batch.utils.sql_utils import SQLUtils
from ibm_wos_utils.joblib.clients.scoring_client import ScoringClient
from ibm_wos_utils.joblib.jobs.aios_spark_job import AIOSBaseJob
from ibm_wos_utils.joblib.utils.db_utils import DbUtils
from ibm_wos_utils.joblib.utils.joblib_utils import JoblibUtils


class GroupBiasComputationJob(AIOSBaseJob):

    def __init__(self, arguments, job_name):
        """
        Constructor for the job class.
        :arguments: The arguments to the Spark job.
        """
        super().__init__(arguments)
        self.name = job_name

    def calculate_group_bias(self, data, inputs: dict, data_types: dict, model_type: str, total_group_counts: dict=None) -> dict:
        """
        The Spark job which calculates the disparate impact ratio and publishes the fairness metrics for the payload and their corresponding perturbed data.
        :data: The spark data frame containing the payload data. (from pyspark.sql.dataframe import DataFrame)
        :inputs: The inputs dictionary.
        :data_types: The dictionary containing data types of all the fairness attributes.
        :model_type: The model type.
        :total_group_counts: [Optional] Dictionary containing counts for each group of all fairness attributes present in the fairness configuration. This if given, optimises the DI calculation.
            Example,
                If inputs = {
                    "fairness_attributes": ["age", "gender"],
                    "majority": {
                        "age": [[18, 25]],
                        "gender": ["male"]
                    },
                    "minority": {
                        "age": [[26, 90]],
                        "gender": ["female]
                    }...
                } then,
                total_group_counts = {
                    "age": {
                        "[18, 25]": 120,
                        "[26, 90]": 180
                    },
                    "gender": {
                        "male": 220,
                        "female": 80
                    }
                }
        
        :returns: The DI dictionary.
        """
        # First calculating the disparate impact on the payload data
        di_dict = BatchUtils.calculate_di_dict(
            data, inputs, data_types, model_type, total_group_counts=total_group_counts)
        return di_dict

    def run_job(self) -> None:
        """
        The entry point method for the Spark job.
        """
        self.logger.info("Started the group bias computation job run.")
        job_start_time = time.time()

        try:
            # Reading the inputs from the argument list
            subscription = get(self.arguments, "subscription")
            monitor_instance = get(self.arguments, "monitor_instance")
            output_file_path = get(self.arguments, "output_file_path")
            run_parameters = get(self.arguments, "run_parameters")

            if self.storage_type not in SUPPORTED_STORAGE_TYPES:
                raise Exception("{} storage type is not supported. Supported storage types are {}".format(self.storage_type, SUPPORTED_STORAGE_TYPES))

            # Getting the inputs dictionary
            inputs = BatchUtils.get_inputs_from_monitor_instance(
                monitor_instance)
            
            # Adding the class label in inputs dictionary
            output_data_schema = get(subscription, "entity.asset_properties.output_data_schema")
            inputs["class_label"] = BatchUtils.get_name_with_modeling_role("prediction", output_data_schema)

            # Checking if record timestamp column is present in the PL table
            timestamp_present = BatchUtils.check_if_modeling_role_present(TIMESTAMP_MODELING_ROLE, output_data_schema)
            if not timestamp_present:
                # Raise an exception as the timestamp column is mandatory because of #19570
                raise Exception("Mandatory timestamp column is not present in the schema!")

            # Getting the payload logger data source
            pl_data_source = BatchUtils.get_data_source_from_subscription(
                subscription, PAYLOAD)

            # Getting data types of the fairness attributes
            data_types = BatchUtils.get_data_types(subscription, inputs["fairness_attributes"])

            # Checking if the run is for historical back-dated data
            is_historical_run = run_parameters and run_parameters.get("start_time") and run_parameters.get("end_time")

            # Getting time windows for evaluation. WI #31388
            # For usual flow, there will be single time window with start time as last_processed_ts and end time as none
            # For historical run, the time windows will be computed based on specified time interval and compute windows
            # Fairness evaluation will be done for each window and metrics will be accumulated and written to HDFS/volume as a list of metrics.

            time_windows = BatchUtils.get_time_windows(run_parameters, monitor_instance)
            metrics = []
            exception = None

            for time_window in time_windows:
                try:
                    start_time = time_window[0]
                    end_time = time_window[1]
                    self.logger.info("Evaluating fairness for the time window with start_time {} and end_time {}.".format(start_time, end_time))

                    evaluation_result = self.__evaluate(
                        subscription,
                        monitor_instance,
                        inputs,
                        pl_data_source,
                        data_types,
                        start_time=start_time,
                        end_time=end_time
                    )

                    # Append the result to list of metrics
                    metrics.append(evaluation_result)

                except Exception as ex:
                    if not is_historical_run:
                        raise ex
                    # For historical runs, log the error and continue evaluation for next window
                    self.logger.error("Error occurred during fairness evaluation for the time window with start_time {} and end_time {}. Error: {}".format(
                        start_time, end_time, str(ex)))
                    exception = ex
            
            # If metrics are not available, raise the exception
            if not metrics:
                if exception:
                    raise exception
                raise Exception("Could not compute fairness metrics.")

            # Converting the value of metrics in output as string because of #19045
            output = {
                "metrics": json.dumps(metrics)
            }
            
            # Write to HDFS
            output_file_name = "{}.json".format(self.name)
            output_path = "{}/{}".format(output_file_path, output_file_name)
            self.save_data(path=output_path, data_json=output)
            self.logger.info("The output file successfully stored in HDFS at {}.".format(output_path))

            total_execution_time = time.time() - job_start_time
            self.logger.info("Fairness evaluation job completed. Total time taken {} seconds.".format(total_execution_time))

        except Exception as ex:
            error_message = str(ex)
            # If spark job fails with inner join issue which might happen in case of numeric column in older version of spark, provide an informative error. WI #27915
            cartesian_prod_err_phrases = ["cartesian product", "inner join", "join condition is missing", "cross join"]
            if any(phrase.lower() in error_message.lower() for phrase in cartesian_prod_err_phrases):
                error_message = "Please upgrade the Spark version to 3.2 or later as Fairness job failed with error: {}".format(error_message)
            self.save_exception_trace(error_message)
            raise ex
        
        return

    def __evaluate(self, subscription: dict, monitor_instance: dict, inputs: dict, pl_data_source: dict, data_types: dict, start_time: str = None, end_time: str = None):
        """
        Method which contains core logic for fairness evaluation

        Arguments:
            :subscription: The subscription object.
            :monitor_instance: The fairness monitor instance object.
            :inputs: The fairness configiration inputs.
            :pl_data_source: Details of the payload data source.
            :data_types: Data types of the fairness attributes
            :start_time: The start time of the interval. [Optional]
            :end_time: The end time of the interval. [Optional]
        Returns:
            : Output of the fairness evaluation job.
        """

        service_provider = get(self.arguments, "service_provider")
        service_provider_credentials = get(self.arguments, "service_provider_credentials")
        output_data_schema = get(subscription, "entity.asset_properties.output_data_schema")
        # Reading configuration parameters from monitor instance
        min_records = get(monitor_instance, "entity.parameters.min_records")
        perform_perturbation = get(monitor_instance, "entity.parameters.perform_perturbation", default=False)
        sample_size_percent = get(monitor_instance, "entity.parameters.sample_size_percent")
        numerical_perturb_count_per_row = get(monitor_instance, "entity.parameters.numerical_perturb_count_per_row", default=2)
        float_decimal_place_precision = get(monitor_instance, "entity.parameters.float_decimal_place_precision")
        numerical_perturb_seed = get(monitor_instance, "entity.parameters.numerical_perturb_seed")
        scoring_page_size = get(monitor_instance, "entity.parameters.scoring_page_size", default=1000)
        # Adding swagger_url for Azure subscriptions. WI #36883
        swagger_url = get(subscription, "entity.asset.url")
        score_in_pages = True
        copy_measurement = False

        db_name = get(pl_data_source, "database_name")
        pl_table_name = get(pl_data_source, "table_name")
        pl_schema_name = get(pl_data_source, "schema_name")

        # Reading the data
        payload_start_time = time.time()
        df_spark, borrow_if_needed = self._read_data(
            subscription, monitor_instance, db_name, pl_table_name, schema_name=pl_schema_name, data_type=PAYLOAD, start_time=start_time, end_time=end_time)

        # Getting the model type
        model_type = get(subscription, "entity.asset.problem_type")

        di_dict = self.calculate_group_bias(df_spark, inputs, data_types, model_type)
        rows_analyzed = get(di_dict, "rows_analyzed")

        balanced_di_dict = None
        if perform_perturbation:
            payload_end_time = time.time()
            payload_time_taken = payload_end_time - payload_start_time
            if rows_analyzed == 0:
                # No new records were read, adding flag to copy the previous measurements, if exists
                self.logger.info("No new records were read, adding the copy measurement flag in output file.")
                copy_measurement = True
            else:
                # Reading stratified sample with sample size percent for the last window
                balanced_start_time = time.time()
                
                # Getting the record-id column
                record_id_column = BatchUtils.get_name_with_modeling_role(RECORD_ID_MODELING_ROLE, output_data_schema)

                # Getting the timestamp column name
                timestamp_column = BatchUtils.get_name_with_modeling_role(TIMESTAMP_MODELING_ROLE, output_data_schema)
                
                # Getting the probability column (Would be None in case of regression models)
                probability_column = BatchUtils.get_name_with_modeling_role(PROBABILITY_MODELING_ROLE, output_data_schema)

                # Getting all the columns
                columns_to_map = [field["name"] for field in get(output_data_schema, "fields")]
                columns_to_filter = [record_id_column]
                
                # Checking the last processed time
                last_processed_time = get(monitor_instance, "entity.parameters.last_processed_ts")

                # If start_time is not specified, start_time will be last_processed_time i.e usual flow
                if not start_time:
                    start_time = last_processed_time

                # Getting the partition information
                payload_data_source = BatchUtils.get_data_source_from_subscription(subscription, PAYLOAD)
                partition_column = get(payload_data_source, "parameters.partition_column")
                num_partitions = get(payload_data_source, "parameters.num_partitions")

                # Getting the class labels and class probabilities if available (SPSS) https://github.ibm.com/aiopenscale/tracker/issues/28078
                class_labels = BatchUtils.get_class_labels_from_prediction_metadata(output_data_schema)
                class_probabilities = BatchUtils.get_names_with_modeling_role(CLASS_PROBABILITY_MODELING_ROLE, output_data_schema)

                # Initialising the scoring client
                feature_columns = BatchUtils.get_names_with_modeling_role(FEATURE_MODELING_ROLE, output_data_schema)
                prediction_column = BatchUtils.get_name_with_modeling_role(PREDICTION_MODELING_ROLE, output_data_schema)
                scoring_url = get(subscription, "entity.deployment.scoring_endpoint.url", default=get(subscription, "entity.deployment.url"))
                meta_fields = BatchUtils.get_names_with_modeling_role(META_FIELD_MODELING_ROLE, output_data_schema)
                service_type = get(service_provider, "entity.service_type")
                prediction_data_type = BatchUtils.get_data_types(subscription, [prediction_column])[prediction_column]
                scoring_client = ScoringClient(
                    service_type=service_type,
                    model_type=model_type,
                    scoring_url=scoring_url,
                    swagger_url=swagger_url,
                    credentials=service_provider_credentials,
                    features=feature_columns,
                    prediction=prediction_column,
                    probability=probability_column,
                    prediction_data_type=prediction_data_type,
                    metafields=meta_fields,
                    page_size=scoring_page_size,
                    class_labels=class_labels,
                    class_probabilities=class_probabilities
                )

                # Getting the scoring output fields
                scoring_output_fields = []
                for field_schema in output_data_schema["fields"]:
                    field_name = field_schema["name"]
                    field_modelling_role = get(field_schema, "metadata.modeling_role")
                    is_deleted_field = get(field_schema, "metadata.deleted")
                    if field_modelling_role is not None and field_modelling_role in [FEATURE_MODELING_ROLE, META_FIELD_MODELING_ROLE, PREDICTION_MODELING_ROLE, PROBABILITY_MODELING_ROLE] and not is_deleted_field:
                        if "." in field_name:
                            field_name = "`{}`".format(field_name)
                        scoring_output_fields.append(field_name)

                # Accumulating the input columns for scoring
                input_data_schema = get(subscription, "entity.asset_properties.input_data_schema")
                input_columns = JoblibUtils.get_columns_with_modeling_role(input_data_schema, "feature")
                meta_columns = JoblibUtils.get_columns_with_modeling_role(input_data_schema, "meta-field")
                input_columns.extend(meta_columns)

                # Getting all the labels
                all_labels = inputs["favourable_class"] + inputs["unfavourable_class"]

                # Initialising the perturb data size counter
                perturbed_data_size = 0

                # Perturbing the sample read, scoring and calculating DI for balanced
                for fairness_attribute in inputs["fairness_attributes"]:
                    # Building inputs just for current fairness attribute
                    fair_att_inputs = copy.deepcopy(inputs)
                    fair_att_inputs["fairness_attributes"] = [fairness_attribute]
                    fair_att_inputs["majority"] = {
                        fairness_attribute: inputs["majority"][fairness_attribute]
                    }
                    fair_att_inputs["minority"] = {
                        fairness_attribute: inputs["minority"][fairness_attribute]
                    }
                    fair_att_inputs["threshold"] = [inputs["threshold"][inputs["fairness_attributes"].index(fairness_attribute)]]

                    self.logger.info("Reading the stratified sample for fairness attribute {} balanced data calculation.".format(fairness_attribute))
                    balanced_sample_read_start_time = time.time()

                    # For a protected attribute, checking if correlated attributes exist. If not found, then perturbation is not performed.
                    is_protected_attribute = fairness_attribute in inputs.get("protected_attributes")
                    if is_protected_attribute and BatchUtils.should_skip_perturbation_for_prot_attr(inputs, fairness_attribute):
                        self.logger.info("No correlated attributes found for the protected attribute {}, hence skipping perturbation.".format(fairness_attribute))
                        # Update balanced DI with the same value as payload DI
                        if balanced_di_dict is not None:
                            balanced_di_dict[fairness_attribute] = di_dict.get(fairness_attribute)
                        else:
                            balanced_di_dict = di_dict
                        continue

                    # If last_processed time is None, we will read all the data as it would be the first run,
                    # else, we would read from the last window
                    balanced_pl_sample_df, balanced_pl_sample_total_group_counts = BatchUtils.read_stratified_samples(
                        sample_size_percent=sample_size_percent,
                        inputs=fair_att_inputs,
                        data_types=data_types,
                        spark=self.spark,
                        location_type=self.location_type_map.get(PAYLOAD),
                        db_name=db_name,
                        table_name=pl_table_name,
                        columns_to_map=columns_to_map,
                        columns_to_filter=columns_to_filter,
                        model_type=model_type,
                        all_labels=all_labels,
                        schema_name=pl_schema_name,
                        jdbc_connection_properties=self.jdbc_connection_properties_map[PAYLOAD],
                        record_timestamp_column=timestamp_column,
                        start_time=start_time,
                        end_time=end_time,
                        probability_column=probability_column,
                        order_by_timestamp_desc=True,
                        partition_column=partition_column,
                        num_partitions=num_partitions
                    )
                    balanced_sample_read_end_time = time.time()
                    self.logger.info("Completed reading the stratified sample for fairness attribute {} balanced dataset calculation. Time taken {} seconds.".format(fairness_attribute, balanced_sample_read_end_time - balanced_sample_read_start_time))

                    # Filtering columns from data read other than scoring output fields
                    balanced_pl_sample_df = balanced_pl_sample_df[scoring_output_fields]
                    
                    # Starting the perturbation
                    self.logger.info("Starting the perturbation of the sample read for balanced dataset for fairness attribute {}.".format(fairness_attribute))
                    sample_pert_df = None
                    # Counts for each group in perturbed data
                    total_pert_group_counts = {
                        fairness_attribute: dict()
                    }
                    # Correlation information for protected attribute
                    correlation_info = None
                    if is_protected_attribute:
                        correlated_attributes = get(inputs, "correlated_attributes.{}".format(fairness_attribute))
                        correlated_majority = get(inputs, "correlated_majority.{}".format(fairness_attribute))
                        correlated_minority = get(inputs, "correlated_minority.{}".format(fairness_attribute))
                        correlation_info = {
                            "correlated_attributes": correlated_attributes,
                            "correlated_maj_min": correlated_majority
                        }

                    pert_start_time = time.time()
                    # Perturbing the minority groups
                    for mino in fair_att_inputs["minority"][fairness_attribute]:
                        from_group_count = balanced_pl_sample_total_group_counts[fairness_attribute][str(mino)]
                        to_groups = fair_att_inputs["majority"][fairness_attribute]
                        mino_pert_df, pert_to_groups_count = PerturbationUtils.perform_perturbation(
                            data=balanced_pl_sample_df,
                            column_to_perturb=fairness_attribute,
                            from_group=mino,
                            to_groups=to_groups,
                            spark=self.spark,
                            numerical_perturb_count_per_row=numerical_perturb_count_per_row,
                            float_decimal_place_precision=float_decimal_place_precision,
                            numerical_perturb_seed=numerical_perturb_seed,
                            from_group_count=from_group_count,
                            correlation_info=correlation_info
                        )
                        sample_pert_df = sample_pert_df.unionByName(mino_pert_df) if sample_pert_df is not None else mino_pert_df
                        for to_group in to_groups:
                            perturbed_to_group_count = pert_to_groups_count[str(to_group)]
                            perturbed_data_size += perturbed_to_group_count
                            if str(to_group) not in total_pert_group_counts[fairness_attribute]:
                                total_pert_group_counts[fairness_attribute][str(to_group)] = perturbed_to_group_count
                            else:
                                total_pert_group_counts[fairness_attribute][str(to_group)] += perturbed_to_group_count
                    
                    # Perturbing the majority groups
                    # While perturbing majority to minority, using correlated_minority of protected attribute for perturbation of correlated attributes
                    if correlation_info is not None:
                        correlation_info["correlated_maj_min"] = correlated_minority

                    for maj in fair_att_inputs["majority"][fairness_attribute]:
                        from_group_count = balanced_pl_sample_total_group_counts[fairness_attribute][str(maj)]
                        to_groups = fair_att_inputs["minority"][fairness_attribute]
                        maj_pert_df, pert_to_groups_count = PerturbationUtils.perform_perturbation(
                            data=balanced_pl_sample_df,
                            column_to_perturb=fairness_attribute,
                            from_group=maj,
                            to_groups=to_groups,
                            spark=self.spark,
                            numerical_perturb_count_per_row=numerical_perturb_count_per_row,
                            float_decimal_place_precision=float_decimal_place_precision,
                            numerical_perturb_seed=numerical_perturb_seed,
                            from_group_count=from_group_count,
                            correlation_info=correlation_info
                        )
                        sample_pert_df = sample_pert_df.unionByName(maj_pert_df) if sample_pert_df is not None else maj_pert_df
                        for to_group in to_groups:
                            perturbed_to_group_count = pert_to_groups_count[str(to_group)]
                            perturbed_data_size += perturbed_to_group_count
                            if str(to_group) not in total_pert_group_counts[fairness_attribute]:
                                total_pert_group_counts[fairness_attribute][str(to_group)] = perturbed_to_group_count
                            else:
                                total_pert_group_counts[fairness_attribute][str(to_group)] += perturbed_to_group_count
                    
                    pert_end_time = time.time()
                    self.logger.info("Completed perturbation of the fairness attribute {} for the stratified sample read for balanced dataset calculation. Time taken {} seconds.".format(fairness_attribute, pert_end_time - pert_start_time))
                    
                    # Now scoring the perturbed records
                    # Accumulating the input columns for scoring
                    # Adding "`" around names for columns with `.`
                    for col in input_columns:
                        if "." in col:
                            idx = input_columns.index(col)
                            input_columns[idx] = "`{}`".format(col)
                    sample_pert_df = sample_pert_df[input_columns]
                    # Removing "`" around names for columns with `.`
                    for col in input_columns:
                        if "." in col:
                            idx = input_columns.index(col)
                            input_columns[idx] = col[1:-1]

                    # Scoring the data
                    self.logger.info("Starting the scoring for the perturbed data for fairness attribute {} of the stratified sample for balanced dataset calculation.".format(fairness_attribute))
                    balanced_sample_pert_scoring_start = time.time()

                    predictions_df = scoring_client.score(sample_pert_df, include_features_in_response=True)
                    
                    balanced_sample_pert_scoring_end = time.time()
                    self.logger.info("Completed scoring of the perturbed data of the fairness attribute {} for the stratified sample for the balanced dataset calculation. Time taken {} seconds.".format(fairness_attribute, balanced_sample_pert_scoring_end - balanced_sample_pert_scoring_start))
                    
                    # Appending with the sample payload data read
                    fair_att_balanced_df = balanced_pl_sample_df.unionByName(predictions_df)

                    # Adding the total group counts as well
                    balanced_total_group_counts = BatchUtils.merge_group_counts_dicts({fairness_attribute: balanced_pl_sample_total_group_counts[fairness_attribute]}, total_pert_group_counts)

                    # Calculating the DI on balanced data
                    self.logger.info("Starting the DI calculation of the balanced dataset for fairness attribute {}.".format(fairness_attribute))
                    balanced_data_di_calc_start_time = time.time()

                    # Calculating DI for current fairness attribute on balanced data
                    fair_att_balanced_di_dict = self.calculate_group_bias(fair_att_balanced_df, fair_att_inputs, data_types, model_type, total_group_counts=balanced_total_group_counts)

                    if balanced_di_dict is not None:
                        # Need to add counts for the current fairness attribute in the global balanced DI dict
                        balanced_di_dict[fairness_attribute] = fair_att_balanced_di_dict[fairness_attribute]
                    else:
                        # This is the first DI dict
                        balanced_di_dict = fair_att_balanced_di_dict
                    
                    balanced_data_di_calc_end_time = time.time()
                    self.logger.info("DI calculation of the fairness attribute {} for the balanced dataset completed. Time taken: {} seconds.".format(fairness_attribute, balanced_data_di_calc_end_time - balanced_data_di_calc_start_time))

                # Adding the perturbed_data_size
                balanced_di_dict["perturbed_data_size"] = perturbed_data_size
                
                balanced_end_time = time.time()
                balanced_time_taken = balanced_end_time - balanced_start_time
        else:
            if borrow_if_needed and rows_analyzed < min_records and rows_analyzed != 0:
                # Getting the last processed time
                last_processed_time = get(
                    monitor_instance, "entity.parameters.last_processed_ts")

                # If start_time is not specified, start_time will be last_processed_time i.e usual flow
                if not start_time:
                    start_time = last_processed_time

                # Getting the timestamp column name
                timestamp_column = BatchUtils.get_name_with_modeling_role(
                    TIMESTAMP_MODELING_ROLE, output_data_schema)

                # Reading the borrowed records
                borrowed_df = self._read_borrowed_data(
                    subscription, db_name, pl_table_name, min_records - rows_analyzed, timestamp_column, start_time, inputs, schema_name=pl_schema_name)

                # Calculating DI variables on borrowed records
                borrowed_di_dict = self.calculate_group_bias(
                    borrowed_df, inputs, data_types, model_type)

                # Merging the DI values
                di_dict = BatchUtils.merge_di_dicts(di_dict, borrowed_di_dict)
            elif rows_analyzed == 0:
                # No new records were read, adding flag to copy the previous measurements, if exists
                self.logger.info("No new records were read, adding the copy measurement flag in output file.")
                copy_measurement = True

            payload_end_time = time.time()
            payload_time_taken = payload_end_time - payload_start_time

        output_json = None
        # Checking if enough records were present
        if min_records is not None:
            rows_analyzed = get(di_dict, "rows_analyzed")
            if rows_analyzed < min_records:
                self.logger.warning("Not enough records received for group bias computation as rows analyzed {} and min_records {}. Hence, not adding the DI dictionary in output file.".format(rows_analyzed, min_records))
                # Not enough records present in the PL table
                output_json = {
                    "job_output": [
                        {
                            "data_name": PAYLOAD,
                            "rows_analyzed": rows_analyzed,
                            "time_taken": payload_time_taken
                        }
                    ]
                }

        if output_json is None:
            # Building the output JSON
            self.logger.info("Adding the DI dictionary computed in the output file.")
            output_json = {
                "job_output": [
                    {
                        "data_name": PAYLOAD,
                        "counts": di_dict,
                        "time_taken": payload_time_taken
                    }
                ]
            }
        self.logger.info("Total time taken for payload dataset calculation in the time window with start_time {} and end_time {} was {} seconds.".format(start_time, end_time, payload_time_taken))

        # Checking if balanced data DI valus are present and adding if yes
        if balanced_di_dict is not None:
            output_json["job_output"].append(
                {
                    "data_name": "balanced",
                    "counts": balanced_di_dict,
                    "time_taken": balanced_time_taken
                }
            )
            self.logger.info("Total time taken for balanced dataset calculation in the time window with start_time {} and end_time {} was {} seconds.".format(start_time, end_time, balanced_time_taken))
        
        # Adding the copy measurement flag for `payload` data
        output_json["job_output"][0]["copy_measurement"] = copy_measurement
        
        # Compute feedback based metrics distribution 
        try:
            feedback_distribution_info = None
            is_feedback_based_metrics_configured = get(self.arguments, "is_feedback_based_metrics_configured", False) 
            if is_feedback_based_metrics_configured is True:
                self.logger.info("Computing feedback based confusion matrix because metrics are configured")
                feedback_distribution_info = self.compute_feedback_confusion_metric_distribution(subscription,monitor_instance, inputs, start_time=start_time, end_time=end_time)
            else:
                self.logger.info("Not computing feedback based confusion matrix because it is not configured")     
            if feedback_distribution_info is not None:
                output_json["job_output"].append(feedback_distribution_info)    
        except Exception as feedback_exc:
            import traceback
            tr = traceback.format_exc()
            self.logger.info("Computation of feedback based confusion matrix failed at {}.".format(tr))
            raise feedback_exc

        # Adding start_time and end_time of the window to the output as it needs to be added in measurement
        output_json["start_time"] = start_time
        output_json["end_time"] = end_time

        return output_json
        
    def _read_data(self, subscription: dict, monitor_instance: dict, db_name: str, table_name: str, schema_name: str=None, data_type = None, start_time: str = None, end_time: str = None): # (DataFrame, bool)
        """
        Reads and returns data frame for group bias computation.
        :subscription: The subscription object.
        :monitor_instance: The monitor instance object.
        :db_name: The database name.
        :table_name: The table name.
        :schema_name: The name of the schema in which the table resides. [Optional]
        :start_time: The start time of the interval. [Optional]
        :end_time: The end time of the interval. [Optional]

        :returns: The data and a flag indicating if records are to be borrowed if required. (from pyspark.sql.dataframe import DataFrame)
        """
        df = None
        borrow_if_needed = False
        self.logger.info("Start reading data of type {}".format(data_type))
        # Checking if record timestamp column is present in the PL table
        output_data_schema = get(subscription, "entity.asset_properties.output_data_schema")
        timestamp_present = BatchUtils.check_if_modeling_role_present(TIMESTAMP_MODELING_ROLE, output_data_schema)
        
        # Getting the record-id column
        record_id_column = BatchUtils.get_name_with_modeling_role(RECORD_ID_MODELING_ROLE, output_data_schema)
        
        # Getting the probability column (Would be None in case of regression models)
        probability_column = BatchUtils.get_name_with_modeling_role(PROBABILITY_MODELING_ROLE, output_data_schema)

        # Getting all the columns
        columns_to_map = [field["name"] for field in get(output_data_schema, "fields")]
        columns_to_filter = [record_id_column]

        # Getting the min records
        min_records = get(monitor_instance, "entity.parameters.min_records")

        # Getting the partition information
        payload_data_source = BatchUtils.get_data_source_from_subscription(subscription, PAYLOAD)
        partition_column = get(payload_data_source, "parameters.partition_column")
        num_partitions = get(payload_data_source, "parameters.num_partitions")
        if num_partitions is None:
            spark_settings = self.arguments.get("spark_settings", BatchUtils.get_spark_settings_from_subscription(subscription))
            if spark_settings is not None:
                num_partitions = int(spark_settings.get("max_num_executors", 1)) * int(spark_settings.get("executor_cores", 1))
            else:
                num_partitions = 1
        # Reading the data
        if timestamp_present:
            self.logger.info("Timestamp column present in the payload logger table.")
            # Using start time and end time of the window to read data.
            # In usual flow start time will be last_processed_time, end time will be None
            # Checking the last processed time if start_time is not specified, i.e usual flow
            if not start_time:
                start_time = get(monitor_instance, "entity.parameters.last_processed_ts")
            
            # Getting the timestamp column name
            timestamp_column = BatchUtils.get_name_with_modeling_role(
                TIMESTAMP_MODELING_ROLE, output_data_schema)
            
            if min_records is not None:
                self.logger.info("Min records is given in the monitor instance with value {}.".format(min_records))
                if start_time is not None:
                    # This is not the first run, reading from last processed time
                    self.logger.info("This is not the first run for the subscription.")
                    df = DbUtils.get_table_as_dataframe(
                        self.spark,
                        self.location_type_map.get(data_type),
                        db_name,
                        table_name,
                        schema_name=schema_name,
                        connection_properties=self.jdbc_connection_properties_map[data_type],
                        columns_to_map=columns_to_map,
                        columns_to_filter=columns_to_filter,
                        record_timestamp_column=timestamp_column,
                        start_time=start_time,
                        end_time=end_time,
                        partition_column=partition_column,
                        num_partitions=num_partitions
                    )
                    borrow_if_needed = True
                else:
                    self.logger.info("This is the first run for the subscription.")
                    # Reading all the records
                    df = DbUtils.get_table_as_dataframe(
                        self.spark,
                        self.location_type_map.get(data_type),
                        db_name,
                        table_name,
                        schema_name=schema_name,
                        connection_properties=self.jdbc_connection_properties_map[data_type],
                        columns_to_map=columns_to_map,
                        columns_to_filter=columns_to_filter,
                        probability_column=probability_column,
                        partition_column=partition_column,
                        num_partitions=num_partitions
                    )
            else:
                self.logger.info("Min records is not given in the monitor instance.")
                # The `min_records` is not given
                if start_time is not None:
                    self.logger.info("This is not the first run for the subscription.")
                    # This is not the first run, reading from last processed time
                    df = DbUtils.get_table_as_dataframe(
                        self.spark,
                        self.location_type_map.get(data_type),
                        db_name,
                        table_name,
                        schema_name=schema_name,
                        connection_properties=self.jdbc_connection_properties_map[data_type],
                        columns_to_map=columns_to_map,
                        columns_to_filter=columns_to_filter,
                        record_timestamp_column=timestamp_column,
                        start_time=start_time,
                        end_time=end_time,
                        partition_column=partition_column,
                        num_partitions=num_partitions
                    )
                else:
                    self.logger.info("This is the first run for the subscription.")
                    # This is the first run, reading all the records
                    df = DbUtils.get_table_as_dataframe(
                        self.spark,
                        self.location_type_map.get(data_type),
                        db_name,
                        table_name,
                        schema_name=schema_name,
                        connection_properties=self.jdbc_connection_properties_map[data_type],
                        columns_to_map=columns_to_map,
                        columns_to_filter=columns_to_filter,
                        probability_column=probability_column,
                        partition_column=partition_column,
                        num_partitions=num_partitions
                    )
        # This code would be made reachable once #19570 is implemented
        """
        else:
            self.logger.info("Timestamp column not present in the payload logger table.")
            # ------------
            if min_records is None:
                self.logger.info("Min records is not given in the monitor instance.")
                # When both min records and record-timestamp column is not present
                df = DbUtils.get_table_as_dataframe(
                        self.spark,
                        self.location_type_map.get(data_type),
                        db_name,
                        table_name,
                        schema_name=schema_name,
                        connection_properties=self.jdbc_connection_properties_map[data_type],
                        columns_to_map=columns_to_map,
                        columns_to_filter=columns_to_filter,
                        probability_column=probability_column,
                        partition_column=partition_column,
                        num_partitions=num_partitions
                    )
            else:
                self.logger.info("Min records is given in the monitor instance without timestamp column, which is not supported.")
                # This case is handled at the configuration level,
                # we throw an error in this case
                pass
            # ------------
        """
        self.logger.info("End reading data of type {}".format(data_type))
        return df, borrow_if_needed

    def _read_borrowed_data(self, subscription: dict, db_name: str, table_name: str, num_records: int, timestamp_column: str, last_processed_time: str, inputs: dict, schema_name: str=None): # DataFrame
        """
        Reads and returns the latest borrowed records older than last processed time.
        :subscription: Yhe subscription object.
        :db_name: The database name.
        :table_name: The table name.
        :num_records: The number of records to be read.
        :timestamp_column: The timestamp column in the table.
        :last_processed_time: The last processed time for fairness.
        :inputs: The inputs dictionary.
        :schema_name: The name of the schema in which the table resides. [Optional]

        :returns: Returns the borrowed records data frame. (from pyspark.sql.dataframe import DataFrame)
        """
        df = None

        self.logger.info("Borrowing records from previous window.")

        # Checking if record timestamp column is present in the PL table
        output_data_schema = get(
            subscription, "entity.asset_properties.output_data_schema")
        timestamp_present = BatchUtils.check_if_modeling_role_present(
            TIMESTAMP_MODELING_ROLE, output_data_schema)
        
        # Getting the record-id column
        record_id_column = BatchUtils.get_name_with_modeling_role(RECORD_ID_MODELING_ROLE, output_data_schema)
        
        # Getting the probability column (Would be None in case of regression models)
        probability_column = BatchUtils.get_name_with_modeling_role(PROBABILITY_MODELING_ROLE, output_data_schema)

        # Getting all the columns
        columns_to_map = [field["name"] for field in get(output_data_schema, "fields")]
        columns_to_filter = [record_id_column]

        # Getting the partition information
        payload_data_source = BatchUtils.get_data_source_from_subscription(subscription, PAYLOAD)
        partition_column = get(payload_data_source, "parameters.partition_column")
        num_partitions = get(payload_data_source, "parameters.num_partitions")
        if num_partitions is None:
            spark_settings = self.arguments.get("spark_settings", BatchUtils.get_spark_settings_from_subscription(subscription))
            if spark_settings is not None:
                num_partitions = int(spark_settings.get("max_num_executors", 1)) * int(spark_settings.get("executor_cores", 1))
            else:
                num_partitions = 1

        # Reading the data
        df = DbUtils.get_table_as_dataframe(
            self.spark,
            self.location_type_map.get(PAYLOAD),
            db_name,
            table_name,
            schema_name=schema_name,
            connection_properties=self.jdbc_connection_properties_map[PAYLOAD],
            columns_to_map=columns_to_map,
            columns_to_filter=columns_to_filter,
            record_timestamp_column=timestamp_column,
            end_time=last_processed_time,
            probability_column=probability_column,
            order_by_timestamp_desc=True,
            partition_column=partition_column,
            num_partitions=num_partitions
        )

        # Getting all labels
        all_labels = get(inputs, "favourable_class") + get(inputs, "unfavourable_class")
        label_column = get(inputs, "class_label")

        # Filtering unused label rows
        model_type = get(subscription, "entity.asset.problem_type")
        if model_type == REGRESSION_MODEL_TYPE:
            all_label_query = SQLUtils.get_num_filter_query(label_column, all_labels)
        else:
            all_label_query = SQLUtils.get_cat_filter_query(label_column, "==", all_labels)
        
        # Applying the query
        df = df.filter(all_label_query)

        # Now applying the limit to get the required number of records
        df = df.limit(num_records)

        return df
    
    
    def compute_feedback_confusion_metric_distribution(self, subscription,monitor_instance, inputs, start_time: str = None, end_time: str = None):
        self.logger.info("Start computing feedback based metrics for the time window with start_time {} and end_time {}.".format(start_time, end_time))
        feedback_start_time = time.time()        
            # Getting the payload logger data source
        feedback_data_source = BatchUtils.get_data_source_from_subscription(
            subscription, FEEDBACK)
        self.logger.info("Feedback datasource {}".format(feedback_data_source))
        #Compute confusion matrix only if feedback data source is available
        
        if feedback_data_source is not None:
            feedback_db_name = get(feedback_data_source, "database_name")
            feedback_table_name = get(feedback_data_source, "table_name")
            feedback_schema_name = get(feedback_data_source, "schema_name")
            
            feedback_jdbc_connection_properties = self.jdbc_connection_properties_map[FEEDBACK]
            
            self.logger.info("Start Reading feedback data")
            spark_df, borrow_if_needed = self._read_data(subscription, monitor_instance, feedback_db_name, feedback_table_name, schema_name=feedback_schema_name, data_type = FEEDBACK, start_time=start_time, end_time=end_time)
            self.logger.info("End reading feedback data...")
            
            favourable_class = inputs['favourable_class']
            unfavourable_class = inputs['unfavourable_class']
            
            prediction_col = BatchUtils.get_name_with_modeling_role("prediction", get(subscription, "entity.asset_properties.output_data_schema"))
            label_col = get(subscription, "entity.asset_properties.label_column")
            
            fields =  ['feature', 'feature_value', 'prediction', 'label', 'count', 'confusion_metrics_role', 'group']
            rows = []
            data_types = BatchUtils.get_data_types(subscription,inputs["fairness_attributes"])
            for feature_name in inputs["fairness_attributes"]:
                majority_group = inputs['majority'][feature_name]
                minority_group = inputs['minority'][feature_name]
                feature_data_type = data_types[feature_name]  
                                    
                for majority in majority_group:
                    if feature_data_type in NUMERICAL_DATA_TYPES:
                        majority_value = "{}-{}".format(majority[0], majority[1])
                    else:
                        majority_value =  majority   
                    
                    for fav in favourable_class: # true_positive
                        if feature_data_type in NUMERICAL_DATA_TYPES:
                            true_positives = spark_df.filter( (spark_df[feature_name]>=majority[0]) & (spark_df[feature_name]<=majority[1]) & (spark_df[prediction_col]==fav) & (spark_df[label_col]==fav) ).count()
                        else:
                            true_positives = spark_df.filter( (spark_df[feature_name]==majority) & (spark_df[prediction_col]==fav) & (spark_df[label_col]==fav) ).count()
                        row = [feature_name, majority_value, fav, fav, true_positives, "true_positive", "reference"]
                        rows.append(row)
                        for unfav in unfavourable_class: # false_positive
                            if feature_data_type in NUMERICAL_DATA_TYPES:
                                false_positives = spark_df.filter( (spark_df[feature_name]>=majority[0]) & (spark_df[feature_name]<=majority[1]) & (spark_df[prediction_col]==fav) & (spark_df[label_col]==unfav) ).count()
                            else:                            
                                false_positives = spark_df.filter( (spark_df[feature_name]==majority) & (spark_df[prediction_col]==fav) & (spark_df[label_col]==unfav) ).count()
                            row = [feature_name, majority_value, fav, unfav, false_positives, "false_positive", "reference"]
                            rows.append(row)
                    for unfav in unfavourable_class: # true_negative  
                        if feature_data_type in NUMERICAL_DATA_TYPES:
                            true_negatives = spark_df.filter( (spark_df[feature_name]>=majority[0]) & (spark_df[feature_name]<=majority[1]) & (spark_df[prediction_col]==unfav) & (spark_df[label_col]==unfav) ).count()
                        else: 
                            true_negatives = spark_df.filter( (spark_df[feature_name]==majority) & (spark_df[prediction_col]==unfav) & (spark_df[label_col]==unfav) ).count()
                        row = [feature_name, majority_value, unfav, unfav, true_negatives, "true_negative", "reference"]
                        rows.append(row)
                        for fav in favourable_class: # false_negative
                            if feature_data_type in NUMERICAL_DATA_TYPES:
                                false_negatives = spark_df.filter( (spark_df[feature_name]>=majority[0]) & (spark_df[feature_name]<=majority[1]) & (spark_df[prediction_col]==unfav) & (spark_df[label_col]==fav) ).count()
                            else:
                                false_negatives = spark_df.filter( (spark_df[feature_name]==majority) & (spark_df[prediction_col]==unfav) & (spark_df[label_col]==fav) ).count()               
                            row = [feature_name, majority_value, unfav, fav, false_negatives, "false_negative", "reference"]
                            rows.append(row)
                            
                for minority in minority_group:
                    if feature_data_type in NUMERICAL_DATA_TYPES:
                        minority_value = "{}-{}".format(minority[0], minority[1])
                    else:
                        minority_value =  minority
                            
                    for fav in favourable_class: # true_positive
                        if feature_data_type in NUMERICAL_DATA_TYPES:
                            true_positives = spark_df.filter( (spark_df[feature_name]>=minority[0]) & (spark_df[feature_name]<=minority[1]) & (spark_df[prediction_col]==fav) & (spark_df[label_col]==fav) ).count()
                        else:
                            true_positives = spark_df.filter( (spark_df[feature_name]==minority) & (spark_df[prediction_col]==fav) & (spark_df[label_col]==fav) ).count()
                        row = [feature_name, minority_value, fav, fav, true_positives, "true_positive", "monitored"]
                        rows.append(row)
                        for unfav in unfavourable_class: # false_positive
                            if feature_data_type in NUMERICAL_DATA_TYPES:
                                false_positives = spark_df.filter( (spark_df[feature_name]>=minority[0]) & (spark_df[feature_name]<=minority[1]) & (spark_df[prediction_col]==fav) & (spark_df[label_col]==unfav) ).count()
                            else:
                                false_positives = spark_df.filter( (spark_df[feature_name]==minority) & (spark_df[prediction_col]==fav) & (spark_df[label_col]==unfav) ).count()
                            row = [feature_name, minority_value, fav, unfav, false_positives, "false_positive", "monitored"]
                            rows.append(row)
                    for unfav in unfavourable_class: # true_negative   
                        if feature_data_type in NUMERICAL_DATA_TYPES:
                            true_negatives = spark_df.filter( (spark_df[feature_name]>=minority[0]) & (spark_df[feature_name]<=minority[1]) & (spark_df[prediction_col]==unfav) & (spark_df[label_col]==unfav) ).count()
                        else:
                            true_negatives = spark_df.filter( (spark_df[feature_name]==minority) & (spark_df[prediction_col]==unfav) & (spark_df[label_col]==unfav) ).count()
                        row = [feature_name, minority_value, unfav, unfav, true_negatives, "true_negative", "monitored"]
                        rows.append(row)
                        for fav in favourable_class: # false_negative 
                            if feature_data_type in NUMERICAL_DATA_TYPES:
                                false_negatives = spark_df.filter( (spark_df[feature_name]>=minority[0]) & (spark_df[feature_name]<=minority[1]) & (spark_df[prediction_col]==unfav) & (spark_df[label_col]==fav) ).count()
                            else: 
                                false_negatives = spark_df.filter( (spark_df[feature_name]==minority) & (spark_df[prediction_col]==unfav) & (spark_df[label_col]==fav) ).count()
                            row = [feature_name, minority_value, unfav, fav, false_negatives, "false_negative", "monitored"]
                            rows.append(row)
                        
            feedback_rowcount = spark_df.count()
            
            feedback_time_taken = time.time() - feedback_start_time
            
            feedback_distribution = {    
                    "data_distribution": {
                        "fields": fields,
                        "values": rows
                    },
                    "records_count":feedback_rowcount       
            } 
            
             
            data_summary_id = "feedback_distribution"
            feedback_distribution_info =  {
                    "data_name": FEEDBACK,
                    "distribution":feedback_distribution,
                    "rows_analyzed": feedback_rowcount,
                    "time_taken": feedback_time_taken
                }
            self.logger.info("Finished computing feedback based metrics for the time window with start_time {} and end_time {}. It took {} secs".format(start_time, end_time, feedback_time_taken))
            return feedback_distribution_info
        else:
            self.logger.info("Feedback datasource not found so not computing fairness metrics")
            return None
    