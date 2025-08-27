# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2021
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

from ibm_wos_utils.joblib.utils import constants
from ibm_wos_utils.joblib.utils.constants import JobStatus

def get_common_job_status(status):
    job_status = str(status).lower()
    if job_status in constants.JOB_RUNNING_STATES:
        return JobStatus.RUNNING
    elif job_status in constants.JOB_FINISHED_STATES:
        return JobStatus.FINISHED
    elif job_status in constants.JOB_FAILED_STATES:
        return JobStatus.FAILED
    else:
        return JobStatus.UNKNOWN