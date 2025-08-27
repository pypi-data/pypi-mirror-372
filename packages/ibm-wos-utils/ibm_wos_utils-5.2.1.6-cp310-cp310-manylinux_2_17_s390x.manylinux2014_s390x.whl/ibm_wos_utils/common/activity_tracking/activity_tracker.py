# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2023
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S. Copyright Office.
# ----------------------------------------------------------------------------------------------------

from ibm_wos_utils.common.activity_tracking.activity_tracker_utils import ActivityTrackerUtils, ActivityTrackingInfo
from ibm_wos_utils.common.security.user import User


class ActivityTracker:

    """
    Class for Activity tracking.

    Arguments:
    data_mart_id: The data mart id.
    """

    def __init__(self, service_instance_id):
        self.service_instance_id = service_instance_id

    def log(self, user: User, object_type: str, action_event: str, data_event: bool, message: str,  component: str, outcome: str, request_path: str, request_method: str, response_status_code: int,request_user_agent: str):
        """
        Logs activity for the  action.

        Arguments:
        :user: A user object for setting user details in Activity log.
        :object_type: The object-type can be quality-monitor_enable, quality-monitor_run, drift_v2-monitor_enable, drift_v2-monitor_run, etc., 
        :action_event: Action relatd to the activity.
        :data_event: Whether the activity is data event.
        :message: The message associated with the activity.
        :component: Which service has called this activity.
        :outcome: The outcome of the action.
        :request_path: Value of request.path.
        :request_method: Value of request.method.
        :request_user_agent: Value of the context-header user-agent.
        :response_status_code: The status code of the response.
        """

        # Initializing AT related variables
        at_event_info = ActivityTrackingInfo(
            action="aiopenscale.{}.{}".format(object_type, action_event),
            data_event=data_event,
            message="Watson Openscale: {}.{} {} {}".format(object_type, action_event, component,
                                                           message)
        )

        # Logging the AT event
        ActivityTrackerUtils.log_event(
            at_event_info=at_event_info,
            outcome=outcome,
            status_code=response_status_code,
            user=user,
            service_instance_id=self.service_instance_id,
            request_path=request_path,
            request_method=request_method,
            request_user_agent=request_user_agent or ""
        )
