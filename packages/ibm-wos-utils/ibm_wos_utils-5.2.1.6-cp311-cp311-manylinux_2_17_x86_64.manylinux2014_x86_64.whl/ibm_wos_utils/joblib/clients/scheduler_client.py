# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2020, 2021
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

import json
import uuid

from ibm_wos_utils.joblib.exceptions.client_errors import ClientError, MissingValueError
from ibm_wos_utils.joblib.utils.rest_util import RestUtil

class SchedulerClient():
    """
    Client to interact with the Scheduling service.
    """

    def __init__(self, gateway_url: str, bearer_token: str):
        """
        The constructor for the client.
        :gateway_url: The gateway URL.
        :bearer_token: The authorization token.
        """
        self.scheduler_url = "{}/v1/schedules".format(gateway_url if gateway_url[-1] != "/" else gateway_url[0:-1])
        self.bearer_token = bearer_token

    def create_schedule(self, application_id: str, start_date: str, status: str, repeat_interval: int, repeat_type: str, target_href: str, http_method: str, artifact_id: str, target_payload: dict, target_headers: list, end_date: str=None, max_invocations:int=None, target_auth_api_key: str=None, generate_iam_token: bool=False, name: str="IBM WOS Utils Schedule.", description: str="IBM WOS Utils Schedule.", tags: list=[]) -> dict:
        """
        Creates a schedule with the given parameters and returns the API response.
        :application_id: The application ID.
        :start_date: The start date for the schedule.
        :status: The status of the schedule (enable/disable).
        :repeat_interval: The repeat interval of the schedule.
        :repeat_type: The time unit to be used for each repeat interval.
        :target_href: The target URL for the schedule to call.
        :http_method: The HTTP method to be used for the given target URL.
        :artifact_id: The ID of the artifact for which the schedule is being created.
        :target_payload: The request payload to be sent while calling the target URL.
        :target_headers: The headers to be sent while calling the target URL.
        Example:
        [
            {
                "name": "content-type",
                "value": "application/json",
                "sensitive": false
            }
        ]
        *Note:* In case of CP4D the headers should contain the credentials and/or the impersonate headers to be able to call the given OpenScale APIs.
        :end_date: The end date for the schedule.
        :max_invocations: The maximum invocations to be done of the schedule.
        :target_auth_api_key: Required in case of cloud environment for the schedule to be able to generate token and use for the calls to the target URL.
        :generate_iam_token: Boolean flag to generate the IAM token (True in case of cloud environments).
        :name: The name of the schedule.
        :description: The description for the schedule.
        :tags: The list of tags for the schedule.
        """
        schedule_response = None

        if end_date is None and max_invocations is None:
            raise MissingValueError("end_date/max_invocations")

        # Building the request payload
        request_payload = {
            "application_id": application_id,
            "name": name,
            "description": description,
            "tags": tags,
            "start_date": start_date,
            "status": status,
            "repeat": {
                "repeat_interval": repeat_interval,
                "repeat_type": repeat_type
            },
            "repeat_end": {
                "end_date": end_date,
                "max_invocations": max_invocations
            },
            "target": {
                "href": target_href,
                "user_api_key": target_auth_api_key,
                "generate_iam_token": generate_iam_token,
                "method": http_method,
                "artifact_id": artifact_id,
                "payload": json.dumps(target_payload),
                "headers": target_headers
            }
        }
        headers = {
            "Accept": "application/json",
            "Authorization": "bearer {}".format(self.bearer_token),
            "Content-Type": "application/json"
        }

        # Making the REST call to create the schedule
        response = RestUtil.request().post(url=self.scheduler_url, json=request_payload, headers=headers)
        
        # Checking the response
        if not response.ok:
            # Schedule creation failed, raising an exception.
            raise ClientError("Create schedule call for application {}, artifact {} failed with status code {}. Error: {}".format(application_id, artifact_id, response.status_code, response.text))

        schedule_response = json.loads(response.text)
        return schedule_response
    
    def get_schedule(self, schedule_id: str) -> dict:
        """
        Returns the schedule object with the given ID.
        :schedule_id: The ID of the schedule to be retrieved.
        *Note:* The method absorbs the 404 error in case the schedule does not exist.
        """
        schedule_response = None

        # Generating the schedule URL
        schedule_url = "{}/{}".format(self.scheduler_url, schedule_id)
        headers = {
            "Accept": "application/json",
            "Authorization": "bearer {}".format(self.bearer_token)
        }

        # Making the REST call to get the schedule object
        response = RestUtil.request().get(url=schedule_url, headers=headers)
        
        # Checking the response
        if not response.ok:
            # Schedule retrieval failed, raising an exception.
            raise ClientError("Get schedule {} failed with status code {}. Error: {}".format(schedule_id, response.status_code, response.text))

        schedule_response = json.loads(response.text)
        return schedule_response
    
    def delete_schedule(self, schedule_id: str) -> None:
        """
        Deletes the schedule with the given ID.
        :schedule_id: The ID of the schedule to be deleted.
        """

        # Generating the schedule URL
        schedule_url = "{}/{}".format(self.scheduler_url, schedule_id)
        headers = {
            "Accept": "application/json",
            "Authorization": "bearer {}".format(self.bearer_token)
        }

        # Making the REST call to delete the schedule
        response = RestUtil.request().delete(url=schedule_url, headers=headers)

        # Checking the response
        if not response.ok and response.status_code != 404:
            # Schedule deletion failed, raising an exception.
            raise ClientError("Delete schedule {} failed with status code {}. Error: {}".format(schedule_id, response.status_code, response.text))
        return
    
    def list_schedules(self, application_id: str, limit: int=None, offset: int=None, sort: str=None, schedule_name: str=None, schedule_status: str=None, schedule_artifact_id: str=None) -> dict:
        """
        Lists all the schedules satisfying the given parameters.
        :application_id: The application/project ID to which the schedule belongs to.
        :limit: The limit to the number of schedules to be returned.
        :offset: The offset from where the schedules are to be read.
        :sort: The query to be used to sort the schedules.
        :schedule_name: Filters the result based on the given schedule name.
        :schedule_status: Filters the result based on the given schedule status.
        :schedule_artifact_id: Filters the result based on the given schedule artifact ID.
        """
        schedules_response = None

        # Generating the schedules URL
        schedule_url = "{}?application_id={}".format(self.scheduler_url, application_id)
        if limit:
            schedule_url += "&limit={}".format(limit)
        if offset:
            schedule_url += "&offset={}".format(offset)
        if sort:
            schedule_url += "&sort={}".format(sort)
        if schedule_name:
            schedule_url += "&entity.schedule.name={}".format(schedule_name)
        if schedule_status:
            schedule_url += "&entity.schedule.status={}".format(schedule_status)
        if schedule_artifact_id:
            schedule_url += "&entity.schedule.target.artifact_id={}".format(schedule_artifact_id)
        headers = {
            "Accept": "application/json",
            "Authorization": "bearer {}".format(self.bearer_token)
        }

        # Making the REST call to list the schedules
        response = RestUtil.request().get(url=schedule_url, headers=headers)

        # Checking the response
        if not response.ok:
            # Listing schedules failed, raising an exception.
            raise ClientError("List schedules for application {} failed with status code {}. Error: {}".format(application_id, response.status_code, response.text))

        schedules_response = json.loads(response.text)
        return schedules_response
    
    def delete_schedules(self, application_id: str, schedule_ids: list) -> None:
        """
        Deletes all the schedules in the given list of schedule IDs belonging to the given application/project.
        :application_id: The application/project ID to which the schedules belong to.
        :schedule_ids: The list of schedule IDs to be deleted.
        """

        # Generating the schedules URL
        schedule_url = "{}?application_id={}".format(self.scheduler_url, application_id)
        comma_separated_ids = ""
        for schedule_id in schedule_ids:
            comma_separated_ids += "{},".format(schedule_id)
        # Removing the last comma
        comma_separated_ids = comma_separated_ids[0:len(comma_separated_ids) - 1]
        schedule_url += "&schedule_ids={}".format(comma_separated_ids)
        headers = {
            "Accept": "application/json",
            "Authorization": "bearer {}".format(self.bearer_token)
        }

        # Making the REST call to delete the schedules
        response = RestUtil.request().delete(url=schedule_url, headers=headers)

        # Checking the response
        if not response.ok:
            # Deleting schedules failed, raising an exception.
            raise ClientError("Deleting schedules {} for application {} failed with status code {}. Error: {}".format(schedule_ids, application_id, response.status_code, response.text))
        return
    
    def patch_schedule(self, application_id: str, schedule_id: str, patch_payload: list) -> dict:
        """
        Patches the given schedule with the given payload and returns the patched schedule response.
        :application_id: The ID of the application/project to which the schedule belongs to.
        :schedule_id: The ID of the schedule to be patched.
        :patch_payload: The patch payload to be used to patch the schedule.
        """
        schedule_response = None

        # Generating the URL
        schedule_url = "{}/{}?application_id={}".format(self.scheduler_url, schedule_id, application_id)
        headers = {
            "Accept": "application/json",
            "Authorization": "bearer {}".format(self.bearer_token),
            "Content-Type": "application/json-patch+json"
        }

        # Making the REST call to patch the schedule
        response = RestUtil.request().patch(url=schedule_url, json=patch_payload, headers=headers)

        # Checking the response
        if not response.ok:
            # Patching the schedule failes, raising an exception.
            raise ClientError("Patching the schedule {} failed with status code {}. Error: {}".format(schedule_id, response.status_code, response.text))

        schedule_response = json.loads(response.text)
        return schedule_response
    
    def post_schedule_runs(self, schedule_id: str, target_execution_status_request: dict) -> None:
        """
        Posts the runs for the given schedule.
        :schedule_id: The ID of the schedule.
        :target_execution_status_request: The request payload.
        """

        # Generating the URL
        schedule_runs_url = "{}/{}/runs".format(self.scheduler_url, schedule_id)
        headers = {
            "Accept": "application/json",
            "Authorization": "bearer {}".format(self.bearer_token),
            "Content-Type": "application/json"
        }

        # Making the REST call to post the schedule runs
        response = RestUtil.request().post(url=schedule_runs_url, json=target_execution_status_request, headers=headers)

        # Checking the response
        if not response.ok:
            # POST schedule runs failed, raising an exception
            raise ClientError("POST schedule runs for schedule {} failed with status code {}. Error: {}".format(schedule_id, response.status_code, response.text))
        return
    
    def get_schedule_runs(self, schedule_id: str) -> dict:
        """
        Returns the runs of the given schedule.
        :schedule_id: The ID of the schedule.
        """
        schedule_runs_response = None

        # Generating the URL
        schedule_runs_url = "{}/{}/runs".format(self.scheduler_url, schedule_id)
        headers = {
            "Accept": "application/json",
            "Authorization": "bearer {}".format(self.bearer_token)
        }

        # Making the REST call to get the schedule runs
        response = RestUtil.request().get(url=schedule_runs_url, headers=headers)

        # Checking the response
        if not response.ok:
            # GET schedule runs failed, raising an exception
            raise ClientError("GET schedule runs for schedule {} failed with status code {}. Error: {}".format(schedule_id, response.status_code, response.text))

        schedule_runs_response = json.loads(response.text)
        return schedule_runs_response
    
    def get_schedule_metrics(self, application_id: str=None) -> dict:
        """
        Returns the metrics for the given schedule.
        :application_id: The ID of the application for whose schedules metrics are to be returned.
        """
        schedule_metrics_response = None

        # Generating the URL
        schedule_metrics_url = "{}/metrics".format(self.scheduler_url)
        if application_id:
            schedule_metrics_url += "?application_id={}".format(application_id)
        headers = {
            "Accept": "application/json",
            "Authorization": "bearer {}".format(self.bearer_token)
        }

        # Making the REST call to get the schedule metrics
        response = RestUtil.request().get(url=schedule_metrics_url, headers=headers)

        # Checking the response
        if not response.ok:
            # GET schedule metrics failed, raising an exception.
            raise ClientError("GET schedule metrics for application {} failed with status code {}. Error: {}".format(application_id, response.status_code, response.text))

        schedule_metrics_response = json.loads(response.text)
        return schedule_metrics_response