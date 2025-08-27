# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2021
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------


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


def cleanup_null_values(json_obj):
    for key in list(json_obj.keys()):
        if json_obj[key] is None:
            del json_obj[key]
        elif type(json_obj[key]) == dict:
            cleanup_null_values(json_obj[key])
