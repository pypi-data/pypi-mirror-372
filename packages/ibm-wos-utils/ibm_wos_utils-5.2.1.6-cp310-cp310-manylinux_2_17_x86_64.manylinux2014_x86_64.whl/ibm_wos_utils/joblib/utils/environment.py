# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2022, 2023
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S. Copyright Office.
# ----------------------------------------------------------------------------------------------------

import os

from ibm_wos_utils.common.utils.python_utils import strtobool


class Environment():
    """
    Utility class to read environment variable values
    """
    environment = {}

    tls_cert = "/etc/internal-tls/tls.crt"
    tls_cert_key = "/etc/internal-tls/tls.key"

    @classmethod
    def set_environment(cls, environment):
        if environment:
            cls.environment.update(environment)

    @classmethod
    def get_property_value(cls, property_name, default=None):
        prop_value = cls.environment.get(property_name)

        if prop_value is None:
            prop_value = os.environ.get(property_name)

        if prop_value is None:
            prop_value = default

        return prop_value

    @classmethod
    def get_property_boolean_value(cls, property_name, default=None):
        val = cls.get_property_value(property_name, default=default)
        if isinstance(val, bool):
            return val

        if val:
            try:
                return bool(strtobool(val))
            except ValueError:
                return False
        # return False for other values or None
        return False

    def is_iae_jobs_queuing_enabled(self):
        return self.get_property_boolean_value("ENABLE_IAE_JOBS_QUEUING", "true")

    def get_wos_env_location(self):
        default_wos_env_location = "$mount_path/py_packages/wos_env/lib/python3.10/site-packages:$mount_path/py_packages/wos_env/lib/python3.11/site-packages"
        return self.get_property_value("WOS_ENV_LOCATION", default=default_wos_env_location)

    def get_ld_library_path(self):
        default_ld_library_path = "/home/spark/conda/envs/python3.10/lib:/opt/ibm/connectors/dsdriver/dsdriver/lib:/opt/ibm/connectors/others-db-drivers/oracle/lib:/opt/ibm/jdk/lib/server:/opt/ibm/jdk/lib:/usr/local/lib:/lib64"
        ld_library_path = "{}:{}".format(
            default_ld_library_path, self.get_property_value("LD_LIBRARY_PATH", default=""))
        return ld_library_path

    @classmethod
    def get_cloud_iam_public_keys_url(cls):
        return cls.get_property_value("IAM_PUBLIC_KEYS_URL")

    @classmethod
    def is_cpd(cls):
        return cls.get_property_boolean_value("ENABLE_ICP", "false")

    @classmethod
    def get_cpd_iam_public_keys_url(cls):
        return cls.get_property_value("ICP4D_JWT_PUBLIC_KEY_URL")

    @classmethod
    def get_gateway_url(cls):
        return cls.get_property_value("AIOS_GATEWAY_URL")

    @classmethod
    def get_tls_cert(cls) -> str:
        return cls.tls_cert

    @classmethod
    def get_tls_cert_key(cls) -> str:
        return cls.tls_cert_key

    @classmethod
    def get_pod_host(cls):
        return cls.get_property_value("CPD_POD_HOST")

    @classmethod
    def get_host(cls):
        return cls.get_property_value("HOST", "")

    @classmethod
    def get_pod_name(cls):
        return cls.get_property_value("HOSTNAME", "")

    @classmethod
    def get_atrk_service_name(cls):
        return cls.get_property_value("AT_SERVICE_NAME", "aiopenscale")

    @classmethod
    def get_node_worker_name(cls):
        return cls.get_property_value("CPD_POD_NODE")

    @classmethod
    def get_icpd_external_route(cls):
        return cls.get_property_value("ICP_ROUTE")

    @classmethod
    def get_namespace(cls):
        return cls.get_property_value("CPD_POD_NAMESPACE")

    @classmethod
    def get_region(cls):
        # ng | eu-gb | eu-de | au-syd
        return cls.get_property_value("REGION", "ng")
