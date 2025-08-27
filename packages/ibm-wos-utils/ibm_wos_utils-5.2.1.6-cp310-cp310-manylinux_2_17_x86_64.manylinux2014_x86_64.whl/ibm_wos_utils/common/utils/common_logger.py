# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2024
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

"""
Common logger class for logging messages.
"""

import json
import logging
import os
import re
import sys
import traceback

from ibm_wos_utils.common.utils.date_util import DateUtil


LOG_MASKING_REGEX = [
    "(user *[\"\']?[:= ] *[\"\']?)[^\s\"]+",
    "(username *[\"\']?[:= ] *[\"\']?)[^\s\"]+",
    "(password *[\"\']?[:= ] *[\"\']?)[^\s\"]+",
    "(metastore_url *[\"\']?[:= ] *[\"\']?)[^\s\"]+",
    "(jdbc_url *[\"\']?[:= ] *[\"\']?)[^\s\"]+",
    "(certificate *[\"\']?[:= ] *[\"\']?)[^\s\"]+",
    "(credentials *[\"\']?[:= ] *[\"\']?)[^\s\"]+",
    "(api_?key *[\"\']?[:= ] *[\"\']?)[^\s\"]+",
    "((?<!is_service_)token *[\"\']?[:= ] *[\"\']?)[^\s\"]+",
    "(iam_token *[\"\']?[:= ] *[\"\']?)[^\s\"]+",
    "(ssl *[\"\']?[:= ] *[\"\']?)[^\s\"]+",
    "[a-zA-Z0-9+_\.-]+@[a-zA-Z0-9-\.]+",
    "(Bearer *[\"\']?)[^\s\"]+",
    "(bearer *[\"\']?)[^\s\"]+",
    "eyJraWQi+[a-zA-Z0-9._-]*",
    "eyJhbGci+[a-zA-Z0-9._-]*",
    "eyJ0eXAi+[a-zA-Z0-9._-]*",
    "(iam-ServiceId *[\"\']?)[^\s\"]+",
    "(iam *[\"\']?)[^\s\"]+",
    "(ServiceId *[\"\']?)[^\s\"]+"
]

class CommonLogger:
    """
    Usage:
    # import logger
        from ibm_wos_utils.common.utils.common_logger import CommonLogger

    # Get the instance of logger
        logger = CommonLogger(__name__)

    # Log the message
        logger.log_info("Processing Heartbeat request")
    """

    def __init__(self, name, json_enabled: bool=True):
        self.logger = self.get_logger(name)
        self.log_source = None
        self.json_enabled = json_enabled

    def get_logger(self, logger_name=None, logger_level=logging.DEBUG):
        logger = None
        try:
            logging.basicConfig(
                format="%(message)s", level=logging.INFO,)

            if logger_name is None:
                logger_name = "__WOS_UTILS__"
            logger = logging.getLogger(logger_name)
            logger.setLevel(logger_level)
            logger.setFormatter(logging.Formatter(
                fmt="%(message)s"))

        except:
            pass
        return logger

    def msg_to_log(self, attributes, msg):
        if self.json_enabled:
            message_details = attributes["message_details"]
            attributes["message_details"] = self._mask_sensitive_fields(message_details)
            log_str = json.dumps(attributes)
        else:
            exception = attributes.get("exception")
            if exception is None:
                log_str = "[" + self.log_source + "] " + msg
            else:
                log_str = "[" + self.log_source + "] " + msg + "\n" + exception
            if attributes.get("perf", False):
                log_str += f" Time taken: {attributes.get('response_time')/1000} seconds."
            log_str = self._mask_sensitive_fields(log_str)

        return log_str

    def log_info(self, msg, **kwargs):
        attributes = self.get_logging_attributes("INFO", **kwargs)
        attributes["message_details"] = msg
        self.logger.info(self.msg_to_log(attributes, msg))

    def log_error(self, err_msg, **kwargs):
        attributes = self.get_logging_attributes("ERROR", **kwargs)
        attributes["message_details"] = err_msg
        self.logger.error(self.msg_to_log(attributes, err_msg))

    def log_exception(self, exc_msg, **kwargs):
        attributes = self.get_logging_attributes("ERROR", **kwargs)
        attributes["message_details"] = exc_msg
        exc_info = kwargs.get("exc_info", False)
        if exc_info is True:
            type_, value_, traceback_ = sys.exc_info()
            attributes["exception"] = "".join(traceback.format_exception(
                type_, value_, traceback_))
        self.logger.error(self.msg_to_log(attributes, exc_msg))

    def log_warning(self, msg, **kwargs):
        attributes = self.get_logging_attributes("WARNING", **kwargs)
        attributes["message_details"] = msg
        exc_info = kwargs.get("exc_info", False)
        if exc_info is True:
            type_, value_, traceback_ = sys.exc_info()
            attributes["exception"] = "".join(traceback.format_exception(
                type_, value_, traceback_))
        self.logger.warning(self.msg_to_log(attributes, msg))

    def log_debug(self, msg, **kwargs):
        attributes = self.get_logging_attributes("DEBUG", **kwargs)
        if attributes.get("debug"):
            attributes["message_details"] = msg
            self.logger.debug(self.msg_to_log(attributes, msg))

    def log_critical(self, msg, **kwargs):
        attributes = self.get_logging_attributes("CRITICAL", **kwargs)
        attributes["message_details"] = msg
        self.logger.critical(self.msg_to_log(attributes, msg))

    def get_logging_attributes(self, level, **kwargs):
        attributes = {}

        attributes["component_id"] = "common-wos-utils"
        attributes["log_level"] = level
        attributes["timestamp"] = DateUtil.get_current_datetime()

        fn, lno, func = self.logger.findCaller(False)[0:3]
        self.log_source = fn + ":" + str(lno) + " - " + func
        attributes["filename"] = fn
        attributes["method"] = func
        attributes["line_number"] = str(lno)
        attributes["logSourceCRN"] = os.environ.get("LOG_SOURCE_CRN")
        attributes["saveServiceCopy"] = os.environ.get("SAVE_SERVICE_COPY")

        start_time = kwargs.get("start_time", None)
        if start_time:
            elapsed_time = DateUtil.current_milli_time() - start_time
            attributes["response_time"] = elapsed_time
            attributes["perf"] = True

        additional_info = kwargs.get("additional_info", None)
        if additional_info:
            attributes["additional_info"] = additional_info

        return attributes

    def _mask_sensitive_fields(self, log_str):
        """
        Masks sensitive fields in the string identified by regular expressions
        defined in LOG_MASKING_REGEX in the Constants class

        :log_str: The message to be logged
        :returns: The masked version of the message
        """

        for regex in LOG_MASKING_REGEX:
            match_object = re.search(regex, log_str)
            if match_object is not None:
                start = match_object.start()
                end = match_object.end()
                match = log_str[start:end]
                log_str = log_str.replace(match, "***")
        
        return log_str

