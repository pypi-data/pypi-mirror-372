# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2022
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------
import base64
import logging
import os
import tempfile
import ssl
from retrying import retry
import time

try:
    import ibm_db
except:
    pass

logger = logging.getLogger(__name__)

CONNECTION_TIMEOUT = 180  # Timeout in seconds for Db2 connections


class DB2Utils:
    """
    Utility class for creating remote table in db2
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
            dsn = "DATABASE="+self.database_name+";HOSTNAME="+self.host_name+";PORT="+str(self.port)+";PROTOCOL=TCPIP;UID="+str(
                self.username).lower()+";PWD="+self.password+";CONNECTTIMEOUT=" + str(CONNECTION_TIMEOUT) + ";"
            # if in icp, and when ssl is on, then set the certificate as well.
            if self.use_ssl:
                self.create_certificate_file()
                dsn = dsn + "SECURITY=ssl;SSLServerCertificate=" + self.cert_file + ";"
            # Create the connection
            self.connection = self.get_connection_with_retry(dsn)
        except Exception as e:
            logger.exception(str(e), exc_info=True)
            raise Exception(str(e))

        logger.info("Finished getting DB connection.")

    @retry(stop_max_attempt_number=3, wait_exponential_multiplier=1000)
    def get_connection_with_retry(self, dsn: str):
        """Retry scoring with wait of 2^x * 1000 milliseconds between each retry"""
        ibm_db_conn = ibm_db.connect(dsn, "", "")
        return ibm_db_conn

    def create_certificate_file(self):
        if self.certificate_base64:
            # if certificate already set in the connection_details
            if 'BEGIN CERTIFICATE' not in self.certificate_base64:
                # If 'BEGIN CERTIFICATE' is not present, assuming that it will be a base64 encoded.
                certificate = base64.b64decode(
                    self.certificate_base64.strip()).decode()
            else:
                certificate = self.certificate_base64.strip()
        else:
            # else get it from the host
            certificate = ssl.get_server_certificate(
                (self.host_name, self.port))
        with tempfile.NamedTemporaryFile(mode="w", prefix="db2ssl_", suffix="_cert.arm", delete=False) as f:
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

    def close_connection(self):
        try:
            if self.connection:
                self.connection.close()
        except Exception:
            logger.warning("Failed attempting to close DB2 connection.")

    def execute_queries(self, queries: list = []):
        for query in queries:
            try:
                ibm_db.exec_immediate(self.connection, query)
                time.sleep(1)
                logger.info(
                    "Executed the alter table query successfully {}".format(query))
            except Exception as e:
                logger.warn(
                    "Query {} failed with exception: {}".format(query, str(e)))
                pass

    def generate_partition_column_query(self, schema_name, table_name, partition_column):
        '''
        generates the list of ddls to execute in order to create partition using a new partition column
        on an existing table
        Example: 
            "ALTER TABLE "test_db"."german_credit_risk" ALTER COLUMN "scoring_timestamp" SET GENERATED ALWAYS AS IDENTITY;"
        '''

        partition_column_query = "ALTER TABLE \"{0}\".\"{1}\" ALTER COLUMN \"{2}\" SET GENERATED ALWAYS AS IDENTITY;".format(
            schema_name, table_name, partition_column)

        return partition_column_query

    def generate_primary_keys_query(self, schema_name, table_name, primary_keys: list = []):
        '''
        generates the alter table query to add primary keys to a db2 table.
        sample query: ALTER TABLE "db2_test"."sample" PRIMARY KEY ("emp_id");
        sample query: ALTER TABLE "db2_test"."sample" PRIMARY KEY ("emp_id", "cust_id");
        '''
        if not primary_keys:
            return None

        primary_keys_str = ""
        for col in primary_keys:
            primary_keys_str += "\"" + str(col) + "\"" + ","
        primary_keys_str = primary_keys_str.rstrip(",")

        return "ALTER TABLE \"{}\".\"{}\" PRIMARY KEY ({});".format(schema_name, table_name, primary_keys_str)

    def generate_index_columns_query(self, schema_name, table_name, index_columns: list = []):
        '''
        generates the alter table query to add index columns to a db2 table.
        sample query: CREATE INDEX "feedback_table_d840dd5da2ab4021a7e753c947de5240_index" ON "db2_test"."feedback_table_d840dd5da2ab4021a7e753c947de5240" ("scoring_timestamp" DESC)
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
        # As db2 has a limit of 128 bytes on the index name
        index_name = index_name_full if len(
            index_name_full) < 1024 else table_name[:1016] + "_index_1"

        index_query = "CREATE INDEX \"{1}\" ON \"{0}\".\"{2}\" ({3});".format(
            schema_name, index_name, table_name, index_str)

        return index_query
