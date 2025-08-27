# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2020, 2021
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

import logging
from importlib import import_module
from py4j.java_gateway import java_import

logger = logging.getLogger(__name__)


class DialectUtils:
    """
    Class for JDBC dialect related utility methods
    """

    @classmethod
    def register_hive_dialect(cls, spark):
        dialect_class = "com.hive.jdbc.utils.HiveDialect"
        cls._register_dialect(spark, dialect_class)
        logger.info("Registered hive dialect.")

    @classmethod
    def _register_dialect(cls, spark, dialect_class):
        try:
            gw = spark.sparkContext._gateway
            java_import(gw.jvm, str(dialect_class))
            job_class = getattr(gw.jvm, dialect_class)
            gw.jvm.org.apache.spark.sql.jdbc.JdbcDialects.registerDialect(
                job_class())
        except Exception as e:
            error_message = "Error while registering hive dialect. Error: {}".format(
                str(e))
            # Ignoring the error and just logging the warning
            logger.warning(error_message)
