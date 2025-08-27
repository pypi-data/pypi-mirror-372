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
from ibm_common_scoring_utils.utils.python_utils import convert_df_to_list,get

import pandas as pd

class SPSSProvider(ServiceProvider):
    def __init__(self,config:Configuration):
        super().__init__(config)


    def get_headers(self):
        pass

    def score(self,df:pd.DataFrame):
        """
            Score SPSS deployment
        """
        try:    
            scoring_payload = self.convert_df_to_request(df)

            start_time = DateTimeUtil.current_milli_time()
            response = RestUtil.request().post(
                    url=self.config.scoring_url,auth=(self.credentials.username,self.credentials.password),json=scoring_payload
            )
            self.logger.log_debug(f"Time taken to score SPSS deployment {DateTimeUtil.current_milli_time()-start_time}ms")
            if (not response.ok):
                    raise Exception(f"Error while scoring SPSS deployment with url {self.config.scoring_url}.Error code:{response.status_code} Reason:{response.text}")
            

            return self.convert_response_to_df(response.json())
        except Exception as ex:
                msg =f"Error while scoring SPSS deployment with scoring url:{self.config.scoring_url} .Reason:{str(ex)}"
                self.logger.log_error(msg)
                raise Exception(msg)

    def validate_credentials(self):
        """
         Method to validate credentials for custom ML 
         Sample credentials dict:
            {
                "url":"<SPSS host>",
                "username":"*****",
                "password":"*****"
            }
        """
       
        missing_values = []
        if (self.credentials.username is None):
            missing_values.append("username")

        if (self.credentials.password is None):
            missing_values.append("password")

        if (self.config.prediction is None):
            missing_values.append("prediction")

        if self.config.model_type != ModelType.REGRESSION.value:
            if (len(self.config.class_probabilites) == 0):
                missing_values.append("class_probabilities")

        if len(missing_values)>0:
            raise Exception(f"Missing credentials infromation.Keys information:{missing_values}")
            

    def convert_df_to_request(self,df:pd.DataFrame):
        """
            Convert spark dataframe to Custom ML request
            Sample request:
             {
                "id": "ai_drug_mlp_proba",
                "requestInputTable": [{
                    "requestInputRow": [{
                        "input": [{
                            "name": "field1",
                            "value": 23
                        }, {
                            "name": "field2",
                            "value": "F"
                        }, {
                            "name": "field3",
                            "value": "HIGH"
                        }]
                    }]
            }]
        """
        start_time = DateTimeUtil.current_milli_time()
        #Construct id from scroing url
        id = self.config.scoring_url.rsplit("/")[-2]

        #Get the rows from df
        inputs = convert_df_to_list(df,features=self.config.features)

        #Construct the input rows
        input_rows = [{"input":[{"name":field,"value":value} for field,value in zip(self.config.features,input)]} for input in inputs]

        payload_data = {
                "id":id,
                "requestInputTable": [{
                    "requestInputRow": input_rows
                }]
            }
        self.logger.log_debug(f"Completed constructing scoring request in {DateTimeUtil.current_milli_time()-start_time}ms")
        return payload_data



    def convert_response_to_df(self,response) -> pd.DataFrame:
        """
            Convert response to spark dataframe
            Sample response:
            1. Binary 
                {
                        "providedBy": "german_credit_risk_tutorial",
                        "id": "f8304f85-fb29-45f2-83cd-a8e7de1d0fbc",
                        "columnNames": {
                            "name": [
                                "$N-Risk",
                                "$NC-Risk",
                                "$NP-No Risk",
                                "$NP-Risk"
                            ]
                        },
                        "rowValues": [
                            {
                                "value": [
                                    {
                                        "value": "No Risk"
                                    },
                                    {
                                        "value": "0.631346542302199"
                                    },
                                    {
                                        "value": "0.631346542302199"
                                    },
                                    {
                                        "value": "0.368653457697801"
                                    }
                                ]
                            }
                        ]
                    }
               
            2. Multiclass
                {
                "providedBy": "ai_drug_mlp_proba",
                "id": "fab4587d-bf80-4b24-9c73-57e17aa790f8",
                "columnNames": {
                    "name": [
                        "$N-Drug",
                        "$NC-Drug",
                        "$NP-drugA",
                        "$NP-drugB",
                        "$NP-drugC"
                    ]
                },
                "rowValues": [
                    {
                        "value": [
                            {
                                "value": "drugY"
                            },
                            {
                                "value": "0.9999929901781122"
                            },
                            {
                                "value": "6.88638806109765E-6"
                            },
                            {
                                "value": "1.2039675699035683E-7"
                            },
                            {
                                "value": "2.869979205615013E-9"
                            }
                        ]
                    }
                ]
            3. Regression:
                {
                    "providedBy": "boston_house_prices_tutorial",
                    "id": "99953076-803b-4509-a877-38f807e841aa",
                    "columnNames": {
                        "name": [
                            "$R-MEDV"
                        ]
                    },
                    "rowValues": [
                        {
                            "value": [
                                {
                                    "value": "22.5661538461539"
                                }
                            ]
                        }
                    ]
                }
        """
        start_time = DateTimeUtil.current_milli_time()
        #Detect prediction and probability column depending on model type
        col_names = get(response,"columnNames.name")

        prediction_column_index,class_probabilities_index = self.__get_prediction_and_probability_index(col_names)

        #Constrcut spark df from the response depending on model type
        row_values = get(response,"rowValues")
        if self.config.model_type == ModelType.BINARY.value:
            if len(self.config.class_probabilites) == 1:
                if len(self.config.class_labels) == 2:
                    # Case user supplies $NC-Risk and class_labels
                    # Check for index of prediction in class label and then construct probability
                    values = []
                    for row in row_values :
                        prediction = row["value"][prediction_column_index]["value"]
                        prediction_index = self.config.class_labels.index(prediction)
                        prob = float(row["value"][class_probabilities_index[0]]["value"])
                        values.append([prediction,[prob,1-prob]] if(prediction_index == 0) else [prediction,[1-prob,prob]])
                else:
                    #Case of user supplying class_probabilities : [$NP-Risk]
                    values =[[row["value"][prediction_column_index]["value"],[float(row["value"][class_probabilities_index[0]]["value"]),1-float(row["value"][class_probabilities_index[0]]["value"])]] for row in row_values]
            else:
                #Case of 2 class probabilites . Example :[$NP-Risk , $NP-No Risk]
                values =[[row["value"][prediction_column_index]["value"],[float(row["value"][prob_index]["value"]) for prob_index in class_probabilities_index]] for row in row_values]

            response_df = pd.DataFrame(values,columns=[self.config.prediction,self.config.probability])
        elif self.config.model_type == ModelType.MULTICLASS.value:
            values =[[row["value"][prediction_column_index]["value"],[float(row["value"][prob_index]["value"]) for prob_index in class_probabilities_index]] for row in row_values]
            response_df = pd.DataFrame(values,columns=[self.config.prediction,self.config.probability])
        else:
            #Regression
            values = [[float(row["value"][prediction_column_index]["value"])] for row in row_values]
            response_df = pd.DataFrame(values,columns=[self.config.prediction])

        self.logger.log_debug(f"Completed converting  scoring response to  datafame in {DateTimeUtil.current_milli_time()-start_time}ms")
        return response_df



    def __get_prediction_and_probability_index(self,col_names:list):
        #Consider only output columns
        output_cols = list(set(col_names)-set(self.config.features))

        #Check is prediction column exists else auto detect
        prediction_column_index = self.__get_prediction_index(col_names,output_cols)
        class_probabilities_index = self.__get_probability_index(col_names,output_cols)

        return prediction_column_index,class_probabilities_index

    
    def __get_prediction_index(self,col_names:list,output_cols:dict):
        try:
            prediction_column_index = col_names.index(self.config.prediction)
            return prediction_column_index
        except Exception as ex:
            self.logger.log_warning(f"Unable to detect prediction:{self.config.prediction}.Trying to auto detect...")
            prediction_column_index = None

        #Autodetect prediction column index 
        prediction_column_index = []
        if self.config.model_type == ModelType.REGRESSION.value:
            prediction_column_index =[col_names.index(col)  for col in output_cols if col.startswith("$R-")]
        else:
            prediction_column_index =[col_names.index(col)  for col in output_cols if col.startswith("$N-")]

        
        #If above logic does not detect anything try from config
        prediction_column_index =[col_names.index(col)  for col in output_cols if col == self.config.prediction]


        if prediction_column_index is None or len(prediction_column_index) == 0:
            raise Exception("Unable to detect prediction column index for SPSS deployment")

        #Set prediction column name
        self.config.prediction = col_names[prediction_column_index[0]]
        self.logger.log_warning(f"Prediction column auto detected as {self.config.prediction}")

        return prediction_column_index[0]


    def __get_probability_index(self,col_names:list,output_cols:dict):
        if self.config.model_type == ModelType.REGRESSION.value:
            return None

        class_probabilities_index = []

        # Check for SPSS output columns with NP values for both binary and multiclass
        class_probabilities_index = [col_names.index(col) for col in self.config.class_probabilites]

        #Set class probabilities in config
        self.config.class_probabilites = [col_names[x] for x in class_probabilities_index]

        if len(self.config.class_probabilites) == 0:
            raise Exception("Unable to detect class probabilities index for SPSS deployment")

        self.logger.log_warning(f"Class probabilities auto detected as {self.config.class_probabilites}")
        return class_probabilities_index


        

            
