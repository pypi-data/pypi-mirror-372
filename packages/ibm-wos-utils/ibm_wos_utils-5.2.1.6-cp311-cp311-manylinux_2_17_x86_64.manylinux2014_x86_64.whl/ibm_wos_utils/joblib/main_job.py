# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2020, 2021
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------
from importlib import import_module
from ibm_wos_utils.joblib.jobs.aios_spark_job import AIOSBaseJob
from ibm_wos_utils.joblib.utils.param_utils import get_dict_from_param_list

import sys

# Remove the job_name, job_class from the parameters
job_name = sys.argv.pop(1)
job_class_path = sys.argv.pop(1)

arguments = get_dict_from_param_list(sys.argv)

print("Starting '{}' Job".format(job_class_path))
pkg_list = job_class_path.split(".")
job_class = getattr(import_module(".".join(pkg_list[:-1])), pkg_list[-1])
job_object = job_class(arguments, job_name)

# if not (isinstance(job_object, AIOSBaseJob) and job_class_path.startswith("ibm_wos_utils.")): Removing the classpath check for now as its hindering development. Will enable during final release of the lib.
if not isinstance(job_object, AIOSBaseJob):
    error_msg = "Unsupported job '{}' provided. Please provide a valid job.".format(
        job_class_path)
    AIOSBaseJob(arguments, job_name).save_exception_trace(error_msg=error_msg)
    raise Exception(error_msg)


job_object.run_job()
job_object.finish_job()
