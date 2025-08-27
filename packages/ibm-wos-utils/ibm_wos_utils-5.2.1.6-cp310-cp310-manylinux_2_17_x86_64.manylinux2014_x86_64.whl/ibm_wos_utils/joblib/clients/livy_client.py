# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2020, 2021
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

import json
import datetime
import time
from time import sleep


from ibm_wos_utils.joblib.utils.rest_util import RestUtil
from ibm_wos_utils.joblib.utils import constants


class LivyClient():

    """Client class to interact with Remote Spark using Livy Rest API"""

    def __init__(self, server_url, token):
        self.server_url = server_url
        self.token = token

    def run_batch_job(self, job_json, background=True):

        job_url = "{}/batches".format(self.server_url)
        response = RestUtil.request().post(
            url=job_url, json=job_json, headers={"Content-Type": "application/json"})

        if not response.ok:
            raise Exception(
                "Failed to run job. Error {} ". format(response.text))

        job_response = response.json()
        job_id = job_response.get("id")
        state = job_response.get("state")
        if background is False:
            start_time = time.time()
            elapsed_time = 0
            sleep_time = 15
            timeout = constants.SYNC_JOB_MAX_WAIT_TIME
            while state not in (constants.LIVY_JOB_FINISHED_STATE, constants.LIVY_JOB_FAILED_STATE,
                                constants.LIVY_JOB_DEAD_STATE, constants.LIVY_JOB_KILLED_STATE):
                if elapsed_time > timeout:
                    raise Exception(
                        "Job didn't come to Finished/Failed state in {} seconds. Current state is ".format(timeout, state))
                print("{}: Sleeping for {} seconds. Current state {}".format(
                    datetime.datetime.now(), sleep_time, state))
                sleep(sleep_time)
                elapsed_time = time.time() - start_time
                state = self.get_job_state(job_id)

        return job_id, state

    def get_job_state(self, job_id):
        job_url = "{}/batches/{}".format(self.server_url, job_id)

        response = RestUtil.request().get(url=job_url)
        if not response.ok:
            raise Exception("Failed to get jobs state.")

        return response.json()['state']
