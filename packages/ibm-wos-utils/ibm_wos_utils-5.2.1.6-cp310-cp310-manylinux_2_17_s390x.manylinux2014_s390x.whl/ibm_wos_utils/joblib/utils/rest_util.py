# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2020, 2021
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

from urllib3 import disable_warnings
from http import HTTPStatus

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Supress info and warning logs from requests and urllib3
import logging
logging.getLogger("requests").setLevel(logging.CRITICAL)
logging.getLogger("urllib3").setLevel(logging.CRITICAL)
disable_warnings()


class RestUtil:

    RETRY_COUNT = 5
    BACK_OFF_FACTOR = 0.5
    RETRY_AFTER_STATUS_CODES = (
        HTTPStatus.BAD_GATEWAY,
        HTTPStatus.SERVICE_UNAVAILABLE,
        HTTPStatus.GATEWAY_TIMEOUT)

    @staticmethod
    def override_response_encoding(r, *args, **kwargs):
        if r.encoding is None:
            r.encoding = 'utf-8'
        return r

    @classmethod
    def request(cls, session=None, method_list=[], **kwargs):
        session = session or requests.Session()
        session.hooks['response'].append(RestUtil.override_response_encoding)
        session.verify = False

        # some requests might want to pass other status on which they have to be retried.
        # such status should be passed as a tuple
        additional_retry_status_codes = kwargs.get(
            "additional_retry_status_codes", None)
        if additional_retry_status_codes:
            cls.RETRY_AFTER_STATUS_CODES = cls.RETRY_AFTER_STATUS_CODES + \
                additional_retry_status_codes

        #  Construct an iterable set of method to retry.
        method_list = {item for item in method_list +
                       list(Retry.DEFAULT_ALLOWED_METHODS)}

        adapter = HTTPAdapter()
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    @classmethod
    def request_with_retry(cls, session=None, method_list=[], retry_count=RETRY_COUNT, **kwargs):
        session = session or requests.Session()
        session.hooks['response'].append(RestUtil.override_response_encoding)
        session.verify = False

        # some requests might want to pass other status on which they have to be retried.
        # such status should be passed as a tuple
        additional_retry_status_codes = kwargs.get(
            "additional_retry_status_codes", None)
        if additional_retry_status_codes:
            cls.RETRY_AFTER_STATUS_CODES = cls.RETRY_AFTER_STATUS_CODES + \
                additional_retry_status_codes
        # Get connection retry count from arguments. If not provided, default to retry_count.
        connect_retry_count = kwargs.get(
            "connect_retry_count", retry_count)
        #  Construct an iterable set of method to retry.
        method_list = {item for item in method_list +
                       list(Retry.DEFAULT_ALLOWED_METHODS)}

        back_off_factor = cls.BACK_OFF_FACTOR
        if kwargs.get("back_off_factor") is not None:
            back_off_factor = kwargs.get("back_off_factor")

        retry = Retry(
            total=retry_count,
            read=retry_count,
            connect=connect_retry_count,
            allowed_methods=method_list,
            # Time delay between requests is calculated using
            # {backoff factor} * (2 ^ ({number of total retries} - 1)) seconds
            backoff_factor=back_off_factor,
            status_forcelist=cls.RETRY_AFTER_STATUS_CODES,
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session
