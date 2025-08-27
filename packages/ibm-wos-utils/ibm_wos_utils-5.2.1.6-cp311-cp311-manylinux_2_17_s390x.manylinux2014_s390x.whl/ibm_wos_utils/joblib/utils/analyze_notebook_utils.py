# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2020, 2021
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------


import io
import json
import tarfile
import tempfile
import zipfile

import numpy as np
import pandas as pd
import pyspark.sql.functions as F
from ibm_wos_utils.drift.batch.constraints.custom_range import (Range,
                                                                merge_ranges)
from ibm_wos_utils.drift.batch.constraints.entity import DataConstraintSet
from ibm_wos_utils.drift.batch.constraints.schema import \
    DriftedTransactionsSchema
from ibm_wos_utils.drift.batch.util.constants import ColumnType, ConstraintName
from ibm_wos_utils.joblib.utils.constants import StorageType
from ibm_wos_utils.joblib.utils.python_utils import get
from IPython.display import HTML, display
from pyspark.ml.feature import Bucketizer
from pyspark.sql import Column, DataFrame
from tabulate import tabulate


def get_drift_archive_contents(
        drift_archive,
        model_drift_enabled,
        data_drift_enabled):
    """Reads the downloaded drift archive and returns a tuple of Drifted Transactions Schema,
    Drift Model Properties, Data Drift Constraints

    Arguments:
        drift_archive {bytes} -- Downloaded drift archive
        model_drift_enabled {boolean} -- Whether model drift is enabled.
        data_drift_enabled {boolean} -- Whether data drift is enabled.

    Returns:
        tuple -- A tuple of DriftedTransactionsSchema, DDM Properties and DataConstraintSet
    """
    ddm_properties = None
    constraints_set = None
    schema = None
    with tempfile.TemporaryDirectory() as tmp:
        member = "archive.tar.gz"
        with zipfile.ZipFile(io.BytesIO(drift_archive)) as zf:
            zf.extract(member, tmp)
        with tarfile.open(tmp + "/" + member, mode="r:gz") as tar:
            schema_json = json.load(
                tar.extractfile("drifted_transactions_schema.json"))
            schema = DriftedTransactionsSchema()
            schema.from_json(schema_json)

            if model_drift_enabled:
                ddm_properties = json.load(
                    tar.extractfile("ddm_properties.json"))

            if data_drift_enabled:
                constraints_json = json.load(
                    tar.extractfile("data_drift_constraints.json"))
                constraints_set = DataConstraintSet()
                constraints_set.from_json(constraints_json)

    return schema, ddm_properties, constraints_set


def show_last_n_drift_measurements(n: int, client, subscription_id: str):
    """Shows Last `n` drift measurements of a subscription

    Arguments:
        n {int} -- Number of measurements to fetch
        client {[type]} -- IBM Watson OpenScale API Client
        subscription_id {str} -- Subscription ID
    """
    measurements = client.monitor_instances.measurements.query(
        target_id=subscription_id,
        monitor_definition_id="drift",
        recent_count=n).result.measurements
    results = []

    for measurement in measurements:
        results.append([measurement.metadata.id,
                        measurement.entity.run_id,
                        measurement.entity.monitor_instance_id,
                        measurement.entity.target.target_id,
                        measurement.entity.timestamp])
    results = pd.DataFrame(
        results,
        columns=[
            "Measurement ID",
            "Monitor Run ID",
            "Monitor Instance ID",
            "Subscription ID",
            "Timestamp"])
    results.sort_values(by="Timestamp", ascending=False, inplace=True)

    display(results)


def get_table_details_from_subscription(subscription, table_type: str, default_num_partitions: int = 12):
    """Gets Table Details from Subscription

    Arguments:
        subscription  -- Subscription
        table_type {str} -- Table Type

    Keyword Arguments:
        default_num_partitions {int) -- Default Number of Partitions {{default: 12}}

    Raises:
        Exception: If the table_type is not found in subscription

    Returns:
        tuple -- A tuple of table details: database name, schema name, table  name
    """
    data_source = [
        source for source in subscription.entity.data_sources if source.type == table_type]
    if len(data_source) == 0:
        raise Exception(
            "Details not found for data source type: {} in subscription.".format(table_type))
    data_source = data_source[0].to_dict()

    database_name = get(data_source, "database_name")
    schema_name = get(data_source, "schema_name")
    table_name = get(data_source, "table_name")

    type = get(data_source, "connection.type")

    if type == StorageType.HIVE.value:
        return database_name, schema_name, table_name

    partition_column = get(data_source, "parameters.partition_column")
    if partition_column is None:
        partition_column = get_record_timestamp_column(subscription)

    num_partitions = get(data_source, "parameters.num_partitions", default_num_partitions)

    return database_name, schema_name, table_name, partition_column, num_partitions


def show_dataframe(
        spark_df,
        num_rows=10,
        priority_columns=[],
        record_id_column="scoring_id",
        record_timestamp_column="scoring_timestamp"):
    """Shows specified number of rows of a PySpark DataFrame

    Arguments:
        spark_df {DataFrame} -- Pyspark DataFrame

    Keyword Arguments:
        num_rows {int} -- Number of Rows to show (default: {10})
        priority_columns {list} -- Columns to show first (default: {[]})
        record_id_column {str} -- Column with record-id modeling role (default: {"scoring_id"})
        record_timestamp_column {str} -- Column with record-timestamp modeling role (default: {"scoring_timestamp"})

    """
    show_df = spark_df.limit(num_rows).toPandas()
    original_columns = list(show_df.columns)
    new_columns = []
    priority_columns += [record_id_column, record_timestamp_column]
    for column in priority_columns:
        if column in original_columns:
            new_columns.append(column)
            original_columns.remove(column)
    new_columns += original_columns
    display(HTML(
        tabulate(
            show_df[new_columns],
            headers=new_columns,
            tablefmt="html")))


def get_query(
        constraints_set: DataConstraintSet,
        schema: DriftedTransactionsSchema,
        constraint_id: str) -> Column:
    """Get PySpark Query for filter/where

    Arguments:
        constraints_set {DataConstraintSet} -- Data Constraints Set
        schema {DriftedTransactionsSchema} -- Drifted Transactions Schema
        constraint_id {str} -- Constraint ID

    Returns:
        Column -- PySpark Column with query
    """
    constraint = constraints_set.constraints.get(constraint_id)
    bitmap = {constraint.name.value: ["_"] *
              len(schema.bitmap[constraint.name.value])}
    idx = schema.bitmap[constraint.name.value].index(constraint_id)
    bitmap[constraint.name.value][idx] = "1"

    subqueries = []
    for name, values in bitmap.items():
        if "1" in values:
            subqueries.append(F.col(name).like("".join(values)))

    if not subqueries:
        return

    return subqueries.pop()


def get_column_query(
        constraints_set: DataConstraintSet,
        schema: DriftedTransactionsSchema,
        column: str,
        constraint_names=[]):
    """Get PySpark query for filter/where

    Arguments:
        constraints_set {DataConstraintSet} -- Data Constraints Set
        schema {DriftedTransactionsSchema} -- Drifted Transactions Schema
        column {str} -- Name of the column

    Keyword Arguments:
        constraint_names {list} -- Constraint Names (default: {[]})

    Returns:
        Column -- PySpark Column with query
    """
    if not constraint_names:
        constraint_names = list(ConstraintName)

    learnt_constraints = constraints_set.get_constraints_for_column(column)

    subqueries = []

    for ctr_id in learnt_constraints:
        subqueries.append(get_query(constraints_set, schema, ctr_id))

    if not subqueries:
        return

    result = subqueries.pop()

    for subquery in subqueries:
        result = (result | subquery)

    return result


def show_constraints_by_column(
        constraints_set: DataConstraintSet,
        column: str):
    """Shows all the constraints learnt for the given column

    Arguments:
        constraints_set {DataConstraintSet} -- Data Constraints Set
        column {str} -- Name of the column
    """
    constraints = constraints_set.get_constraints_for_column(column)

    data = [[ctr_id, ctr.name.value, ctr.kind.value, ctr.columns]
            for ctr_id, ctr in constraints.items()]

    if data:
        display(
            HTML(
                tabulate(
                    data,
                    headers=[
                        "Constraint ID",
                        "Constraint Name",
                        "Constraint Kind",
                        "Constraint Columns"],
                    tablefmt="html")))
    else:
        print("No constraints to show.")


def explain_categorical_distribution_constraint(
        drifted_transactions_df: DataFrame,
        payload_table_df: DataFrame,
        constraints_set: DataConstraintSet,
        schema: DriftedTransactionsSchema,
        constraint_id: str):
    """Explain Categorical Distribution Constraint and Return Spark DataFrame with Payload Transactions
    violating Categorical Distribution Constraint

    Arguments:
        drifted_transactions_df {DataFrame} -- PySpark DataFrame with Drifted Transactions
        payload_table_df {DataFrame} -- PySpark DataFrame with Payload Table
        constraints_set {DataConstraintSet} -- Data Constraints Set
        schema {DriftedTransactionsSchema} -- Drifted Transactions Schema
        constraint_id {str} -- Constraint ID to explain

    Raises:
        Exception: If the constraint is not of correct type

    Returns:
        DataFrame -- DataFrame with Payload Transactions violating this constraint
    """

    constraint = constraints_set.constraints.get(constraint_id)

    if constraint.name != ConstraintName.CATEGORICAL_DISTRIBUTION_CONSTRAINT:
        raise Exception(
            "Constraint with ID '{}' is of type: {} and not {}".format(
                constraint_id,
                constraint.name.value,
                ConstraintName.CATEGORICAL_DISTRIBUTION_CONSTRAINT.value))

    column = constraints_set.columns[constraint.columns[0]]

    def transform_key(
        key): return key if column.dtype is ColumnType.CATEGORICAL else eval(key)

    frequency_distribution = {
        transform_key(key): value for key,
        value in constraint.content["frequency_distribution"].items()}
    df = pd.Series(frequency_distribution).to_frame().reset_index()
    df.columns = [column.name, "count"]

    print(
        "The frequency distribution of column '{}' at training time:".format(
            column.name))
    display(df)

    filter_query = get_query(constraints_set, schema, constraint_id)

    result = drifted_transactions_df\
        .where("is_data_drift")\
        .where(filter_query)\
        .select(["scoring_id"])
    count = result.count()

    print(
        "Total {} transactions are violating constraint with id '{}'.".format(
            count,
            constraint_id))

    if count == 0:
        return

    result = payload_table_df\
        .join(result, ["scoring_id"], "leftsemi")\
        .join(result, ["scoring_id"], "left")

    summary = result.groupBy(column.name)\
        .count()\
        .sort(column.name)\
        .toPandas()
    display(summary)
    return result


def explain_numeric_range_constraint(
        drifted_transactions_df: DataFrame,
        payload_table_df: DataFrame,
        constraints_set: DataConstraintSet,
        schema: DriftedTransactionsSchema,
        constraint_id: str):
    """Explain Numeric Range Constraint and Return Spark DataFrame with Payload Transactions
    violating Numeric Range Constraint

    Arguments:
        drifted_transactions_df {DataFrame} -- PySpark DataFrame with Drifted Transactions
        payload_table_df {DataFrame} -- PySpark DataFrame with Payload Table
        constraints_set {DataConstraintSet} -- Data Constraints Set
        schema {DriftedTransactionsSchema} -- Drifted Transactions Schema
        constraint_id {str} -- Constraint ID to explain

    Raises:
        Exception: If the constraint is not of correct type

    Returns:
        DataFrame -- DataFrame with Payload Transactions violating this constraint
    """

    constraint = constraints_set.constraints.get(constraint_id)

    if constraint.name != ConstraintName.NUMERIC_RANGE_CONSTRAINT:
        raise Exception(
            "Constraint with ID '{}' is of type: {} and not {}".format(
                constraint_id,
                constraint.name.value,
                ConstraintName.NUMERIC_RANGE_CONSTRAINT.value))

    column = constraints_set.columns[constraint.columns[0]]

    buckets = {
        eval(key): value for key,
        value in constraint.content["ranges"].items()}

    step_size = np.min(np.diff(list(buckets.keys())))
    ranges = merge_ranges([Range(bounds=(key, key + step_size),
                                 count=value) for key,
                           value in buckets.items()],
                          discard=True)
    ranges = [num_range.to_json() for num_range in ranges]

    print(
        "The column '{}' has following numeric ranges at training time:".format(
            column.name))
    display(pd.DataFrame.from_dict(ranges))

    filter_query = get_query(constraints_set, schema, constraint_id)

    result = drifted_transactions_df\
        .where("is_data_drift")\
        .where(filter_query)\
        .select(["scoring_id"])
    count = result.count()

    print(
        "Total {} transactions are violating constraint with id '{}'.".format(
            count,
            constraint_id))

    if count == 0:
        return

    result = payload_table_df\
        .join(result, ["scoring_id"], "leftsemi")\
        .join(result, ["scoring_id"], "left")\


    summary_df = result.select(column.name).summary(
        ["min", "max"]).toPandas().set_index("summary").astype(float).squeeze()

    is_integer = "int" in dict(
        payload_table_df.dtypes)[column.name]
    if is_integer:
        splits = np.arange(
            start=summary_df.loc["min"],
            stop=summary_df.loc["max"] +
            column.bin_width,
            step=column.bin_width,
            dtype=int)
    else:
        bins = (summary_df.loc["max"] -
                summary_df.loc["min"]) / column.bin_width
        splits = np.linspace(
            summary_df.loc["min"], summary_df.loc["max"], int(
                np.ceil(bins)))
    bucket_col = "{}_buckets".format(column.name)
    bucketizer = Bucketizer(
        splits=splits,
        inputCol=column.name,
        outputCol=bucket_col,
        handleInvalid="keep")
    bucketized_data = bucketizer.transform(result.select(column.name))\
        .groupBy(bucket_col)\
        .count()\
        .dropna(subset=[bucket_col])\
        .sort(bucket_col)\
        .toPandas()

    buckets = [(elem, elem + column.bin_width) for elem in splits]
    ranges = bucketized_data.apply(lambda row: Range(bounds=buckets[int(
        row[bucket_col])], count=int(row["count"])), axis=1).to_list()
    ranges = merge_ranges(ranges)
    ranges = [num_range.to_json() for num_range in ranges]
    display(pd.DataFrame.from_dict(ranges))

    return result


def explain_catnum_range_constraint(
        drifted_transactions_df: DataFrame,
        payload_table_df: DataFrame,
        constraints_set: DataConstraintSet,
        schema: DriftedTransactionsSchema,
        constraint_id: str):
    """Explain Cat Numeric Range Constraint and Return Spark DataFrame with Payload Transactions
    violating Cat Numeric Range Constraint

    Arguments:
        drifted_transactions_df {DataFrame} -- PySpark DataFrame with Drifted Transactions
        payload_table_df {DataFrame} -- PySpark DataFrame with Payload Table
        constraints_set {DataConstraintSet} -- Data Constraints Set
        schema {DriftedTransactionsSchema} -- Drifted Transactions Schema
        constraint_id {str} -- Constraint ID to explain

    Raises:
        Exception: If the constraint is not of correct type

    Returns:
        DataFrame -- DataFrame with Payload Transactions violating this constraint
    """
    constraint = constraints_set.constraints.get(constraint_id)

    if constraint.name != ConstraintName.CAT_NUM_RANGE_CONSTRAINT:
        raise Exception(
            "Constraint with ID '{}' is of type: {} and not {}".format(
                constraint_id,
                constraint.name.value,
                ConstraintName.CAT_NUM_RANGE_CONSTRAINT.value))

    source_column = constraints_set.columns[constraint.content["source_column"]]
    target_column = constraints_set.columns[constraint.content["target_column"]]

    def transform_key(
        key): return key if source_column.dtype is ColumnType.CATEGORICAL else eval(key)

    catnum_ranges = constraint.content["ranges"]

    ranges = []
    for elem in catnum_ranges:
        for numrange in catnum_ranges[elem]:
            flat_range = {source_column.name: elem}
            flat_range.update(numrange)
            ranges.append(flat_range)

    print(
        "The columns '{}-{}' have following cat-numeric ranges at training time:".format(
            source_column.name,
            target_column.name))
    display(pd.DataFrame.from_dict(ranges))

    filter_query = get_query(constraints_set, schema, constraint_id)

    result = drifted_transactions_df\
        .where("is_data_drift")\
        .where(filter_query)\
        .select(["scoring_id"])
    count = result.count()

    print(
        "Total {} transactions are violating constraint with id '{}'.".format(
            count,
            constraint_id))

    if count == 0:
        return

    result = payload_table_df\
        .join(result, ["scoring_id"], "leftsemi")\
        .join(result, ["scoring_id"], "left")\

    summary_df = result.select(target_column.name).summary(
        ["min", "max"]).toPandas().set_index("summary").astype(float).squeeze()
    is_integer = "int" in dict(
        payload_table_df.dtypes)[target_column.name]
    if is_integer:
        splits = np.arange(
            start=summary_df.loc["min"],
            stop=summary_df.loc["max"] +
            target_column.bin_width,
            step=target_column.bin_width,
            dtype=int)
    else:
        bins = (summary_df.loc["max"] -
                summary_df.loc["min"]) / target_column.bin_width
        splits = np.linspace(
            summary_df.loc["min"], summary_df.loc["max"], int(
                np.ceil(bins)))

    bucket_col = "{}_buckets".format(target_column.name)
    bucketizer = Bucketizer(
        splits=splits,
        inputCol=target_column.name,
        outputCol=bucket_col,
        handleInvalid="keep")
    bucketized_data = bucketizer.transform(
        result.select(
            source_column.name,
            target_column.name)) .groupBy(
        source_column.name,
        bucket_col) .count() .dropna(
                subset=[bucket_col]) .sort(bucket_col) .toPandas()

    buckets = [(elem, elem + target_column.bin_width) for elem in splits]

    ranges = []
    for src_val in bucketized_data[source_column.name].unique():
        catranges = bucketized_data[bucketized_data[source_column.name] == src_val].apply(
            lambda row: Range(bounds=buckets[int(row[bucket_col])], count=int(row["count"])), axis=1).to_list()

        for numrange in merge_ranges(catranges):
            tmprange = {source_column.name: src_val}
            tmprange.update(numrange.to_json())
            ranges.append(tmprange)

    display(pd.DataFrame.from_dict(ranges))
    return result


def explain_catcat_distribution_constraint(
        drifted_transactions_df: DataFrame,
        payload_table_df: DataFrame,
        constraints_set: DataConstraintSet,
        schema: DriftedTransactionsSchema,
        constraint_id: str):
    """Explain Cat-Cat Distribution Constraint and Return Spark DataFrame with Payload Transactions
    violating Cat-Cat Distribution Constraint

    Arguments:
        drifted_transactions_df {DataFrame} -- PySpark DataFrame with Drifted Transactions
        payload_table_df {DataFrame} -- PySpark DataFrame with Payload Table
        constraints_set {DataConstraintSet} -- Data Constraints Set
        schema {DriftedTransactionsSchema} -- Drifted Transactions Schema
        constraint_id {str} -- Constraint ID to explain

    Raises:
        Exception: If the constraint is not of correct type

    Returns:
        DataFrame -- DataFrame with Payload Transactions violating this constraint
    """
    constraint = constraints_set.constraints.get(constraint_id)

    if constraint.name != ConstraintName.CAT_CAT_DISTRIBUTION_CONSTRAINT:
        raise Exception(
            "Constraint with ID '{}' is of type: {} and not {}".format(
                constraint_id,
                constraint.name.value,
                ConstraintName.CAT_NUM_RANGE_CONSTRAINT.value))

    source_column = constraints_set.columns[constraint.content["source_column"]]
    target_column = constraints_set.columns[constraint.content["target_column"]]

    rare_combinations = []

    for combination in constraint.content["rare_combinations"]:
        for tgt_value in combination["target_values"]:
            rare_combinations.append(
                {
                    "{} Category".format(
                        source_column.name): combination["source_value"], "{} Category".format(
                        target_column.name): tgt_value})
    print(
        "The columns '{}-{}' have following rare combinations at training time:".format(
            source_column.name,
            target_column.name))
    display(pd.DataFrame.from_dict(rare_combinations))

    filter_query = get_query(constraints_set, schema, constraint_id)
    result = drifted_transactions_df\
        .where("is_data_drift")\
        .where(filter_query)\
        .select(["scoring_id"])
    count = result.count()

    print(
        "Total {} transactions are violating constraint with id '{}'. Here's a summary: ".format(
            count,
            constraint_id))

    if count == 0:
        return

    result = payload_table_df\
        .join(result, ["scoring_id"], "leftsemi")\
        .join(result, ["scoring_id"], "left")\

    summary_counts = result.groupBy(
        source_column.name,
        target_column.name) .count() .withColumnRenamed(
        source_column.name,
        "{} Category".format(
            source_column.name)) .withColumnRenamed(
                target_column.name,
                "{} Category".format(
                    target_column.name)) .sort(
                        "count",
        ascending=False) .toPandas()
    display(summary_counts)
    return result


def get_record_timestamp_column(subscription) -> str:
    """Gets record timestamp column from the Subscription object.

    Arguments:
        subscription {ibm_watson_openscale.base_classes.watson_open_scale_v2.SubscriptionResponse} -- Subscription response object from IBM Watson Openscale client

    Returns:
        str -- Name of the record timestamp column (default: scoring_timestamp)
    """
    record_timestamp_column = "scoring_timestamp"
    
    columns = [field.name for field in subscription.entity.asset_properties.output_data_schema.fields\
        if get(field, "metadata.modeling_role") == "record_timestamp"]

    if len(columns) == 1:
        record_timestamp_column = columns[0]

    return record_timestamp_column
