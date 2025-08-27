# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2021
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------


import json
import pathlib
import tarfile
import tempfile
import uuid

import pyspark.sql.functions as F
from ibm_wos_utils.joblib.utils.param_utils import get
from IPython.display import display, Markdown

spark_to_db2_map = {
    "boolean": "boolean",
    "byte": "bigint",
    "short": "bigint",
    "integer": "bigint",
    "long": "bigint",
    "float": "double",
    "double": "double",
    "timestamp": "timestamp",
    "string": "varchar",
    "binary": "blob"
}

def __generate_table_name(prefix, suffix=None):
    return "{}_table_{}".format(
        prefix, suffix or str(
            uuid.uuid4())).replace(
        "-", "")


def __generate_table_ddl(
        ddl_fields,
        table_name: str,
        schema_name: str,
        max_length_categories: dict = {},
        partition_column: str = None):

    if not schema_name:
        raise Exception("Schema Name is required.")
    
    if not table_name:
        raise Exception("Table Name is required")

    if not max_length_categories:
        max_length_categories = {}
        # see if this can be constructed using ddl_fields
        # ddl_field may have length property or metadata.columnInfo.columnLength
        for field in ddl_fields:
            feature_length = get(field, "length")
            if not feature_length:
                feature_length = get(field, "metadata.columnInfo.columnLength")

            if feature_length is not None and feature_length > 0:
                max_length_categories[get(field, "name")] = feature_length
    
    column_string = "("

    is_partition_column_a_feature_column = False
    for field in ddl_fields:
        feature_name = field.get("name")
        feature_type = field.get("type")

        if partition_column is not None and partition_column.lower() == feature_name.lower():
            is_partition_column_a_feature_column = True

        if isinstance(feature_type, dict):
            feature_type = "varchar"
        else:
            db2_element_type = spark_to_db2_map.get(feature_type)
            if db2_element_type is not None:
                feature_type = db2_element_type
                
        get_varchar_length = lambda x: max(64, get(max_length_categories, x, 32)*2)

        if feature_type == "varchar":
            if get(field, "metadata.modeling_role") == "probability":
                feature_type += "(32000)"
            else:
                feature_type += "({})".format(get_varchar_length(feature_name))

        column_string += "\"{}\" {}".format(feature_name, feature_type.upper())
        
        if get(field, "metadata.modeling_role") in ["prediction", "target", "probability", "record-id", "record-timestamp"]:
            column_string += " NOT NULL"
            
        if get(field, "metadata.modeling_role") == "record-id":
            column_string += " PRIMARY KEY"

        column_string += ", "

    if partition_column is not None and not is_partition_column_a_feature_column:
        column_string += "\"{}\" BIGINT GENERATED ALWAYS AS IDENTITY, ".format(partition_column)

    ddl_column_string = column_string[:-2] + ")"

    ddl_string = "CREATE TABLE \"{}\".\"{}\" {};".format(
        schema_name, table_name, ddl_column_string)

    return ddl_string

def __alter_table_ddl(schema_name: str, table_name: str, create_ddl: str, partition_column: str):

    md = "**Create Table SQL Query:** Run the following query, to create a new table\n"
    md += create_ddl + "\n\n"
    md += "**Alter Table SQL Queries:** Run the following queries, in the given order, to add a partition column in your existing table.\n"
    md += "1. `ALTER TABLE \"{0}\".\"{1}\" ADD COLUMN \"{2}\" BIGINT NOT NULL DEFAULT 0;`\n".format(schema_name, table_name, partition_column)
    md += "2. `ALTER TABLE \"{0}\".\"{1}\" ALTER COLUMN \"{2}\" DROP DEFAULT;`\n".format(schema_name, table_name, partition_column)
    md += "3. `ALTER TABLE \"{0}\".\"{1}\" ALTER COLUMN \"{2}\" SET GENERATED ALWAYS AS IDENTITY;`\n".format(schema_name, table_name, partition_column)
    md += "4. `CALL SYSPROC.ADMIN_CMD('REORG TABLE \"{0}\".\"{1}\"');`\n".format(schema_name, table_name)
    md += "5. `UPDATE \"{0}\".\"{1}\" SET \"{2}\" = DEFAULT;`".format(schema_name, table_name, partition_column)
    
    return md

def __generate_table_ddl_from_schema(schema_name: str, table_name: str, table_schema: dict, primary_key_cols: list = [], partition_column: str = None):
    if not schema_name:
        raise Exception("Schema Name is required.")
    
    if not table_name:
        raise Exception("Table Name is required")

    column_components = []
    is_partition_column_a_feature_column = False
    for column, column_meta in table_schema["columns"].items():
        db2_element_type = spark_to_db2_map.get(column_meta["type"])
        if db2_element_type is None:
            db2_element_type = column_meta["type"]
        
        column_string = "\"{}\" {}".format(column, db2_element_type.upper())
        
        if "length" in column_meta:
            column_string += "({})".format(column_meta["length"])
            
        if column_meta.get("not_null"):
            column_string  += " NOT NULL"
            
        if column_meta.get("unique") and not len(primary_key_cols):
            column_string += " PRIMARY KEY"
            
        if "default" in column_meta:
            column_string += " DEFAULT {}".format(column_meta["default"])

        if partition_column is not None and partition_column.lower() == column.lower():
            is_partition_column_a_feature_column = True
        
        column_components.append(column_string)

    if len(primary_key_cols):
        primary_key_cols = ["\"{}\"".format(col) for col in primary_key_cols]
        primary_key_str = "PRIMARY KEY({})".format(",".join(primary_key_cols))
        column_components.append(primary_key_str)

    if partition_column is not None and not is_partition_column_a_feature_column:
        column_components.append("\"{}\" BIGINT GENERATED ALWAYS AS IDENTITY".format(partition_column))
        
    ddl_string = "CREATE TABLE \"{}\".\"{}\" ({});".format(
        schema_name, table_name, ", ".join(column_components))
    
    return ddl_string


def generate_scored_training_table_ddl(
        common_config_data,
        schema_name: str,
        table_prefix: str = "scored_training",
        table_suffix: str = None,
        max_length_categories: dict = {},
        partition_column: str = None):
    """Generates Create DDL statement for Scored Training Table of an IBM Watson OpenScale batch subscription.

    Arguments:
        common_config_data {dict} -- Common Configuration JSON
        schema_name {str} -- Schema Name where the table is to be created.

    Keyword Arguments:
        table_prefix {str} -- Prefix for this table name (default: {"scored_training"})
        table_suffix {str} -- Suffix for this table name. Defaults to a random UUID.
        max_length_categories {dict} -- Dictionary with Categorical Columns as keys, and maximum length of categories as values (default: {{}})
        partition_column {str} -- Partition Column for this table (default: {None})

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

    create_ddl = __generate_table_ddl(
        ddl_fields,
        table_name,
        schema_name,
        max_length_categories,
        partition_column)
    
    if partition_column is not None:
        alter_ddl = __alter_table_ddl(schema_name, table_name, create_ddl, partition_column)
        display(Markdown(alter_ddl))
    else:
        display(create_ddl)

def generate_feedback_table_ddl(
        common_config_data,
        schema_name: str,
        table_prefix: str = "feedback",
        table_suffix: str = None,
        max_length_categories: dict = {},
        create_index: bool = True,
        partition_column: str = None):
    """Generates Create DDL statement for Feedback Table of an IBM Watson OpenScale batch subscription.

    Arguments:
        common_config_data {dict} -- Common Configuration JSON
        schema_name {str} -- Schema Name where the table is to be created.

    Keyword Arguments:
        table_prefix {str} -- Prefix for this table name (default: {"feedback"})
        table_suffix {str} -- Suffix for this table name. Defaults to a random UUID.
        max_length_categories {dict} -- Dictionary with Categorical Columns as keys, and maximum length of categories as values (default: {{}})
        create_index {bool} -- Flag to control whether an index is created on record-timestamp column. (default: {True})
        partition_column {str} -- Partition Column for this table (default: {None})

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

    create_ddl = __generate_table_ddl(
        ddl_fields,
        table_name,
        schema_name,
        max_length_categories,
        partition_column)

    if create_index and (record_timestamp is not None):
        create_ddl = "- `" + create_ddl + "`\n\n"
        create_ddl += "- `CREATE INDEX \"{1}_index\" ON \"{0}\".\"{1}\" (\"{2}\" DESC)`".format(schema_name, table_name, record_timestamp)

    if partition_column is not None:
        alter_ddl = __alter_table_ddl(schema_name, table_name, create_ddl, partition_column)
        display(Markdown(alter_ddl))
    else:
        display(Markdown(create_ddl))

def generate_payload_table_ddl(
        common_config_data,
        schema_name: str,
        table_prefix: str = "payload",
        table_suffix: str = None,
        max_length_categories: dict = {},
        create_index: bool = True,
        partition_column: str = None):
    """Generates Create DDL statement for Payload Table of an IBM Watson OpenScale batch subscription.

    Arguments:
        common_config_data {dict} -- Common Configuration JSON
        schema_name {str} -- Schema Name where the table is to be created.

    Keyword Arguments:
        table_prefix {str} -- Prefix for this table name (default: {"payload"})
        table_suffix {str} -- Suffix for this table name. Defaults to a random UUID.
        max_length_categories {dict} -- Dictionary with Categorical Columns as keys, and maximum length of categories as values (default: {{}})
        create_index {bool} -- Flag to control whether an index is created on record-timestamp column. (default: {True})
        partition_column {str} -- Partition Column for this table (default: {None})

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

    create_ddl = __generate_table_ddl(
        ddl_fields,
        table_name,
        schema_name,
        max_length_categories,
        partition_column=partition_column)

    if create_index and (record_timestamp is not None):
        create_ddl = "- `" + create_ddl + "`\n\n"
        create_ddl += "- `CREATE INDEX \"{1}_index\" ON \"{0}\".\"{1}\" (\"{2}\" DESC)`".format(schema_name, table_name, record_timestamp)

    if partition_column is not None:
        alter_ddl = __alter_table_ddl(schema_name, table_name, create_ddl, partition_column)
        display(Markdown(alter_ddl))
    else:
        display(Markdown(create_ddl))

def generate_drift_table_ddl(
        drift_archive: bytearray,
        schema_name: str,
        table_prefix: str = "drifted_transactions",
        table_suffix: str = None,
        partition_column: str = None):
    """Generates Create DDL statement for Drifted Transactions Table of an IBM Watson OpenScale batch subscription.

    Arguments:
        drift_archive {bytearray} -- Drift Archive
        schema_name {str} -- Schema Name where the table is to be created.

    Keyword Arguments:
        table_prefix {str} -- Prefix for this table name (default: {"drifted_transactions"})
        table_suffix {str} -- Suffix for this table name. Defaults to a random UUID.
        partition_column {str} -- Partition Column for this table (default: {None})

    Returns:
        str -- Create DDL statement for Drifted Transactions Table
    """

    table_suffix = table_suffix or str(uuid.uuid4())
    table_name = __generate_table_name(table_prefix, table_suffix)

    table_schema = {}
    with tempfile.NamedTemporaryFile() as tmp_file:
        tmp_file.write(drift_archive)
        tmp_file.flush()
        with tarfile.open(tmp_file.name, "r:gz") as tf:
            with tf.extractfile("drifted_transactions_schema.json") as json_data:
                table_schema = json.load(json_data)
    
    create_ddl = __generate_table_ddl_from_schema(schema_name, table_name, table_schema, primary_key_cols=["scoring_id", "run_id"], partition_column=partition_column)
    create_ddl = "- `" + create_ddl + "`\n\n"
    create_ddl += "\n"
    create_ddl += "- `CREATE INDEX \"{1}_index\" ON \"{0}\".\"{1}\" (\"run_id\", \"is_model_drift\", \"is_data_drift\")`".format(schema_name, table_name)

    if partition_column is not None:
        alter_ddl = __alter_table_ddl(schema_name, table_name, create_ddl, partition_column)
        display(Markdown(alter_ddl))
    else:
        display(Markdown(create_ddl))

def generate_explanations_table_ddl(
        schema_name: str,
        table_prefix: str = "explanations",
        table_suffix: str = None,
        partition_column: str = None):
    """Generates Create DDL statement for Explanations Table of an IBM Watson OpenScale batch subscription.

    Arguments:
        schema_name {str} -- Schema Name where the table is to be created.

    Keyword Arguments:
        table_prefix {str} -- Prefix for this table name (default: {"explanations"})
        table_suffix {str} -- Suffix for this table name. Defaults to a random UUID.
        partition_column {str} -- Partition Column for this table (default: {None})

    Returns:
        str -- Create DDL statement for Explanations Table
    """

    table_suffix = table_suffix or str(uuid.uuid4())
    table_name = __generate_table_name(table_prefix, table_suffix)
    
    table_schema = {}
    
    current_dir = str(pathlib.Path(__file__).parent.absolute())
    with open(current_dir + "/explanations_table.json", "r") as fp:
        table_schema = json.load(fp)
    
    create_ddl = __generate_table_ddl_from_schema(schema_name, table_name, table_schema, partition_column=partition_column)
    create_ddl = "- `" + create_ddl + "`\n\n"
    create_ddl += "\n"
    create_ddl += "- `CREATE INDEX \"{1}_index\" ON \"{0}\".\"{1}\" (\"subscription_id\", \"request_id\", \"scoring_id\", \"finished_at\" DESC)`".format(schema_name, table_name)

    if partition_column is not None:
        alter_ddl = __alter_table_ddl(schema_name, table_name, create_ddl, partition_column)
        display(Markdown(alter_ddl))
    else:
        display(Markdown(create_ddl))
