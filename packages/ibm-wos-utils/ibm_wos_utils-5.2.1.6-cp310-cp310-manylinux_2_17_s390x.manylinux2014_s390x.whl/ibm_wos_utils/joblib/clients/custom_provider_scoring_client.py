# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2019, 2021
# The source code for this program is not published or otherwise divested of its trade
# secrets, irrespective of what has been deposited with the U.S. Copyright Office.
# ----------------------------------------------------------------------------------------------------

import pandas as pd

try:
    from pyspark.sql import DataFrame, Row
except ImportError as ie:
    pass
from ibm_wos_utils.joblib.clients.token_client import TokenClient
from ibm_wos_utils.joblib.exceptions.client_errors import DependentServiceError, InvalidInputError
from ibm_wos_utils.joblib.utils.date_util import DateUtil
from ibm_wos_utils.joblib.utils.joblib_utils import JoblibUtils
from ibm_wos_utils.joblib.utils.rest_util import RestUtil

"""
Utility class for Scoring the Custom ML provider deployment using REST API.
"""

HEADER_CONTENT_TYPE = "Content-Type"
HEADER_VALUE_APPLJSON = "application/json"
HEADER_ACCEPT = "Accept"
HEADER_VALUE_APPLJSONCHARSETUTF8 = "application/json;charset=utf-8"
HEADER_AUTHORIZATION = "Authorization"
HEADER_CACHE_CONTROL = "Cache-Control"
HEADER_VALUE_NO_CACHE = "no-cache"

class CustomProviderScoringClient():

    def __init__(self, subscription: dict, scoring_url: str, auth_url: str, username: str, api_key: str=None, password: str=None, iam_enabled: bool=False, bedrock_url: str=None, score_in_pages: bool=True, page_size: int=1000):
        """
        The constructor for the class. Initialises the variables needed for scoring.
        :subscription: The subscription object.
        :scoring_url: The scoring URL to be used.
        :auth_url: The authorisation URL for generating the token.
        :username: The username for generating the token.
        :api_key: The API key for generating the token. [Optional. One of api_key, password is compulsory.]
        :password: The password for generating the token. [Optional. One of api_key, password is compulsory.]
        :iam_enabled: The boolean flag indicating whether the CPD environment is IAM integration enabled or not. [Optional. Default: False.]
        :bedrock_url: The bedrock URL for generating the bedrock token for CPD environments where IAM integration is enabled. [Optional. Default: None.]
        :score_in_pages: Boolean flag to enable scoring in pages. [Optional. Default: true]
        :page_size: The size of the page in the number of rows. [Optional. Default: 1000]
        """
        self.subscription = subscription
        self.scoring_url = scoring_url
        self.auth_url = auth_url
        self.username = username
        if api_key is None and password is None:
            raise InvalidInputError("One of API key or password is required for scoring.")
        self.api_key = api_key
        self.password = password
        self.iam_enabled = iam_enabled
        self.bedrock_url = bedrock_url
        self.score_in_pages = score_in_pages
        self.page_size = page_size
        self.token = self._generate_token()

    def score(self, index, data: DataFrame):
        """
        Method to perform the scoring via the REST call using the given token and deployment.
        :index: Index passed as part of `mapPartitionsWithIndex` call as UDF.
        :data: The data frame containing data to be scored.        

        :returns: The predictions received via the scoring URL.

        Example: To be used as follows:
            ```
            predictions_df = scoring_df.rdd.mapPartitionsWithIndex(custom_provider_scoring_client.score).toDF(scoring_output_schema)
            ```
            where scoring_df is the `data` that needs to be scored,
            custom_provider_scoring_client is the object of this class,
            scoring_output_schema is the `StructType` for the scoring output schema
        """
        import pandas as pd
        from ibm_wos_utils.joblib.utils.joblib_utils import JoblibUtils

        # Converting to pandas data frame
        input_data_schema = self.subscription["entity"]["asset_properties"]["input_data_schema"]
        input_columns = JoblibUtils.get_columns_with_modeling_role(input_data_schema, "feature")
        meta_columns = JoblibUtils.get_columns_with_modeling_role(input_data_schema, "meta-field")
        input_columns.extend(meta_columns)
        pd_df = pd.DataFrame(
            data,
            columns=input_columns
        )
        num_records = len(pd_df)
        offset = 0

        while offset < num_records:
            # Taking a page for scoring
            page_df = pd_df[offset: offset + self.page_size]
            offset += self.page_size

            # Getting the scoring payload
            page_scoring_payload = self._get_payload(page_df, input_data_schema)

            # Scoring the page
            page_predictions = self._make_rest_call(
                url=self.scoring_url,
                payload=page_scoring_payload
            )
            page_pred_df = pd.DataFrame(
                page_predictions["predictions"][0]["values"],
                columns=page_predictions["predictions"][0]["fields"]
            )
            # Taking only prediction and probability columns from scored response (https://github.ibm.com/aiopenscale/tracker/issues/26653#issuecomment-46010277)
            output_data_schema = self.subscription["entity"]["asset_properties"]["output_data_schema"]
            prediction_column = JoblibUtils.get_column_by_modeling_role(output_data_schema, "prediction")
            probability_column = JoblibUtils.get_column_by_modeling_role(output_data_schema, "probability")
            output_columns = input_columns
            output_columns.append(prediction_column)
            if probability_column is not None:
                output_columns.append(probability_column)
            page_pred_df = page_pred_df[output_columns]

            page_pred_df = page_pred_df.apply(lambda row: Row(**row.to_dict()), axis=1)

            for _, element in page_pred_df.items():
                yield element

    def _generate_token(self) -> None:
        """
        Generates and sets the token as object variable with the API key and the authorisation URL set in the object.

        :returns: None.
        """

        if self.api_key is not None:
            # Generating token using API key
            token = TokenClient.get_iam_token_with_apikey(
                server_url=self.auth_url,
                username=self.username,
                apikey=self.api_key
            )
        else:
            # Generating token using the password
            token = TokenClient.get_iam_token(
                server_url=self.auth_url,
                username=self.username,
                password=self.password,
                iam_enabled=self.iam_enabled,
                bedrock_url=self.bedrock_url
            )
        
        # Setting the token to the object-level variable
        self.iam_token = token
        
        return

    # Build the payload
    def _get_payload(self, payload_df: pd.DataFrame, input_data_schema: dict) -> dict:
        """
        Generates and returns the scoring payload (dict) from the given data frame.
        :payload_df: The data frame containing data to be scored.
        :input_data_schema: The input data schema to figure out the feature and meta fields.

        :returns: The scoring payload.
        """
        scoring_payload = None

        # Getting the feature fields
        feature_fields = JoblibUtils.get_columns_with_modeling_role(input_data_schema, "feature")
        input_df = payload_df[feature_fields]

        scoring_payload = {
            "input_data": [
                {
                    "fields": input_df.columns.tolist(),
                    "values": input_df.values.tolist()
                }
            ]
        }

        # Getting the meta fields
        meta_fields = JoblibUtils.get_columns_with_modeling_role(input_data_schema, "meta-field")

        if len(meta_fields) > 0:
            # Meta fields are present
            meta_df = payload_df[meta_fields]
            scoring_payload["input_data"][0]["meta"] = {
                "fields": meta_df.columns.tolist(),
                "values": meta_df.values.tolist()
            }

        return scoring_payload

    def _get_headers(self) -> dict:
        """
        Generates the headers to be sent for the REST call to the scoring URL.
        :token: The token to be used for authorisation.

        :returns: The headers in a dictionary.
        """
        headers = {}
        
        headers[HEADER_CONTENT_TYPE] = HEADER_VALUE_APPLJSON
        headers[HEADER_ACCEPT] = HEADER_VALUE_APPLJSONCHARSETUTF8
        # Generating the token
        self._generate_token()
        headers[HEADER_AUTHORIZATION] = "Bearer {}".format(self.iam_token)
        headers[HEADER_CACHE_CONTROL] = HEADER_VALUE_NO_CACHE

        return headers
    
    def _make_rest_call(self, url: str, payload: dict, http_method: str="POST") -> dict:
        """
        Makes the REST call to the given URL with the given payload and headers.
        :url: The URL to which the call is to be made.
        :payload: The request body payload.
        :http_method: The HTTP method to be used.

        :returns: The REST response received from the API.
        """
        response_dict = None

        # Getting the headers
        headers = self._get_headers()

        # Making the REST call
        response = RestUtil.request_with_retry(
            method_list=[http_method],
            retry_count=5,
            back_off_factor=10
        ).post(
            url=url,
            json=payload,
            headers=headers,
            timeout=(150, 150),
            verify=False
        )

        if not response.ok:
            raise DependentServiceError("Scoring failed with error: {}".format(response.text), response)
        
        response_dict = response.json()

        return response_dict