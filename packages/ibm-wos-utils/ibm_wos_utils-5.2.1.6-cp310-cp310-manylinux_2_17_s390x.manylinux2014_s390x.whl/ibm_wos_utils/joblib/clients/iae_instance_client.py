# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2020, 2021
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

from http import HTTPStatus
import json
import datetime
import time
import urllib
import requests
import os
import pathlib
import tarfile
from time import sleep
import logging
from ibm_wos_utils.joblib.exceptions.client_errors import *
from ibm_wos_utils.joblib.utils import constants
from ibm_wos_utils.joblib.utils.constants import UPLOAD_FILE_RETRY_COUNT, UPLOAD_FILE_RETRY_STATUS_CODES, IAE_VOLUME_MOUNT_PATH, IAEJobsEndpointType
from ibm_wos_utils.joblib.utils.environment import Environment
from ibm_wos_utils.joblib.utils.joblib_utils import JoblibUtils
from ibm_wos_utils.joblib.utils.param_utils import get
from ibm_wos_utils.joblib.utils.validator import validate_type
from ibm_wos_utils.joblib.utils.rest_util import RestUtil

logger = logging.getLogger(__name__)

environment = Environment()

class IAEInstanceClient():

    """Client class to manage spark instance and data volumes"""

    def __init__(self, server_url, service_instance_name, service_instance_id, volume, token, fetch_spark_instance=False):
        self.server_url = server_url
        self.service_instance_name = service_instance_name
        self.service_instance_id = service_instance_id
        self.volume = volume
        self.token = token
        self.spark_instance = None
        self.service_instances_base_url = "{}/zen-data/v3/service_instances".format(self.server_url)
        if fetch_spark_instance:
            self.spark_instance = self.get_instance(name=self.service_instance_name)
        # Check if spark instance's volume is used to store WOS data. WI #28878
        self.check_if_instance_volume_used()
        # Fetch volume details to check volume existence. WI #27064
        self.volume_details = self.get_volume(self.volume)

    def get_instance(self, name=None):
        instance = self._get_instance(name=name)
        return IAESparkInstance(self.server_url, instance)

    def _get_instance(self, name=None):
        if name is None:
            name = constants.SPARK_INSTANCE
        validate_type("instance_name", name, str, is_mandatory=True)
        url = "{}?addon_type=spark".format(
            self.service_instances_base_url)

        response = RestUtil.request().get(
            url=url, headers=self.__get_headers(), verify=False)
        if not response.ok:
            raise DependentServiceError(
                "Getting spark instance failed.", response)
        instances = response.json().get("service_instances")
        instance = None
        # If service_instance_id is specified, use it to fetch the instance details, otherwise check instance name
        for service_instance in instances:
            if (self.service_instance_id and str(self.service_instance_id) == str(service_instance.get("id")) ) or \
                service_instance.get("display_name") == name:
                instance = service_instance
                break

        if instance is None:
            raise ObjectNotFoundError(
                "Spark instance with id {} and name '{}' could not be found.".format(self.service_instance_id, name))
        return instance

    def get_volume(self, name):
        validate_type("volume_name", name, str, is_mandatory=True)
        url = "{}?addon_type=volumes".format(
            self.service_instances_base_url)

        response = RestUtil.request().get(
            url=url, headers=self.__get_headers(), verify=False)
        if not response.ok:
            raise DependentServiceError(
                "Getting data volumes failed.", response)
        instances = response.json().get("service_instances")
        
        instance = next((i for i in instances if i.get(
            "display_name") == name), None)
        if instance is None:
            raise ObjectNotFoundError(
                "Volume with name '{}' could not be found.".format(name))
        return instance.get("ID")

    def get_instance_volume(self, service_name):
        if self.spark_instance is None:
            self.spark_instance = self.get_instance(service_name)
        instance = self.spark_instance.instace_details
        return instance["metadata"]["volumeName"]

    def create_instance(self, name=None):
        if name is None:
            name = constants.SPARK_INSTANCE
        vol_name = name + "Data"
        self.create_volume(
            name=vol_name,
            description="OpenScale spark volume",
            size="5Gi")
        payload = {
            "serviceInstanceType": "spark",
            "serviceInstanceDisplayName": name,
            "serviceInstanceVersion": "3.0.0",
            "preExistingOwner": False,
            "createArguments": {
                "metadata": {
                    "volumeName": vol_name,
                    "storageClass": "",
                    "storageSize": ""
                }
            },
            "parameters": {},
            "serviceInstanceDescription": "OpenScale spark instance",
            "metadata": {},
            "ownerServiceInstanceUsername": "",
            "transientFields": {}
        }
        url = "{}/zen-data/v2/serviceInstance".format(self.server_url)
        response = RestUtil.request().post(
            url=url, data=json.dumps(payload), headers=self.__get_headers(), verify=False)
        if not response.ok:
            raise DependentServiceError(
                "Creating spark instance {} failed.".format(name), response)
        return response.json().get("id")

    def create_volume(self, name, description, size="2Gi"):
        validate_type("volume_name", name, str, is_mandatory=True)
        payload = {
            "createArguments": {
                "metadata": {
                    "storageClass": "nfs-client",
                    "storageSize": size
                },
                "resources": {},
                "serviceInstanceDescription": description
            },
            "preExistingOwner": False,
            "serviceInstanceDisplayName": name,
            "serviceInstanceType": "volumes",
            "serviceInstanceVersion": "-",
            "transientFields": {}
        }

        url = "{}/zen-data/v2/serviceInstance".format(
            self.server_url)
        response = RestUtil.request().post(
            url=url, data=json.dumps(payload), headers=self.__get_headers(), verify=False)
        if not response.ok:
            raise DependentServiceError(
                "Creating volume {} failed.".format(name), response)
        return response.json().get("id")

    def delete_instance(self, name=None):
        if name is None:
            name = constants.SPARK_INSTANCE
        validate_type("instance_name", name, str, is_mandatory=True)
        vol_name = constants.SPARK_VOLUME
        payload = {"serviceInstanceType": "spark", "serviceInstanceVersion": "3.0.0",
                   "serviceInstanceDisplayName": name}
        url = "{}/zen-data/v2/serviceInstance".format(
            self.server_url)
        response = RestUtil.request().delete(
            url=url, data=json.dumps(payload), headers=self.__get_headers(), verify=False)
        if not response.ok:
            raise DependentServiceError(
                "Deleting spark instance {} failed.".format(name), response)
        self.delete_volume(name="aiosSparkData")

    def delete_volume(self, name=None):
        if name is None:
            name = constants.SPARK_VOLUME
        validate_type("volume_name", name, str, is_mandatory=True)
        """Deleting a volume doesn't delete from actual storage"""
        payload = {"serviceInstanceType": "volumes", "serviceInstanceVersion": "-",
                   "serviceInstanceDisplayName": name}
        url = "{}/zen-data/v2/serviceInstance".format(
            self.server_url)
        response = RestUtil.request().delete(
            url=url, data=json.dumps(payload), headers=self.__get_headers(), verify=False)
        if not response.ok:
            raise DependentServiceError(
                "Deleting volume {} failed.".format(name), response)

    def start_volume_file_server(self, name=None):
        if name is None:
            name = constants.SPARK_VOLUME
        validate_type("volume_name", name, str, is_mandatory=True)
        url = "{}/zen-data/v1/volumes/volume_services/{}".format(
            self.server_url, name)
        response = RestUtil.request().post(
            url=url, data=json.dumps({}), headers=self.__get_headers(), verify=False)
        if not response.ok:
            raise DependentServiceError(
                "Starting volume {} file server failed.".format(name), response)

    def stop_volume_file_server(self, name=None):
        if name is None:
            name = constants.SPARK_VOLUME
        validate_type("volume_name", name, str, is_mandatory=True)
        url = "{}/zen-data/v1/volumes/volume_services/{}".format(
            self.server_url, name)
        response = RestUtil.request().delete(
            url=url, headers=self.__get_headers(), verify=False)
        if not response.ok:
            raise DependentServiceError(
                "Stopping volume {} file server failed.".format(name), response)

    def get_directories(self, vol_name, path):
        validate_type("volume_name", vol_name, str, is_mandatory=True)
        validate_type("directory_path", path, str, is_mandatory=True)
        path = path.replace("/", "%2F")
        url = "{}/zen-volumes/{}/v1/volumes/directories/{}".format(
            self.server_url, vol_name, path)
        response = RestUtil.request().get(
            url=url, headers=self.__get_headers(), verify=False)
        if not response.ok:
            raise DependentServiceError(
                "Getting volume {} directories failed.".format(vol_name), response)
        return response.json()

    def upload_file(self, vol_name, src_file_path, tgt_file_path):
        validate_type("volume_name", vol_name, str, is_mandatory=True)
        validate_type("source_file_path", src_file_path,
                      str, is_mandatory=True)
        validate_type("target_file_path", tgt_file_path,
                      str, is_mandatory=True)
        tgt_file_path = tgt_file_path.replace("/", "%2F")
        url = "{}/zen-volumes/{}/v1/volumes/files/{}".format(
            self.server_url, vol_name, tgt_file_path)
        # Retrying with backoff
        delay = 5  # Initial delay for retry
        backoff_factor = 2
        for i in range(UPLOAD_FILE_RETRY_COUNT):
            with open(src_file_path, "rb") as f:
                response = RestUtil.request().put(
                    url=url, headers={
                        "Authorization": "Bearer {}".format(self.token)
                    }, files={"upFile": f}, verify=False)
            if not response.ok:
                # If status code is one of [not_found, gateway_timeout] then retry the operation
                status_code = response.status_code
                if status_code in UPLOAD_FILE_RETRY_STATUS_CODES:
                    if i == UPLOAD_FILE_RETRY_COUNT-1:
                        # Uploading failed even after retrying
                        raise MaxRetryError("upload_file", error=response.text)
                    # Retry with backoff
                    print("\nThe operation upload_file failed with status {}, retrying in {} seconds.".format(
                        status_code, delay))
                    time.sleep(delay)
                    delay *= backoff_factor
                else:
                    raise DependentServiceError(
                        "Uploading file to volume {} failed.".format(vol_name), response)
            else:
                # If response is successful, then breaking the loop
                break
        logger.info("\nSuccessfully uploaded file {} to volume {}".format(
            src_file_path, vol_name))
        print("Successfully uploaded file {} to volume {} at location {}".format(
            src_file_path, vol_name, tgt_file_path))
        return response.json()

    def create_archive(self, src_dir):
        validate_type("source_directory", src_dir, str, is_mandatory=True)
        dir_name = os.path.basename(src_dir)
        tar_file = dir_name+".tar.gz"
        with tarfile.open(tar_file, "w:gz") as tar:
            tar.add(src_dir, arcname=dir_name)

        return tar_file

    def upload_archive(self, vol_name, archive_file, tgt_file_path):
        validate_type("volume_name", vol_name, str, is_mandatory=True)
        validate_type("archive_file", archive_file, str, is_mandatory=True)
        validate_type("target_file_path", tgt_file_path,
                      str, is_mandatory=True)
        tgt_file_path = tgt_file_path.replace("/", "%2F")
        url = "{}/zen-volumes/{}/v1/volumes/files/{}?extract=true".format(
            self.server_url, vol_name, tgt_file_path)
        with open(archive_file, "rb") as f:
            response = RestUtil.request().put(
                url=url, headers={
                    "Authorization": "Bearer {}".format(self.token)
                }, files={"upFile": f}, verify=False)

        if not response.ok:
            raise DependentServiceError("Uploading archive {} to volume {} failed.".format(
                archive_file, vol_name), response)
        print("Successfully uploaded archive {} to volume {} at location {}".format(
            archive_file, vol_name, tgt_file_path))
        return response.json()

    def pretty_print_POST(self, req):
        """
        At this point it is completely built and ready
        to be fired; it is "prepared".

        However pay attention at the formatting used in 
        this function because it is programmed to be pretty 
        printed and may differ from the actual request.
        """
        print('{}\n{}\r\n{}\r\n\r\n{}'.format(
            '-----------START-----------',
            req.method + ' ' + req.url,
            '\r\n'.join('{}: {}'.format(k, v) for k, v in req.headers.items()),
            req.body,
        ))

    def get_files_from_dir(self, vol_name, file_path):
        validate_type("volume_name", vol_name, str, is_mandatory=True)
        validate_type("file_path", file_path, str, is_mandatory=True)
        file_path = file_path.replace("/", "%2F")
        url = "{}/zen-volumes/{}/v1/volumes/directories/{}".format(
            self.server_url, vol_name, file_path)
        response = RestUtil.request().get(
            url=url, headers={
                "Authorization": "Bearer {}".format(self.token)
            }, verify=False)

        if not response.ok:
            raise DependentServiceError("Getting list of files in directory {} from volume {} failed.".format(
                file_path, vol_name), response)
        response = response.json()
        file_list = []
        if "responseObject" in response and "directoryContents" in response["responseObject"]:
            file_list = response["responseObject"]["directoryContents"]
        return file_list

    def get_file(self, vol_name, file_path):
        validate_type("volume_name", vol_name, str, is_mandatory=True)
        validate_type("file_path", file_path, str, is_mandatory=True)
        file_name = os.path.basename(file_path)

        if file_path.startswith(IAE_VOLUME_MOUNT_PATH):
            file_path = file_path[len(IAE_VOLUME_MOUNT_PATH):]

        file_path = file_path.replace("/", "%2F")
        url = "{}/zen-volumes/{}/v1/volumes/files/{}".format(
            self.server_url, vol_name, file_path)
        response = RestUtil.request().get(
            url=url, headers={
                "Authorization": "Bearer {}".format(self.token)
            }, verify=False)

        if not response.ok:
            raise DependentServiceError(
                "Getting file {} from volume {} failed.".format(file_path, vol_name), response)
        logger.info("Successfully read file {} from volume {}.".format(
            file_path, vol_name))
        return response.content

    def delete_file(self, vol_name, file_path):
        validate_type("volume_name", vol_name, str, is_mandatory=True)
        validate_type("file_path", file_path, str, is_mandatory=True)
        file_path = file_path.replace("/", "%2F")
        url = "{}/zen-volumes/{}/v1/volumes/files/{}".format(
            self.server_url, vol_name, file_path)
        response = RestUtil.request().delete(
            url=url, headers={
                "Authorization": "Bearer {}".format(self.token)
            }, verify=False)

        if not response.ok:
            logger.error("Volume {} delete file failed. Response {}".format(
                vol_name, response.text))
            raise DependentServiceError(
                "Deleting file {} from volume {} failed.".format(file_path, vol_name), response)
        logger.info("Successfully deleted file {} from volume {}".format(
            file_path, vol_name))

    def get_instance_token(self, instance_id):
        url = "{}/zen-data/v2/serviceInstance/token".format(self.server_url)
        response = RestUtil.request().post(
            url=url, data=json.dumps({"serviceInstanceID": str(instance_id)}), headers=self.__get_headers(), verify=False)
        if not response.ok:
            raise DependentServiceError(
                "Getting token for service instance id {} failed.".format(instance_id), response)
        return response.json().get("AccessToken")

    def run_job(self, job_json, background=True, timeout=constants.SYNC_JOB_MAX_WAIT_TIME):
        validate_type("job_payload", job_json, dict, is_mandatory=True)
        if self.spark_instance is None:
            self.spark_instance = self.get_instance(name=self.service_instance_name)
        job_url = self.spark_instance.jobs_url
        #instance_token = self.get_instance_token(spark_instance.instance_id)

        logger.info("Submitting spark job to IAE instance {}. Job URL: {}".format(
            self.spark_instance.instance_id, job_url))
        response = requests.post(
            url=job_url, json=job_json, headers=self.__get_headers(), verify=False)
        if not response.ok:
            # Response code will be 503 when there are insufficient resources.
            if response.status_code == HTTPStatus.SERVICE_UNAVAILABLE.value:
                raise ServiceUnavailableError(response)
            raise DependentServiceError("Failed to run job.", response)
        job_response = response.json()
        if self.spark_instance.use_iae_v4:
            job_id = job_response.get("application_id")
            state = job_response.get("state")
        else:
            job_id = job_response.get("id")
            state = job_response.get("job_state")
        job_response["id"] = job_id
        # Add state field to response which is used by calling service
        job_response["state"] = str(state).lower()
        print("\nSuccessfully submitted spark job to IAE instance {}. Job ID: {}, Status {}".format(
            self.spark_instance.instance_id, job_id, state))
        logger.info("Successfully submitted spark job to IAE instance {}. Job ID: {}, Status {}".format(
            self.spark_instance.instance_id, job_id, state))
        if background is False:
            start_time = time.time()
            elapsed_time = 0
            sleep_time = 15
            while state not in (constants.IAE_JOB_FINISHED_STATE, constants.IAE_JOB_FAILED_STATE, constants.IAE_JOB_STOPPED_STATE):
                if elapsed_time > timeout:
                    raise Exception(
                        "Job didn't come to FINISHED/FAILED/STOPPED state in {} seconds. Current state is {}".format(timeout, state))
                print("{}: Sleeping for {} seconds. Current state {}".format(
                    datetime.datetime.now(), sleep_time, state))
                sleep(sleep_time)
                elapsed_time = time.time() - start_time
                job_status_response = self.get_job_state(job_id, job_url=job_url)
                state = job_status_response.get("state")

            # Update latest job state to the response at the end of loop in case of sync job
            job_response["state"] = str(state).lower()
        # Sometimes the API to get status returns finished status even when job is failed. So checking the status again in when API returns status as finished. WI 21371
        if str(state).lower() in constants.JOB_FINISHED_STATES:
            job_status_response = self.get_job_state(job_id, job_url=job_url)
            state = job_status_response.get("state")
            job_response["state"] = str(state).lower()
        return job_response

    def delete_job(self, job_id):
        validate_type("job_id", job_id, str, is_mandatory=True)
        spark_instance = self.get_instance(name=self.service_instance_name)
        jobs_url = spark_instance.jobs_url + "/" + job_id

        response = requests.delete(
            url=jobs_url, headers=self.__get_headers(), verify=False)
        if not response.ok:
            raise DependentServiceError(
                "Failed to delete job with URL {}.".format(jobs_url), response)
        return

    def get_job_state(self, job_id, instance_token=None, job_url=None):
        validate_type("job_id", job_id, str, is_mandatory=True)
        if self.spark_instance is None:
            self.spark_instance = self.get_instance(name=self.service_instance_name)
        if job_url is None:
            job_url = self.spark_instance.jobs_url
        if not job_url.endswith(job_id):
            job_url = job_url + "/" + job_id

        # Sometimes jobs status API returns incorrect status in case of Failed job.
        # We need to check driver_state also to conclude that job successfully completed
        if "driver_state=true" not in job_url:
            job_url += "?driver_state=true"

        response = RestUtil.request().get(
            url=job_url, headers=self.__get_headers(), verify=False)
        if not response.ok:
            raise DependentServiceError(
                "Failed to get status for job with id {}.".format(job_id), response)
        job_response = response.json()

        job_state = None
        driver_state = None
        # If response of get status API is a list when called from run_job, get the status from 1st element
        if type(job_response) is list:
            job_response = job_response[0]

        if self.spark_instance.use_iae_v4:
            job_state = job_response.get("state")
        else:
            job_state = job_response.get("job_state")
        driver_state = job_response.get("driver_state")

        # Log job status. Log only required fields instead of logging entire API response. WI #26209
        job_status = {
            "job_id": job_id,
            "state": job_state
        }
        if driver_state:
            job_status["driver_state"] = driver_state
        if "state_details" in job_response:
            job_status["state_details"] = job_response.get("state_details")
        logger.info("Job status details: {}".format(
            str(job_status)))

        # If job state is finished, check for driver_state to conclude that job successfully completed
        # If job state is finished but driver state is error, then return driver state else return job state
        if str(job_state).lower() in constants.JOB_FINISHED_STATES and (driver_state is not None and str(driver_state).lower() in constants.JOB_FAILED_STATES):
            job_status["state"] = driver_state
            
        # Returning entire response instead of just state as response contains state_details which can be used to know root cause in case of failure. WI #31007
        return job_status

    def get_job_logs(self, job_id):
        raise NotImplementedError("get_job_logs")

    def delete_job_artifacts(self, job_id):
        raise NotImplementedError("delete_job_artifacts")

    def __get_headers(self):
        return {"Authorization": "Bearer {}".format(self.token),
                "Content-Type": "application/json"}

    def kill_job(self, job_id):
        raise NotImplementedError("kill_job")

    def get_resource_quota(self, instance_url):
        logger.info("Fetching resource quota for the spark instance. Instance URL: {}".format(
            instance_url))
        response = requests.get(
            url=instance_url, headers=self.__get_headers(), verify=False)
        if not response.ok:
            logger.warning(
                "Error while fetching resource quota for the spark instance. Error {}".format(response.text))
            return None
        resource_details = response.json()
        resource_quota = resource_details.get("resource_quota")
        if not resource_quota:
            resource_quota = {}
            resource_quota["cpu_quota"] = resource_details.get("cpu_quota")
            memory_quota = resource_details.get("memory_quota")
            resource_quota["memory_quota_gibibytes"] = int(
                memory_quota.replace("g", ""))
            resource_quota["avail_cpu_quota"] = resource_details.get(
                "available_cpu_quota")
            avail_memory_quota = resource_details.get("availalbe_memory_quota")
            resource_quota["avail_memory_quota_gibibytes"] = int(
                avail_memory_quota.replace("g", ""))
        return resource_quota

    def check_resource_quota(self, resource_quota, job_payload):
        if resource_quota and job_payload:
            if self.spark_instance.use_iae_v4:
                num_workers = int(get(job_payload, "application_details.num-executors"))
                executor_cores = int(get(job_payload, "application_details.executor-cores"))
                executor_memory = get(
                    job_payload, "application_details.executor-memory")
                executor_memory = int(executor_memory.replace("G", ""))
                driver_cores = int(get(job_payload, "application_details.driver-cores"))
                driver_memory = get(job_payload, "application_details.driver-memory")
                driver_memory = int(driver_memory.replace("G", ""))
            else:
                num_workers = get(job_payload, "engine.size.num_workers")
                executor_cores = get(job_payload, "engine.size.worker_size.cpu")
                executor_memory = get(
                    job_payload, "engine.size.worker_size.memory")
                executor_memory = int(executor_memory.replace("g", ""))
                driver_cores = get(job_payload, "engine.size.driver_size.cpu")
                driver_memory = get(job_payload, "engine.size.driver_size.memory")
                driver_memory = int(driver_memory.replace("g", ""))

            required_cpu = num_workers * executor_cores + driver_cores
            required_memory = num_workers * executor_memory + driver_memory
            available_cpu = resource_quota.get("avail_cpu_quota")
            available_memory = resource_quota.get(
                "avail_memory_quota_gibibytes")

            if required_cpu > available_cpu or required_memory > available_memory:
                error_message = "The available resource quota(CPU {} cores, Memory {}g) is less than the resource quota requested by the job(CPU {} cores, Memory {}g). Please increase the resource quota and retry.".format(
                    available_cpu, available_memory, required_cpu, required_memory)
                raise ServiceUnavailableError(message=error_message)

    def get_secret_from_vault(self, secret_urn: str):
        logger.info("Fetching zen-secret from the vault.")
        validate_type("secret_urn", secret_urn, str, is_mandatory=True)
        url = "{}/zen-data/v2/secrets/{}".format(self.server_url, secret_urn)
        response = RestUtil.request().get(
            url=url, headers=self.__get_headers(), verify=False)
        if not response.ok:
            raise DependentServiceError(
                "Error while fetching zen-secret the vault.", response)

        logger.info("Successfully fetched zen-secret from the vault.")
        return response.json()

    def invoke_delegation_token_provider(self, endpoint: str):
        logger.info("Fetching delegation token from the custom API endpoint.")
        validate_type("endpoint", endpoint, str, is_mandatory=True)
        response = RestUtil.request().get(
            url=endpoint, headers=self.__get_headers(), verify=False)
        if not response.ok:
            raise DependentServiceError(
                "Error while fetching delegation token from the custom API endpoint.", response)

        logger.info(
            "Successfully fetched delegation token from the custom API endpoint.")
        return response.json()

    def check_if_instance_volume_used(self):
        # As per IAE documentation, spark instance's volume should not be used to store job data.
        # Doc links: https://www.ibm.com/docs/en/cloud-paks/cp-data/4.6.x?topic=spark-accessing-data-from-applications and https://www.ibm.com/docs/en/cloud-paks/cp-data/4.6.x?topic=jobs-spark-api-syntax-parameters-return-codes
        instance_volume = self.get_instance_volume(self.service_instance_name)
        if instance_volume is not None and instance_volume == self.volume:
            raise BadRequestError("IAE Spark job can not access data stored on spark instance's (default) volume, please use a different volume to store WOS related data. Related documentation link: https://www.ibm.com/docs/en/cloud-paks/cp-data/4.6.x?topic=spark-accessing-data-from-applications")

class IAESparkInstance():
    def __init__(self, server_url, instance):
        validate_type("server_url", server_url, str, is_mandatory=True)
        validate_type("spark_instance", instance, dict, is_mandatory=True)
        self.analytics_engines_base_url = "{}/v4/analytics_engines".format(server_url)
        self.instace_details = instance
        self.use_iae_v4 = False
        connection_info = instance.get("connection_info")
        # Check if spark instance has V4 or V3 endpoint. If not found, then fallback to use V2 endpoint
        spark_jobs_endpoint = None
        if IAEJobsEndpointType.V4_ENDPOINT.value in connection_info or IAEJobsEndpointType.V3_ENDPOINT.value in connection_info:
            spark_jobs_endpoint = connection_info.get(IAEJobsEndpointType.V4_ENDPOINT.value)
            if not spark_jobs_endpoint:
                spark_jobs_endpoint = connection_info.get(IAEJobsEndpointType.V3_ENDPOINT.value)
            self.use_iae_v4 = True
        else:
            spark_jobs_endpoint = connection_info.get(IAEJobsEndpointType.V2_ENDPOINT.value)
            if spark_jobs_endpoint is None or spark_jobs_endpoint.strip() == "":
                spark_jobs_endpoint = connection_info.get(IAEJobsEndpointType.V1_ENDPOINT.value)

        # Fetch spark instance_id from the url
        self.instance_id = JoblibUtils.get_spark_instance_id_from_url(spark_jobs_endpoint)

        # Add jobs_url which is used to submit job and instance_url which is used to check available resource quota
        # If it is V4 or V3 instance then use V4 endpoint, otherwise fallback to V2
        if self.use_iae_v4:
            self.instance_url = "{}/{}".format(self.analytics_engines_base_url, self.instance_id)
            self.jobs_url = "{}/spark_applications".format(self.instance_url)
        else:
            self.jobs_url = spark_jobs_endpoint.replace(
            "$HOST", server_url)
            instance_endpoint = spark_jobs_endpoint.split("/v2/jobs")[0]
            self.instance_url = instance_endpoint.replace(
                "$HOST", server_url)
