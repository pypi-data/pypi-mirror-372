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
import os
import pathlib
import time
import uuid
import logging
import tempfile
from pathlib import Path
from string import Template

from ibm_wos_utils.joblib.clients.engine import Client
from ibm_wos_utils.joblib.exceptions.client_errors import *
from ibm_wos_utils.joblib.utils import constants
from ibm_wos_utils.joblib.utils.constants import UPLOAD_FILE_RETRY_COUNT, UPLOAD_FILE_RETRY_STATUS_CODES
from ibm_wos_utils.joblib.utils.db_utils import DbUtils
from ibm_wos_utils.joblib.utils.joblib_utils import JoblibUtils
from ibm_wos_utils.joblib.utils.param_utils import get
from ibm_wos_utils.joblib.utils.rest_util import RestUtil
from ibm_wos_utils.joblib.utils.validator import validate_type
from requests.auth import HTTPBasicAuth

from ibm_wos_utils.joblib.utils.jobstatus_utils import get_common_job_status

logger = logging.getLogger(__name__)


class RemoteEngineClient(Client):

    def __init__(self, server_url, username, password):
        # Validate required parameters
        validate_type("server_url", server_url, str, True)
        validate_type("username", username, str, True)
        validate_type("password", password, str, True)

        self.server_url = server_url
        self.username = username
        self.password = password
        self.jobs_url = "/openscale/spark_wrapper/v1/jobs"
        self.files_url = "/openscale/spark_wrapper/v1/files"

        self.HDFS_BASE = "$hdfs/"

    def upload_job_artifacts(self, file_list, target_folder, overwrite=True):
        # Validate incoming parameters
        validate_type("file_list", file_list, list, True)
        validate_type("target_folder", target_folder, str, True)

        basic_auth = HTTPBasicAuth(self.username, self.password)
        for my_file in file_list:
            file_name = Path(my_file).name
            url = "{}{}?overwrite={}&file={}".format(
                self.server_url, self.files_url, overwrite, target_folder + "/" + file_name)

            # Retrying with backoff
            delay = 5  # Initial delay for retry
            backoff_factor = 2
            for i in range(UPLOAD_FILE_RETRY_COUNT):
                with open(my_file, "rb") as file_stream:
                    file_data = file_stream.read()
                    response = RestUtil.request().put(url=url, auth=basic_auth, headers={
                        "Content-Type": "application/octet-stream"}, data=bytes(file_data))
                if not response.ok:
                    # If status code is one of [not_found, gateway_timeout] then retry the operation
                    status_code = response.status_code
                    if status_code in UPLOAD_FILE_RETRY_STATUS_CODES:
                        if i == UPLOAD_FILE_RETRY_COUNT-1:
                            # Uploading failed even after retrying
                            raise MaxRetryError(
                                "upload_file", error=response.text)
                        # Retry with backoff
                        print("\nThe operation upload_file failed with status {}, retrying in {} seconds.".format(
                            status_code, delay))
                        time.sleep(delay)
                        delay *= backoff_factor
                    else:
                        raise DependentServiceError("Uploading of file {} failed. Error: ".format(
                            my_file, response.text), response)
                else:
                    # If response is successful, then breaking the loop
                    break
        return response.json()

    def run_job(self, job_name, job_class, job_args, data_file_list=None, background=True, timeout=constants.SYNC_JOB_MAX_WAIT_TIME):
        job_class_path = job_class.__module__ + "." + job_class.__name__
        # Validate incoming parameters
        validate_type("job_name", job_name, str, True)
        validate_type("job_class", job_class_path, str, True)
        validate_type("job_args", job_args, dict, True)
        validate_type("data_file_list", data_file_list, list, False)

        basic_auth = HTTPBasicAuth(self.username, self.password)

        # Push entry job if it is not already pushed
        entry_job_path = self.HDFS_BASE + constants.ENTRY_JOB_BASE_FOLDER
        # Upload the main job
        clients_dir = str(pathlib.Path(__file__).parent.absolute())
        file_list = [str(clients_dir) + "/../" + constants.ENTRY_JOB_FILE]
        self.upload_job_artifacts(file_list, entry_job_path)

        certificate_files = None

        # Create temp file containing the arguments json
        fp = tempfile.NamedTemporaryFile(delete=True)
        head, filename = os.path.split(fp.name)

        # Compose Job payload
        json_payload, data_path, output_file_path, arguments = self.__get_job_payload(
            job_name, job_class_path, job_args, filename)

        # If SSL certificate is specified in job parameters, then creating certificate files
        certificate_files = self.check_and_create_ssl_cert_files(arguments)

        # write arguments to file
        fp.write(bytes(json.dumps(arguments), 'utf-8'))
        fp.seek(0)
        if data_file_list is None:
            data_file_list = [fp.name]
        else:
            data_file_list.append(fp.name)

        # Creating list of files to be placed in the working directory of each executor
        files = []
        # If certificate file is created, uploading it to HDFS
        if certificate_files:
            for certificate_file in certificate_files:
                data_file_list.append(certificate_file)
                directory, cert_file_name = os.path.split(certificate_file)
                files.append("{}/{}".format(data_path, cert_file_name))

        # If there are some files to be put in working directory of each executor, adding them using files option.
        if files:
            json_payload["files"] = files

        self.upload_job_artifacts(data_file_list, data_path)

        # Run the job
        url = "{}/{}?background_mode={}&timeout={}".format(
            self.server_url, self.jobs_url, background, timeout)
        response = RestUtil.request().post(
            url=url, auth=basic_auth, json=json_payload, headers={"Content-Type": "application/json"})

        # delete the temp file
        fp.close()
        # If temporary file is created for ssl certificate, deleting it
        if certificate_files:
            for certificate_file in certificate_files:
                JoblibUtils.delete_local_file(certificate_file)

        if not response.ok:
            raise DependentServiceError(
                "Failed to run job. Error: {}".format(response.text), response)
        job_response = response.json()
        job_response["output_file_path"] = output_file_path
        state = job_response.get("state")
        job_response['state'] = get_common_job_status(str(state).lower()).value
        return job_response

    def get_job_status(self, job_id, job_name=None, output_file_path=None):

        # Validate incoming parameters
        validate_type("job_id", job_id, int, True)

        basic_auth = HTTPBasicAuth(self.username, self.password)
        url = "{}{}/{}/status?".format(self.server_url, self.jobs_url, job_id)
        response = RestUtil.request().get(url=url, auth=basic_auth, headers={})
        if not response.ok:
            raise DependentServiceError("Unable to get the status of job_id . Error {}".format(
                job_id, response.text), response)
        job_response = response.json()
        state = job_response.get("state")
        job_response['state'] = get_common_job_status(str(state).lower()).value

        if job_response['state'] == constants.JobStatus.FINISHED.value and job_name=="create_table_job":

            if not output_file_path:
                logger.warning("output file path must be specified to execute post processing steps for create table job.")

            try:
                table_info_json = self.get_file(output_file_path + "/table_info.json")
                table_info_json = json.loads(table_info_json)
                if table_info_json:
                    self.create_table_job_post_processing_steps(table_info_json)
            except Exception as e:
                logger.warn("An error occurred during the post processing of create table {}".format(str(e)))

        return job_response

    def get_file(self, file_path):
        # Validate incoming parameters
        validate_type("file_path", file_path, str, True)

        basic_auth = HTTPBasicAuth(self.username, self.password)
        url = "{}{}?file={}".format(self.server_url, self.files_url, file_path)
        response = RestUtil.request().get(url=url, auth=basic_auth, headers={})
        if not response.ok:
            raise DependentServiceError("Unable to get the file {}. Error {}".format(
                file_path, response.text), response)
        return response.content

    def get_exception(self, output_file_path):
        data = self.get_file(output_file_path + "/exception.json")
        return json.loads(data.decode("utf-8"))

    def get_job_logs(self, job_id):
        # Validate incoming parameters
        validate_type("job_id", job_id, int, True)
        raise NotImplementedError("kill_job")

    def delete_job_artifacts(self, job_id):
        # Validate incoming parameters
        validate_type("job_id", job_id, int, True)
        raise NotImplementedError("kill_job")

    def kill_job(self, job_id):
        #validate_type("job_id", job_id, int, True)
        raise NotImplementedError("kill_job")

    def __get_job_payload(self, job_name, job_class, param_dict, argumentfile_name):
        if "arguments" not in param_dict:
            param_dict["arguments"] = {}
        # copy original parameters
        original_argument = param_dict["arguments"].copy()
        subscription_id = get(
            param_dict, "arguments.subscription_id") or str(uuid.uuid4())
        run_id = get(param_dict, "arguments.monitoring_run_id") or str(
            uuid.uuid4())

        data_path = job_name + "/" + subscription_id + "/data"
        # removing original prameters and adding path related params so that $hdfs gets replaced by wrapper app
        param_dict["arguments"] = {}
        data_path = self.HDFS_BASE + data_path
        param_dict["arguments"]["data_file_path"] = data_path

        output_file_path = data_path[0:-5] + "/output/" + run_id
        param_dict["arguments"]["output_file_path"] = output_file_path
        param_dict["arguments"]["param_file_name"] = argumentfile_name

        # Get storage types
        storage_type_map = JoblibUtils.get_storage_types_from_data_sources(original_argument)
        param_dict["arguments"]["storage_type_map"] = storage_type_map

        # If the storage is common for all data sources, setting the storage type in arguments. This is to fix #29635
        if "storage" in original_argument:
            param_dict["arguments"]["storage_type"] = get(original_argument, "storage.type")

        # Add spark type in the arguments. WI #27704
        param_dict["arguments"]["spark_type"] = constants.SparkType.REMOTE_SPARK.value

        spark_settings = param_dict.get("spark_settings") or {}
        if (spark_settings is not None) and (len(spark_settings) != 0):
            # Update spark_settings to use modified parameter names
            JoblibUtils.update_spark_parameters(spark_settings)
        else:
            # TODO Need to remove this once every monitor passes it as parameter
            spark_settings["max_num_executors"] = "2"
            spark_settings["min_num_executors"] = "1"
            spark_settings["executor_cores"] = "2"
            spark_settings["executor_memory"] = "2"
            spark_settings["driver_cores"] = "2"
            spark_settings["driver_memory"] = "1"

        original_argument["spark_settings"] = spark_settings
        arg_str = json.dumps(param_dict["arguments"])
        arg_str = arg_str.replace('"', '\"').replace(
            '{', '\{').replace('}', '\}')

        arguments = [job_name, job_class, arg_str]
        replacement_dict = {}
        replacement_dict["arguments"] = arguments
        replacement_dict["hdfs"] = self.HDFS_BASE
        replacement_dict["dependency_zip"] = param_dict["dependency_zip"]
        replacement_dict["conf"] = param_dict.get("conf", {})
        if replacement_dict["conf"] is None:
            replacement_dict["conf"] = {}

        replacement_dict.update(spark_settings)
        clients_dir = pathlib.Path(__file__).parent.absolute()
        with open(str(clients_dir) + "/../jobs/livy_job.json.template", "r") as content_file:
            template_content = content_file.read()
        json_str = Template(template_content)
        json_str = json_str.substitute(replacement_dict)
        json_str = json_str.replace('"', '\\\"')
        json_str = json_str.replace("'", "\"")

        return json.loads(json_str), data_path, output_file_path, original_argument

    def download_directory(self, directory_path):
        # Validate incoming parameters
        validate_type("directory_path", directory_path, str, True)

        basic_auth = HTTPBasicAuth(self.username, self.password)
        url = "{}{}?directory={}".format(
            self.server_url, self.files_url, directory_path)
        response = RestUtil.request().get(url=url, auth=basic_auth, headers={})
        if not response.ok:
            raise DependentServiceError("Unable to get the directory {}. Error {}".format(
                directory_path, response.text), response)
        return response.content

    def delete_directory(self, directory_path):
        # Validate incoming parameters
        validate_type("directory_path", directory_path, str, True)

        basic_auth = HTTPBasicAuth(self.username, self.password)
        url = "{}{}?directory={}".format(
            self.server_url, self.files_url, directory_path)
        response = RestUtil.request().delete(url=url, auth=basic_auth, headers={})
        if not response.ok:
            logger.error("An error occurred while deleting the directory {0}. Error {1}".format(
                directory_path, response.text))
            raise DependentServiceError("Unable to delete the directory {0}. Error {1}".format(
                directory_path, response.text), response)
        return response.content

    def upload_directory(self, directory_path, archive_directory_content):
        # Validate incoming parameters
        validate_type("directory_path", directory_path, str, True)

        basic_auth = HTTPBasicAuth(self.username, self.password)
        url = "{}{}?directory={}".format(
            self.server_url, self.files_url, directory_path)
        response = RestUtil.request().put(url=url, data=archive_directory_content,
                                          auth=basic_auth, headers={})
        if not response.ok:
            logger.error("An error occurred while uploading the directory {0}. Error {1}".format(
                directory_path, response.text))
            raise DependentServiceError("Unable to upload the directory {0}. Error {1}".format(
                directory_path, response.text), response)
        response = response.text.replace("\"", "").replace("\n", "")
        return response
