# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2025
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------


import sys
import pandas as pd

from ibm_wos_utils.common.clients.data_set_client import DataSetsClient
from ibm_wos_utils.common.utils.python_utils import get
from ibm_wos_utils.common.utils.common_logger import CommonLogger
from ibm_wos_utils.common.readers.training_data_reader import TrainingDataReader

logger = CommonLogger(__name__)


class DataSetReader(TrainingDataReader):
    def __init__(
        self, service_instance_id, access_token, subscription_id=None, dataset_id=None
    ):
        self.service_instance_id = service_instance_id
        self.access_token = access_token
        self.subscription_id = subscription_id
        self.client = DataSetsClient(self.service_instance_id, self.access_token)
        self.training_dataset_id = dataset_id or self.__get_training_dataset_id()

    def __get_training_dataset_id(self):
        dataset_details = self.client.get_data_set(
            self.subscription_id, data_set_type="training"
        )
        return get(dataset_details, "metadata.id")

    def get_input_data(self, max_row=None):
        limit = 1000
        offset = 0
        training_df = pd.DataFrame()
        column_names = []
        column_values = []

        while True:
            if max_row:
                remaining_rows = max_row - offset
                if remaining_rows <= 0:
                    break
                limit = min(1000, remaining_rows)
            training_record_details = self.client.get_records(
                self.training_dataset_id, limit=limit, offset=offset, format_type="list"
            )
            if not training_record_details.get("records"):
                break
            training_records = training_record_details.get("records")[0]
            training_records_count = len(training_records["values"])

            if not column_names:
                column_names = training_records["fields"]
                logger.log_debug(
                    "Columns in training data read from dataset:{}.".format(
                        column_names
                    )
                )
            for val in training_records["values"]:
                column_values.append(val)
            offset += training_records_count
            logger.log_debug("offset:{}".format(offset))

        # Convert record values to training data frame
        training_df = pd.DataFrame(column_values, columns=column_names)
        logger.log_debug(
            "Shape of the training data frame from dataset:{}.".format(
                training_df.shape
            )
        )
        return training_df, None

    def get_input_data_size(self):
        training_record_details = self.client.get_records(
            self.training_dataset_id,
            limit=100,
            offset=0,
            include_total_count=True,
            format_type="list",
        )

        total_count = get(training_record_details, "total_count")
        if not total_count:
            return 0

        if not training_record_details.get("records"):
            return 0

        training_records = training_record_details.get("records")[0]
        column_names = training_records["fields"]
        column_values = []
        for val in training_records["values"]:
            column_values.append(val)

        chunk_df = pd.DataFrame(column_values, columns=column_names)
        chunk_size = sys.getsizeof(chunk_df)
        chunk_average_size = chunk_size / len(chunk_df)

        return total_count * chunk_average_size
