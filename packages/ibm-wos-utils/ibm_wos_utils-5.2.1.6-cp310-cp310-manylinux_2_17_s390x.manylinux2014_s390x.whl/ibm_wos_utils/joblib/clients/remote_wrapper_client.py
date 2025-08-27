# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2020, 2021
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

from ibm_wos_utils.joblib.clients.web_hdfs_client import WebHDFSClient
from ibm_wos_utils.joblib.clients.livy_client import LivyClient

from ibm_wos_utils.joblib.utils.rest_util import RestUtil
from ibm_wos_utils.joblib.utils import constants

from string import Template
import json


class RemoteWrapperClient():

    """Client class to for connecting to Remote Spark and HDFS instance"""

    def __init__(self, hdfs_file_url, hdfs_url, livy_url, token):
        self.hdfs_file_url = hdfs_file_url
        self.hdfs_url = hdfs_url
        self.livy_url = livy_url
        self.token = token

    def run_job(self, job_params, background=True):
        job_client = LivyClient(self.livy_url, self.token)
        job_payload = self.__get_job_payload(job_params)
        return job_client.run_batch_job(job_payload, background)

    def get_job_status(self, job_id):
        job_client = LivyClient(self.livy_url, self.token)
        return job_client.get_job_state(job_id)

    def get_log(self):
        pass

    def upload_file(self, src_file_path, tgt_file_path, volumn_name=None):
        ic = WebHDFSClient(self.hdfs_url, self.token)
        ic.upload_file(src_file_path, tgt_file_path)

    def get_job_output(self, job_id, src_file_path, tgt_file_path=None):
        # return application/octet-stream
        hdfs = WebHDFSClient(self.hdfs_url, self.token)
        hdfs.get_file(src_file_path, tgt_file_path)

    def __get_job_payload(self, param_dict):
        '''
        Following values needs to be replaced in job payload template
            arguments - List of parameters
            job_file_path - Full HDFS path to the job file
            dependency_zip - Full HDFS path to the job dependency zip file
        '''
        param_dict['hdfs_path_url'] = self.hdfs_file_url
        import pathlib
        clients_dir = pathlib.Path(__file__).parent.absolute()
        with open(str(clients_dir) + "/../jobs/livy_job.json.template", 'r') as content_file:
            template_content = content_file.read()

        json_str = Template(template_content)
        json_str = json_str.substitute(param_dict)
        return json.loads(json_str)
