# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2023
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S. Copyright Office.
# ----------------------------------------------------------------------------------------------------

from ibm_wos_utils.data_health.batch.utils.constants import Metrics
from ibm_wos_utils.fairness.batch.utils.batch_utils import BatchUtils as FairnessBatchUtils
from ibm_wos_utils.fairness.batch.utils.python_util import get


class BatchUtils:
    """
    Class for utility methods for `data_health`.
    """

    @classmethod
    def get_all_names_from_schema(cls, schema: dict) -> list:
        """
        Gets all the column names from the given schema.
        :schema: The schema object.

        :returns: The list of column names in the schema.
        """
        columns = list()

        schema_fields = get(schema, "fields", default=[])
        for field in schema_fields:
            field_name = get(field, "name")
            if field_name is not None and isinstance(field_name, str):
                columns.append(field_name)

        return columns
    
    @classmethod
    def get_feedback_table_columns(cls, subscription: dict) -> list:
        """
        Gets all the columns present in the feedback table for the given batch subscription.
        :subscription: The subscription object.

        :returns: The list of columns present in the feedback table.
        """
        feedback_columns = list()
        
        # Getting the columns with modeling role and `deleted` not set to `true` from output data schema
        output_data_schema = get(subscription, "entity.asset_properties.output_data_schema")
        for field in output_data_schema["fields"]:
            field_name = get(field, "name")
            field_modeling_role = get(field, "metadata.modeling_role")
            is_deleted_field = get(field, "metadata.deleted", default=False)
            if field_modeling_role is not None and not is_deleted_field:
                feedback_columns.append(field_name)
        
        # Getting the label column from training data schema
        training_data_schema = get(subscription, "entity.asset_properties.training_data_schema")
        label_column = FairnessBatchUtils.get_name_with_modeling_role("target", training_data_schema)
        if label_column is not None:
            feedback_columns.append(label_column)

        return feedback_columns
    
    @classmethod
    def initialize_metric_values(cls, metrics: list) -> dict:
        """
        Generates initial metrics object to be stored in ETCD with empty values.
        :metrics: The list of metrics to be initialized.

        :returns: The metric_values object initialized with 0 values.
        """
        metric_values = {
            "metrics": {},
            "summary": {
                "payload": {
                    "total_count": 0
                },
                "feedback": {
                    "total_count": 0
                }
            }
        }

        for metric in metrics:
            if metric == Metrics.ABSENCE_COUNT.value:
                metric_values["metrics"][metric] = {
                    "payload": {},
                    "feedback": {}
                }
            elif metric == Metrics.EMPTY_STRINGS.value:
                metric_values["metrics"][metric] = {
                    "payload": {},
                    "feedback": {}
                }
            elif metric == Metrics.CLASS_CONFUSION.value:
                metric_values["metrics"][metric] = {
                    "payload": {}
                }
            elif metric == Metrics.DUPLICATE_ROWS.value:
                metric_values["metrics"][metric] = {
                    "payload": 0,
                    "feedback": 0
                }
            elif metric == Metrics.UNIQUE_COLUMNS.value:
                metric_values["metrics"][metric] = {
                    "payload": {},
                    "feedback": {}
                }

        return metric_values
    
    @classmethod
    def get_table_details(cls, tables: list, table_type: str) -> dict:
        """
        Gets the table details for the given table type from the tables sent as Spark job arguments.
        :tables: The list of table details.
        :table_type: The type of the table [payload/feedback].

        :returns: The table details.
        """
        table_details = None

        for table in tables:
            if table["type"] == table_type:
                table_details = table
                break

        return table_details