# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# © Copyright IBM Corp. 2022,2024  All Rights Reserved.
# US Government Users Restricted Rights -Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------

from ibm_common_scoring_utils.clients.service_provider import ServiceProvider
from ibm_common_scoring_utils.common.configuration import Configuration
from ibm_common_scoring_utils.utils.auth_utils import get_cp4d_impersonated_token, get_cp4d_jwt_token, get_iam_token
from ibm_common_scoring_utils.utils.constants import AuthProvider, get_auth_providers, ExecutionType
from ibm_common_scoring_utils.utils.python_utils import convert_df_to_list, get
from ibm_common_scoring_utils.utils.rest_util import RestUtil
from ibm_common_scoring_utils.utils.data_time_util import DateTimeUtil
from ibm_common_scoring_utils.utils.wml_fm_utils import score_fmaas, get_input_prompt, get_input_string, get_prompt_string
from ibm_common_scoring_utils.core.executors.asyncio_executor import AsyncIOExecutor
from ibm_common_scoring_utils.utils.wml_fm_utils import ScoringTask

import pandas as pd
import asyncio


class WMLProvider(ServiceProvider):
    def __init__(self, config: Configuration):
        super().__init__(config)

        # Validate additional properties in configuration specific to WML scoring
        self.validate_configuration()

    def get_headers(self, token=None):
        """
            Get headers for WML
        """
        # Check if the token is supplied from config :
        token = self.credentials.wml_token
        if token is None:
            if self.credentials.wml_location in [AuthProvider.CLOUD.value, AuthProvider.CLOUD_REMOTE.value]:
                # Cloud
                token = get_iam_token(
                    self.credentials.apikey, auth_url=self.credentials.auth_url)
            else:
                # CPD case
                if self.credentials.wml_location == AuthProvider.CPD_LOCAL.value:
                    token = get_cp4d_impersonated_token(host=self.credentials.url,
                                                        uid=self.credentials.uid,
                                                        zen_service_broker_secret=self.credentials.zen_service_broker_secret,
                                                        username=self.credentials.username)
                else:
                    token = get_cp4d_jwt_token(
                        self.credentials.url, username=self.credentials.username, apikey=self.credentials.apikey)

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        # Update existing headers with configuration.headers
        headers.update(self.credentials.headers)

        return headers

    def __get_scoring_url(self):
        """
            Method to add version query parameter if it does not exist 
        """
        if self.config.scoring_url.find("?version=") != -1:
            return self.config.scoring_url
        else:
            # Add version param with a dummy value
            return self.config.scoring_url.strip() + "?version=2022-09-22"

    def score(self, df, **kwargs) -> pd.DataFrame:
        """
            Method to score WML deployments
        """
        if self.config.is_foundation_model:
            execution_type = kwargs.get(
                "execution_type") or ExecutionType.ASYNC.value
            return self.score_fm(df, execution_type)
        else:
            return self.score_tm(df)

    def score_tm(self, df: pd.DataFrame):
        """
            Score WML deployment for traditional online models
        """
        try:
            scoring_payload = self.convert_df_to_request(df)
            start_time = DateTimeUtil.current_milli_time()
            scoring_url = self.__get_scoring_url()

            # Note 520,522 are the status codes for connection time out , we can extend the list if needed
            response = RestUtil.request(additional_retry_status_codes=[520, 521, 522, 523, 524]).post(
                url=scoring_url,
                headers=self.get_headers(),
                json=scoring_payload, verify=False
            )

            self.logger.log_debug(
                f"Time taken to score wml deployment {DateTimeUtil.current_milli_time()-start_time}ms")

            if (not response.ok):
                raise Exception(
                    f"Error while scoring WML deployment with url {scoring_url}.Error code:{response.status_code}.Reason:{response.text}")

            return self.convert_response_to_df(response.json())
        except Exception as ex:
            msg = f"Error while scoring WML .Reason:{str(ex)}"
            self.logger.log_error(msg)
            raise Exception(msg)

    def validate_credentials(self):
        """
            Validate WML credentials existence
            For cloud :
            {
                "wml_location": "cloud"/"cloud_remote",
                "apikey":"****",
                "auth_url": <optional (to work on non production env)>
            }

            For CPD with WML Remote:
            {
                "wml_location":"one of cpd_remote",
                "apikey":"****"
                "username":"admin",
                "url": "<host url>"
            }

            For CPD with WML Local:
            {
                "wml_location":"cpd_local",
                "uid":"****"
                "zen_service_borker_secret":"admin",
                "url": "<host url>"
            }
        """
        # Make wml_location as mandatory value
        if self.credentials.wml_location is None:
            raise KeyError(
                f"Missing WML location . Acceptable values are:{get_auth_providers()}")

        missing_values = []
        # api_key is need for coud , cloud_remote , cpd_remote
        if self.credentials.apikey is None and not (self.credentials.wml_location == AuthProvider.CPD_LOCAL.value):
            if self.credentials.wml_token is None:
                missing_values.append("apikey")

        if self.credentials.wml_location == AuthProvider.CPD_REMOTE.value:
            if self.credentials.username is None:
                missing_values.append("username")

            if self.credentials.url is None:
                missing_values.append("url")

        # Check for wml_location : cpd_local
        if self.credentials.wml_location == AuthProvider.CPD_LOCAL.value:
            # uid and zen_service_broker_secret has to coexist
            if self.credentials.uid == None:
                missing_values.append("uid")

            if self.credentials.zen_service_broker_secret == None:
                missing_values.append("zen_service_broker_secret")

        if len(missing_values) > 0:
            raise KeyError(
                f"Missing credentials information.Keys information:{missing_values}")

    def validate_configuration(self):
        # Additional validation only for LLM-as-a-Judge scoring
        if self.config.is_fmaas_scoring:
            missing_values = []
            model_id = get(
                self.config.prompt_template_asset_json, "prompt.model_id")
            if model_id is None:
                missing_values.append(
                    "prompt_template_asset_details.prompt.model_id")
            is_template = get(
                self.config.prompt_template_asset_json, "is_template")
            if not is_template == False and self.config.platform_url is None:
                missing_values.append("platform_url")

            if len(missing_values) > 0:
                raise KeyError(
                    f"Missing configuration information.Keys information:{missing_values}")
        return

    def convert_df_to_request(self, df: pd.DataFrame) -> dict:
        """
            Convert spark dataframe to WML request
        """
        start_time = DateTimeUtil.current_milli_time()
        fields = self.config.features
        values = convert_df_to_list(df, fields)

        scoring_payload = {"input_data": [{
            "fields": fields,
            "values": values
        }]}

        # Construct meta info
        if len(self.config.meta_fields) > 0:
            meta_fields = self.config.meta_fields
            meta_values = convert_df_to_list(df, meta_fields)
            meta_payload = {
                "fields": meta_fields,
                "values": meta_values
            }
            scoring_payload["input_data"][0]["meta"] = meta_payload

        self.logger.log_debug(
            f"Completed constructing scoring request in {DateTimeUtil.current_milli_time()-start_time}ms")
        return scoring_payload

    def convert_response_to_df(self, response: dict) -> pd.DataFrame:
        """
             Convert response to spark dataframe
        """
        start_time = DateTimeUtil.current_milli_time()
        predictions = response.get("predictions")[0]

        # Extract only prediction and probability
        fields = predictions.get("fields")
        values = predictions.get("values")

        # Considering regression and classification cases respectively
        if len(fields) in [1, 2]:
            # No need of additional extraction
            response_df = pd.DataFrame(values, columns=fields)
        else:
            # Extract only prediction and probability to avoid conversion problems
            try:
                prediction_column_index = fields.index(self.config.prediction)
                probability_column_index = fields.index(
                    self.config.probability)
            except Exception as ex:
                msg = f"Error detecting prediction/probability column index. Response field are:{fields}"
                self.logger.log_warning(msg)
                raise Exception(msg)

            response1 = [[value[prediction_column_index],
                          value[probability_column_index]]for value in values]
            response_df = pd.DataFrame(
                response1, columns=[self.config.prediction, self.config.probability])

        self.logger.log_debug(
            f"Completed converting  scoring response to datafame in {DateTimeUtil.current_milli_time()-start_time}ms")
        return response_df

    def score_fm(self, data, execution_type=ExecutionType.ASYNC.value):
        """
            Method to score the foundation model behind the scenes
        """
        try:
            if self.config.is_fmaas_scoring:
                return self.score_fm_with_pta(self.config, self.get_headers(self.credentials.wml_token), data, execution_type)
            else:
                return self.score_fm_with_deployment(self.config, self.get_headers(self.credentials.wml_token), data)
        except Exception as ex:
            msg = f"Error while scoring WML using FMaaS .Reason:{str(ex)}"
            self.logger.log_error(msg)
            raise Exception(msg)

    def score_fm_with_pta(self, config: Configuration, headers, df: pd.DataFrame, execution_type):
        """
            Method to score FMaaS using prompt template asset details. 
            This method will be deprecated once the deployment scoring endpoint for FM is available
        """
        prompt_template_asset = config.prompt_template_asset_json

        # Extract information from prompt template asset
        model_id = get(prompt_template_asset, "prompt.model_id")
        is_prompt_template = get(prompt_template_asset, "is_template", True)
        model_parameters = get(prompt_template_asset,
                               "prompt.model_parameters")
        if is_prompt_template:
            prompt_variables = get(prompt_template_asset, "prompt_variables")
            features = list(prompt_variables.keys())
            asset_id = get(prompt_template_asset, "id")
        else:
            # Case of llm-as-judge
            features = self.config.features

        # Convert dataframe to values
        rows = convert_df_to_list(df, features)

        # Set scoring url to FMaaS url - modify as per the current paths
        self.config.scoring_url = f"{self.credentials.url}/ml/v1/text/generation?version=2023-05-29"

        # Get prompt string with parameters:
        if is_prompt_template:
            try:
                # Bypass this path
                input_api_response = get_prompt_string(self.config.platform_url, asset_id, self.get_headers(
                    token=self.credentials.wml_token), project_id=self.config.project_id, space_id=self.config.space_id)
                input_string = input_api_response.get("input")
            except Exception as ex:
                self.logger.log_error(
                    f"Error getting prompt string from the API . Reason:{str(ex)}.Trying inbuilt utility function ...")
                input_string = get_input_string(prompt_template_asset)

        response_rows = []
        scoring_tasks = []
        for row in rows:
            if is_prompt_template:
                input_text = get_input_prompt(row, features, input_string)
            else:
                input_text = row[0]

            payload = {
                "model_id": model_id,
                "input": input_text
            }

            if model_parameters is not None:
                payload["parameters"] = model_parameters

            # Add project/space details
            if config.project_id:
                payload["project_id"] = config.project_id
            else:
                payload["space_id"] = config.space_id

            # Sync execution is kept as of now for testing purpose , Can you be removed later.
            if execution_type == ExecutionType.SYNC.value:
                score_response, response_time = score_fmaas(
                    self.config.scoring_url, payload, headers)

                # results
                results = get(score_response, "results")[0]
                prediction = get(results, config.prediction)
                response_row = [score_response, prediction, response_time]
                response_rows.append(response_row)
            else:
                scoring_tasks.append(ScoringTask(
                    headers, payload, self.config.scoring_url, config, self))

        # Execute in parallel for async mode
        if execution_type == ExecutionType.ASYNC.value:
            try:
                response_rows = AsyncIOExecutor.execute_http_tasks(
                    self.config.batch_size, *scoring_tasks)
            except asyncio.TimeoutError:
                raise Exception("Timeout during scoring")

        # Construct response
        response_df = pd.DataFrame(response_rows, columns=[
                                   "prompt_response", config.prediction, "response_time"])
        return response_df

    def score_fm_with_deployment(self, config: Configuration, headers, df: pd.DataFrame):
        """
            Method to score FMs using deployment scoring url using asyncio
            Args:
                config (Configuration): _description_
                headers (dict): headers to be 
                df (pd.DataFrame): _description_
        """
        # Convert dataframe to dict of feature value
        rows = df[self.config.features].to_dict(orient="records")

        if config.using_service_token:
            # Adding `IBM-WATSONXAI-CONSUMER` header
            headers["IBM-WATSONXAI-CONSUMER"] = "wos"

        response_rows = []
        scoring_tasks = []
        for row in rows:
            # Score Request sample:
            # {
            #     "parameters": {
            #         "prompt_variables": {
            #             "doc_type": "emails",
            #             "url": "https://outlook.office.com/mail/inbox/id/LWRiZDllYmM4ZU%2BO8%3D",
            #             "entity_name": "Golden Retail",
            #             "country_name": "London"
            #         },
            #         "decoding_method": "greedy",
            #         "max_new_tokens": 20,
            #         "min_new_tokens": 0,
            #         "random_seed": null,
            #         "stop_sequences": [],
            #         "temperature": 0.7,
            #         "top_k": 50,
            #         "top_p": 1,
            #         "repetition_penalty": 1
            #     }
            # }
            payload = {
                "parameters": {
                    "prompt_variables": row
                }
            }

            if self.config.enable_moderations:
                payload['moderations'] = self.__get_moderation_payload()

            # Adding the scoring task to the list
            scoring_tasks.append(ScoringTask(
                headers, payload, self.config.scoring_url, config, self))

        # Execute scoring using asyncio with a parallel batch size of 10 by default or self.config.batch_size
        try:
            response_rows = AsyncIOExecutor.execute_http_tasks(
                self.config.batch_size, *scoring_tasks)
        except asyncio.TimeoutError:
            raise Exception("Timeout during scoring")

        # Construct response
        response_df = pd.DataFrame(response_rows, columns=[
                                   "prompt_response", config.prediction, "response_time"])

        return response_df

    # Moderation settings for HAP and PII
    def __get_moderation_payload(self):
        return {
            "hap": {
                "input": {
                    "enabled": True,
                    "threshold": 0.5,
                    "mask": {
                        "remove_entity_value": True
                    }
                },
                "output": {
                    "enabled": True,
                    "threshold": 0.5,
                    "mask": {
                        "remove_entity_value": True
                    }
                }
            },
            "pii": {
                "input": {
                    "enabled": True,
                    "threshold": 0.5,
                    "mask": {
                        "remove_entity_value": True
                    }
                },
                "output": {
                    "enabled": True,
                    "threshold": 0.5,
                    "mask": {
                        "remove_entity_value": True
                    }
                }
            }
        }
