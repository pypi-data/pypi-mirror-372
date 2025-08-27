# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# © Copyright IBM Corp. 2022  All Rights Reserved.
# US Government Users Restricted Rights -Use, duplication or disclosure restricted by 
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------

"""
Common logger class for logging messages in json format.
"""

import json
import logging
import os
import sys
import time
import traceback


class ScoringUtilsLogger:
    def __init__(self, name):
        self.logger = self.get_logger(name)

    def get_logger(self, loggerName=None, logger_level=logging.DEBUG):
        logger = None
        try:
            logging.basicConfig(
                format="%(message)s",
                level=logging.INFO,
            )
            if loggerName is None:
                loggerName = "__common-scoring-utils__"
            logger = logging.getLogger(loggerName)
            logger.setLevel(logger_level)
            logger.setFormatter(logging.Formatter(fmt="%(message)s"))
        except:
            pass
        return logger

    def log_verbose(self, msg, additional_attributes=None):
        verbose_logging = os.environ.get("VERBOSE_LOGGING", False)
        if verbose_logging:
            attributes = self.get_json_format(
                "VERBOSE", msg, additional_attributes)
            self.logger.info(json.dumps(attributes))

    def log_info(self, msg, additional_attributes=None):
        attributes = self.get_json_format("INFO", msg, additional_attributes)
        self.logger.info(json.dumps(attributes))

    def log_error(self, err_msg, additional_attributes=None):
        attributes = self.get_json_format(
            "ERROR", err_msg, additional_attributes)
        type_, value_, traceback_ = sys.exc_info()
        attributes["exception"] = "".join(
            traceback.format_exception(type_, value_, traceback_)
        )
        self.logger.error(json.dumps(attributes))

    def log_warning(self, msg, additional_attributes=None):
        attributes = self.get_json_format(
            "WARNING", msg, additional_attributes)
        self.logger.warning(json.dumps(attributes))

    def log_debug(self, msg, additional_attributes=None):
        attributes = self.get_json_format("DEBUG", msg, additional_attributes)
        self.logger.debug(json.dumps(attributes))

    def log_critical(self, msg, additional_attributes=None):
        attributes = self.get_json_format(
            "CRITICAL", msg, additional_attributes)
        self.logger.critical(json.dumps(attributes))

    def get_json_format(self, level, msg, additional_attributes=None):
        attributes = {}
        attributes["appname"] = "common-scoring-utils"
        attributes["log_level"] = level
        attributes["logSourceCRN"] = os.environ.get("LOG_SOURCE_CRN")
        attributes["saveServiceCopy"] = os.environ.get("SAVE_SERVICE_COPY")

        t = time.localtime()
        attributes["timestamp"] = time.asctime(t)

        try:
            fn, lno, func = self.logger.findCaller(False)[0:3]
            self.log_source = fn + ":" + str(lno) + " - " + func + "()"
        except:
            # Ignore error while finding the caller for cythonized code
            # https://github.com/cython/cython/issues/2735
            pass

        if additional_attributes:
            for key, value in additional_attributes.items():
                attributes[key] = value
        attributes["message_details"] = msg
        return attributes
