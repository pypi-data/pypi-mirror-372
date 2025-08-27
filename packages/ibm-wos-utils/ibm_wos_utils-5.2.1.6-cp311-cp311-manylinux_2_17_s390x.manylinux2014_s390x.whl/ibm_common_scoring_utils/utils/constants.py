# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# © Copyright IBM Corp. 2022  All Rights Reserved.
# US Government Users Restricted Rights -Use, duplication or disclosure restricted by 
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------


from enum import Enum

class ModelType(Enum):
    BINARY = "binary"
    MULTICLASS = "multiclass"
    REGRESSION = "regression"
    QA = "question_answering"
    SUMMARIZATION = "summarization"
    GENERATION = "generation"
    EXTRACTION = "extraction"
    CODE = "code"
    CLASSIFICATION = "classification"
    RAG = "retrieval_augmented_generation"


class ServiceProviderType(Enum):
    #Going with same terminology as defined in openscale , to be reviewed and adjust later .
    WML = "watson_machine_learning"
    AWS = "amazon_sagemaker"
    AZURE_STUDIO = "azure_machine_learning"
    AZURE_SERVICE = "azure_machine_learning_service"
    CUSTOM_ML = "custom_machine_learning"
    SPSS = "spss_collaboration_and_deployment_services"


class AuthProvider(Enum):
    CLOUD = "cloud"
    CLOUD_REMOTE = "cloud_remote" #To match enum for WML cloud on cpd
    CPD_LOCAL = "cpd_local"
    CPD_REMOTE = "cpd_remote"

    #Enum used in custom provider case
    CPD = "cpd"


class AuthType(Enum):
    APIKEY_SINGLE = "apikey"
    APIKEY_DOUBLE = "api_key"
    BASIC = "basic"
    
    
class ExecutionType(Enum):
    SYNC = "sync"
    ASYNC = "async"


def get_model_types():
    model_types = [model_type.value for model_type in ModelType]
    return model_types


def get_service_types():
    model_engines = [model_egine.value for model_egine in ServiceProviderType]
    return model_engines


def is_classfication_model(model_type:str):
    if model_type in [ModelType.BINARY.value , ModelType.MULTICLASS.value, ModelType.CLASSIFICATION.value]:
        return True
    else:
        return False


def get_auth_providers():
    return [auth_provider.value for auth_provider in AuthProvider]


def get_auth_types():
    return [auth_type.value for auth_type in AuthType]


    

