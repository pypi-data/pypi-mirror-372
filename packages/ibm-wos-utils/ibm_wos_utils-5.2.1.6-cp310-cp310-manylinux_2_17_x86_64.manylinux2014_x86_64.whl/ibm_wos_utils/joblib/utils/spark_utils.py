# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2020, 2021
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------


from ibm_wos_utils.joblib.utils.rest_util import RestUtil


def get_spark_info_from_subscription(server_url, service_instance_id, subscription_id, token):
    url = "{}/openscale/{}/v2/subscriptions/{}".format(
        server_url, service_instance_id, subscription_id)
    response = RestUtil.request().get(
        url=url, headers={"Authorization": "Bearer {}".format(token)})
    if not response.ok:
        raise Exception("Failed to retrieve spark information for subscription {}. Error : {}".format(
            subscription_id, response.text))


def get_spark_info_from_datamart(server_url, service_instance_id, datamart_id, token):
    url = "{}/openscale/{}/v2/data_marts/{}".format(
        server_url, service_instance_id, datamart_id)
    response = RestUtil.request().get(
        url=url, headers={"Authorization": "Bearer {}".format(token)})
    if not response.ok:
        raise Exception("Failed to retrieve spark information for Datamart {}. Error : {}".format(
            datamart_id, response.text))
