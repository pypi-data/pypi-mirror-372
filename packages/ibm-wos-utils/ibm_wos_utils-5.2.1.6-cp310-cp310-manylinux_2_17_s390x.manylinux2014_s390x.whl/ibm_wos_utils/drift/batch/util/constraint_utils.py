# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2020, 2022
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

import hashlib
from decimal import Decimal

import numpy as np
from ibm_wos_utils.drift.batch.util.constants import (RANGE_BUFFER_CONSTANT,
                                                      ConstraintName)


def get_constraint_id(constraint_name: ConstraintName, columns: list):
    """Returns Constraint ID. It is a hash of constraint name + column names
    in lower case sorted alphabetically.

    Arguments:
        constraint_name {ConstraintName} -- Constraint Name
        columns {list} -- List of column names

    Returns:
        str -- constraint id
    """
    return hashlib.sha224(bytes(",".join(
        [constraint_name.value] + sorted(map(lambda x: x.lower(), columns))), "utf-8")).hexdigest()

def get_processed_key(key):
    """Converts key to a string

    Arguments:
        key {object} -- Keys of the dictionary

    Returns:
        str -- String so that it can be used as a key in a dictionary
    """

    if isinstance(key, Decimal):
        key = float(key)

    return str(key)

def get_limits_with_buffer(col_min, col_max):
    buffer = RANGE_BUFFER_CONSTANT * (col_max - col_min)

    # If both col_min and col_max are integers, bump up the buffer to
    # the next integer
    if np.issubdtype(
            type(col_min),
            np.integer) and np.issubdtype(
            type(col_max),
            np.integer):
        buffer = np.ceil(buffer).astype(int)

    return col_min - buffer, col_max + buffer

def get_primitive_value(num):
    """Get the python numeric primitive value from numpy/python numeric values"""
    if type(num) in (int, float):
        return num

    return num.item()

def get_max_bins_for_column(column_name, approx_distinct_count, max_ranges_modifier = 0.01):
    """Returns the maximum number of bins for a column based on the constraint and distinct count of the column.

    Arguments:
        column_name {str} -- Name of the column
        approx_distinct_count {dict} -- Dictionary of column name -> approximate distinct count of values in the column.
        max_ranges_modifier {float | dict} -- User specified maximum number of bins for a column. 
                                1. float: Multiply this value with the approximate distinct count to get the maximum
                                number of bins for all numerical columns.
                                2. dict: Dictionary of column name -> float. Multiply the float value with the approximate
                                distinct count to get the maximum number of bins for the specified column.

    Returns:
        int -- Maximum number of bins for a column
    """    
    max_bins_for_column = int(0.01 * approx_distinct_count.get(column_name))

    if isinstance(max_ranges_modifier, float):
        max_bins_for_column = int(max_ranges_modifier * approx_distinct_count.get(column_name))
    
    if isinstance(max_ranges_modifier, dict):
        if column_name in max_ranges_modifier:
            max_bins_for_column = int(max_ranges_modifier.get(column_name) * approx_distinct_count.get(column_name))

    return max_bins_for_column

def get_tail_thresholds(tail_discard_threshold: float):
    """Returns the tail discard thresholds in string percentiles based on the tail_discard_threshold.
    The thresholds are the top and bottom percentiles of the data. For tail_discard_threshold = 0.01,
    this returns (1.0%, 99.0%)

    The tail_discard_threshold when converted to percentile is rounded to one decimal. For example,
    if tail_discard_threshold = 0.0152, the returned thresholds are (1.5%, 98.5%)

    Arguments:
        tail_discard_threshold {float} -- Float value of threshold

    Returns:
        tuple -- A tuple of string percentiles values.
    """

    if tail_discard_threshold <= 0 or tail_discard_threshold > 0.1:
        raise ValueError("Tail discard percentile threshold should be greater than 0 and less than 0.1")
    
    return ("{:.1%}".format(tail_discard_threshold), "{:.1%}".format(1 - tail_discard_threshold))

def check_user_override(
    column_names:list, constraint_kind:str, user_overrides:list):

    learn_distribution_constraint = True
    learn_range_constraint = True

    if not user_overrides:
        return learn_distribution_constraint, learn_range_constraint

    column_names = [x.upper() for x in column_names]
    input_constraint_kind = "single" if constraint_kind == "single_column" else "double"

    # iterate over configs provided by user and check if given input is one of them
    for config in user_overrides:
        # find the config user has overridden and return distribution and range constraint overrides if any
        config_constraint_kind = config.get("constraint_type")
        if config_constraint_kind != input_constraint_kind:
            continue

        config_features = config.get("features")

        if config_constraint_kind == "single":
            # convert all features to upper-case
            config_features = [x.upper() for x in config_features]

            # check if given column name is part of this config's features
            if set(column_names).issubset(set(config_features)):
                # found config
                # return values for "learn_distribution_constraint" and "learn_range_constraint"
                learn_distribution_constraint = config.get("learn_distribution_constraint")
                learn_range_constraint = config.get("learn_range_constraint")
                break

        if config_constraint_kind == "double":
            # sort input column names
            column_names.sort()

            # iterate over this config's feature pairs and identify if given input column(s) are part of it.
            for feature_pair in config_features:
                feature_pair = [x.upper() for x in feature_pair]
                feature_pair.sort()

                if len(feature_pair) == 1:
                    # single value means override is applicable to all constraints where this column is present
                    if set(feature_pair).issubset(set(column_names)):
                        learn_distribution_constraint = config.get("learn_distribution_constraint")
                        learn_range_constraint = config.get("learn_range_constraint")
                        break

                if column_names == feature_pair:
                    # found config
                    # return values for "learn_distribution_constraint" and "learn_range_constraint"
                    learn_distribution_constraint = config.get("learn_distribution_constraint")
                    learn_range_constraint = config.get("learn_range_constraint")
                    break


    learn_distribution_constraint = True \
        if learn_distribution_constraint is None or learn_distribution_constraint == True else False
    learn_range_constraint = True \
        if learn_range_constraint is None or learn_range_constraint == True else False

    return learn_distribution_constraint, learn_range_constraint