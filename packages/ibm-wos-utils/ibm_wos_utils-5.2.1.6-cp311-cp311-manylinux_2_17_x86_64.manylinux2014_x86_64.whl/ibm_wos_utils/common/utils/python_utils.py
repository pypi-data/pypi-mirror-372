# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2023
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

def strtobool(val: str):
    """Convert a string representation of truth to true (1) or false (0).
    True values are 'y', 'yes', 't', 'true', 'on', and '1'; false values
    are 'n', 'no', 'f', 'false', 'off', and '0'.  Raises ValueError if
    'val' is anything else.
    """
    val = val.lower()
    if val in ('y', 'yes', 't', 'true', 'on', '1'):
        return 1
    elif val in ('n', 'no', 'f', 'false', 'off', '0'):
        return 0
    else:
        raise ValueError("invalid truth value %r" % (val,))


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