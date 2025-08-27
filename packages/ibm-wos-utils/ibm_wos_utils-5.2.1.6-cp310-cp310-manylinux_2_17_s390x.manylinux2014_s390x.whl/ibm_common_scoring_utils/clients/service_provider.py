# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# © Copyright IBM Corp. 2022  All Rights Reserved.
# US Government Users Restricted Rights -Use, duplication or disclosure restricted by 
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------


from abc import ABC, abstractmethod
from ibm_common_scoring_utils.common.configuration import Configuration, Credentials
from ibm_common_scoring_utils.utils.scoring_utils_logger import ScoringUtilsLogger


class ServiceProvider(ABC):
    def __init__(self, config: Configuration):
        self.logger = ScoringUtilsLogger(__name__)
        self.config = config
        self.credentials = Credentials(self.config.credentials)
        
        #Validate credentials 
        self.validate_credentials()
        
    @abstractmethod
    def get_headers(self):
        pass

    @abstractmethod
    def score(self):
        pass

    @abstractmethod
    def convert_df_to_request(self):
        pass
    
    @abstractmethod
    def convert_response_to_df(self):
        pass

    @abstractmethod
    def validate_credentials(self):
        pass


