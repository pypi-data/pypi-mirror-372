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
from ibm_common_scoring_utils.utils.python_utils import convert_df_to_list
from ibm_common_scoring_utils.utils.data_time_util import DateTimeUtil

import boto3
import numpy as np
import io
import json
import pandas as pd


class AmazonSageMakerProvier(ServiceProvider):
    def __init__(self,config:Configuration) :
        super().__init__(config)


    def get_headers(self):
        pass


    def score(self,df:pd.DataFrame):
        """
            Score AWS deployment
        
        """
        try:
            payload_data = self.convert_df_to_request(df)

            runtime = boto3.client('sagemaker-runtime', 
                                    region_name=self.credentials.region, 
                                    aws_access_key_id=self.credentials.access_key_id, 
                                    aws_secret_access_key=self.credentials.secret_access_key)
            start_time = DateTimeUtil.current_milli_time()

            response = runtime.invoke_endpoint(EndpointName=self.config.scoring_url, ContentType='text/csv', Body=payload_data)
            self.logger.log_debug(f"Time taken to score AWS deployment {DateTimeUtil.current_milli_time()-start_time}ms")

            results_decoded = json.loads(response['Body'].read().decode())

            return self.convert_response_to_df(results_decoded)
            
        except Exception as ex:
            msg =f"Error while scoring scoring AWS deployment with scoring endpoint:{self.config.scoring_url}.Reason:{str(ex)}"
            self.logger.log_error(msg)
            raise Exception(msg)
        

    def validate_credentials(self):
        """
            Method to validate credentials for AWS 
            Sample AWS credentials dict 
            credentials :{
                "access_key_id":"*****",
                "secret_access_key":"*****",
                "region":"us-east-1"
            }
        
        """
        missing_values = []
        if self.credentials.access_key_id is None:
            missing_values.append("access_key_id")

        if self.credentials.secret_access_key is None:
            missing_values.append("secret_access_key")

        if self.credentials.region is None:
            missing_values.append("region")
        
        if len(missing_values) > 0:
                raise KeyError(f"Missing credentials information.Keys information:{missing_values}")


    def convert_df_to_request(self,df:pd.DataFrame):
        """
            Convert spark df to AWS request 
            
        """
        start_time = DateTimeUtil.current_milli_time()
        #the spark df will be coverted to csv format instead of json to speed up the request constuction process 
        payload_bytes = io.BytesIO()
        np.savetxt(payload_bytes,convert_df_to_list(df,self.config.features),delimiter=',')
        payload_data = payload_bytes.getvalue().decode().rstrip()
        self.logger.log_debug(f"Completed constructing scoring request in {DateTimeUtil.current_milli_time()-start_time}ms")
        return payload_data
       

    def convert_response_to_df(self,response:dict) -> pd.DataFrame:
        """
            Covert AWS response to spark df 
            Sample response :
            1. Binary:
               {
                    "predictions": [
                        {
                            "score": 1.0,
                            "predicted_label": 1.0
                        }
                    ]
                }
            2. Multiclass:
                { 
                  "predictions": [
                    {
                        "score": [
                            0.39379584789276123,
                            0.09229674935340881,
                            0.09971172362565994,
                            0.07799549400806427,
                            0.33620020747184753
                        ],
                        "predicted_label": 0.0
                    }]}
            3. Regression:
                    {
                        "predictions": [
                            {
                                "score": 1.2625820636749268
                            }
                         ]
                    }
        """
        start_time = DateTimeUtil.current_milli_time()
        predictions = response['predictions']

        #Convert response to pandas dataframe extracting output columns
        response_df_columns = [self.config.prediction,self.config.probability]
        if self.config.model_type == ModelType.BINARY.value:
            response_df_values = [[prediction["predicted_label"],[prediction["score"],1-prediction["score"]]]for prediction in predictions]
        elif self.config.model_type == ModelType.MULTICLASS.value:
            response_df_values = [[prediction["predicted_label"],prediction["score"]]for prediction in predictions]
        else:
            response_df_values = [[prediction["score"]]for prediction in predictions]
            response_df_columns.remove(self.config.probability)

        response_df = pd.DataFrame(response_df_values,columns=response_df_columns)

        self.logger.log_debug(f"Completed converting  scoring response to  datafame in {DateTimeUtil.current_milli_time()-start_time}ms")
        return response_df
