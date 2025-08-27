# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2020, 2021
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

CLASSIFICATION_MODEL_DATA_TYPES = ["string" ,"boolean", "int", "long", "bigint", "float", "double"]
REGRESSION_MODEL_DATA_TYPES = ["int", "bigint", "long","float", "double"]

CLASSIFICATION_CAST_DATA_TYPES = ["boolean", "int", "bigint", "long", "float", "double"]

REGRESSION_MODEL_TYPE = "regression"
BINARY_CLASSIFICATION_MODEL_TYPE = "binary"
MULTI_CLASSIFICATION_MODEL_TYPE = "multiclass"

#This is the output file where the spark job writes the metrics output
JOB_OUTPUT_FILE_NAME = "output"
JOB_OUTPUT_FILE_FORMAT = "json"
COPY_METRICS_MESSAGE = "copy previous quality metrics"

