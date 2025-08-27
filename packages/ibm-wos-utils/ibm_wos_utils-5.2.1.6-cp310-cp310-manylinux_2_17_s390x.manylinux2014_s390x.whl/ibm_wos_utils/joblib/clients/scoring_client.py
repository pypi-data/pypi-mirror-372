# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2020, 2022
# The source code for this program is not published or otherwise divested of its trade
# secrets, irrespective of what has been deposited with the U.S. Copyright Office.
# ----------------------------------------------------------------------------------------------------

try:
    from pyspark.sql import Row
    from pyspark.sql.functions import lit
    from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType, FloatType, ArrayType, LongType ,FloatType, DecimalType
except ImportError as ie:
    pass

"""
    Utility class for Scoring the any service provider deployment using scoring utility.
    Usage example:
        scoring_client = ScoringClient(service_type = "custom_machine_learning",
                                        model_type="binary",
                                        scoring_url=scoring_url,
                                        swagger_url=swagger_url,
                                        credentials=custom_ml_credentials,
                                        features=features,
                                        prediction="prediction",
                                        probability="probability",
                                        prediction_data_type="string")

        response_df = scoring_client.score(spark_df,include_features_in_response=False)
"""

class ScoringClient():
    
    def __init__(self, service_type:str, model_type:str, scoring_url:str, credentials:dict, features:list, 
                        prediction:str, prediction_data_type:str="string", probability:str=None,metafields:list=[],
                        page_size=1000,class_probabilities=[],class_labels=[],swagger_url:str=None,):
        """
        The constructor for the class. Initialises the variables needed for scoring.
        :service_type: Service Provider Type (Eg: watson_machine_learning)
        :model_type: Type of the deployment binary/multiclass/regression
        :scoring_url: Scoring url to score the model
        :credentials: Credentials needs to connect to deployment for scoring
        :features: Feature column list
        :prediction: Prediction column 
        :prediction_data_type: Prediction column data type(To be retained from output data schema of subscription)
        :probability: Probability column 
        :metafields: Meta fields needs for scoring (if any) 
        :page_size: Size of page to be considered for scoring (default:1000)
        :class_probabilities: List of class probabilites (Applicable for SPSS)
        :class_labels: List of class labels (Applicable for SPSS)
        """
        self.service_type = service_type
        self.model_type = model_type
        self.scoring_url = scoring_url
        self.credentials = credentials
        self.features = features
        self.metafields = metafields
        self.prediction = prediction
        self.probability = probability
        self.page_size = page_size
        
        #For SPSS
        self.class_probabilities = class_probabilities
        self.class_labels = class_labels

        #Additional values
        self.prediction_data_type = prediction_data_type

        #internal fields
        self.input_df_columns = None
        self.include_features_in_response = None

        #For azure studio
        self.swagger_url = swagger_url

        #Construct score utility configuration object 
        self.config = self.__get_score_utility_conf()

        #Flag to check if prediction column casting is needed
        self.number_datatypes = self.__get_number_data_types()
        self.is_prediction_column_casting_needed = False


    def __get_score_utility_conf(self):
        config = {
            "features": self.features,
            "service_type": self.service_type,
            "model_type": self.model_type,
            "credentials": self.credentials,
            "scoring_url": self.scoring_url,
            "swagger_url":self.swagger_url,
            "prediction": self.prediction,
            "probability": self.probability,
            "meta_fields": self.metafields,
            "class_probabilities":self.class_probabilities,
            "class_labels":self.class_labels
        }
        return config

    def __get_number_data_types(self):
        return ["int","integer","long","bigint"]


    def __get_score_response_schema(self,input_fields:list):
        """
            Method to get response schema
        """
        output_columns = []
        if self.include_features_in_response:
            output_columns = input_fields.copy()

        # 1. For regression the prediction type is float/double so no issue 
        # 2. For classification if the prediction column is int/long then the we have pd row to spark row conversion changing int to float and spark df conversion failing
        #    So we will first consider string and do casting outside
        if self.model_type != "regression" and self.prediction_data_type in self.number_datatypes:
            prediction_type = "string"
            self.is_prediction_column_casting_needed = True
        else:
            prediction_type = self.prediction_data_type

        output_columns.append(StructField(self.prediction,self.__get_spark_data_type(prediction_type),True))
        
        #Include probability column
        if self.model_type != "regression":
            #Add probability for classification cases
            output_columns.append(StructField(self.probability,ArrayType(DoubleType()),True))
 
        response_schema = StructType(output_columns)

        return response_schema


    def __get_spark_data_type(self,schema_data_type:str):
        """
            Method to get spark data type equivalent to data type saved in output schema
        """
        schema_spark_mapper = {
            "string": StringType(),
            "integer": IntegerType(),
            "float": FloatType(),
            "double":DoubleType(),
            "long":LongType(),
            "decimal": DecimalType(),
            "boolean": StringType() # convert boolean type to string as done by wos-utils. Tracker: #28410
        }
        return schema_spark_mapper.get(schema_data_type)

    @classmethod
    def check_for_dot_in_feature_names(cls,features:list):
        """
            Method to detect and backticks(`) if "." is detected in feature column names
            Returns:
                feature column list with backticks if "." is available
        """
        new_features = []
        for col in features:
            if col.find(".") != -1:
                col = f"`{col}`"
            new_features.append(col)
        return new_features

    @classmethod
    def is_df_numeric(cls,df, features:list):
        """
            Method to detect if df has float+int data types alone
            Returns:
                True  :  if df has ONLY double/float + int
                False :  For rest of the combinations  (ONLY int , ONLY double/float, string+ numeric etc ... )
        """
        #Check and get features with backtick(``) if the feature names has "." . Tracker#27654
        features = ScoringClient.check_for_dot_in_feature_names(features)

        #Get feature data types from df and remove duplicates
        data_types = list(set([col_dtype[1] for col_dtype in df[features].dtypes]))

        #Return true if there is a string in datatypes. "string" is the highest datatype ,so any mix with string should make sure that data type is retained
        if ("string" in data_types):
            return True

        #Return True if data_types does not have int or long
        number_dtypes = ["int","integer","bigint","long"]
        data_types = set(data_types) - set(number_dtypes)
        if len(data_types) == len(features) :
            return True

        #If you come to this point and see if length is 0 that means df has all int, bigint , float
        if len(data_types) == 0:
            return False

        #Now that int is confirmed , if one of the below is available return False else return true
        dt_checks = ["double","float","decimal"]
        for data_type in data_types:
            if data_type in dt_checks:
                #At this point as we have checked that 
                return False

        return True


    def score(self, input_df, include_features_in_response:bool=False):
        """
            Method to score the input df
            Args:
              :input_df{spark.sql.dataframe} : Input Dataframe supplied for scoring
              :include_features_in_response{bool}: Flag to include feature+ meta data columns in response

            Response:
                Response spark dataframe with "self.

            Note: Input df should be supplied with right data types , there is no special data type conversion handled in this client
        """
        try:
            self.input_df_columns = list(input_df.columns)
            self.include_features_in_response = include_features_in_response
            join_dfs = False

            #Check and set global variable
            if include_features_in_response:
                self.include_features_in_response = ScoringClient.is_df_numeric(input_df,self.features)
                
                #Set join dfs to true based on the df data types check
                if not self.include_features_in_response:
                    join_dfs = True


            #get the output schema
            feature_in_response = ScoringClient.check_for_dot_in_feature_names(self.features+ self.metafields)
            score_response_schema = self.__get_score_response_schema(input_df[feature_in_response].schema.fields)

            # Scoring on partitioned data. Returns spark_df
            score_df = input_df.rdd.mapPartitions(self.score_partition_fn).toDF(score_response_schema)

            #Type cast prediction column if needed.
            if self.is_prediction_column_casting_needed:
                score_df = score_df.withColumn(self.prediction,score_df[self.prediction].cast(self.prediction_data_type))

            #Check and combine input df with response df
            if join_dfs:
                import uuid
                dummy_column = str(uuid.uuid4())
                input_df = input_df[self.features].withColumn(dummy_column,lit(0))
                score_df = score_df.withColumn(dummy_column,lit(0))

                #Now combine
                score_df = input_df.join(score_df,score_df[dummy_column]==input_df[dummy_column]).drop(dummy_column)
                
            return score_df
        except Exception as ex:
            raise Exception(f"Error while scoring. Details:{str(ex)}")


    def score_partition_fn(self, data):

        """
        Method to perform the scoring via the REST call using the given token and deployment.
        :data: Partioned data (of type interator chain of Rows).        

        :returns: Output from scoring utility
        """
        import pandas as pd
        from more_itertools import ichunked
        from ibm_common_scoring_utils.core.score_manager import ScoreManager

        # Divide into pages(aka chunks) and score
        pages = ichunked(data, self.page_size)
        for page in pages:

            # Convert partitioned data to df
            input_pd_df = pd.DataFrame(data=page, columns=self.input_df_columns)

            # Call scoring utility
            score_response_df = ScoreManager(self.config).score(input_pd_df,include_features_in_response=self.include_features_in_response)
            
            # Convert response df to Spark rows
            score_response_df = score_response_df.apply(lambda row: Row(**row.to_dict()), axis=1)

            for _, element in score_response_df.items():
                yield element


    

   
    