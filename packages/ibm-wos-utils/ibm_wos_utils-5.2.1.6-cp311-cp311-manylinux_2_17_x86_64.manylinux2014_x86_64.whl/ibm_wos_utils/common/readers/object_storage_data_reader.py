# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2025
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

import io
import logging
import ibm_boto3
import pandas as pd

from ibm_botocore.client import Config
from ibm_botocore.exceptions import ClientError

from ibm_wos_utils.common.utils.date_util import DateUtil
from ibm_wos_utils.common.utils.common_logger import CommonLogger
from ibm_wos_utils.common.utils.python_utils import get
from ibm_wos_utils.common.readers.training_data_reader import TrainingDataReader

logger = CommonLogger(__name__)
# Suppress info and warning logs from the libraries
logging.getLogger("ibm_boto3").setLevel(logging.CRITICAL)
logging.getLogger("ibm_botocore").setLevel(logging.CRITICAL)


class ObjectStorageDataReader(TrainingDataReader):
    def __init__(self, params):
        self.params = params
        self.client = self.initialize()

    def initialize(self):
        raise NotImplementedError("Subclasses must implement this method.")

    def get_input_data(
        self,
        categorical_cols,
        label_col,
        prediction_column,
        output_data_schema,
        max_row=None,
        random_sample=False,
    ):
        """
        Fetches the input data from the storages and returns it as a pandas DataFrame.
        """
        logger.log_debug("Reading input training data from object storage.")

        start_time = DateUtil.current_milli_time()
        bucket_name = self.params.get("training_data_bucket")
        file_name = self.params.get("training_data_file_name")
        size_to_read = 500 * 1024**2
        size_limit_exceeded = False

        try:
            obj = self.client.Object(bucket_name, file_name).get()
            content_length = obj.get("ContentLength", 0)
            read_size = min(size_to_read, content_length)
            dtype_dict = (
                {col: "object" for col in categorical_cols} if categorical_cols else {}
            )
            if prediction_column:
                prediction_datatype = next(
                    (
                        get(field, "type")
                        for field in get(output_data_schema, "fields")
                        if get(field, "name") == prediction_column
                    ),
                    None,
                )

                if prediction_datatype in {"string", "varchar"}:
                    dtype_dict[label_col] = "object"

            logger.log_info(
                f"Reading {read_size / (1024**2):.2f} MB of data from COS")

            bytes_data = io.BytesIO(obj["Body"].read(read_size))
            n_rows = max_row if max_row and not random_sample else None
            # if sep is None, python engine can detect the separator internally which c based engine cannot do
            # so setting sep to None and using python engine will add support for tab separated files as well.
            input_data_df = pd.read_csv(
                bytes_data,
                sep=None,
                encoding="utf-8-sig",
                dtype=dtype_dict,
                nrows=n_rows,
            )

            # if size read is greater 500mb then remove the last row; it could possibly be truncated
            if read_size < content_length:
                input_data_df.drop(input_data_df.tail(1).index, inplace=True)
                size_limit_exceeded = True

            # apply random sampling if required
            if random_sample and max_row:
                input_data_df = input_data_df.sample(
                    n=min(max_row, len(input_data_df)), random_state=43
                )

        except UnicodeDecodeError:
            self._handle_unicode_error()
        except ClientError as ce:
            self._handle_client_error(ce, file_name, bucket_name)

        logger.log_debug(
            "Completed reading training data from Object Storage.",
            start_time=start_time,
        )
        return input_data_df, size_limit_exceeded

    def get_input_data_size(self):
        """
        Get the size of the input data.
        """
        bucket_name = self.params.get("training_data_bucket")
        file_name = self.params.get("training_data_file_name")

        try:
            obj = self.client.Object(bucket_name, file_name).get()
            return obj["ContentLength"], obj["ContentType"]
        except UnicodeDecodeError:
            self._handle_unicode_error()
        except ClientError as ce:
            self._handle_client_error(ce, file_name, bucket_name)

    def _handle_client_error(self, error, file_name, bucket_name):
        """Handle errors encountered when interacting with object storage."""
        logger.log_error(
            "There was a problem retrieving the file {} in bucket {} from AWS S3. Reason: {}".format(
                file_name, bucket_name, error.response
            )
        )
        if (
            error.response.get("Error")
            and error.response.get("Error").get("Code")
            and error.response.get("Error").get("Code") == "NoSuchKey"
        ):
            raise Exception(
                f"One of the {file_name} file or the {bucket_name} bucket specified in subscription do not exist."
            )
        else:
            raise Exception(
                f"Unable to read the {file_name} training data file in the {bucket_name} COS bucket."
            )

    def _handle_unicode_error(self):
        logger.log_exception(
            "The File supplied as input training data reference is not UTF-8 encoded.",
            exc_info=True,
        )
        raise Exception(
            "The file supplied as input training data reference is not UTF-8 encoded."
        )


class S3DataReader(ObjectStorageDataReader):
    def initialize(self):
        """Initialize the S3 client."""
        return ibm_boto3.resource(
            "s3",
            aws_access_key_id=self.params.get(
                "training_data_access_key_id"),
            aws_secret_access_key=self.params.get(
                "training_data_secret_access_key"
            ),
            region_name=self.params.get("region_name"),
        )


class CosDataReader(ObjectStorageDataReader):
    def initialize(self):
        """Initialize the COS client."""
        return ibm_boto3.resource(
            "s3",
            ibm_api_key_id=self.params.get("training_data_api_key"),
            ibm_service_instance_id=self.params.get(
                "training_data_resource_instance_id"
            ),
            ibm_auth_endpoint=self.params.get("training_data_auth_endpoint"),
            config=Config(signature_version="oauth"),
            endpoint_url=self.params.get("training_data_service_endpoint"),
        )
