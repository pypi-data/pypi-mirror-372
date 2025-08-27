# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2020, 2021
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

import json

from ibm_wos_utils.common.utils.python_utils import strtobool


def get_dict_from_param_list(param_list):
    str_json = param_list[1]

    return json.loads(str_json.replace('\{', '{').replace('\}', '}'))
    '''
    param_dict = {}
    for param in param_list:
        tokens = param.split(":",1)
        if len(tokens)==1:
            continue
        key = tokens[0]
        value = tokens[1]
        if len(tokens)>1 and ":" in value:
            str_json = tokens[1].replace('\'', '"')
            #print(str_json)
            value = json.loads(str_json)
        
        param_dict[key] = value    
    
    return param_dict    
    '''


def get(obj: dict, path, default=None):
    """Gets the deep nested value from a dictionary

    Arguments:
        obj {dict} -- Dictionary to retrieve the value from
        path {list|str} -- List or . delimited string of path describing path.

    Keyword Arguments:
        default {mixed} -- default value to return if path does not exist (default: {None})

    Returns:
        mixed -- Value of obj at path
    """
    if isinstance(path, str):
        path = path.split(".")

    new_obj = {
        **obj
    }
    for key in path:
        if not new_obj:
            # for cases where key has null/none value
            return default

        if key in new_obj.keys():
            new_obj = new_obj.get(key)
        else:
            return default
    return new_obj


def get_boolean_value(value):
    """
    Converts string representation of value to its boolean equivalent
    """
    bool_value = False
    if value:
        value = str(value)
        try:
            bool_value = bool(strtobool(value))
        except ValueError:
            bool_value = False
    return bool_value
    return bool_value
