# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2023
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S. Copyright Office.
# ----------------------------------------------------------------------------------------------------

import json
import logging

from ibm_wos_utils.joblib.utils.environment import Environment as Env
from ibm_wos_utils.joblib.utils.rest_util import RestUtil

logging.basicConfig(
    format="%(message)s", level=logging.INFO,)


class AuditLoggerClient():
    """
    Client class to call Audit Logger APIs.
    """

    def __init__(self):
        self.audit_svc_url = "{}/records".format(Env.get_gateway_url())

    def log_event(self, payload: dict) -> None:
        """
        Makes the call to log event in Audit Logger in CPD.
        :payload: The event payload to log.

        :returns: None.
        """

        # Generating the headers
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        # Making the call
        response = RestUtil.request_with_retry().post(
            self.audit_svc_url,
            json=payload,
            headers=headers,
            cert=(Env.get_tls_cert(), Env.get_tls_cert_key())
        )
        if not response.ok:
            logging.error("Failed to audit log event {}. Error status code: {}".format(
                payload["action"], response.status_code))

        return
