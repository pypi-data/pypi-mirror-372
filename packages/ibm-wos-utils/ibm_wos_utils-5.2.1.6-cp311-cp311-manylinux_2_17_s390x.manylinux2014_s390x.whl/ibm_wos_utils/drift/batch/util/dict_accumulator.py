# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2020, 2021
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

import numpy as np
from pyspark import AccumulatorParam


def merge_two_dicts(dict1, dict2):
    """Recursively merge two dictionaries using the strategy
    1. If the value is a dictionary, call this method again
    2. If the value is a number, add them up
    3. Else, key is not present in dict1, just add that key,value pair.

    Arguments:
        dict1 {dict} -- first dictionary
        dict2 {dict} -- second dictionary

    Returns:
        dict -- merged dictionary
    """
    new_dict = dict1.copy()
    for k, v in dict2.items():
        if (k in dict1 and isinstance(dict1[k], dict)):
            new_dict[k] = merge_two_dicts(dict1[k], dict2[k])
        elif (k in dict1 and np.issubdtype(type(dict1[k]), np.number)):
            new_dict[k] = dict1[k] + dict2[k]
        else:
            new_dict[k] = dict2[k]

    return new_dict


class DictParam(AccumulatorParam):
    def zero(self, value={}):
        return dict()

    def addInPlace(self, dict1, dict2):
        return merge_two_dicts(dict1, dict2)
