
# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2020, 2021
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

import logging
import sys

def getLogger(name):
    logger = logging.getLogger(name)
    formatter = logging.Formatter(
        '%(asctime)s %(name)s %(levelname)s %(message)s')
    s_hdlr = logging.StreamHandler(sys.stdout)
    s_hdlr.setFormatter(formatter)
    logger.addHandler(s_hdlr)
    logger.setLevel(logging.INFO)
    return logger

logger = getLogger("aios-feedback-service")
