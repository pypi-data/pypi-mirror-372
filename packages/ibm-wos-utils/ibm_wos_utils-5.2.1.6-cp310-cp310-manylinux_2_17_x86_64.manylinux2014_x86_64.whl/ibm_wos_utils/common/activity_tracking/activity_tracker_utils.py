# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2023
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S. Copyright Office.
# ----------------------------------------------------------------------------------------------------

import io
import json
import os
import uuid
import logging

from ibm_wos_utils.common.security.user import User
from ibm_wos_utils.joblib.clients.audit_logger_client import AuditLoggerClient
from ibm_wos_utils.joblib.utils.date_util import DateUtil
from ibm_wos_utils.joblib.utils.environment import Environment as Env


logging.basicConfig(
    format="%(message)s", level=logging.INFO,)


class ActivityTrackingInfo:

    def __init__(self, action: str, data_event: bool, message: str):
        """
        Constructor for the `ActivityTrackingInfo` object.
        :action: The action of the activity.
        :data_event: Whether the activity is a data event of management event.
        :message: The message associated with the activity.
        """
        self.action = action
        self.data_event = data_event
        self.message = message


class ActivityTrackerUtils:

    @classmethod
    def log_event(cls, at_event_info: ActivityTrackingInfo, outcome: str, user: User, service_instance_id, status_code: int, request_path: str, request_method: str, request_user_agent: str) -> None:
        """
        Logs event for Activity Tracker in the file mount.
        :at_event_info: The AT event information object.
        :outcome: The outcome of the action.
        :status_code: The status code.
        :user: User object.
        :service_instance_id: The data_mart_id.
        :request_path: Value of request.path.
        :request_method: Value of request.method.
        :request_user_agent: Value of the context-header user-agent.

        :returns: None.
        """
        try:

            status_type, severity = cls.get_status_type_and_severity(
                status_code)

            # Checking cloud environment
            is_cpd = Env.is_cpd()

            # Getting the host address
            host = Env.get_pod_host() if is_cpd else Env.get_host()

            payload = {
                "action": at_event_info.action,
                "eventTime": DateUtil.get_current_datetime().isoformat(),
                "hostname": Env.get_pod_name(),
                "dataEvent": at_event_info.data_event,
                "initiator": {
                    "credential": {
                        "type": "token"
                    },
                    "host": {
                        "address": host,
                        "agent": request_user_agent
                    },
                    "id": user.iam_id,
                    "name": user.name,
                    "typeURI": "service/security/account/user"
                },
                "target": {
                    "id": cls.get_target_id(user, service_instance_id),
                    "name": Env.get_pod_name(),
                    "typeURI": "aiopenscale/{}".format(at_event_info.action),
                    "host": {
                        "address": host
                    }
                },
                "requestData": {
                    "path": request_path,
                    "type": request_method
                },
                "observer": {
                    "id": "target",
                    "name": user.iam_id
                },
                "logSourceCRN": user.crn,
                "name": user.bss_account_id,
                "message": at_event_info.message,
                "outcome": outcome,
                "pid": os.getpid(),
                "reason": {
                    "reasonCode": status_code,
                    "reasonType": status_type
                },
                "responseData": str(uuid.uuid4()).replace("-", ""),
                "saveServiceCopy": True,
                "severity": severity,
                "time": DateUtil.get_current_datetime().isoformat()
            }

            # Log AT details into a file
            if is_cpd:
                audit_logger_client = AuditLoggerClient()
                audit_logger_client.log_event(payload)
            else:
                # Getting the file path
                file_path = cls.get_file_path()

                # Writing payload to file
                with io.open(file_path, "a") as f:
                    f.write(json.dumps(payload))
                    f.write("\n")
        except Exception as exc:
            logging.error(
                "Failed to log Activity Tracker event. Error: " + str(exc))

        logging.info("Finished logging Activity Tracker event.")

        return

    @classmethod
    def get_file_path(cls) -> str:
        """
        Gets the file path with name to which the events are to be logged.

        :returns: The file path.
        """
        file_path = "/var/log/at/openscale/{}-{}.log".format(
            Env.get_atrk_service_name(), Env.get_pod_name())

        return file_path

    @classmethod
    def get_target_id(cls, user, service_instance_id) -> str:
        """
        Returns the target ID based on cloud environment.

        :returns: The target ID string.
        """
        target_id = None

        # Building the target ID
        if Env.is_cpd():
            target_id = "crn:v1:cp4d:private:aiopenscale:w/{}.{}:n/{}:{}:monitor_instance".format(
                Env.get_node_worker_name(), Env.get_icpd_external_route(), Env.get_namespace(), service_instance_id)
        else:
            target_id = "crn:v1:bluemix:public:aiopenscale:{}:a/{}:{}:monitor_instance".format(
                Env.get_region(), user.bss_account_id, service_instance_id)

        return target_id

    @classmethod
    def get_status_type_and_severity(cls, status_code: int) -> str:
        """
        Gets the status type and severity given the status code.
        :status_code: The HTTP status code.

        :returns: The status type.
        """
        """Status code dictionary and status_type and severity.
        Format: status_code: (status_type, severity)"""

        status_dict = {
            200: ("OK", "INFO"),
            201: ("Created", "INFO"),
            202: ("Accepted", "INFO"),
            203: ("Non-Authoritative Information", "INFO"),
            204: ("No Content", "INFO"),
            400: ("Bad Request", "ERROR"),
            401: ("Unauthorized", "ERROR"),
            403: ("Forbidden", "ERROR"),
            404: ("Not Found", "ERROR"),
            405: ("Method Not Allowed", "ERROR"),
            409: ("Conflict", "ERROR"),
            410: ("Gone", "ERROR"),
            415: ("Unsupported Media Type", "WARN"),
            429: ("Too Many Requests", "ERROR"),
            500: ("Internal Server Error", "ERROR"),
            501: ("Not Implemented", "ERROR"),
            502: ("Bad Gateway", "ERROR"),
            503: ("Service Unavailable", "ERROR"),
            504: ("Gateway Timeout", "ERROR"),
        }
        """Return None if the status code is not present."""

        return status_dict.get(status_code, (None, None))
