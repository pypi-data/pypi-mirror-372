# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2023
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S. Copyright Office.
# ----------------------------------------------------------------------------------------------------

try:
    from pyspark.sql import DataFrame
except ImportError as ie:
    pass

from ibm_wos_utils.data_health.batch.metrics.metrics_utils import MetricsUtils
from ibm_wos_utils.data_health.batch.utils.constants import BATCH_SUBSCRIPTION_FB_METRICS, BATCH_SUBSCRIPTION_PL_METRICS, DEFAULT_THRESHOLDS, FEATURE_MODELING_ROLE, META_FIELD_MODELING_ROLE, Metrics, PREDICTION_MODELING_ROLE, PROBABILITY_MODELING_ROLE, RECORD_ID_MODELING_ROLE, RECORD_TIMESTAMP_MODELING_ROLE
from ibm_wos_utils.data_health.batch.utils.batch_utils import BatchUtils
from ibm_wos_utils.fairness.batch.utils.batch_utils import BatchUtils as FairnessBatchUtils
from ibm_wos_utils.fairness.batch.utils.python_util import get

class MetricsManager:
    """
    The metrics manager class to be used to calculate the metrics for the data.
    """

    @classmethod
    def calculate_metrics(cls, subscription: dict, monitor_instance: dict, pl_data=None, fb_data=None, top_features_limit: int=None) -> dict:
        """
        Calculates all the Data Health metrics for the given data.
        :subscription: The subscription object.
        :monitor_instance: The `data_health` monitor instance object.
        :pl_data: The payload logging data in a pyspark data frame.
        :fb_data: The feedback data in a pyspark data frame.
        :top_features_limit: The upper limit on number of columns to be considered.

        :returns: The metric values object.
        """
        metric_values = None
        
        # Checking for columns for metrics computation
        columns_for_metrics_computation = get(monitor_instance, "entity.parameters.columns_for_metrics_computation", default=None)

        # Getting the input and output data schema
        input_data_schema = get(subscription, "entity.asset_properties.input_data_schema")
        output_data_schema = get(subscription, "entity.asset_properties.output_data_schema")

        # Getting the record-id and record-timestamp column
        record_id_column = FairnessBatchUtils.get_name_with_modeling_role(RECORD_ID_MODELING_ROLE, output_data_schema)
        timestamp_column = FairnessBatchUtils.get_name_with_modeling_role(RECORD_TIMESTAMP_MODELING_ROLE, output_data_schema)

        # Getting the prediction and probability and label column names
        prediction_column = FairnessBatchUtils.get_name_with_modeling_role(PREDICTION_MODELING_ROLE, output_data_schema)
        probability_column = FairnessBatchUtils.get_name_with_modeling_role(PROBABILITY_MODELING_ROLE, output_data_schema)
        label_column = get(subscription, "entity.asset_properties.label_column")
        
        # Getting feature, meta and prediction/label columns list
        focus_cols = FairnessBatchUtils.get_names_with_modeling_role(FEATURE_MODELING_ROLE, output_data_schema)
        focus_cols.extend(FairnessBatchUtils.get_names_with_modeling_role(META_FIELD_MODELING_ROLE, input_data_schema))

        # Setting the hard-limit on number of feature columns to be used
        if top_features_limit is not None:
            if len(focus_cols) > top_features_limit:
                focus_cols.sort()
                focus_cols = focus_cols[0:top_features_limit]
            if columns_for_metrics_computation is not None and len(columns_for_metrics_computation) > top_features_limit:
                columns_for_metrics_computation.sort()
                columns_for_metrics_computation = columns_for_metrics_computation[0:top_features_limit]

        # Calculating metrics for payload data
        if pl_data is not None:
            # Adding the prediction column to focus columns
            focus_cols.append(prediction_column)
            if columns_for_metrics_computation is not None:
                # Adding the label column to focus columns
                columns_for_metrics_computation.append(prediction_column)
            
            # Getting the list of metrics to be calculated
            metrics = BATCH_SUBSCRIPTION_PL_METRICS

            # Checking if the model type is regression
            problem_type = get(subscription, "entity.asset.problem_type")
            if problem_type is not None and problem_type == "regression":
                # Removing the metrics supported only for classification models
                metrics = list(set(metrics) - set(CLASSIFICATION_MODEL_METRICS))
            
            # Getting the total count
            total_count = pl_data.count()
            
            if total_count > 0:
                # Calculating the metric values for the payload data
                metric_values = cls._calculate_metric_values_for_data(
                    subscription=subscription,
                    monitor_instance=monitor_instance,
                    data=pl_data,
                    metrics=metrics,
                    columns=columns_for_metrics_computation if columns_for_metrics_computation is not None else focus_cols,
                    is_payload=True
                )

                # Adding the total count, start and end timestamps
                start_timestamp, end_timestamp = MetricsUtils.get_start_end_timestamps_from_data(pl_data, timestamp_column)
                metric_values["summary"]["payload"] = {
                    "start_timestamp": start_timestamp,
                    "end_timestamp": end_timestamp,
                    "total_count": total_count
                }
        
        # Calculating metrics for feedback data
        if fb_data is not None:
            # Removing the prediction column added during payload data calculation
            if prediction_column in focus_cols:
                focus_cols.remove(prediction_column)
            
            # Adding the label column to focus columns
            focus_cols.append(label_column)
            
            if columns_for_metrics_computation is not None:
                # Removing the prediction column added during payload data calculation
                if prediction_column in columns_for_metrics_computation:
                    columns_for_metrics_computation.remove(prediction_column)
                
                # Adding the label column to columns for metrics computation
                columns_for_metrics_computation.append(label_column)
            
            # Getting the list of metrics to be calculated
            metrics = BATCH_SUBSCRIPTION_FB_METRICS

            # Checking if the model type is regression
            problem_type = get(subscription, "entity.asset.problem_type")
            if problem_type is not None and problem_type == "regression":
                # Removing the metrics supported only for classification models
                metrics = list(set(metrics) - set(CLASSIFICATION_MODEL_METRICS))
            
            # Getting the total count
            total_count = fb_data.count()
            
            if total_count > 0:
                # Calculating the metric values for the feedback data
                metric_values = cls._calculate_metric_values_for_data(
                    subscription=subscription,
                    monitor_instance=monitor_instance,
                    data=fb_data,
                    metrics=metrics,
                    columns=columns_for_metrics_computation if columns_for_metrics_computation is not None else focus_cols,
                    is_payload=False,
                    metric_values=metric_values
                )

                # Adding the total count, start and end timestamps
                start_timestamp, end_timestamp = MetricsUtils.get_start_end_timestamps_from_data(fb_data, timestamp_column)
                metric_values["summary"]["feedback"] = {
                    "start_timestamp": start_timestamp,
                    "end_timestamp": end_timestamp,
                    "total_count": total_count
                }

        return metric_values
    
    @classmethod
    def _calculate_metric_values_for_data(cls, subscription: dict, monitor_instance: dict, data, metrics: list, columns: list, is_payload: bool, metric_values: dict=None) -> dict:
        """
        Calculates the given metrics on the given data.
        :subscription: The subscription object.
        :monitor_instance: The monitor instance object.
        :data: The data on which the metrics are to be calculated in a pyspark data frame.
        :metrics: The list of metrics to be calculated.
        :columns: The list of columns to be used for column-based metrics.
        :is_payload: Whether the data is payload or feedback.
        :metric_values: The `metric_values` object for already calculated metrics. [Optional]

        :returns: The updated `metric_values` object.
        """

        # Initialising the `metric_values` object
        metric_values = BatchUtils.initialize_metric_values(metrics) if metric_values is None else metric_values

        # Getting the problem type
        problem_type = get(subscription, "entity.asset.problem_type")

        # Getting the input and output data schema
        input_data_schema = get(subscription, "entity.asset_properties.input_data_schema")
        output_data_schema = get(subscription, "entity.asset_properties.output_data_schema")

        # Getting the record-id and probability column
        record_id_column = FairnessBatchUtils.get_name_with_modeling_role(RECORD_ID_MODELING_ROLE, output_data_schema)
        probability_column = FairnessBatchUtils.get_name_with_modeling_role(PROBABILITY_MODELING_ROLE, output_data_schema)

        # Calculating the metrics
        for metric in metrics:
            if metric == Metrics.ABSENCE_COUNT.value:
                # Calculating the `absence_count` metric
                absence_count_dict = MetricsUtils.absence_count(data, columns)

                # Updating the `metric_values` object with results
                metric_values = cls._update_column_based_metric_values(metric, absence_count_dict, is_payload, metric_values)
            elif metric == Metrics.EMPTY_STRINGS.value:
                # Calculating the `empty_strings` metric
                empty_strings_dict = MetricsUtils.empty_strings(data, columns)
                
                # Updating the `metric_values` object with results
                metric_values = cls._update_column_based_metric_values(metric, empty_strings_dict, is_payload, metric_values)
            elif metric == Metrics.CLASS_CONFUSION.value:
                # Initialising the boundaries and minimum distances
                binary_confidence_boundary = binary_class_confusion_distance = multiclass_class_confusion_distance = None

                if problem_type == "binary":
                    binary_confidence_boundary = get(monitor_instance, "entity.parameters.binary_classification_decision_boundary", default=DEFAULT_THRESHOLDS["{}_BINARY_CONFIDENCE_BOUNDARY".format(metric)])
                    binary_class_confusion_distance = get(monitor_instance, "entity.parameters.min_distance_decision_boundary", default=DEFAULT_THRESHOLDS["{}_BINARY".format(metric)])
                elif problem_type == "multiclass":
                    multiclass_class_confusion_distance = get(monitor_instance, "entity.parameters.min_distance_top_labels", default=DEFAULT_THRESHOLDS["{}_MULTICLASS".format(metric)])
                else:
                    # The `class_confusion` metric is not supported for regression models
                    continue

                # Calculating the `class_confusion` metric
                record_ids, count = MetricsUtils.class_confusion(
                    data=data,
                    problem_type=problem_type,
                    probability_column=probability_column,
                    record_id_column=record_id_column,
                    binary_confidence_boundary=binary_confidence_boundary,
                    binary_class_confusion_distance=binary_class_confusion_distance,
                    multiclass_class_confusion_distance=multiclass_class_confusion_distance
                )

                # Updating the `metric_values` object with results
                metric_values["metrics"][metric]["payload" if is_payload else "feedback"] = {
                    "count": count,
                    "scoring_ids" if is_payload else "record_ids": record_ids
                }
            elif metric == Metrics.DUPLICATE_ROWS.value:
                # Calculating the `duplicate_rows` metric
                num_duplicate_rows = MetricsUtils.duplicate_rows(data, columns)

                # Updating the `metric_values` object with results
                metric_values["metrics"][metric]["payload" if is_payload else "feedback"] = num_duplicate_rows
            elif metric == Metrics.UNIQUE_COLUMNS.value:
                # Calculating the `unique_columns` metric
                distinct_counts_dict = MetricsUtils.unique_columns(data, columns)
                
                # Updating the `metric_values` object with results
                metric_values = cls._update_column_based_metric_values(metric, distinct_counts_dict, is_payload, metric_values)

        return metric_values
    
    @classmethod
    def _update_column_based_metric_values(cls, metric: str, column_metric_values: dict, is_payload: bool, metric_values: dict) -> dict:
        """
        Updates the given `metric_values` object with the metric (column-based) values of all the given columns.
        :metric: The name of the column-based metric.
        :column_metric_values: The dictionary containing the values for each column to be updated.
        :is_payload: Whether the metric was computed on payload or feedback data.
        :metric_values: The `metric_values` object.

        :returns: The updated `metric_values` object.
        """

        # Adding the values for the columns
        for column in column_metric_values:
            # Adding the value
            metric_values["metrics"][metric]["payload" if is_payload else "feedback"][column] = column_metric_values[column]

        return metric_values