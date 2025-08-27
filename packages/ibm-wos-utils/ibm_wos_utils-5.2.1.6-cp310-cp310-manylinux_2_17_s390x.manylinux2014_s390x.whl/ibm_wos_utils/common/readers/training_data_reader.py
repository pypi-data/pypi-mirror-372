# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2025
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

import pandas as pd

from typing import Optional, Tuple

from ibm_wos_utils.common.utils.reader_util import TrainingDataSourceType
from ibm_wos_utils.common.utils.python_utils import get
from ibm_wos_utils.joblib.utils.environment import Environment


class TrainingDataReader(object):

    @staticmethod
    def get_input_data(
        training_data_ref: dict,
        service_instance_id: Optional[str] = None,
        subscription_id: Optional[str] = None,
        categorical_cols: Optional[list] = None,
        label_col: Optional[str] = None,
        prediction_column: Optional[str] = None,
        output_data_schema: Optional[dict] = None,
        access_token: Optional[str] = None,
        max_row: Optional[int] = None,
        random_sample: Optional[bool] = False,
        retry_non_ssl: Optional[bool] = False,
    ) -> Tuple[pd.DataFrame, Optional[bool]]:
        """
        Invoke appropriate data readers based on the data source:

        1. **COS and S3 Data Reader**
        Method: `get_input_data`
        Parameters:
        - `training_data_ref`: Training data connection details
        - `categorical_cols`: List of categorical columns.
        - `label_col`: Label column name.
        - `prediction_column`: Prediction column.
        - `output_data_schema`: Output data schema.
        - `max_row` (Optional): Maximum number of rows to read.
        - `random_sample` (Optional): Flag to randomly sample data.

        2. **DB2 and Postgres Data Reader**
        Method: `get_input_data`
        Parameters:
        - `training_data_ref`: Training data connection details
        - `max_row` (Optional): Maximum number of rows to read.
        - `random_sample` (Optional): Flag to randomly sample data.

        3. **Dataset Reader**
        Method: `get_input_data`
        Parameters:
        - `training_data_ref`: Training data connection details
        - `service_instance_id`: ID of the service instance.
        - `access_token`: Service specific access token
        - `subscription_id` (Optional): Subscription ID if `training_data_ref` doesn't contain `dataset_id`
        """

        training_data_source = training_data_ref.get("type")
        if not training_data_source:
            raise Exception("Training data source is missing.")

        if training_data_source == TrainingDataSourceType.COS.value:
            from ibm_wos_utils.common.readers.object_storage_data_reader import (
                CosDataReader,
            )

            return CosDataReader(
                TrainingDataReader.get_cos_params(training_data_ref)
            ).get_input_data(
                categorical_cols,
                label_col,
                prediction_column,
                output_data_schema,
                max_row,
                random_sample,
            )
        elif training_data_source == TrainingDataSourceType.S3.value:
            from ibm_wos_utils.common.readers.object_storage_data_reader import (
                S3DataReader,
            )

            return S3DataReader(
                TrainingDataReader.get_s3_params(training_data_ref)
            ).get_input_data(
                categorical_cols,
                label_col,
                prediction_column,
                output_data_schema,
                max_row,
                random_sample,
            )
        elif training_data_source == TrainingDataSourceType.DB2.value:
            from ibm_wos_utils.common.readers.db_data_reader import Db2DataReader

            return Db2DataReader(
                TrainingDataReader.get_db2_params(
                    training_data_ref), retry_non_ssl
            ).get_input_data(
                max_row,
                random_sample,
            )
        elif training_data_source == TrainingDataSourceType.DATASET.value:
            from ibm_wos_utils.common.readers.data_set_reader import DataSetReader

            return DataSetReader(
                service_instance_id=service_instance_id,
                access_token=access_token,
                subscription_id=subscription_id,
                dataset_id=TrainingDataReader.get_dataset_params(
                    training_data_ref),
            ).get_input_data(max_row)
        elif training_data_source == TrainingDataSourceType.POSTGRES.value:
            from ibm_wos_utils.common.readers.db_data_reader import PostgresDataReader

            return PostgresDataReader(
                TrainingDataReader.get_postgres_params(training_data_ref)
            ).get_input_data(
                max_row,
                random_sample,
            )
        raise Exception("Invalid training data reference.")

    @staticmethod
    def get_cos_params(training_data_ref: dict) -> dict:
        params = {}
        params["training_data_api_key"] = get(
            training_data_ref, "connection.api_key")
        params["training_data_resource_instance_id"] = get(
            training_data_ref, "connection.resource_instance_id"
        )
        params["training_data_service_endpoint"] = get(
            training_data_ref, "connection.url"
        )
        params["training_data_auth_endpoint"] = get(
            training_data_ref, "connection.iam_url"
        )
        params["training_data_bucket"] = get(
            training_data_ref, "location.bucket")
        params["training_data_file_name"] = get(
            training_data_ref, "location.file_name")

        missing_values = []
        for key in params.keys():
            if not params.get(key):
                missing_values.append(key[len("training_data_"):])

        if len(missing_values):
            raise Exception(
                "The {0} required parameter value to fetch input data from {1} is missing.".format(
                    ",".join(missing_values), TrainingDataSourceType.COS.value
                )
            )
        return params

    @staticmethod
    def get_db2_params(training_data_ref: dict) -> dict:
        params = {}
        params["training_data_db_name"] = get(
            training_data_ref, "connection.database_name"
        )
        port = get(training_data_ref, "connection.port")
        if port:
            params["training_data_db_port"] = port
        else:
            # if port is not user provided,
            # use the default SSL port for BM DashDB on Cloud
            # default non SSL port for DB2 on ICP
            if Environment.is_cpd():
                params["training_data_db_port"] = 50000
            else:
                params["training_data_db_port"] = 50001
        params["training_data_db_host"] = get(
            training_data_ref, "connection.hostname")
        params["training_data_db_username"] = get(
            training_data_ref, "connection.username"
        )
        params["training_data_db_password"] = get(
            training_data_ref, "connection.password"
        )
        params["ssl"] = get(training_data_ref, "connection.ssl")
        params["certificate_base64"] = get(
            training_data_ref, "connection.certificate_base64"
        )
        params["training_data_db_tablename"] = get(
            training_data_ref, "location.table_name"
        )
        params["training_data_db_schemaname"] = get(
            training_data_ref, "location.schema_name"
        )

        missing_values = []
        for key in params.keys():
            if key.startswith("training_data_db_") and not params.get(key):
                missing_values.append(key[len("training_data_db_"):])

        if len(missing_values):
            raise Exception(
                "The {0} required parameter value to fetch input data from {1} is missing.".format(
                    ",".join(missing_values), TrainingDataSourceType.DB2.value
                )
            )
        return params

    @staticmethod
    def get_postgres_params(training_data_ref: dict) -> dict:
        params = {}
        params["training_data_db_name"] = get(
            training_data_ref, "connection.database_name"
        )
        params["training_data_db_port"] = get(
            training_data_ref, "connection.port", 5432
        )
        params["training_data_db_host"] = get(
            training_data_ref, "connection.hostname")
        params["training_data_db_username"] = get(
            training_data_ref, "connection.username"
        )
        params["training_data_db_password"] = get(
            training_data_ref, "connection.password"
        )
        params["ssl_mode"] = get(
            training_data_ref, "connection.ssl_mode", "require")
        params["certificate_base64"] = get(
            training_data_ref, "connection.certificate_base64"
        )
        params["training_data_db_schemaname"] = get(
            training_data_ref, "location.schema_name"
        )
        params["training_data_db_tablename"] = get(
            training_data_ref, "location.table_name"
        )

        # Check for missing required parameters
        missing_values = []
        for key in params.keys():
            if key.startswith("training_data_db_") and not params.get(key):
                missing_values.append(key[len("training_data_db_"):])

        if len(missing_values):
            raise Exception(
                "The {0} required parameter value to fetch input data from {1} is missing.".format(
                    ",".join(
                        missing_values), TrainingDataSourceType.POSTGRES.value
                )
            )
        return params

    @staticmethod
    def get_s3_params(training_data_ref: dict) -> dict:
        params = {}
        params["training_data_access_key_id"] = get(
            training_data_ref, "connection.access_key_id"
        )
        params["training_data_secret_access_key"] = get(
            training_data_ref, "connection.secret_access_key"
        )
        params["region_name"] = get(
            training_data_ref, "connection.region_name"
        )
        params["training_data_bucket"] = get(
            training_data_ref, "location.bucket")
        params["training_data_file_name"] = get(
            training_data_ref, "location.file_name")
        missing_values = []
        for key in params.keys():
            if key.startswith("training_data_") and not params.get(key):
                missing_values.append(key[len("training_data_"):])

        if len(missing_values):
            raise Exception(
                "The {0} required parameter value to fetch input data from {1} is missing.".format(
                    ",".join(missing_values), TrainingDataSourceType.S3.value
                )
            )
        return params

    @staticmethod
    def get_dataset_params(training_data_ref: dict) -> dict:
        return get(training_data_ref, "location.dataset_id")
