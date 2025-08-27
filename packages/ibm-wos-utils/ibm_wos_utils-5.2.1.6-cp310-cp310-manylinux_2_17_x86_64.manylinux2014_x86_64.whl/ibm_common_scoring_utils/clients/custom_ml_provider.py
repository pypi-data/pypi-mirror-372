# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# © Copyright IBM Corp. 2022  All Rights Reserved.
# US Government Users Restricted Rights -Use, duplication or disclosure restricted by 
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------

from ibm_common_scoring_utils.clients.service_provider import ServiceProvider
from ibm_common_scoring_utils.common.configuration import Configuration
from ibm_common_scoring_utils.utils.auth_utils import get_cp4d_jwt_token, get_iam_token
from ibm_common_scoring_utils.utils.constants import AuthProvider, AuthType, get_auth_providers
from ibm_common_scoring_utils.utils.python_utils import convert_df_to_list
from ibm_common_scoring_utils.utils.data_time_util import DateTimeUtil
from ibm_common_scoring_utils.utils.constants import ModelType

from base64 import b64encode
import pandas as pd


from ibm_common_scoring_utils.utils.rest_util import RestUtil

class CustomMLProvider(ServiceProvider):
        def __init__(self,config:Configuration):
                super().__init__(config)

        def get_headers(self):
                auth_header = None

                #Add support for Basic Auth 
                if self.credentials.auth_type == AuthType.BASIC.value:
                        auth_encode = b64encode(bytes(f"{self.credentials.username}:{self.credentials.password}","utf-8")).decode("ascii")
                        auth_header = f"Basic {auth_encode}"

                elif self.credentials.auth_type in [AuthType.APIKEY_DOUBLE.value, AuthType.APIKEY_SINGLE.value]:
                        if self.credentials.auth_provider == AuthProvider.CLOUD.value:
                                token = get_iam_token(self.credentials.apikey,self.credentials.auth_url)
                        else:   
                                #Check and fix the url . Tracker#29073
                                if self.credentials.auth_url is not None:
                                        host = self.credentials.auth_url
                                else:
                                        #Fall back logic
                                        host = self.credentials.url

                                token = get_cp4d_jwt_token(host, username=self.credentials.username,apikey=self.credentials.apikey)

                        auth_header = f"Bearer {token}"

                if auth_header is None:
                        raise Exception("Error while creating headers")
               
                headers = {
                        "Authorization": auth_header,
                        "Content-Type": "application/json"
                 }

                return headers

        def score(self,df:pd.DataFrame):
                """
                 Score Custom ML deployment
                """
                try:    
                        scoring_payload = self.convert_df_to_request(df)

                        start_time = DateTimeUtil.current_milli_time()

                        #Note 520,522 are the status codes for connection time out , we can extend the list if needed
                        response = RestUtil.request().post(
                                url=self.config.scoring_url,
                                headers=self.get_headers(),
                                json=scoring_payload,verify=False
                        )
                        self.logger.log_debug(f"Time taken to score custom ML deployment {DateTimeUtil.current_milli_time()-start_time}ms")
                        if (not response.ok):
                                print(f"Error code is {response.status_code}")
                                raise Exception(f"Error while scoring custom ML deployment with url {self.config.scoring_url}.Error code:{response.status_code} Reason:{response.text}")
                        

                        return self.convert_response_to_df(response.json())
                except Exception as ex:
                        msg =f"Error while scoring Custom ML deployment with scoring url:{self.config.scoring_url} .Reason:{str(ex)}"
                        self.logger.log_error(msg)
                        raise Exception(msg)
                

        def validate_credentials(self):
                """
                        Method to validate credentials for custom ML 
                        Sample credentials dict:
                        Basic Auth:
                        credentials :{
                                "auth_type":"basic",
                                "username":"admin",
                                "password":"*****"
                        }

                        API Key based :
                        1. On CPD 
                        credentials :{
                                "auth_type": "api_key",
                                "auth_provider": "cpd",
                                "username":"admin",
                                "apikey":"*******",
                                "url": "<hostname>",
                                "auth_url": "<hostname>"
                        }

                        2. On Cloud 
                        credentials :{
                                "auth_type": "api_key",
                                "auth_provider": "cloud",
                                "apikey":"*******"
                        }

                """
                if self.credentials.auth_type is None:
                        raise KeyError(f"Auth type missing in credentials. Acceptable values : {[AuthType.BASIC.value,AuthType.APIKEY_DOUBLE.value]}")
                
                
                missing_values = []
                if self.credentials.auth_type == AuthType.BASIC.value:
                        if self.config.is_foundation_model:
                                raise KeyError(f"Custom provider does not support auth_type:{AuthType.BASIC.value} for FMaaS scoring")
                        
                        if self.credentials.username is None :
                                missing_values.append("username")

                        if self.credentials.password is None: 
                                missing_values.append("password")
                        
                else:   
                        #Validate properties needed for APIKey
                        if self.credentials.auth_provider is None :
                                raise KeyError(f"Missing auth_provider in credentials. Acceptable valus: {get_auth_providers()}")

                        
                        if self.credentials.apikey is None :
                                missing_values.append("apikey")

                        if self.credentials.username is None and not self.credentials.auth_provider == AuthProvider.CLOUD.value: 
                                missing_values.append("username")

                        #Check and raise a error for missing url /auth_url for auth_provider: cpd
                        if self.credentials.auth_provider == AuthProvider.CPD.value:
                                if (self.credentials.auth_url is None or self.credentials.auth_url == "") and (self.credentials.url is None or self.credentials.url == ""):
                                        #auth_url is mandatory hence add missing values as auth_url
                                        missing_values.append("auth_url")

                if len(missing_values) > 0:
                        raise KeyError(f"Missing credentials information.Keys information:{missing_values}")
                                
        
        def convert_df_to_request(self,df:pd.DataFrame) -> dict:
                """
                Convert spark dataframe to Custom ML request
                """
                start_time = DateTimeUtil.current_milli_time()
                fields = self.config.features
                values = convert_df_to_list(df,fields)

                #First construct basic custom payload
                scoring_payload = {
                        "fields":fields,
                        "values":values
                }

                #Construct meta info
                if len(self.config.meta_fields) > 0:
                        meta_fields = self.config.meta_fields
                        meta_values = convert_df_to_list(df,meta_fields)
                        meta_payload = {
                                "fields":meta_fields,
                                "values":meta_values
                        }
                        scoring_payload["meta"] = meta_payload

                #Update the scoring payload if the auth type is apikey
                if not self.credentials.auth_type == AuthType.BASIC.value:
                        scoring_payload = {"input_data":[scoring_payload]}
                
                self.logger.log_debug(f"Completed constructing scoring request in {DateTimeUtil.current_milli_time()-start_time}ms")
                return scoring_payload


        def convert_response_to_df(self,response:dict) -> pd.DataFrame:
                """
                Convert response to spark dataframe
                """
                start_time = DateTimeUtil.current_milli_time()

                #Retain the information from response depending on auth type
                if not self.credentials.auth_type == AuthType.BASIC.value:
                        predictions = response.get("predictions")[0]
                else:
                        predictions = response

                #Convert to data frame
                response_df = pd.DataFrame(predictions.get("values"),columns=predictions.get("fields"))

                #Extract only output columns
                output_cols = [self.config.prediction,self.config.probability]
                
                #Probability column will not be available for case of regression models (traditional) or foundation models (custom route)
                if self.config.model_type == ModelType.REGRESSION.value or self.config.is_foundation_model:
                        output_cols.remove(self.config.probability)
                response_df = response_df[output_cols]

                self.logger.log_debug(f"Completed converting  scoring response to datafame in {DateTimeUtil.current_milli_time()-start_time}ms")
                return response_df
                