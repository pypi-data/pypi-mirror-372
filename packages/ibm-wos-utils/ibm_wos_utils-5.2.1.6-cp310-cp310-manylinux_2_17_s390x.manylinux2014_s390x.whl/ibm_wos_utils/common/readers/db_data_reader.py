# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2025
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------


import base64
import os
import ssl
import sys
import tempfile
import uuid
import ibm_db
import ibm_db_dbi
import pandas as pd
import pandas.io.sql as psql
import psycopg2

from abc import abstractmethod
from retrying import retry

from ibm_wos_utils.common.utils.date_util import DateUtil
from ibm_wos_utils.common.utils.common_logger import CommonLogger
from ibm_wos_utils.joblib.utils.environment import Environment
from ibm_wos_utils.common.readers.training_data_reader import TrainingDataReader

logger = CommonLogger(__name__)
CONNECTION_TIMEOUT = 180  # Timeout in seconds for Db2 connections


class DatabaseDataReader(TrainingDataReader):
    def __init__(self, params):
        self.params = params
        self.db = self.params["training_data_db_name"]
        self.port = self.params["training_data_db_port"]
        self.host = self.params["training_data_db_host"]
        self.username = self.params["training_data_db_username"]
        self.password = self.params["training_data_db_password"]
        self.schema_name = self.params["training_data_db_schemaname"]
        self.table_name = self.params["training_data_db_tablename"]
        self.certificate_base64 = self.params["certificate_base64"]
        self.row_id_column = "row_id_{}".format(uuid.uuid4())
        self.cert_file = None
        self.initialize()

    @abstractmethod
    def initialize(self):
        raise NotImplementedError("Subclasses must implement this method.")

    def get_query_to_count_rows(self):
        return f'SELECT COUNT(*) FROM "{self.schema_name}"."{self.table_name}"'

    def get_input_data(self, max_row=None, random_sample=False):
        """
        Fetches the input data from the DB source and returns it as a pandas DataFrame.
        """

        logger.log_debug("Reading input training data from DB.")
        start_time = DateUtil.current_milli_time()

        offset = 0
        limit = 10000
        dfs = []
        total_rows_fetched = 0
        size_limit_exceeded = False

        try:
            while True:
                if max_row:
                    remaining_rows = max_row - total_rows_fetched
                    if remaining_rows <= 0:
                        break
                    limit = min(limit, remaining_rows)

                chunk_df = psql.read_sql(
                    self.get_query_to_execute(limit, offset, random_sample),
                    self.connection,
                )

                if chunk_df.empty:
                    break

                obj_size_in_mb = (
                    sum(map(sys.getsizeof, dfs)) + sys.getsizeof(chunk_df)
                ) / (1024**2)
                if obj_size_in_mb > 500:
                    size_limit_exceeded = True
                    logger.log_debug(
                        "Rows fetched object size exceeds 500 MB; Terminating."
                    )
                    break

                dfs.append(chunk_df)
                total_rows_fetched += chunk_df.shape[0]
                offset += chunk_df.shape[0]
        except Exception as ex:
            logger.log_exception(str(ex), exc_info=True)
            raise Exception(
                "There was an error reading the training data from the database."
            )
        finally:
            self.close_connection()
            self.delete_certificate_file()

        df = pd.concat(dfs, ignore_index=True)
        if self.row_id_column in df.columns:
            df.drop(columns=[self.row_id_column], inplace=True)

        logger.log_info(
            "Completed reading input data using Db DataReader.", start_time=start_time
        )

        return df, size_limit_exceeded

    def get_input_data_size(self):
        offset = 0
        limit = 1000
        data_size = 0
        try:
            row_count = psql.read_sql(
                self.get_query_to_count_rows(), self.connection)
            chunk_df = psql.read_sql(
                self.get_query_to_execute(limit, offset), self.connection
            )
            chunk_size = sys.getsizeof(chunk_df)
            chunk_average_size = chunk_size / len(chunk_df)

            # data size in bytes
            data_size = row_count.values[0][0] * chunk_average_size
        except Exception as ex:
            logger.log_exception(str(ex), exc_info=True)
            raise Exception(
                "An error occurred while reading data from database.")
        finally:
            self.close_connection()
            self.delete_certificate_file()

        return data_size

    def close_connection(self):
        try:
            if self.connection:
                self.connection.close()
        except Exception:
            logger.log_warning("Failed attempting to close DB connection.")

    def create_certificate_file(self):
        if self.certificate_base64:
            certificate = base64.b64decode(
                self.certificate_base64.strip()).decode()
        else:
            certificate = ssl.get_server_certificate((self.host, self.port))

        with tempfile.NamedTemporaryFile(
            mode="w", prefix="db_ssl_", suffix="_cert.arm", delete=False
        ) as f:
            self.cert_file = f.name
            f.write(certificate)

    def delete_certificate_file(self):
        if self.cert_file:
            try:
                os.remove(self.cert_file)
            except:
                logger.log_warning(
                    "Failed while deleting cert file " + self.cert_file + "."
                )


class Db2DataReader(DatabaseDataReader):

    db2_error_tuple = "08"  # Class Code 08: Connection Exception

    def __init__(self, params, retry_non_ssl=False):
        self.retry_non_ssl = retry_non_ssl
        super().__init__(params)
        self.use_row_id = self.check_use_row_id()

    def check_use_row_id(self):
        try:
            query = f'SELECT rowid as "{self.row_id_column}", * FROM "{self.schema_name}"."{self.table_name}"'
            query += f' ORDER BY "{self.row_id_column}" LIMIT 1'
            psql.read_sql(query, self.connection)
        except Exception as ex:
            ex_str = str(ex)
            logger.log_exception(ex_str, exc_info=True)
            if all(
                x in ex_str
                for x in ["SQLSTATE=42704", "SQLCODE=-204", "undefined name"]
            ):
                raise Exception(
                    "The SQL schema or table does not exist. The schema or table names are case-sensitive. Please check the training data configuration."
                )
            elif all(
                x in ex_str
                for x in [
                    "SQLSTATE=42703",
                    "SQLCODE=-206",
                    '"ROWID" is not valid in the context where it is used.',
                ]
            ):
                return False
            else:
                raise Exception(
                    "An error occurred while reading data from database.")
        return True

    def initialize(self):
        try:
            start_time = DateUtil.current_milli_time()
            dsn = (
                "DATABASE="
                + self.db
                + ";HOSTNAME="
                + self.host
                + ";PORT="
                + str(self.port)
                + ";PROTOCOL=TCPIP;UID="
                + str(self.username).lower()
                + ";PWD="
                + self.password
                + ";"
            )

            # Attempt SSL connection by default for Non-ICP environment and if enabled in ICP environment
            if Environment.is_cpd():
                if self.params.get("ssl"):
                    self.create_certificate_file()
                    dsn = (
                        dsn
                        + "SECURITY=ssl;SSLServerCertificate="
                        + str(self.cert_file)
                        + ";"
                    )
            else:
                dsn = dsn + "SECURITY=ssl;"

            # Create the connection
            self.connection = self.get_connection_with_retry(dsn)
        except Exception as e:
            self.delete_certificate_file()
            if self.is_connection_error(e) and self.retry_non_ssl:
                self.retry_with_non_ssl()
            else:
                logger.log_exception(str(e), exc_info=True)
                raise Exception(
                    "There was an error connecting to the training data database."
                )

        logger.log_debug("Finished getting DB connection.",
                         start_time=start_time)

    @retry(stop_max_attempt_number=3, wait_exponential_multiplier=1000)
    def get_connection_with_retry(self, dsn: str):
        """Retry scoring with wait of 2^x * 1000 milliseconds between each retry"""
        ibm_db_conn = ibm_db.connect(dsn, "", "")
        return ibm_db_dbi.Connection(ibm_db_conn)

    def get_query_to_execute(self, limit: str, offset: str, random_sample=False):
        # Query with OFFSET, LIMIT is constructed

        query = "SELECT rowid" if self.use_row_id else "SELECT row_number() over()"
        query += f' as "{self.row_id_column}", * FROM "{self.schema_name}"."{self.table_name}" ORDER BY "{self.row_id_column}" LIMIT {limit} OFFSET {offset}'
        if random_sample:
            query = f'SELECT * FROM {self.schema_name}."{self.table_name}" order by rand() fetch first {limit} rows only'
        return query

    def is_connection_error(self, error: Exception):
        """
        Parses the error message string to identify if the error was connection problem.
        The error class code is fetched from the SQL_STATE to identify if it is a connection problem.
        """
        err_message = str(error)
        if err_message:
            index = err_message.find("SQLSTATE=")
            if (err_message != "") & (index != -1):
                error_code = err_message[(index + 9): (index + 14)]
                prefix_code = error_code[:2]
                if prefix_code in self.db2_error_tuple:
                    return True
        return False

    def retry_with_non_ssl(self):
        """
        We know its connection exception; check if SSL connection is not
        enforced to attempt non-SSL connection
        when in ICP, if non-ssl failed, and if the below toggle is true (quite mis-leading in icp, so please read this comment carefully)
        then try with SSL mode.
        """
        if Environment.is_cpd():
            logger.log_warning(
                "In ICP environment, communication with port:"
                + str(self.port)
                + " failed, attempting SSL communication."
            )
        else:
            logger.log_warning(
                "SSL communication with port:"
                + str(self.port)
                + " failed, attempting Non-SSL communication."
            )
        try:
            dsn = (
                "DATABASE="
                + self.db
                + ";HOSTNAME="
                + self.host
                + ";PORT="
                + str(self.port)
                + ";PROTOCOL=TCPIP;UID="
                + str(self.username).lower()
                + ";PWD="
                + self.password
                + ";CONNECTTIMEOUT="
                + str(CONNECTION_TIMEOUT)
                + ";"
            )
            # if icp environment, then make use of SSL mode
            if Environment.is_cpd():
                dsn = dsn + "SECURITY=ssl;"
                if self.params.get("ssl"):
                    self.create_certificate_file()
                    dsn = dsn + "SSLServerCertificate=" + self.cert_file + ";"
            self.connection = self.get_connection_with_retry(dsn)
        except Exception as e:
            self.delete_certificate_file()
            logger.log_exception(str(e), exc_info=True)
            raise Exception(
                "There was an error connecting to the training data database."
            )


class PostgresDataReader(DatabaseDataReader):
    def __init__(self, params):
        self.sslmode = params.get("ssl_mode", "require")
        super().__init__(params)

    def initialize(self):
        """
        Creates a connection to the Postgres database.
        Handles SSL certificate and connection retries.
        """
        try:
            start_time = DateUtil.current_milli_time()
            # Construct the base DSN string
            dsn = f"dbname={self.db} user={self.username} password={self.password} host={self.host} port={self.port} sslmode={self.sslmode}"

            # Handle SSL configuration
            if self.sslmode in ("verify-ca", "verify-full"):
                self.create_certificate_file()
                dsn += f" sslrootcert={self.cert_file}"

            # Establish the connection with retry logic
            self.connection = self.get_connection_with_retry(dsn)

        except Exception as e:
            self.delete_certificate_file()
            logger.log_exception(
                "Failed to establish Postgres connection", exc_info=True
            )
            raise Exception(
                "There was an error connecting to the training data database."
            )

        logger.log_debug("Finished getting Postgres connection",
                         start_time=start_time)

    @retry(stop_max_attempt_number=3, wait_exponential_multiplier=1000)
    def get_connection_with_retry(self, dsn):
        """Retry connection with exponential backoff."""
        return psycopg2.connect(dsn)

    def get_query_to_execute(self, limit, offset, random_sample=False):
        query = f'SELECT *, row_number() over() as "{self.row_id_column}" FROM "{self.schema_name}"."{self.table_name}"'
        query += f' ORDER BY "{self.row_id_column}" LIMIT {limit} OFFSET {offset}'
        if random_sample:
            query = f'SELECT * FROM {self.schema_name}."{self.table_name}" order by random() limit {limit}'
        return query
