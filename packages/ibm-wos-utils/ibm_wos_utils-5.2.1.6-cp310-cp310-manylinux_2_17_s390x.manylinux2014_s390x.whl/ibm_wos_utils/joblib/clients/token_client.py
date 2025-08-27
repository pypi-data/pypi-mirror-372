# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2020, 2021
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

import urllib3

from http import HTTPStatus
from ibm_wos_utils.joblib.exceptions.client_errors import AuthenticationError, DependentServiceError
from ibm_wos_utils.joblib.utils.rest_util import RestUtil


class TokenClient():

    @classmethod
    def get_iam_token(cls, server_url: str, username: str, password: str, iam_enabled: bool=False, bedrock_url: str=None) -> str:
        """
        Generates IAM token with the given URL and credentials.
        :server_url: The URL to be used for token generation.
        :username: The username.
        :password: The password.
        :iam_enabled: Whether the CPD cluster is IAM enabled. [Optional, default is False]
        :bedrock_url: The bedrock URL for CPD with IAM enabled. [Optional]

        :returns: The IAM token.
        """
        iam_token = None

        # Generating the IAM token
        url = "{}/v1/preauth/validateAuth".format(server_url)
        headers = {
            "Accept": "application/json",
            "username": username
        }
        
        if iam_enabled:
            # Generating the bedrock token
            bedrock_url = bedrock_url if bedrock_url is not None else cls._get_bedrock_url(server_url)
            bedrock_token_url = "{}/idprovider/v1/auth/identitytoken".format(bedrock_url)
            data = {
                "grant_type": "password",
                "username": username,
                "password": password,
                "scope": "openid"
            }
            response = RestUtil.request().post(bedrock_token_url, data, verify=False)
            if not response.ok:
                if response.status_code == HTTPStatus.UNAUTHORIZED.value:
                    raise AuthenticationError("The credentials provided to generate access token are invalid.")
                else:
                    raise DependentServiceError("An error occurred while generating the bedrock token.", response)
            bedrock_token = response.json()["access_token"]
            headers["iam-token"] = bedrock_token
        else:
            headers["password"] = password
        
        # Making the REST call
        response = RestUtil.request().get(url=url, headers=headers)
        
        if not response.ok:
            if response.status_code == HTTPStatus.UNAUTHORIZED.value:
                raise AuthenticationError(
                    "The credentials provided to generate access token are invalid.")
            raise DependentServiceError(
                "An error occurred while generating access token.", response)
        
        # Getting the token from the response
        iam_token = response.json().get("accessToken")
        
        return iam_token

    @classmethod
    def get_iam_token_with_apikey(cls, server_url: str, username: str, apikey: str) -> str:
        """
        Generates IAM token with the given URL and credentials.
        :server_url: The URL to be used for token generation.
        :username: The username.
        :apikey: The API key.

        :returns: The IAM token.
        """
        iam_token = None

        # Generating the IAM token
        url = "{}/icp4d-api/v1/authorize".format(server_url)
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        data = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "username": username,
            "api_key": apikey
        }

        # Making the REST call
        response = RestUtil.request().post(url, json=data, headers=headers, verify=False)
        
        if not response.ok:
            if response.status_code == HTTPStatus.UNAUTHORIZED.value:
                raise AuthenticationError(
                    "The credentials provided to generate access token are invalid.")
            raise DependentServiceError(
                "An error occurred while generating access token.", response)
        
        # Getting the token from the response
        iam_token = response.json().get("token")

        return iam_token
    
    @classmethod
    def _get_bedrock_url(cls, server_url: str) -> str:
        """
        Generates the default bedrock URL from the given server URL.
        :server_url: The server URL.

        :returns: The bedrock URL.
        """
        bedrock_url = None

        # Generating the default bedrock URL
        fqdn = urllib3.util.parse_url(server_url).netloc
        domain = '.'.join(fqdn.split('.')[1:])
        bedrock_url = 'https://cp-console.{}'.format(domain)

        return bedrock_url
