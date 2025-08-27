# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# © Copyright IBM Corp. 2022  All Rights Reserved.
# US Government Users Restricted Rights -Use, duplication or disclosure restricted by 
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------


from ibm_common_scoring_utils.clients.service_provider import ServiceProvider
from ibm_common_scoring_utils.common.configuration import Configuration
from ibm_common_scoring_utils.utils.constants import ModelType
from ibm_common_scoring_utils.utils.rest_util import RestUtil
from ibm_common_scoring_utils.utils.data_time_util import DateTimeUtil
from ibm_common_scoring_utils.utils.python_utils import convert_df_to_list

import pandas as pd
import json

class AzureServiceProvider(ServiceProvider):
    def __init__(self, config:Configuration):
        super().__init__(config)


    def get_headers(self,azure_token:str=None):
        headers = {
            "Content-Type": "application/json"
        }

        if azure_token is not None:
            headers["Authorization"] = f"Bearer {azure_token}"
        return headers


    def score(self,df:pd.DataFrame):
        """
            Score Azure service deployment
        """
        try:
            scoring_payload = self.convert_df_to_request(df)
            start_time = DateTimeUtil.current_milli_time()

            response = RestUtil.request().post(
                url=self.config.scoring_url,headers=self.get_headers(self.credentials.azure_token),json=scoring_payload)

            self.logger.log_debug(f"Time taken to score Azure service deployment {DateTimeUtil.current_milli_time()-start_time}ms")
            print(response.json())

            if (not response.ok):
                if (response.status_code == 401 and self.credentials.azure_secondary_key is not None):
                    #Try with secondary key
                    response = RestUtil.request().post(
                        url=self.config.scoring_url,headers=self.get_headers(self.credentials.secret_access_key),json=scoring_payload)
                    
                    if response.ok:
                        return self.convert_response_to_df(response.json())

                raise Exception(f"Error while scoring Azure service deployment with url {self.config.scoring_url}.Error code:{response.status_code}.Reason:{response.text}")
            return self.convert_response_to_df(response.json())

        except Exception as ex:
            msg =f"Error while scoring scoring Azure service with scoring endpoint:{self.config.scoring_url}.Reason:{str(ex)}"
            self.logger.log_error(msg)
            raise Exception(msg)


    def validate_credentials(self):
        missing_values = []
        if self.credentials.azure_token is None:
            missing_values.append("token")

        if self.credentials.azure_secondary_key is None:
            missing_values.append("secondaryKey")

        if len(missing_values) == 2:
            self.logger.log_warning(f"Missing keys:{missing_values} .Scoring will be attempted without any authroization token")
        


    def convert_df_to_request(self,df:pd.DataFrame) -> dict:
        """
         Convert input dataframe to azure studio request
         Args:
          df: input pandas dataframe

          Returns:
          {
            "input": {
                {
                    "field1": "*****",
                    "field2": "*****"
		        },
                {
                    "field1": "*****",
                    "field2": "*****"
		        }
	      }}
          
        """
        start_time = DateTimeUtil.current_milli_time()
        values = convert_df_to_list(df[self.config.features],self.config.features)
        payload_data = {
            "input": [{field:value for field,value in zip(self.config.features,value)}for value in values]
        }
        self.logger.log_debug(f"Completed constructing scoring request in {DateTimeUtil.current_milli_time()-start_time}ms")
        return payload_data

    def convert_response_to_df(self,response:dict) -> pd.DataFrame:
        """
           Convertes azure studio response to spark df 
           Sample:
           1. Binary/Multiclass:
           {
            "output": {
                [{
                    "Scored Label": "****",
                    "Scored Probabilities": "***"
		        }]
	        }

            3. Regression:
              {
                "output": {
                    [{
                        "Scored Label": "****",
                    }]
	        }
             
        """
        start_time = DateTimeUtil.current_milli_time()

        #Check type of response and then jsonify #Issue 27854-[55]
        if isinstance(response,str):
            response = json.loads(response)
        results = response.get("output")

        #Extract results
        output_cols = [self.config.prediction]
        if self.config.model_type in [ModelType.BINARY.value,ModelType.MULTICLASS.value]:
            values = [[result[col] for col in ["Scored Labels","Scored Probabilities"]] for result in results]
            output_cols.append(self.config.probability)
        else:
            values = [[result["Scored Labels"]] for result in results]

       
        #Construct response df
        response_df = pd.DataFrame(values,columns=output_cols)
        self.logger.log_debug(f"Completed converting  scoring response to  datafame in {DateTimeUtil.current_milli_time()-start_time}ms")
        return response_df