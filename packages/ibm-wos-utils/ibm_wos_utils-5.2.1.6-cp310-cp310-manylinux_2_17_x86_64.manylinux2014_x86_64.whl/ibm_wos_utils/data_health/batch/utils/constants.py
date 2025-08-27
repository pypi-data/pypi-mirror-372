# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2019, 2023
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S. Copyright Office.
# ----------------------------------------------------------------------------------------------------

from enum import Enum

"""
Contains constants used for the Data Health monitor.
"""

class Metrics(Enum):

    # Column based metrics
    ABSENCE_COUNT = "absence_count"
    EMPTY_STRINGS = "empty_strings"
    UNIQUE_COLUMNS = "unique_columns"

    # Collective metrics
    CLASS_CONFUSION = "class_confusion"
    DUPLICATE_ROWS = "duplicate_rows"

# Metrics on individual columns of the data
COLUMN_BASED_METRICS = [
    Metrics.ABSENCE_COUNT.value,
    Metrics.EMPTY_STRINGS.value,
    Metrics.UNIQUE_COLUMNS.value
]

# Default boundaries for metrics
DEFAULT_THRESHOLDS = {
    "{}_BINARY".format(Metrics.CLASS_CONFUSION.value): 0.05, # the distance from confidence boundary
    "{}_BINARY_CONFIDENCE_BOUNDARY".format(Metrics.CLASS_CONFUSION.value): 0.5, # the confidence boundary
    "{}_MULTICLASS".format(Metrics.CLASS_CONFUSION.value): 0.05 # the difference between top two classes
}
THRESHOLD_LIMIT_DIRECTIONS = {
    Metrics.ABSENCE_COUNT.value: "upper_limit",
    Metrics.EMPTY_STRINGS.value: "upper_limit",
    Metrics.DUPLICATE_ROWS.value: "upper_limit",
    Metrics.UNIQUE_COLUMNS.value: "upper_limit",
    Metrics.CLASS_CONFUSION.value: "upper_limit"
}

# Metrics supported for classification type models only
CLASSIFICATION_MODEL_METRICS = [
    Metrics.CLASS_CONFUSION.value
]

# Metrics supported for batch subscriptions
BATCH_SUBSCRIPTION_PL_METRICS = [
    Metrics.ABSENCE_COUNT.value,
    Metrics.EMPTY_STRINGS.value,
    Metrics.CLASS_CONFUSION.value,
    Metrics.DUPLICATE_ROWS.value,
    Metrics.UNIQUE_COLUMNS.value
]
BATCH_SUBSCRIPTION_FB_METRICS = [
    Metrics.ABSENCE_COUNT.value,
    Metrics.EMPTY_STRINGS.value,
    Metrics.DUPLICATE_ROWS.value,
    Metrics.UNIQUE_COLUMNS.value
]

# Modelling roles
RECORD_ID_MODELING_ROLE = "record-id"
RECORD_TIMESTAMP_MODELING_ROLE = "record-timestamp"
FEATURE_MODELING_ROLE = "feature"
META_FIELD_MODELING_ROLE = "meta-field"
PREDICTION_MODELING_ROLE = "prediction"
PROBABILITY_MODELING_ROLE = "probability"

# Datasets
PAYLOAD = "payload"
FEEDBACK = "feedback"
DATA_HEALTH = "data_health"