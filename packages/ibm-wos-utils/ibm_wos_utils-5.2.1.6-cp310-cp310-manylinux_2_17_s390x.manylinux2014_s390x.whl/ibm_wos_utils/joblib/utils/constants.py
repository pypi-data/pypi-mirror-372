# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2020, 2021
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

import re
from enum import Enum
from http import HTTPStatus

SPARK_INSTANCE = 'BatchTestingInstance'
SPARK_VOLUME = 'aios'
IAE_SPARK_INTEGRATED_SYSTEM = 'watson_data_catalog'
IAE_JOB_FINISHED_STATE = 'FINISHED'
IAE_JOB_FAILED_STATE = 'FAILED'
IAE_JOB_STOPPED_STATE = 'STOPPED'

LIVY_JOB_FINISHED_STATE = 'success'
LIVY_JOB_FAILED_STATE = 'error'
LIVY_JOB_DEAD_STATE = 'dead'
LIVY_JOB_KILLED_STATE = 'killed'

SYNC_JOB_MAX_WAIT_TIME = 300

ENTRY_JOB_FILE = 'main_job.py'
ENTRY_JOB_BASE_FOLDER = "job"
IAE_SPARK_JOB_NAME = "Watson Openscale IAE Spark Job"
IAE_VOLUME_MOUNT_PATH = "/openscale"

TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
UPLOAD_FILE_RETRY_COUNT = 3
UPLOAD_FILE_RETRY_STATUS_CODES = [
    HTTPStatus.NOT_FOUND,
    HTTPStatus.BAD_GATEWAY,
    HTTPStatus.SERVICE_UNAVAILABLE,
    HTTPStatus.GATEWAY_TIMEOUT
]

# Number of seconds to wait while connecting to database
DEFAULT_CONNECTION_TIMEOUT = 180
# The JDBC fetch size, which determines how many rows to fetch per round trip
DEFAULT_FETCH_SIZE = 100000

# Timestamp format while writing dataframe to JSON
WRITE_TO_JSON_TIMESTAMP_FORMAT = "yyyy-MM-dd'T'hh:mm:ss:SSSSSSZZ"

JOB_RUNNING_STATES = ["starting", "running", "waiting", "accepted", "queued"]
JOB_FINISHED_STATES = ["finished", "success"]
JOB_FAILED_STATES = ["error", "dead", "killed", "failed", "stopped"]

COLUMN_DENIED_CHARS_REGEX = re.compile("\.")

SERVICE_ID = "ServiceId"


class SparkType(Enum):
    REMOTE_SPARK = "custom"
    IAE_SPARK = "cpd_iae"


class StorageType(Enum):
    HIVE = "hive"
    JDBC = "jdbc"


class LocationType(Enum):
    HIVE_METASTORE = "metastore"
    JDBC = "jdbc"


class JDBCDatabaseType(Enum):
    DB2 = "db2"
    HIVE = "hive"
    POSTGRESQL = "postgresql"


class WriteMode(Enum):
    APPEND = "append"
    OVERWRITE = "overwrite"


class JobStatus(Enum):
    RUNNING = "running"
    FINISHED = "finished"
    FAILED = "failed"
    UNKNOWN = "unknown"


class DELEGATION_TOKEN_PARAMS(Enum):
    IS_SECURE = "ae.spark.remoteHadoop.isSecure"
    SERVICES = "ae.spark.remoteHadoop.services"
    DELEGATION_TOKEN = "ae.spark.remoteHadoop.delegationToken"
    METASTORE_URL = "spark.hadoop.hive.metastore.uris"
    KERBEROS_PRINCIPAL = "spark.hadoop.hive.metastore.kerberos.principal"


class IAEJobsEndpointType(Enum):
    V1_ENDPOINT = "Spark jobs endpoint"
    V2_ENDPOINT = "Spark jobs V2 endpoint"
    V3_ENDPOINT = "Spark jobs V3 endpoint"
    V4_ENDPOINT = "Spark jobs V4 endpoint"