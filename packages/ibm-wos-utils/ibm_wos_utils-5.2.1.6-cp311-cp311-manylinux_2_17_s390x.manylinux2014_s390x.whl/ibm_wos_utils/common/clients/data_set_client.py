# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2025
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

from ibm_wos_utils.common.utils.date_util import DateUtil
from ibm_wos_utils.common.utils.common_logger import CommonLogger
from ibm_wos_utils.joblib.utils.environment import Environment
from ibm_wos_utils.joblib.utils.rest_util import RestUtil

logger = CommonLogger(__name__)


class DataSetsClient:
    """
    Client class to interact with Data Sets service.
    """

    def __init__(self, service_instance_id: str, access_token: str):
        self.service_instance_id = service_instance_id
        self.access_token = access_token
        self.base_url = (
            Environment.get_gateway_url()
            + "/openscale/"
            + self.service_instance_id
            + "/v2/data_sets"
        )

    def __get_header(self):
        header = {}
        header["Content-Type"] = "application/json"
        header["Accept"] = "application/json"
        header["Authorization"] = "Bearer {0}".format(self.access_token)
        return header

    def get_data_set(self, subscription_id, data_set_type="payload_logging"):
        start_time = DateUtil.current_milli_time()
        data_sets_url = (
            self.base_url
            + "?target.target_id={}&target.target_type=subscription&type={}".format(
                subscription_id, data_set_type
            )
        )
        response = RestUtil.request_with_retry().get(
            data_sets_url, headers=self.__get_header()
        )
        logger.log_info(
            "Got data_set using : {}".format(data_sets_url), start_time=start_time
        )

        if response.ok is False:
            raise Exception(
                "An error occured while retrieving the dataset of type {0} for the subscription {1}. Status code: {2}. Reason: {3}".format(
                    data_set_type,
                    subscription_id,
                    response.status_code,
                    response.reason,
                )
            )
        response = response.json().get("data_sets")
        return response[0] if response else {}

    def get_records(
        self,
        data_set_id: str,
        limit=None,
        offset=None,
        include_total_count=None,
        format_type=None,
    ):
        start_time = DateUtil.current_milli_time()
        url = "{}/{}/records".format(self.base_url, data_set_id)
        query_params = []

        if limit is not None:
            query_params.append("limit={}".format(limit))
        if offset is not None:
            query_params.append("offset={}".format(offset))
        if include_total_count is not None:
            query_params.append("include_total_count={}".format(include_total_count))
        if format_type is not None:
            query_params.append("format={}".format(format_type))

        if query_params:
            url = "{}?{}".format(url, "&".join(query_params))

        logger.log_debug("Getting data_set records using : {}".format(url))
        response = RestUtil.request().get(url, headers=self.__get_header())
        logger.log_info(
            "Got data set records using : {}".format(url), start_time=start_time
        )

        if not response.ok:
            logger.log_debug("Fetching records failed : " + str(response.reason))
            raise Exception(
                "An error occurred while retrieving records from the dataset {0}. Status code: {1}. Reason: {2}".format(
                    data_set_id, response.status_code, response.reason
                )
            )

        return response.json()
