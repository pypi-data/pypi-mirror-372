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
    from pyspark.sql.functions import array_max, array_sort, col, count, isnan, max, min, sum, size, slice, to_timestamp, trim, when
except ImportError as ie:
    pass

class MetricsUtils:
    """
    Class for implementation/utility methods for metrics.
    """

    @classmethod
    def absence_count(cls, data, columns: list) -> dict:
        """
        Computes the absence count on the given data for the given columns.
        :data: The pyspark data frame containing data.
        :columns: The list of columns on which the absence counts are to be calculated.

        :returns: A dictionary containing counts against column names as keys.
        """
        absence_counts = dict()

        absence_counts_df = data.select([count(when(isnan(c) | col(c).isNull(), c)).alias(c) for c in columns])
        for column in columns:
            absence_counts[column] = absence_counts_df.collect()[0][column]

        return absence_counts
    
    @classmethod
    def empty_strings(cls, data, cat_columns: list) -> dict:
        """
        Computes the empty strings on the given data for the given columns.
        :data: The pyspark data frame containing data.
        :cat_columns: The list of categorical columns on which the empty strings are to be calculated.

        :returns: A dictionary containing the counts against column names as keys.
        """
        empty_strings = dict()

        for column in cat_columns:
            count_blank = data.filter(trim(col(column)) == "").count()
            empty_strings[column] = count_blank

        return empty_strings
    
    @classmethod
    def class_confusion(
        cls,
        data,
        problem_type: str,
        probability_column: str,
        record_id_column: str=None,
        binary_confidence_boundary: float=None,
        binary_class_confusion_distance: float=None,
        multiclass_class_confusion_distance: float=None
    ) -> list:
        """
        Computes the rows with class confusion for classification type models.
        :data: The pyspark data frame containing data.
        :problem_type: The model classification type [binary/multiclass].
        :probability_column: The name of the probability column.
        :record_id_column: The name of the record ID column. [Optional]
        :binary_confidence_boundary: The confidence boundary for the binary classification models. [Optional]
        :binary_class_confusion_distance: The minimum distance from decision boundary for binary classification models. [Optional]
        :multiclass_class_confusion_distance: The minimum distance between top two label confidences for multi classification models. [Optional]

        :returns: The list of record_ids where the classifier is confused of the prediction and the count of such rows.
        """
        record_ids = None
        class_confusion_count = None
        
        # Checking the problem type
        if problem_type == "binary":
            # Filtering the rows with `class_confusion`
            filtered_df = data.filter((array_max(col(probability_column)) >= binary_confidence_boundary) & (array_max(col(probability_column)) <= binary_confidence_boundary + binary_class_confusion_distance))
            
            if record_id_column is not None:
                # Getting the record IDs
                record_ids = filtered_df.select(record_id_column).rdd.flatMap(lambda x: x).collect()
                class_confusion_count = len(record_ids)
            else:
                class_confusion_count = filtered_df.count()
        elif problem_type == "multiclass":
            # Filtering the rows with `class_confusion`
            filtered_df = data.filter(
                (size(col(probability_column)) >= 2) &
                (slice(array_sort(col(probability_column)), -2, 2)[1] - slice(array_sort(col(probability_column)), -2, 2)[0] < multiclass_class_confusion_distance)
            )

            if record_id_column is not None:
                # Getting the record IDs
                record_ids = filtered_df.select(record_id_column).rdd.flatMap(lambda x: x).collect()
                class_confusion_count = len(record_ids)
            else:
                class_confusion_count = filtered_df.count()
            
        return record_ids, class_confusion_count
    
    @classmethod
    def duplicate_rows(cls, data, columns: list) -> int:
        """
        Computes the number of duplicate rows in the given data.
        :data: The pyspark data frame containing data.
        :columns: The list of columns to be considered.

        :returns: The number of duplicate rows.
        """
        num_duplicate_rows = None

        # Group by columns and count occurrences
        group_by_count_df = data.groupBy(columns).count()

        # Filter the count dataframe for rows with count > 1
        duplicate_df = group_by_count_df.filter(group_by_count_df["count"] > 1)

        # Find the sum of the repeating rows
        sum_df = duplicate_df.agg(sum("count"))

        # Find the number of repeating rows
        duplicate_count_df = duplicate_df.count()

        # Subtract the number of rows from the sum to eliminate original repeating rows,
        # in order to get just the duplicate count
        if sum_df.collect()[0][0] is not None:
            num_duplicate_rows = sum_df.collect()[0][0] - duplicate_count_df
        else:
            # No duplicate rows
            num_duplicate_rows = 0

        return num_duplicate_rows
    
    @classmethod
    def unique_columns(cls, data, columns: list) -> dict:
        """
        Computes the percentages of distinct values for the given columns in the given data.
        :data: The pyspark data frame containing data.
        :columns: The list of columns to be considered.

        :returns: A dictionary containing distinct counts against column names as keys.
        """
        distinct_counts = dict()

        # Get a list of unique columns
        for col in columns:
            distinct_col_values = data.select(col).distinct().collect()
            distinct_counts[col] = len(distinct_col_values)

        return distinct_counts
    
    @classmethod
    def get_start_end_timestamps_from_data(cls, data, timestamp_column: str):
        """
        Gets the start and end timestamps from the given data.
        :data: The data frame containing data.
        :timestamp_column: The name of the timestamp column.

        :returns: The start and end timestamps.
        """
        start_timestamp = end_timestamp = None

        # Checking if the timestamp column is present in the data
        if timestamp_column in data.columns:
            # Checking if the timestamp column is of string type
            if dict(data.dtypes)[timestamp_column] == "string":
                # Converting the column to timestamp type
                data = data.withColumn(timestamp_column, to_timestamp(timestamp_column))
            
            # Getting the start and end timestamps
            start_timestamp = data.select(min(timestamp_column)).collect()[0][0].isoformat() + "Z"
            end_timestamp = data.select(max(timestamp_column)).collect()[0][0].isoformat() + "Z"

        return start_timestamp, end_timestamp