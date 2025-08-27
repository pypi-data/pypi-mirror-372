# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# © Copyright IBM Corp. 2022  All Rights Reserved.
# US Government Users Restricted Rights -Use, duplication or disclosure restricted by 
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------


import pandas as pd

from ibm_common_scoring_utils.common.configuration import Configuration
from ibm_common_scoring_utils.common.score_factory import ScoreFactory
from ibm_common_scoring_utils.utils.python_utils import check_for_missing_features
from ibm_common_scoring_utils.utils.scoring_utils_logger import ScoringUtilsLogger

logger = ScoringUtilsLogger(__name__)

class ScoreManager():
    """
    Entry point class which orchestrates scoring based on service type provided by the user
    """

    def __init__(self,configuration:dict):
          self.config = Configuration(configuration)

    def score( 
        self,
        data_frame: pd.DataFrame,
        include_features_in_response:bool=False,
        **kwargs) -> pd.DataFrame:

        """
          Method to score the deployment behind the scenes.

          Args:
            data_frame {pandas.Dataframe}: Input data which needs to be score based on the service type
            include_features_in_response:{bool} Flag to be enabled to include features (as in input_df) in response_df. 
            
          Returns:
            Pandas dataframe of scored response
          
        """
      
        try :
          #Check if the spark data frame is empty
          if (data_frame is None or len(data_frame)==0):
            raise Exception("Input data frame cannot be empty")

          #Check if the feature columns exists in input df
          check_for_missing_features(data_frame,self.config.features)
          
          #For FMs
          if self.config.enable_logging:
            logger.log_info(f"Scoring requested received for {len(data_frame)} records")
            
          #Call the score factory / function
          return ScoreFactory(self.config).score(data_frame,include_features_in_response,**kwargs)
        except Exception as e:
            msg = f"Error while scoring. Details: {str(e)}"
            logger.log_error(msg)
            raise Exception(msg)
      

