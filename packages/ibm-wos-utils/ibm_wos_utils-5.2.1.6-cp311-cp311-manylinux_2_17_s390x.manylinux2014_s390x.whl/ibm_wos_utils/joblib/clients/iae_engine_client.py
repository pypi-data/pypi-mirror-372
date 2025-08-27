# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2020, 2021
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

import json
import os
import pathlib
import uuid
import tempfile
import tarfile
import logging
import tempfile
from string import Template

from ibm_wos_utils.joblib.clients.engine import Client
from ibm_wos_utils.joblib.clients.iae_instance_client import IAEInstanceClient
from ibm_wos_utils.joblib.exceptions.client_errors import *
from ibm_wos_utils.joblib.utils import constants
from ibm_wos_utils.joblib.utils.constants import DELEGATION_TOKEN_PARAMS
from ibm_wos_utils.joblib.utils.db_utils import DbUtils
from ibm_wos_utils.joblib.utils.joblib_utils import JoblibUtils
from ibm_wos_utils.joblib.utils.param_utils import get
from ibm_wos_utils.joblib.utils.validator import validate_type

from ibm_wos_utils.joblib.utils.jobstatus_utils import get_common_job_status

logger = logging.getLogger(__name__)


class IAEEngineClient(Client):

    def __init__(self, server_url, service_instance_name, service_instance_id, volume, token):
        super().__init__()
        validate_type('server_url', server_url, str, is_mandatory=True)
        validate_type('token', token, str, is_mandatory=True)
        self.server_url = server_url
        self.service_instance_name = service_instance_name
        self.service_instance_id = service_instance_id
        self.volume = volume
        self.token = token
        self.files_url = '/spark_wrapper/v1/files'
        self.iae_instance_client = IAEInstanceClient(
            self.server_url, self.service_instance_name, self.service_instance_id, self.volume, self.token, fetch_spark_instance=True)

    def upload_job_artifacts(self, file_list, target_folder, overwrite=True):
        """
        Method to upload job artifacts.
        :param file_list: List of files to upload
        :type file_list: list
        :param target_folder: Path of destination directory where files will be uploaded
        :type target_folder: str
        :param overwrite: Flag to indicate whether to overwrite file
        :type overwrite: bool
        """
        try:
            #volume = self.iae_instance_client.get_instance_volume(self.service_instance_name)
            for file in file_list:
                folder_path, file_name = os.path.split(file)
                self.iae_instance_client.upload_file(self.volume, file,
                                                     target_folder + "/{}".format(file_name))
        except ClientError as clerr:
            raise clerr
        except Exception as e:
            raise ClientError(
                "Error while uploading job artifacts. Error: {}".format(str(e)))

    def run_job(self, job_name, job_class, job_args, data_file_list=None, background=True, timeout=constants.SYNC_JOB_MAX_WAIT_TIME):
        """
        Method to submit spark job.
        :param job_name: Name of the job
        :type job_name: str
        :param job_class: Job class to be executed
        :type job_class: str
        :param job_args: Input parameters to the job
        :type job_args: dict
        :param data_file_list: List of files to be uploaded, if any
        :type data_file_list: list
        :param background: Flag to indicate whether to run job in async mode 
        :type job_type: bool
        """
        certificate_file = None
        try:
            job_class_path = job_class.__module__ + "." + job_class.__name__
            validate_type("job_name", job_name, str, True)
            validate_type("job_class", job_class_path, str, True)
            validate_type("job_args", job_args, dict, True)
            # Push entry job
            entry_job_path = constants.ENTRY_JOB_BASE_FOLDER
            # Upload the main job
            clients_dir = str(pathlib.Path(__file__).parent.absolute())
            file_list = [str(clients_dir) + "/../" + constants.ENTRY_JOB_FILE]
            self.upload_job_artifacts(file_list, entry_job_path)

            certificate_files = None

            # Create temp file containing the arguments json
            fp = tempfile.NamedTemporaryFile(delete=True)
            head, filename = os.path.split(fp.name)

            # Compose job payload
            json_payload, data_path, output_file_path, arguments = self.get_job_payload(
                job_name, job_class_path, job_args, filename)

            # If SSL certificate is specified in job parameters, then create certificate file and upload to volume
            certificate_files = self.check_and_create_ssl_cert_files(arguments)

            # Check if default volume associated with the spark instance is used. If yes, remove it from job payload.
            instance_volume = self.iae_instance_client.get_instance_volume(
                self.service_instance_name)
            default_volume_used = JoblibUtils.is_default_volume_used(
                json_payload, instance_volume)
            if default_volume_used:
                if json_payload.get("volumes"):
                    del json_payload["volumes"]
                else:
                    del json_payload["engine"]["volumes"]

            # write arguments to file
            fp.write(bytes(json.dumps(arguments), 'utf-8'))
            fp.seek(0)
            if data_file_list is None:
                data_file_list = [fp.name]
            else:
                data_file_list.append(fp.name)

            if certificate_files:
                # Upload certificate file to volume
                data_file_list.extend(certificate_files)

            # Upload dependent files, if any
            if data_file_list is not None and len(data_file_list) > 0:
                self.upload_job_artifacts(data_file_list, data_path)

            # Submit the job
            job_response = None
            try:
                job_response = self.iae_instance_client.run_job(
                    json_payload, background, timeout)
            except Exception as ex:
                raise ex
            finally:
                # delete the temp file
                fp.close()

            job_response['output_file_path'] = output_file_path
            state = job_response.get("state")
            job_response['state'] = get_common_job_status(
                str(state).lower()).value
            job_response['job_data_path'] = data_path

            return job_response

        except ClientError as clerr:
            raise clerr
        except Exception as e:
            raise ClientError(
                "Error while executing spark job. Error: {}".format(str(e)))
        finally:
            # If temporary file is created for ssl certificate_file, delete it
            if certificate_files:
                for certificate_file in certificate_files:
                    JoblibUtils.delete_local_file(certificate_file)

    def get_job_status(self, job_id, job_name=None, output_file_path=None):
        """
        Method to get status of spark job.
        :param job_id: ID of the job
        :type job_id: str
        :param job_state: Status of the job
        :type job_state: str
        """
        try:
            response = self.iae_instance_client.get_job_state(job_id)
            status = response.get("state")
            # Sometimes the API to get status returns finished status even when job is failed. So checking the status again in when API returns status as finished. WI 21371
            if str(status).lower() in constants.JOB_FINISHED_STATES:
                response = self.iae_instance_client.get_job_state(job_id)
                status = response.get("state")
            state = get_common_job_status(str(status).lower()).value
            # Updating common job state in the response
            response["state"] = state

            if state == constants.JobStatus.FINISHED.value and job_name=="create_table_job":
                if not output_file_path:
                    logger.warning("output file path must be specified to execute post processing steps for create table job.")

                try:
                    table_info_json = self.get_file(output_file_path + "/table_info.json")
                    if table_info_json:
                        table_info_json = json.loads(table_info_json)
                        self.create_table_job_post_processing_steps(table_info_json)
                except Exception as e:
                    logger.warn("An error occurred during the post processing of create table {}".format(str(e)))
            return response
        except ClientError as clerr:
            raise clerr
        except Exception as e:
            raise ClientError(
                "Error while fetching job status. Error: {}".format(str(e)))

    def get_file(self, file_path):
        """
        Method to get output written by the spark job.
        :param file_path: Source file location
        :type file_path: str
        """
        try:
            # The spark job writes output in a directory at location file_path
            # Fetch the list of files in the directory
            file_list = self.iae_instance_client.get_files_from_dir(
                self.volume, file_path)
            if len(file_list) == 0:
                raise ClientError("The specified directory {} in volume {} is empty.".format(
                    file_path, self.volume))
            # The directory contains files like _SUCCESS, _SUCCESS.crc, part-00000-.json, .part-00000-.json.crc. Select appropriate file
            output_file = None
            for f in file_list:
                file_name = str(f)
                if file_name.startswith("part-") and not file_name.endswith(".crc"):
                    output_file = file_name
            if output_file is None:
                raise ClientError("Status Code: 404. Error: Could not find job output file in directory {} in volume {}.".format(
                    file_path, self.volume))
            return self.iae_instance_client.get_file(self.volume, file_path+"/"+output_file)
        except ClientError as clerr:
            raise clerr
        except Exception as e:
            raise ClientError(
                "Error while fetching job output. Error: {}".format(str(e)))

    def _get_file(self, file_path):
        """
        Method to get file contents located at given path.
        :param file_path: Source file location
        :type file_path: str
        """
        try:
            return self.iae_instance_client.get_file(self.volume, file_path)
        except ClientError as clerr:
            raise clerr
        except Exception as e:
            raise ClientError(
                "Error while fetching job output. Error: {}".format(str(e)))

    def get_job_logs(self, job_id):
        """
        Method to get logs of spark job.
        :param job_id: ID of the job
        :type job_id: str
        """
        try:
            self.iae_instance_client.get_job_logs(job_id)
        except ClientError as clerr:
            raise clerr
        except Exception as e:
            raise ClientError(
                "Error while fetching job logs. Error: {}".format(str(e)))

    def delete_job_artifacts(self, job_id):
        """
        Method to delete artifacts created for a spark job.
        :param job_id: ID of the job
        :type job_id: str
        """
        try:
            self.iae_instance_client.delete_job_artifacts(job_id)
        except ClientError as clerr:
            raise clerr
        except Exception as e:
            raise ClientError(
                "Error while deleting job artifacts. Error: {}".format(str(e)))

    def get_exception(self, output_file_path):
        data = self.get_file(output_file_path + "/exception.json")
        return json.loads(data.decode("utf-8"))

    def kill_job(self, job_id):
        pass

    def get_job_payload(self, job_name, job_class, param_dict, argumentfile_name):
        payload_dict = dict()
        if "arguments" not in param_dict:
            param_dict["arguments"] = {}
        # copy original parameters
        original_argument = param_dict["arguments"].copy()
        subscription_id = get(
            param_dict, "arguments.subscription_id") or str(uuid.uuid4())
        run_id = get(param_dict, "arguments.monitoring_run_id") or str(
            uuid.uuid4())

        if job_name is None:
            job_name = constants.IAE_SPARK_JOB_NAME
        payload_dict["name"] = job_name
        volume = param_dict.get("volume")
        if volume is None:
            volume = self.volume
        payload_dict["volume_name"] = volume
        volume_mount_path = param_dict.get("mount_path")
        if volume_mount_path is None:
            volume_mount_path = constants.IAE_VOLUME_MOUNT_PATH
        if volume_mount_path is not None and not volume_mount_path.startswith("/"):
            volume_mount_path = "/" + volume_mount_path
        payload_dict["mount_path"] = volume_mount_path
        base_path = job_name + "/" + subscription_id
        data_path = base_path + "/data"
        # removing original prameters and adding path related params so that volume gets replaced by wrapper app
        param_dict["arguments"] = {}

        param_dict["arguments"]["data_file_path"] = "{}/{}".format(
            volume_mount_path, data_path)

        output_file_path = None
        if run_id is not None:
            output_file_path = base_path + "/output/" + run_id
            param_dict["arguments"]["output_file_path"] = "{}/{}".format(
                volume_mount_path, output_file_path)
        param_dict["arguments"]["param_file_name"] = argumentfile_name

        # Get storage types
        storage_type_map = JoblibUtils.get_storage_types_from_data_sources(original_argument)
        param_dict["arguments"]["storage_type_map"] = storage_type_map

        # If the storage is common for all data sources, setting the storage type in arguments. This is to fix #29635
        if "storage" in original_argument:
            param_dict["arguments"]["storage_type"] = get(original_argument, "storage.type")

        # Update conf section in payload from input parameters
        conf = param_dict.get("conf")
        if conf is None:
            conf = {}
        if "spark.app.name" not in conf:
            conf["spark.app.name"] = job_name

        # In case of kerberized hive, add delegation token details to the conf section. WI #24824
        # If storage is common for all tables, get token details from common storage, otherwise get it from individual data source. WI #29635
        if original_argument.get("storage"):
            self.__check_and_add_delegation_token_details(original_argument, conf)
        else:
            data_sources = original_argument.get("tables", [])
            for data_source in data_sources:
                self.__check_and_add_delegation_token_details(data_source, conf)

        payload_dict["conf"] = conf

        # Add spark type in the arguments. WI #27704
        param_dict["arguments"]["spark_type"] = constants.SparkType.IAE_SPARK.value

        # Get the spark configuration parameters
        spark_settings = param_dict.get("spark_settings") or {}
        if (spark_settings is not None) and (len(spark_settings) != 0):
            # Update spark_settings to use modified parameter names
            JoblibUtils.update_spark_parameters(spark_settings)
        else:
            spark_settings["max_num_executors"] = "2"
            spark_settings["executor_cores"] = "2"
            spark_settings["executor_memory"] = "2"
            spark_settings["driver_cores"] = "2"
            spark_settings["driver_memory"] = "1"

        original_argument["spark_settings"] = spark_settings
        arg_str = json.dumps(param_dict["arguments"])
        arg_str = arg_str.replace('"', '\"')
        arguments = [job_name, job_class, arg_str]
        payload_dict["parameter_list"] = arguments
        payload_dict["full_job_file"] = "{}/{}/{}".format(
            volume_mount_path, constants.ENTRY_JOB_BASE_FOLDER, constants.ENTRY_JOB_FILE)

        payload_dict.update(spark_settings)

        # If using IAE V3 APIs, construct job payload in V3 format
        spark_instance = self.iae_instance_client.spark_instance
        if spark_instance and spark_instance.use_iae_v4:
            job_payload = JoblibUtils.get_job_payload_in_v3_format(payload_dict, param_dict)
        else:
            # Read the template file
            clients_dir = pathlib.Path(__file__).parent.absolute()
            with open(str(clients_dir) + "/../jobs/iae_job.json.template", 'r') as content_file:
                template_content = content_file.read()

            json_str = Template(template_content)
            json_str = json_str.substitute(payload_dict)
            json_str = json_str.replace('"', '\\\"')
            json_str = json_str.replace("'", "\"")
            job_payload = json.loads(json_str)

            # Update the env section in payload from input parameters, if specified.
            input_env_dict = param_dict.get("env")
            if input_env_dict:
                env = get(job_payload, "engine.env")
                if env is None:
                    env = {}
                env.update(input_env_dict)
                job_payload["engine"]["env"] = env
        return job_payload, data_path, output_file_path, original_argument

    def __get_job_payload(self, param_dict):
        '''
        Following values needs to be replaced in job payload template
            name - name of the job
            num_of_nodes - eg: 2
            worker_cpu - eg: 2
            worker_memory -eg: 1g
            driver_cpu
            driver_memory
            volume_name
            mount_path
            parameter_list
            full_job_file
        '''

        import pathlib
        clients_dir = pathlib.Path(__file__).parent.absolute()
        with open(str(clients_dir) + "/../jobs/iae_job.json.template", 'r') as content_file:
            template_content = content_file.read()

        json_str = Template(template_content)
        json_str = json_str.substitute(param_dict)
        json_str = json_str.replace("'", "\"")
        return json.loads(json_str)

    def download_directory(self, directory_path):
        return self._get_file(directory_path)

    def delete_directory(self, directory_path):
        try:
            if directory_path.startswith(constants.IAE_VOLUME_MOUNT_PATH):
                directory_path = directory_path[len(
                    constants.IAE_VOLUME_MOUNT_PATH):]
            self.iae_instance_client.delete_file(self.volume, directory_path)
        except Exception as e:
            logger.error(
                "Error while deleting the directory. Error: {}".format(str(e)))
            raise ClientError(
                "Error while deleting the directory. Error: {}".format(str(e)))

    def upload_directory(self, directory_path, archive_directory_content):
        try:
            with tempfile.NamedTemporaryFile(suffix=".tar.gz") as temp:
                temp.write(archive_directory_content)
                temp.flush()
                self.iae_instance_client.upload_archive(
                    self.volume, temp.name, directory_path)
                upload_path = constants.IAE_VOLUME_MOUNT_PATH + directory_path
                return upload_path
        except Exception as e:
            logger.error(
                "An error occurred while uploading the directory. Error: {}".format(str(e)))
            raise ClientError(
                "An error occurred while uploading the directory. Error: {}".format(str(e)))

    def add_delegation_token_to_payload(self, conf: dict, job_args: dict):
        """
        Method to add delegation token details to the job payload under conf section
        - First check if conf already contains token details, if yes then do nothing
        - Otherwise if token details are passed as monitoring run parameters in job_args, get them and update in conf section
        - Otherwise if token details are stored as a secret in a vault, get the token from vault using secret_urn
        - Otherwise if API endpoint to generate token is hosted at the edge node of hadoop cluster, get the token by running the API
        """
        delegation_token_details = dict()
        delegation_token_params_list = [
            param.value for param in DELEGATION_TOKEN_PARAMS]

        # Read isSecure, services, metastore_url, principal
        delegation_token_details[DELEGATION_TOKEN_PARAMS.IS_SECURE.value] = str(
            get(job_args, "storage.connection.kerberos_enabled")).lower()
        delegation_token_details[DELEGATION_TOKEN_PARAMS.SERVICES.value] = "HDFS,HMS"
        delegation_token_details[DELEGATION_TOKEN_PARAMS.METASTORE_URL.value] = get(
            job_args, "storage.connection.metastore_url")
        delegation_token_details[DELEGATION_TOKEN_PARAMS.KERBEROS_PRINCIPAL.value] = get(
            job_args, "storage.credentials.kerberos_principal")

        # Set the token details in job payload under conf section
        for field in delegation_token_details:
            if field not in conf or not conf[field]:
                conf[field] = delegation_token_details.get(field)

        # If conf already contains delegation token, then return
        if JoblibUtils.does_dict_contain_req_details(conf, delegation_token_params_list):
            return

        runtime_credentials = get(job_args, "storage.runtime_credentials")
        delegation_token_urn = get(
            job_args, "storage.credentials.delegation_token_urn")
        delegation_token_endpoint = get(
            job_args, "storage.credentials.delegation_token_endpoint")

        # Checking if token details are specified as part of monitoring run parameters
        if runtime_credentials:
            logger.info(
                "Fetching the delegation token details from monitoring run parameters.")
            for param in DELEGATION_TOKEN_PARAMS:
                param_value = param.value
                if param_value in runtime_credentials and (param_value not in conf or not conf[field]):
                    conf[param_value] = runtime_credentials.get(
                        param_value)
            # Checking if all parameters related to delegation token are found
            if JoblibUtils.does_dict_contain_req_details(conf, delegation_token_params_list):
                return

        # If token details not found in run parameters, checking if vault secret_urn is specified in job_params
        if delegation_token_urn:
            logger.info(
                "Fetching the delegation token details from the zen-secret stored in vault.")
            secret = self.iae_instance_client.get_secret_from_vault(
                delegation_token_urn)
            secret_value = get(secret, "data.secret.generic")
            if secret_value is None or secret_value == {}:
                secret_value = get(secret, "data.secret.generic.value")
            if secret_value:
                for field in secret_value:
                    if field not in conf or not conf[field]:
                        conf[field] = secret_value.get(field)
            if JoblibUtils.does_dict_contain_req_details(conf, delegation_token_params_list):
                return

        # If token details not found in run parameters and secret_urn, checking if API endpoint to generate token is specified in job_params
        if delegation_token_endpoint:
            logger.info(
                "Fetching the delegation token details from the API endpoint hosted in user's cluster.")
            get_delegation_token_resp = self.iae_instance_client.invoke_delegation_token_provider(
                delegation_token_endpoint)
            # The API will store delegation token under delegationToken
            delegation_token = get_delegation_token_resp.get("delegationToken")
            if delegation_token:
                conf[DELEGATION_TOKEN_PARAMS.DELEGATION_TOKEN.value] = delegation_token
            if JoblibUtils.does_dict_contain_req_details(conf, delegation_token_params_list):
                return

        # If not all token details are specified, raise an error mentioning list of missing token parameters
        existing_params = [key for key in conf if conf.get(key)]
        missing_params = delegation_token_params_list if conf is None else list(set(
            delegation_token_params_list) - set(existing_params))
        if len(missing_params) > 0:
            raise BadRequestError(
                "Delegation token information required to communicate with kerberos-enabled hive is not specified or is incomplete. Missing parameters: {}".format(missing_params))

    def __check_and_add_delegation_token_details(self, data_source: dict, conf: dict):
        """
        Checks if storage is kerberos enabled and adds delegation token details to payload
        Arguments:
            data_source: The data source containing storage details
            conf: The conf section of job payload
        """
        storage_type = get(data_source, "storage.type")
        if storage_type is not None and storage_type == constants.StorageType.HIVE.value:
            is_kerberos_enabled = get(
                data_source, "storage.connection.kerberos_enabled")
            if is_kerberos_enabled is not None and str(is_kerberos_enabled).lower() == "true":
                self.add_delegation_token_to_payload(conf, data_source)
