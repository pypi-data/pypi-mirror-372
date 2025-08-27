# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2020, 2021
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

import json
import tarfile
import tempfile
import uuid
from collections.abc import Mapping

from ibm_wos_utils.joblib.utils.param_utils import get

# Mapping between Hive and Spark data types. Data types like "float",
# "double" which are present in both are not added
spark_to_hive_map = {
    "byte": "tinyint",
    "short": "smallint",
    "integer": "int",
    "long": "bigint",
    "calendarinterval": "interval"
}


def __generate_table_name(prefix, suffix=None):
    return "{}_table_{}".format(
        prefix, suffix or str(
            uuid.uuid4())).replace(
        "-", "")


def __generate_table_ddl(
        ddl_fields,
        table_name,
        database_name: str = None,
        path_to_hdfs_directory: str = None,
        stored_as: str = "csv",
        table_properties: dict = {}):

    column_string = "("
    collection_items = False

    for field in ddl_fields:
        feature_name = field.get("name")
        feature_type = field.get("type")

        # for columns with the type stored in a dictionary, prepare column type
        # as a string
        if isinstance(feature_type, Mapping):
            data_type = feature_type.get("type")
            element_type = feature_type.get("elementType")
            hive_element_type = spark_to_hive_map.get(
                element_type, element_type)
            feature_type = "{}<{}>".format(data_type, hive_element_type)
            collection_items = True
        else:
            hive_element_type = spark_to_hive_map.get(feature_type)
            if hive_element_type is not None:
                feature_type = hive_element_type

        column_string += "`{}` {}, ".format(feature_name, feature_type)

    ddl_column_string = column_string[:-2] + ")"

    if database_name:
        ddl_string = "CREATE TABLE IF NOT EXISTS {}.{} {}".format(
            database_name, table_name, ddl_column_string)
    else:
        ddl_string = "CREATE TABLE IF NOT EXISTS {} {}".format(
            table_name, ddl_column_string)

    if stored_as == "csv":
        ddl_string += " ROW FORMAT DELIMITED FIELDS TERMINATED BY ','"
        if collection_items:
            ddl_string += " COLLECTION ITEMS TERMINATED BY '|'"
        ddl_string += " STORED AS TEXTFILE "
    elif stored_as == "parquet":
        ddl_string += " STORED AS PARQUET "
    elif stored_as == "orc":
        ddl_string += " STORED AS ORC "
    else:
        raise Exception(
            "Unsupported storage format '{}' specified.".format(stored_as))

    if path_to_hdfs_directory is not None and path_to_hdfs_directory != "":
        ddl_string += " LOCATION '{}'".format(
            path_to_hdfs_directory)

    if table_properties:
        table_properties_arr = []
        for key, value in table_properties.items():
            table_properties_arr.append("'{}'='{}'".format(key, value))
        ddl_string += " TBLPROPERTIES ({})".format(
            ",".join(table_properties_arr))

    return ddl_string + ";"

def __generate_index_ddl(
        table_name,
        record_timestamp,
        database_name: str = None):

    if database_name:
        ddl = "\nCREATE INDEX {1}_index ON TABLE {0}.{1} ({2}) AS 'COMPACT' WITH DEFERRED REBUILD;\n".format(
            database_name, table_name, record_timestamp)
        ddl += "ALTER INDEX {1}_index ON {0}.{1} REBUILD;".format(
            database_name, table_name)
    else:
        ddl = "\nCREATE INDEX {0}_index ON {0} ({1}) AS 'COMPACT' WITH DEFERRED REBUILD;\n".format(
            table_name, record_timestamp)
        ddl += "ALTER INDEX {0}_index ON {0} REBUILD;".format(
            table_name)
    return ddl

def generate_payload_table_ddl(
        common_config_data,
        database_name: str = None,
        table_prefix: str = "payload",
        table_suffix: str = None,
        path_to_hdfs_directory: str = "",
        stored_as: str = "csv",
        table_properties: dict = {},
        create_index: bool = True):
    """Generates Create DDL statement for Payload Table of an IBM Watson OpenScale batch subscription.

    Arguments:
        common_config_data {dict} -- Common Configuration JSON

    Keyword Arguments:
        database_name {str} -- Database Name where the table is to be created. (default: {None})
        table_prefix {str} -- Prefix for this table name (default: {"payload"})
        table_suffix {str} -- Suffix for this table name. Defaults to a random UUID.
        path_to_hdfs_directory {str} -- Path to HDFS directory that already has the data (default: {""})
        stored_as {str} -- Storage Format of the Data. Currently only 'csv' supported. (default: {"csv"})
        table_properties {dict} -- Additional Table Properties to be included in the DDL as `TBLPROPERTIES` (default: {{}})
        create_index {bool} -- Flag to control whether an index is created on record-timestamp column. (default: {True})

    Returns:
        str -- Create DDL statement for Payload Table
    """

    table_suffix = table_suffix or str(uuid.uuid4())
    table_name = __generate_table_name(table_prefix, table_suffix)
    common_configuration = common_config_data["common_configuration"]
    output_data_schema = common_configuration.get("output_data_schema")
    ddl_fields = [field for field in common_configuration.get("training_data_schema")[
        "fields"] if get(field, "metadata.modeling_role") != "target"]
    record_timestamp = None
    for field in output_data_schema["fields"]:
        modeling_role = field["metadata"].get("modeling_role")

        if modeling_role in (
            "probability",
            "prediction",
            "record-timestamp",
            "record-id",
            "meta-field"):
            ddl_fields.append(field)
        if modeling_role == "record-timestamp":
            record_timestamp = field.get("name")

    result = __generate_table_ddl(
        ddl_fields,
        table_name,
        database_name,
        path_to_hdfs_directory,
        stored_as,
        table_properties)

    if create_index and (record_timestamp is not None):
        result += __generate_index_ddl(table_name, record_timestamp, database_name)
    return result


def generate_feedback_table_ddl(
        common_config_data,
        database_name: str = None,
        table_prefix: str = "feedback",
        table_suffix: str = None,
        path_to_hdfs_directory: str = "",
        stored_as: str = "csv",
        table_properties: dict = {},
        create_index: bool = True):
    """Generates Create DDL statement for Feedback Table of an IBM Watson OpenScale batch subscription.

    Arguments:
        common_config_data {dict} -- Common Configuration JSON

    Keyword Arguments:
        database_name {str} -- Database Name where the table is to be created. (default: {None})
        table_prefix {str} -- Prefix for this table name (default: {"feedback"})
        table_suffix {str} -- Suffix for this table name. Defaults to a random UUID.
        path_to_hdfs_directory {str} -- Path to HDFS directory that already has the data (default: {""})
        stored_as {str} -- Storage Format of the Data. Currently only 'csv' supported. (default: {"csv"})
        table_properties {dict} -- Additional Table Properties to be included in the DDL as `TBLPROPERTIES` (default: {{}})
        create_index {bool} -- Flag to control whether an index is created on record-timestamp column. (default: {True})

    Returns:
        str -- Create DDL statement for Feedback Table
    """

    table_suffix = table_suffix or str(uuid.uuid4())
    table_name = __generate_table_name(table_prefix, table_suffix)
    common_configuration = common_config_data["common_configuration"]
    output_data_schema = common_configuration.get("output_data_schema")
    ddl_fields = common_configuration.get(
        "training_data_schema")["fields"].copy()
    record_timestamp = None

    for field in output_data_schema["fields"]:
        modeling_role = field["metadata"].get("modeling_role")

        if modeling_role in (
            "probability",
            "prediction",
            "record-timestamp",
            "record-id"):
            ddl_fields.append(field)
        if modeling_role == "record-timestamp":
            record_timestamp = field.get("name")

    result= __generate_table_ddl(
        ddl_fields,
        table_name,
        database_name,
        path_to_hdfs_directory,
        stored_as,
        table_properties)

    if create_index and (record_timestamp is not None):
        result += __generate_index_ddl(table_name, record_timestamp, database_name)

    return result


def generate_scored_training_table_ddl(
        common_config_data,
        database_name: str = None,
        table_prefix: str = "scored_training",
        table_suffix: str = None,
        path_to_hdfs_directory: str = "",
        stored_as: str = "csv",
        table_properties: dict = {}):
    """Generates Create DDL statement for Scored Training Table of an IBM Watson OpenScale batch subscription.

    Arguments:
        common_config_data {dict} -- Common Configuration JSON

    Keyword Arguments:
        database_name {str} -- Database Name where the table is to be created. (default: {None})
        table_prefix {str} -- Prefix for this table name (default: {"scored_training"})
        table_suffix {str} -- Suffix for this table name. Defaults to a random UUID.
        path_to_hdfs_directory {str} -- Path to HDFS directory that already has the data (default: {""})
        stored_as {str} -- Storage Format of the Data. Currently only 'csv' supported. (default: {"csv"})
        table_properties {dict} -- Additional Table Properties to be included in the DDL as `TBLPROPERTIES` (default: {{}})

    Returns:
        str -- Create DDL statement for Scored Training Table
    """

    table_suffix = table_suffix or str(uuid.uuid4())
    table_name = __generate_table_name(table_prefix, table_suffix)
    common_configuration = common_config_data["common_configuration"]
    output_data_schema = common_configuration.get("output_data_schema")
    ddl_fields = common_configuration.get(
        "training_data_schema")["fields"].copy()

    for field in output_data_schema["fields"]:
        modeling_role = field["metadata"].get("modeling_role")

        if modeling_role in (
            "probability",
            "prediction",
            "meta-field"):
            ddl_fields.append(field)

    return __generate_table_ddl(
        ddl_fields,
        table_name,
        database_name,
        path_to_hdfs_directory,
        stored_as,
        table_properties)


def generate_drift_table_ddl(
        drift_archive: bytearray,
        database_name: str = None,
        table_prefix: str = "drifted_transactions",
        table_suffix: str = None):
    """Generates Create DDL statement for Drifted Transactions Table of an IBM Watson OpenScale batch subscription.

    Arguments:
        drift_archive {bytearray} -- Drift Archive

    Keyword Arguments:
        database_name {str} -- Database Name where the table is to be created. (default: {None})
        table_prefix {str} -- Prefix for this table name (default: {"drifted_transactions"})
        table_suffix {str} -- Suffix for this table name. Defaults to a random UUID.

    Returns:
        str -- Create DDL statement for Drifted Transactions Table
    """

    table_suffix = table_suffix or str(uuid.uuid4())
    table_name = __generate_table_name(table_prefix, table_suffix)
    with tempfile.NamedTemporaryFile() as tmp_file:
        tmp_file.write(drift_archive)
        tmp_file.flush()
        with tarfile.open(tmp_file.name, "r:gz") as tf:
            with tf.extractfile("drifted_transactions_schema.json") as json_data:
                schema = json.load(json_data)
    columns = schema["columns"]

    ddl_fields = [{"name": key, "type": columns[key]["type"]}
                  for key in columns]
    result = __generate_table_ddl(ddl_fields, table_name=table_name, database_name=database_name)
    result += "\n"
    result += "CREATE INDEX {1}_index ON TABLE {0}.{1} (run_id, is_model_drift, is_data_drift) AS 'BITMAP' WITH DEFERRED REBUILD;\n".format(
            database_name, table_name)
    result += "ALTER INDEX {1}_index ON {0}.{1} REBUILD;".format(
            database_name, table_name)
    return result


def generate_explanations_table_ddl(
        database_name: str = None,
        table_prefix: str = "explanations",
        table_suffix: str = None,
        path_to_hdfs_directory=None,
        stored_as: str = "orc"):
    """Generates Create DDL statement for Explanations Table of an IBM Watson OpenScale batch subscription.

    Keyword Arguments:
        database_name {str} -- Database Name where the table is to be created. (default: {None})
        table_prefix {str} -- Prefix for this table name (default: {"explanations"})
        table_suffix {str} -- Suffix for this table name. Defaults to a random UUID.
        stored_as {str} -- Storage Format of the Data. (default: {"orc"})

    Returns:
        str -- Create DDL statement for Explanations Table
    """

    table_suffix = table_suffix or str(uuid.uuid4())
    table_name = __generate_table_name(table_prefix, table_suffix)
    ddl_fields = [{"name": f, "type": "string"} for f in ("request_id", "scoring_id", "binding_id", "data_mart_id", "subscription_id",
                                                          "deployment_id", "asset_name", "deployment_name", "prediction", "created_by", "object_hash", "explanation_type", "status")]

    ddl_fields.extend([{"name": f, "type": "timestamp"}
                       for f in ("created_at", "finished_at")])
    ddl_fields.extend([{"name": f, "type": "binary"}
                       for f in ("explanation", "explanation_input", "explanation_output", "error")])
    ddl_fields.extend([{"name": "probability", "type": "float"}])
    ddl_fields = sorted(ddl_fields, key=lambda f: f.get("name"))
    return __generate_table_ddl(ddl_fields, table_name=table_name, database_name=database_name, path_to_hdfs_directory=path_to_hdfs_directory, stored_as=stored_as)

def generate_table_ddl_batch_simplification(
        schema: dict={},
        database_name: str = None,
        table_name: str="feedback",
        path_to_hdfs_directory: str = "",
        stored_as: str = "csv",
        table_properties: dict = {},
        create_index: bool = True):
    """Generates Create DDL statement for Feedback Table of an IBM Watson OpenScale batch subscription.

    Arguments:
        common_config_data {dict} -- Common Configuration JSON

    Keyword Arguments:
        database_name {str} -- Database Name where the table is to be created. (default: {None})
        table_prefix {str} -- Prefix for this table name (default: {"feedback"})
        table_suffix {str} -- Suffix for this table name. Defaults to a random UUID.
        path_to_hdfs_directory {str} -- Path to HDFS directory that already has the data (default: {""})
        stored_as {str} -- Storage Format of the Data. Currently only 'csv' supported. (default: {"csv"})
        table_properties {dict} -- Additional Table Properties to be included in the DDL as `TBLPROPERTIES` (default: {{}})
        create_index {bool} -- Flag to control whether an index is created on record-timestamp column. (default: {True})

    Returns:
        str -- Create DDL statement for Feedback Table
    """

    ddl_fields = schema["fields"].copy()

    result= __generate_table_ddl(
        ddl_fields,
        table_name,
        database_name,
        path_to_hdfs_directory,
        stored_as,
        table_properties)

    return result


