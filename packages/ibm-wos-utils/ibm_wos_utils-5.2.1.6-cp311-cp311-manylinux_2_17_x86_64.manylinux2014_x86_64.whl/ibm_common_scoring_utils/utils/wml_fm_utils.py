# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2023
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------


import json
import time
from functools import reduce
from ibm_common_scoring_utils.common.configuration import Configuration
from ibm_common_scoring_utils.utils.data_time_util import DateTimeUtil
from ibm_common_scoring_utils.utils.python_utils import get

from ibm_common_scoring_utils.utils.rest_util import RestUtil
from ibm_common_scoring_utils.utils.scoring_utils_logger import ScoringUtilsLogger


logger = ScoringUtilsLogger(__name__)


def get_prompt_template_asset(platform_url , asset_id , headers ,project_id=None , space_id=None):
    """
        Method to get the prompt template asset

    Args:
        platform_url (str): Data platform URL
        asset_id (str): Prompt template asset id 
        headers (dict): Auth headers
        
    """
    #Try to get the token from lru cache
    try:
        url = f"{platform_url}/wx/v1/prompts/{asset_id}"
        if project_id:
            url =f"{url}?project_id={project_id}"
        elif space_id:
            url =f"{url}?space_id={space_id}"
        
        response = RestUtil.request().get(url=url,headers=headers,verify=False)
        response_json = json.loads(response.text)
        return response_json
    except Exception as e:
        raise Exception(f"Unable to get prompt template asset id {asset_id} details . Reason:{str(e)}")
    
    
def get_prompt_string(platform_url , asset_id , headers ,project_id=None , space_id=None):
    """
        Method to get the prompt string with parameters for a prompt template asset

    Args:
        platform_url (str): Data platform URL
        asset_id (str): Prompt template asset id 
        headers (dict): Auth headers
        
    """
    #Try to get the token from lru cache
    try:
        url = f"{platform_url}/wx/v1/prompts/{asset_id}/input"
        if project_id:
            url =f"{url}?project_id={project_id}"
        elif space_id:
            url =f"{url}?space_id={space_id}"
        
        response = RestUtil.request().post(url=url,headers=headers,json={},verify=False)
        if response.status_code != 200:
            raise Exception(f"Error getting input string for {asset_id} . Reason:{response.text}")
        response_json = json.loads(response.text)
        return response_json
    except Exception as e:
        raise Exception(f"Unable to get input string for  {asset_id} . Reason:{str(e)}")
    
    
def get_input_string(prompt_template_asset:dict)->str:
    """Method to construct the input string

    Args:
        prompt_template_asset (dict): Prompt template asset json

        Example:
            {
                "id": "1427cfd4-6331-4be1-a1ae-4299e954646f",
                "template_parameters": {
                    "message": {}
                },
                "task_ids": ["few_shot_classification1"],
                "prompt": {
                    "input": ["{message}"],
                    "model_id": "google/flan-ul2",
                    "data": {
                    "instruction": "Given a message submitted to a customer-support chatbot for a cloud software company, classify the customer's message as either a question or a problem description so the chat can be routed to the correct support team.",
                    "input_prefix": "Message:",
                    "output_prefix": "Class name:",
                    "examples": [
                        ["When I try to log in, I get an error.", "Problem"],
                        ["Where can I find the plan prices?", "Question"]
                    ]
                    }
                }
            }

    Returns: 
        input_string(string) : Input string created using prompt.input + prompt.data.
        Example:
            Given a message submitted to a customer-support chatbot for a cloud software company, classify the customer's message as either a question or a problem description so the chat can be routed to the correct support team.
            Message:When I try to log in, I get an error.
            Class name:Problem

            Message:Where can I find the plan prices?
            Class name:Question


            Message:{message}
            Class name:
    """
    input = get(prompt_template_asset,"prompt.input")[0]
    prompt_data = get(prompt_template_asset,"prompt.data") or {}
    
    #Comeup with input_string
    examples = prompt_data.get("examples")
    input_prefix = prompt_data.get("input_prefix") or ""
    output_prefix = prompt_data.get("output_prefix") or ""
    instruction = prompt_data.get("instruction")
    
    #1.Construct input prefix string combining information in prompt.data
    input_prefix_string = ""
    if isinstance(examples,list):
        input_prefix_string = instruction
        example_string = ""
        for example in examples:
            example = list(filter(lambda item: item.strip(), example))
            if isinstance(example,list) and (len(example) == 2):
                example_string = example_string + "\n".join([f"{input_prefix}{example[0]}",f"{output_prefix}{example[1]}"])
                example_string = example_string + "\n\n"
            
        if example_string is not None:
            input_prefix_string = "\n".join([input_prefix_string,example_string])
            
    #2.Add the input string to input prefix string
    input_string = ""
    if isinstance(input,list):
        in_row = input
        if len(in_row) == 1:
            in_row.append("")
        in_string = "\n".join([f"{input_prefix}{in_row[0]}",f"{output_prefix}{in_row[1]}"])
        input_string = "\n".join([input_prefix_string,in_string])
    elif isinstance(input,str):
      if input_prefix_string is not None:
          input_string = "\n".join([input_prefix_string,input])
      else:
        input_string = input
    return input_string


def get_input_prompt(data , features, input_string):
    """_summary_

    Args:
        data (list): data with list of features
        features (list): prompt_template_asset.template_parameters
        input_string (string): input string constucted from prompt template asset details

    Returns:
        string: input string replaces with data (aka features data)
    """
    #Replace the values
    replace_func = lambda t, kv: t.replace(kv[0], kv[1])
    replacements = {"{"+feature+"}":data[features.index(feature)] for feature in features}
    input_text = reduce(replace_func, replacements.items(), input_string)
    return input_text
    

def score_fmaas(scoring_url, payload , headers):
    """
        Method to score data using FMaaS. 
    """
    try:
        start_time = DateTimeUtil.current_milli_time()
        #Note 520,522 are the status codes for connection time out , we can extend the list if needed
        response = RestUtil.request(additional_retry_status_codes=[520,521,522,523,524,429]).post(
                url=scoring_url,
                headers=headers,
                json=payload,
                verify=False
            )
        
        if response.status_code != 200:
            raise Exception(f"response_code:{response.status_code} response_text:{response.text}")
        response_json = json.loads(response.text)
        response_time = DateTimeUtil.current_milli_time() - start_time
        return response_json, response_time
    except Exception as ex:
        raise Exception(f"Error while scoring the foundation model. Details :{str(ex)}")
    

class ScoringTask():
    """Class to assign scoring support for foundation models
    """

    def __init__(self, headers, payload, scoring_url, config: Configuration, provider=None)-> None:
        self.provider = provider 
        self.headers=headers
        self.payload = payload
        self.scoring_url = scoring_url
        self.config = config
        
    async def execute_async(self,**args):
        """
        Executes the core of what this task is supposed to do
        """
        try:
            start_time = DateTimeUtil.current_milli_time()

            http_client_session = args.get("http_client_session")
            
            scoring_post_req = http_client_session.post(
                self.scoring_url,
                json=self.payload,
                headers=self.headers,
                verify_ssl=False,
                timeout=self.config.deployment_rest_timeout
            )

            status, response = await self.get_http_response_async(scoring_post_req)
            
            if status != 200:
                if status == 429 or "429" in response:
                    # Checking if retry count till now
                    retry_count = args.get("retry_count", 0)
                    if retry_count > self.config.max_prompt_scoring_retry_count:
                        raise Exception(f"response_code:{status} response_text:{response}")
                    else:
                        # Sleeping based on binary exponential back-off
                        sleep_interval = 2 ** (retry_count + 1)
                        logger.log_info(f"Sleeping for {sleep_interval} seconds for inferencing request based on binary exponential backoff due to busy server or rate limits.")
                        time.sleep(sleep_interval)
                        args["retry_count"] = retry_count + 1
                        return await self.execute_async(**args)
                elif status == 401 and "authentication_token_expired" in response and self.provider:
                    # Regenerate headers if a failure occoured due to expiry - WI:40646
                    # Expected Response - {"errors":[{"code":"authentication_token_expired","message":"Failed to authenticate the request due to an expired token","more_info":"https://cloud.ibm.com/apidocs/watsonx-ai-cp"}],"trace":"6901dbe1-0a55-458d-9fd2-2ccf8940ca30","status_code":401}
                    refreshed_headers = self.provider.get_headers()
                    logger.log_info(f"Refreshing headers as it is expired within a batch!!")
                    scoring_post_req = http_client_session.post(
                        self.scoring_url,
                        json=self.payload,
                        headers=refreshed_headers,
                        verify_ssl=False,
                        timeout=self.config.deployment_rest_timeout
                    )
                    # Retry scoring with refreshed headers
                    status, response = await self.get_http_response_async(scoring_post_req)
                    if status != 200:
                        raise Exception(f"Retry after 401 failed. response_code:{status} response_text:{response}")
                else:
                    raise Exception(f"response_code:{status} response_text:{response}")
            
            # Retain needed information from response
            response_time = DateTimeUtil.current_milli_time() - start_time
            response_json = json.loads(response)
            results = get(response_json,"results")[0]
            prediction = get(results,"generated_text")
            
            if self.config.enable_moderations and 'moderations' not in response_json['results'][0]:
                response_json['results'][0]['moderations'] = {}
            
            return response_json,prediction,response_time            

        except Exception as ex:
            raise Exception(f"Error while scoring the foundation model. Details :{str(ex)}")
            
    async def get_http_response_async(self,method):
        async with method as response:
            return response.status, await response.text()
    
    
    
    
    
    
    
    