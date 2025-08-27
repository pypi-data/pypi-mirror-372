# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2020, 2021
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------
from ibm_wos_utils.joblib.utils.validator import validate_type
from ibm_wos_utils.joblib.utils import constants
from ibm_wos_utils.joblib.utils.joblib_utils import JoblibUtils
from ibm_wos_utils.joblib.utils.param_utils import get
from .remote_engine_client import RemoteEngineClient
from .iae_engine_client import IAEEngineClient
from .token_client import TokenClient


class EngineClient():

    def __init__(self, credentials):
        '''
        credentials = {
            "connection":{
                "endpoint": "",
                "location_type": ""
            },
            "credentials": {
                "username": "",
                "password": ""
            }
        }
        '''
        validate_type('credentials', credentials, dict, True)
        #validate_type('url', credentials['spark_credentials']['url'], str, True)
        #validate_type('username', credentials['spark_credentials']['username'], str, True)
        #validate_type('password', credentials['spark_credentials']['password'], str, True)
        #validate_type('spark_credentials', credentials['spark_credentials'], dict, True)
        #validate_type('spark_credentials.type', credentials['spark_credentials']['type'], dict, True)

        spark_instance_details = JoblibUtils.get_spark_instance_details(
            credentials)

        # Based on the spark type(Remote spark or IAE), creating corresponding engine client instance
        location_type = spark_instance_details.get("location_type")
        if location_type is not None and location_type == constants.SparkType.IAE_SPARK.value:
            token = TokenClient().get_iam_token_with_apikey(
                spark_instance_details['endpoint'], spark_instance_details['username'], spark_instance_details['apikey'])
            self.engine = IAEEngineClient(
                spark_instance_details['endpoint'], spark_instance_details['display_name'], spark_instance_details.get('instance_id'), spark_instance_details['volume'], token)
        else:
            self.engine = RemoteEngineClient(
                spark_instance_details['endpoint'], spark_instance_details['username'], spark_instance_details['password'])

