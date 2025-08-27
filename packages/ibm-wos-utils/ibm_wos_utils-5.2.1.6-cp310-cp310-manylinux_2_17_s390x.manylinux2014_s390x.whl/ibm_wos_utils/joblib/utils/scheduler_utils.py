# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2020, 2021
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

from ibm_wos_utils.joblib.clients.scheduler_client import SchedulerClient

"""
File to contain utility methods and objects to be used while dealing with the Scheduling service.
"""


class WOSScheduleObject():

    def __init__(self, data_mart_id: str, subscription_id: str, monitor_definition_id: str, monitor_instance_id: str, monitoring_run_id: str, start_date: str, repeat_interval: int, repeat_type: str, job_class: str, job_name: str, job_id: str, target_href: str, http_method: str, target_payload: dict, target_headers: list, scheduler_client: SchedulerClient, max_invocations: int = None, status: str = "enabled", end_date: str = None, target_auth_api_key: str = None, generate_iam_token: bool = False):
        """
        Constructs the WOSScheduleObject with the given parameters.
        :gateway_url: The WOS gateway URL.
        :data_mart_id: The data mart ID.
        :subscription_id: The subscription ID.
        :monitor_definition_id: The monitor definition ID.
        :monitor_instance_id: The monitor instance ID.
        :monitoring_run_id: The monitoring run ID.
        :start_date: The start date for the schedule.
        :repeat_interval: The repeat interval of the schedule.
        :repeat_type: The repeat interval type (seconds/minutes/hour/et cetera).
        :job_class: The qualified name of the job file.
        :job_name: The name of the job.
        :job_id: The job ID.
        :target_href: The target URL for the schedule.
        :http_method: The HTTP method to be used by the schedule for the target REST call.
        :target_payload: The request payload for the target REST call.
        :target_headers: The request headers to be sent for the target REST call.
        :scheduler_client: The scheduler client object for creating the schedule.
        :max_invocations: The maximum number of invocations for the schedule.
        :status: The initial status of the schedule.
        :end_date: The end date of the schedule.
        :target_auth_api_key: The API key to be used for generating token (For public cloud environments).
        :generate_iam_token: The boolean flag for token generation in schedule.
        """
        self.data_mart_id = data_mart_id
        self.subscription_id = subscription_id
        self.monitor_definition_id = monitor_definition_id
        self.monitor_instance_id = monitor_instance_id
        self.monitoring_run_id = monitoring_run_id
        self.start_date = start_date
        self.repeat_interval = repeat_interval
        self.repeat_type = repeat_type
        self.job_class = job_class
        self.job_name = job_name
        self.job_id = job_id
        self.target_href = target_href
        self.http_method = http_method
        self.target_payload = target_payload
        self.target_headers = target_headers
        self.scheduler_client = scheduler_client
        self.max_invocations = max_invocations
        self.status = status
        self.end_date = end_date
        self.target_auth_api_key = target_auth_api_key
        self.generate_iam_token = generate_iam_token


class SchedulerUtil():

    @classmethod
    def get_schedules_app_id(cls, data_mart_id: str, subscription_id: str, monitor_definition_id: str) -> str:
        """
        Returns the application ID used to create all the schedules for Spark jobs based on the environment for the given monitor.
        :data_mart_id: The data mart ID.
        :subscription_id: The subscription ID.
        :monitor_definition_id: The monitor definition ID.
        """
        return "{}_BATCH_DM_{}_SB_{}".format(monitor_definition_id.upper(), data_mart_id, subscription_id)

    @classmethod
    def get_schedule_name(cls, monitor_definition_id: str, monitor_instance_id: str, monitoring_run_id: str) -> str:
        """
        Returns the name of the schedule to be submitted for the polling of Spark job of given monitor, monitor instance and run.
        :monitor_definition_id: The monitor definition ID.
        :monitor_instance_id: The monitor instance ID.
        :monitoring_run_id: The monitoring run ID.
        """
        return "{}_BATCH_MI_{}_MR{}".format(monitor_definition_id.upper(), monitor_instance_id, monitoring_run_id)

    @classmethod
    def create_job_polling_schedule(cls, wos_schedule_object: WOSScheduleObject) -> dict:
        """
        Creates a schedule to poll the status of the given job with the given schedule parameters object.
        :wos_schedule_object: The WOS schedule object.
        """
        schedule_response = None

        # Building the parameters for the schedule

        # The application ID under which all given monitor job-related schedules are created
        application_id = cls.get_schedules_app_id(
            wos_schedule_object.data_mart_id, wos_schedule_object.subscription_id, wos_schedule_object.monitor_definition_id)

        # The artifact ID for which the schedule is being created
        artifact_id = wos_schedule_object.job_id

        # The name of the schedule
        name = cls.get_schedule_name(wos_schedule_object.monitor_definition_id,
                                     wos_schedule_object.monitor_instance_id, wos_schedule_object.monitoring_run_id)

        # The tags to be set in the schedule
        tags = [
            wos_schedule_object.monitor_definition_id,
            wos_schedule_object.job_class,
            wos_schedule_object.job_name,
            wos_schedule_object.job_id
        ]

        # Calling the client to create the schedule
        schedule_response = wos_schedule_object.scheduler_client.create_schedule(application_id, wos_schedule_object.start_date, wos_schedule_object.status, wos_schedule_object.repeat_interval, wos_schedule_object.repeat_type, wos_schedule_object.target_href, wos_schedule_object.http_method, artifact_id,
                                                                                 wos_schedule_object.target_payload, wos_schedule_object.target_headers, end_date=wos_schedule_object.end_date, max_invocations=wos_schedule_object.max_invocations, target_auth_api_key=wos_schedule_object.target_auth_api_key, generate_iam_token=wos_schedule_object.generate_iam_token, name=name, tags=tags)

        return schedule_response
