# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2020, 2021
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

import re

from ibm_wos_utils.joblib.exceptions.client_errors import *

"""Utility methods for validations"""

# Method to validate the parameter
# Example: usage: validate_type(data_mart_id, 'data_mart_id', str, True)


def validate_type(field, value, expected_type, is_mandatory=False):
    if value is None:
        if is_mandatory:
            raise MissingValueError(field)
        else:
            return
    if type(expected_type) is list:
        try:
            next((x for x in expected_type if isinstance(value, x)))
            return True
        except StopIteration:
            return False
    else:
        if not isinstance(value, expected_type):
            raise UnexpectedTypeError(field, expected_type, type(value))
        else:
            return True

# Method to check if resource_id is a valid UUID


def validate_resource_id(field, value):
    if value is None:
        raise MissingValueError(field)
    uuid_pattern = "[0-9a-zA-Z]+-[0-9a-zA-Z]+-[0-9a-zA-Z]+-[0-9a-zA-Z]+-[0-9a-zA-Z]"
    if not re.match(uuid_pattern, value):
        raise InvalidInputError(
            field, error="The value is not in a valid UUID format.")
    return True
