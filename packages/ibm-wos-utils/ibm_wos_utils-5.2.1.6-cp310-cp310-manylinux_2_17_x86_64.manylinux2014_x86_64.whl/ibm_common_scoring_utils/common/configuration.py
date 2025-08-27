# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# © Copyright IBM Corp. 2022 2024 All Rights Reserved.
# US Government Users Restricted Rights -Use, duplication or disclosure restricted by 
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------

import os

from urllib.parse import urlparse
from ibm_common_scoring_utils.utils.constants import ModelType, ServiceProviderType, get_model_types, get_service_types

class Configuration():
    """
        Class responsible for setting and getting configuration information needed for scoring
        Eg:
        
        Traditional Models:
        {
            "features":[],
            "prediction":"prediction",
            "probability":"probability,
            "model_type":"binary",
            "service_type": "wml",
            "credentials":{<credentials based on service type>},
            "scoring_url": "<scoring_url>",
        }
        
        Foundation Models:
        {
            "features":[],
            "prediction":"generated_text",
            "model_type/problem_type":"question_answering",
            "service_type": "wml",
            "credentials":{<wml_credentials>},
            "scoring_url": "<scoring_url>. If blank prompt template json to be referred",
            "project_id":<project_id>, #Supply either project or space id
            "space_id":<space_id>,
            "is_foundation_model":True,
            "prompt_template_asset_details":<dict value of prompt template asset. Needed for FMaaS based scoring>,
            "enable_logging": <True/False. Default value is False> #Introduced for FMs,
            "batch_size": <Number of http requests to be processed using asyncio. Applicable only for FMs>,
            "MAX_PROMPT_SCORING_RETRY_COUNT": <Max number of retries to be attempted for prompt scoring against deployments when rate limit is hit.>,
            "platform_url": <platform_url>
            "is_cp4d_environment": <True/False. Default value is False>
            "enable_moderations": <True/False. Default value is False. Indicates whether we need moderation/guardrails information in the WML inferencing response>. 
        }
        
    """
    def __init__(self, configuration:dict):
        #Validate configuration
        self.validate_configuration(configuration)

        self.features = configuration.get("features")
        self.prediction = configuration.get("prediction") or "prediction"
        self.probability = configuration.get("probability") or "probability"
        self.schema = configuration.get("schema")
        self.model_type = configuration.get("model_type") or configuration.get("problem_type")
        self.credentials = configuration.get("credentials")
        self.using_service_token = configuration.get("using_service_token", False)
        self.service_type = configuration.get("service_type")
        

        #The following property is meant to be used for SPSS - in cases where the probability fields cannot be self detected
        self.class_probabilites = configuration.get("class_probabilities") or []
        self.class_labels = configuration.get("class_labels") or []

        #The following property is meant to be used for Azure studio - swagger url for identifing the scoring and response payload
        self.swagger_url=configuration.get("swagger_url")

        #Meta fields can be used for scoring needs in case of WML and custom ML 
        self.meta_fields = configuration.get("meta_fields") or []
        
        #Properties for LLMs    
        self.is_foundation_model = configuration.get("is_foundation_model") or False
        self.project_id = configuration.get("project_id")
        self.space_id = configuration.get("space_id")
        self.prompt_template_asset_json = configuration.get("prompt_template_asset_details")
        self.batch_size = configuration.get("batch_size") or 10
        self.platform_url = configuration.get("platform_url")
        self.is_cp4d_environment = configuration.get("is_cp4d_environment") or False
        self.enable_moderations = configuration.get("enable_moderations", False)
        
        #Default True.Reset otherwise
        self.enable_logging = True
        if configuration.get("enable_logging") is not None:
            self.enable_logging = configuration.get("enable_logging")
         
        #set scoring url
        self.scoring_url = configuration.get("scoring_url")

        # Replacing with host with platform nginx for CPD and FM inferencing
        if self.is_foundation_model and self.is_cp4d_environment and self.scoring_url is not None:
            # This is done to route the inferencing request from within the pod via the platform nginx server directly
            platform_gateway_url = urlparse(os.environ["PLATFORM_GATEWAY_URL"])
            self.scoring_url = self.scoring_url.replace(urlparse(self.scoring_url).hostname, f"{platform_gateway_url.hostname}:{platform_gateway_url.port}")
        
        #Set fmaas scoring flag
        self.is_fmaas_scoring = False
        if self.is_foundation_model and self.scoring_url is None:
            self.is_fmaas_scoring = True
        
        # Setting the prompt scoring retry variables (sleep is based on binary exponential back-off)
        self.max_prompt_scoring_retry_count = configuration.get("MAX_PROMPT_SCORING_RETRY_COUNT", 5)

        # The REST timeout for calls to deployment inferencing endpoint for prompt deployments
        self.deployment_rest_timeout = configuration.get("DEPLOYMENT_REST_TIMEOUT", 300)
        
        return
        

    @property
    def features(self):
        return self._features

    @features.setter
    def features(self,value):
        if not isinstance(value,list) or len(value) == 0:
            raise ValueError("Features cannot be empty")
        self._features = value

    @property
    def model_type(self):
        return self._model_type

    @model_type.setter
    def model_type(self,value):
        if ModelType(value) is  None:
            raise ValueError(f"Unsupported value type:{value} . Acceptable values are :{get_model_types()}")
        self._model_type = value

    @property
    def service_type(self):
        return self._service_type

    @service_type.setter
    def service_type(self,value):
        if ServiceProviderType(value) is  None:
            raise ValueError(f"Unsupported value type:{value} . Acceptable values are :{get_service_types()}")
        self._service_type = value


    @property
    def scoring_url(self):
        return self._scoring_url

    @scoring_url.setter
    def scoring_url(self,value):
        if value is None and not self.is_foundation_model:
            raise ValueError("scoring_url cannot be empty")
        self._scoring_url = value

    @property
    def credentials(self):
        return self._credentials

    @credentials.setter
    def credentials(self,value):
        if not isinstance(value, dict):
            raise ValueError("credentials cannot be empty")
        self._credentials = value
        

            
    def validate_configuration(self,configuration:dict):
        missing_values = []
       
        if configuration.get("features") is None:
            missing_values.append("features")

        if configuration.get("model_type") is None:
            missing_values.append("model_type")

        if configuration.get("service_type") is None :
             missing_values.append("service_type")

        if configuration.get("credentials") is None:
            if configuration.get("service_type") == ServiceProviderType.AZURE_SERVICE.value:
                configuration["credentials"] = {}
            else:
                missing_values.append("credentials")

        service_type = configuration.get("service_type")
        model_type = configuration.get("model_type")
        if model_type is None:
            model_type = configuration.get("problem_type")
        
        #LLM checks
        is_foundation_model = configuration.get("is_foundation_model") or False
        
        # Check for probability only for WML and Custom ML for rest the probability column value will be probability as there is a coversion
        # involved for constructing probability column
        if service_type in [ServiceProviderType.WML.value,ServiceProviderType.CUSTOM_ML.value] and model_type != ModelType.REGRESSION.value and not is_foundation_model:
            if configuration.get("probability") is None :
                missing_values.append("probability")

            if configuration.get("prediction") is None:
                missing_values.append("prediction")
                
        if is_foundation_model :
            return self.__validate_configuration_for_fm(configuration,missing_values)

        if len(missing_values) > 0:
            raise AttributeError("Missing configuration properties . Details :{}".format(missing_values))
        

    def __validate_configuration_for_fm(self,configuration:dict,missing_values:list):
        space_id = configuration.get("space_id")
        project_id = configuration.get("project_id")
        
        if space_id is None and project_id is None:
            missing_values.append("space_id/project_id")
            
        if configuration.get("prompt_template_asset_details") is None:
                missing_values.append("prompt_template_asset_details")
                
        if configuration.get("prediction") is None:
            configuration["prediction"] = "generated_text"
                
        if len(missing_values) > 0:
            raise AttributeError("Missing configuration properties . Details :{}".format(missing_values))
        


class Credentials():
    """
        Class responsible for setting credentials
    """
    def __init__(self,credentials:dict):
        self.url = credentials.get("url")

        
        self.apikey = credentials.get("apikey")
        if self.apikey is None:
            self.apikey = credentials.get("api_key")

        #WML
        self.instance_id = credentials.get("instance_id")
        self.wml_location = credentials.get("wml_location")
        self.uid = credentials.get("uid") #Needed for wml_location:cpd_local
        self.zen_service_broker_secret = credentials.get("zen_service_broker_secret") #Needed for wml_location:cpd_local
        self.auth_url = credentials.get("auth_url") #Needed to test this utility on internal envs like ys1dev
        self.wml_token = credentials.get("token") #Supplied for FM scoring
        self.platform_url = credentials.get("platform_url") #Supplied for FM scoring
        self.headers=credentials.get("headers") or {} #Needed for secondary token in task credentials

        #Custom ML Provider
        self.auth_provider = credentials.get("auth_provider")
        self.auth_type = credentials.get("auth_type")
        self.username = credentials.get("username")
        self.password = credentials.get("password")
        self.auth_url = credentials.get("auth_url")

        #AWS 
        self.access_key_id = credentials.get("access_key_id")
        self.secret_access_key = credentials.get("secret_access_key")
        self.region = credentials.get("region")

        #Azure studio
        # Note : In case of Azure studio/service each deployment is associated with a api_key which is mapped to "token" in openscale world
        self.azure_token = credentials.get("token")

        #Azure service 
        #Note : In case of Azure service each deployment is associated with token /secondaryKey and having crendetials is not mandatory to have these credentials
        self.azure_secondary_key = credentials.get("secondaryKey")


       


        

        


