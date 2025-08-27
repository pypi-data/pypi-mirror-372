# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2020, 2021
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

import json


from ibm_wos_utils.joblib.utils.rest_util import RestUtil
from ibm_wos_utils.joblib.utils import constants


class WebHDFSClient():

    """Client class to manage connectivity to HDFS files"""

    def __init__(self, server_url, token):
        self.server_url = server_url
        self.token = token

    def upload_file(self, src_file_path, tgt_file_path, overwrite="true"):
        # Step 1. Get the upload URL
        url = "{}/webhdfs/v1/{}?op=CREATE&&overwrite={}".format(
            self.server_url, tgt_file_path, overwrite)

        response = RestUtil.request().put(url=url, allow_redirects=False)
        if not response.ok:
            raise Exception("Uploading of file {} failed(1). Error {}".format(
                tgt_file_path, response.text))

        # Step 2. Upload the actual file to location header
        hdfs_path_url = response.headers['Location']
        with open(src_file_path, "rb") as f:
            response = RestUtil.request().put(url=hdfs_path_url, data=f)
        if not response.ok:
            raise Exception("Uploading of file {} failed(2). Error {}".format(
                tgt_file_path, response.text))

    def get_file(self, src_file_path, tgt_file_path):
        url = "{}/webhdfs/v1/{}?op=OPEN".format(
            self.server_url, src_file_path)

        response = RestUtil.request().get(url=url)
        if not response.ok:
            raise Exception("Retreving of file {} failed(1). Error {}".format(
                src_file_path, response.text))
        if tgt_file_path == None:
            tgt_file_path = src_file_path
        with open(tgt_file_path, "w") as f:
            f.write(response.text)
