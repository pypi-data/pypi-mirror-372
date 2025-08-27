# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2024
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------
import logging
import os
import base64
import ssl
import tempfile
from retrying import retry
import time

try:
    import psycopg2
except:
    pass

logger = logging.getLogger(__name__)

CONNECTION_TIMEOUT = 180  # Timeout in seconds for postgres connections


class POSTGRESUtils:
    """
    Utility class for creating remote table in Postgres
    """

    def __init__(self, database_name, host_name, port, username, password, use_ssl=False, certificate=None):
        self.database_name = database_name
        self.host_name = host_name
        self.port = port
        self.username = username
        self.password = password
        self.tables_status = []
        self.use_ssl = use_ssl
        self.cert_file = None
        self.certificate_base64 = certificate

    def get_connection(self):

        logger.info("Started getting DB connection.")
        try:
            dsn = (f"dbname={self.database_name} "
                   f"user={self.username} "
                   f"password={self.password} "
                   f"host={self.host_name} "
                   f"port={self.port} "
                   f"connect_timeout={str(CONNECTION_TIMEOUT)}"
                   )
            if self.use_ssl:
                self.create_certificate_file()
                dsn += f" sslmode=verify-full sslrootcert={self.cert_file}"
            # Create the connection
            self.connection = self.__get_connection_with_retry(dsn)
        except Exception as e:
            logger.exception(str(e), exc_info=True)
            raise Exception(str(e))

        logger.info("Finished getting DB connection.")

    @retry(stop_max_attempt_number=3, wait_exponential_multiplier=1000)
    def __get_connection_with_retry(self,dsn: str):
        """Retry scoring with wait of 2^x * 1000 milliseconds between each retry"""
        psql_conn = psycopg2.connect(dsn)
        return psql_conn


    def create_certificate_file(self):
        if self.certificate_base64:
            # If a certificate is provided in base64 format
            if 'BEGIN CERTIFICATE' not in self.certificate_base64:
                # Decode the base64-encoded certificate
                certificate = base64.b64decode(self.certificate_base64.strip()).decode()
            else:
                # Use the provided certificate directly
                certificate = self.certificate_base64.strip()
        else:
            # Retrieve the certificate from the server
            certificate = ssl.get_server_certificate((self.host_name, self.port))

        # Write the certificate to a temporary file
        with tempfile.NamedTemporaryFile(mode="w", prefix="db_ssl_", suffix="_cert.pem", delete=False) as f:
            self.cert_file = f.name
            f.write(certificate)

    def delete_certificate_file(self):
        if self.cert_file is not None:
            if (os.path.isfile(self.cert_file)):
                try:
                    os.remove(self.cert_file)
                except:
                    logger.warning(
                        "Failed to delete cert file " + self.cert_file + ".")

    def execute_queries(self, queries: list = []):
        for query in queries:
            try:
                cur = self.connection.cursor()
                cur.execute(query)
                self.connection.commit()
                time.sleep(1)
                logger.info(
                    "Executed the alter table query successfully {}".format(query))
            except Exception as e:
                logger.warn(
                    "Query {} failed with exception: {}".format(query, str(e)))
                pass

    def close_connection(self):
        try:
            if self.connection:
                self.connection.close()
        except Exception:
            logger.warning("Failed attempting to close Postgres connection.")

    def generate_partition_column_query(self, schema_name, table_name, partition_column):
        '''
        generates the list of ddls to execute in order to create partition using a new partition column
        on an existing table
        Example:
            "ALTER TABLE "test_db"."german_credit_risk" ALTER COLUMN "scoring_timestamp" ADD GENERATED ALWAYS AS IDENTITY;"
        '''

        partition_column_query = "ALTER TABLE \"{0}\".\"{1}\" ALTER COLUMN \"{2}\" ADD GENERATED ALWAYS AS IDENTITY;".format(
            schema_name, table_name, partition_column)

        return partition_column_query

    def generate_primary_keys_query(self, schema_name, table_name, primary_keys: list = []):
        '''
        generates the alter table query to add primary keys to a postgres table.
        sample query: ALTER TABLE "postgres_test"."sample" ADD PRIMARY KEY ("emp_id");
        sample query: ALTER TABLE "postgres_test"."sample" ADD PRIMARY KEY ("emp_id", "cust_id");
        '''
        if not primary_keys:
            return None

        primary_keys_str = ""
        for col in primary_keys:
            primary_keys_str += "\"" + str(col) + "\"" + ","
        primary_keys_str = primary_keys_str.rstrip(",")

        return "ALTER TABLE \"{}\".\"{}\"ADD PRIMARY KEY ({});".format(schema_name, table_name, primary_keys_str)

    def generate_index_columns_query(self, schema_name, table_name, index_columns: list = []):
        '''
        generates the alter table query to add index columns to a postgres table.
        sample query: CREATE INDEX "feedback_table_d840dd5da2ab4021a7e753c947de5240_index" ON "postgres_test"."feedback_table_d840dd5da2ab4021a7e753c947de5240" ("scoring_timestamp" DESC)
        sample query: CREATE INDEX "drifted_transactions_table_5c36d18d819a4fc9a831975b44ac6ec1_index" ON "SMPL_NTBK_SCHEMA"."drifted_transactions_table_5c36d18d819a4fc9a831975b44ac6ec1" ("run_id", "is_model_drift", "is_data_drift")
        '''
        if not index_columns:
            return None

        # Convert the index columns array into tuple of the form
        # (subscription_id, request_id)
        index_str = ""
        for col in index_columns:
            # if index columns are of the form ["subscription_id ASC", "request_id", "scoring_id", "finished_at DESC"],
            # the below code formats it accordingly
            col_split = col.split(" ")
            col = col_split[0]
            order = None if len(col_split) < 2 else col_split[1]

            if order:
                index_str += "\"" + str(col) + "\" " + str(order).upper() + ","
                continue
            index_str += "\"" + str(col) + "\"" + ","

        index_str = index_str.rstrip(",")

        index_name_full = "{}_index_1".format(table_name)

        # truncate the index name if the length is grater than 1024
        index_name = index_name_full if len(
            index_name_full) < 1024 else table_name[:1016] + "_index_1"

        index_query = "CREATE INDEX \"{1}\" ON \"{0}\".\"{2}\" ({3});".format(
            schema_name, index_name, table_name, index_str)

        return index_query
