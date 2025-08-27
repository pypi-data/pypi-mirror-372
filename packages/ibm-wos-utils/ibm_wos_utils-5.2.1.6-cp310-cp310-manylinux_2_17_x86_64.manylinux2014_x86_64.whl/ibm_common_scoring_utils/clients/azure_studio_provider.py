# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# © Copyright IBM Corp. 2022  All Rights Reserved.
# US Government Users Restricted Rights -Use, duplication or disclosure restricted by 
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------

import pandas as pd

from ibm_common_scoring_utils.clients.service_provider import ServiceProvider
from ibm_common_scoring_utils.common.configuration import Configuration
from ibm_common_scoring_utils.utils.constants import ModelType
from ibm_common_scoring_utils.utils.python_utils import convert_df_to_list
from ibm_common_scoring_utils.utils.rest_util import RestUtil
from ibm_common_scoring_utils.utils.data_time_util import DateTimeUtil
from ibm_common_scoring_utils.utils.python_utils import get


class AzureStudioProvider(ServiceProvider):
    def __init__(self,config:Configuration):
        super().__init__(config)


    def get_headers(self):
        headers = {
            "Authorization": f"Bearer {self.credentials.azure_token}",
            "Content-Type": "application/json"
        }
        return headers

    def score(self,df:pd.DataFrame):
        """
            Score Azure studio deployment
        """
        try:

            if self.config.swagger_url:
                swagger_json = RestUtil.request().get(self.config.swagger_url).json()
                scoring_payload=swagger_json["definitions"]["ExecutionRequest"]["example"]
                self.scoring_key=list(scoring_payload["Inputs"].keys())[0]
                
            else:
                self.scoring_key="input1"


            scoring_payload = self.convert_df_to_request(df)
            start_time = DateTimeUtil.current_milli_time()

            response = RestUtil.request().post(
                url=self.config.scoring_url,headers=self.get_headers(),json=scoring_payload)

            self.logger.log_debug(f"Time taken to score Azure studio deployment {DateTimeUtil.current_milli_time()-start_time}ms")

            if (not response.ok):
                raise Exception(f"Error while scoring Azure studio deployment with url {self.config.scoring_url}.Error code:{response.status_code}.Reason:{response.text}")
            

            return self.convert_response_to_df(response.json())

        except Exception as ex:
            msg =f"Error while scoring scoring Azure Studio with scoring endpoint:{self.config.scoring_url}.Reason:{str(ex)}"
            self.logger.log_error(msg)
            raise Exception(msg)
            

    def validate_credentials(self):
        if self.credentials.azure_token is None:
            missing_value = ["token"]
            raise Exception(f"Missing credentials infromation.Keys information:{missing_value}")


    def convert_df_to_request(self,df:pd.DataFrame):
        """
         Convert input dataframe to azure studio request
         Args:
          df: input pandas dataframe

          Returns:
          {
            "Inputs": {
                "input1": [{
                    "field1": "*****",
                    "field2": "*****"
		        },
                {
                    "field1": "*****",
                    "field2": "*****"
		        }]
	      }}
          
        """
        start_time = DateTimeUtil.current_milli_time()
        values = convert_df_to_list(df,self.config.features)
        payload_data = {
            "Inputs":{
                self.scoring_key:[{field:value for field,value in zip(self.config.features,value)}for value in values]
            }
        }
        self.logger.log_debug(f"Completed constructing scoring request in {DateTimeUtil.current_milli_time()-start_time}ms")
        return payload_data

    def convert_response_to_df(self,response:dict) -> pd.DataFrame:
        """
           Convertes azure studio response to spark df 
           Sample:
           1. Binary:
           {
            "Results": {
                "output1": [{
                    "Scored Label": "****",
                    "Scored Probabilities": "***",
                    "field1": "***",
                    "field2": "****"
		        }]
	        }}

            2. Mutliclass:
             {
            "Results": {
                "output1": [{
                    "Scored Label": "****",
                    "Scored Probabilities for class \"classA\"": "***",
                    "Scored Probabilities for class \"classB\"": "***",
                    "Scored Probabilities for class \"classC\"": "***",
                    "field1": "***",
                    "field2": "****"
		        }]
	        }}

            3. Regression:
              {
                "Results": {
                    "output1": [{
                        "Scored Label": "****",
                        "field1": "***",
                        "field2": "****"
                    }]
	          }}
             
        """
        start_time = DateTimeUtil.current_milli_time()
        response_key=list(response["Results"].keys())[0]
        outputs = get(response,"Results."+response_key)
        if (self.config.model_type == ModelType.BINARY.value):
            # In azure studio binary , Scored Probabilities will not always contain winning label probability value , But it belongs to the same class label
            # So there are chances that Scored Proabbilties will be <0.5 . We will simply construct normalized array
            response_df_values = [[output["Scored Labels"], [float(output['Scored Probabilities']), 1 - float(output['Scored Probabilities'])]] for output in outputs]

            #Convert the above array to dataframe. We will only consider prediction and probability values in response_df since there is a conversion involved for probability
            response_df = pd.DataFrame(response_df_values,columns=[self.config.prediction, self.config.probability])

        elif(self.config.model_type == ModelType.MULTICLASS.value):
            #We need to construct a probability array of all columns that start with "Scored Probabilities for class"
            response_df_values = []
            for output in outputs:
                response_df_values.append([output["Scored Labels"],[float(prob) for key,prob in output.items() if key.startswith('Scored Probabilities',0)]])
            
            #Convert the above array to dataframe. We will only consider prediction and probability values in response_df since there is a conversion involved for probability
            response_df = pd.DataFrame(response_df_values,columns=[self.config.prediction,self.config.probability])
        else:
            #Extract prediction column from response
            response_df_values = [[float(output["Scored Labels"])] for output in outputs]
            response_df = pd.DataFrame(response_df_values,columns=[self.config.prediction])

        self.logger.log_debug(f"Completed converting  scoring response to  datafame in {DateTimeUtil.current_milli_time()-start_time}ms")
        return response_df
