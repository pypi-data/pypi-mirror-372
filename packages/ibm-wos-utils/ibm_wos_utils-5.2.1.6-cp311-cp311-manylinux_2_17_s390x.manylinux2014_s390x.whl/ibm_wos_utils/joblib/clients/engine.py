# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2020, 2021
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

import json
import logging
import os

from abc import ABC, abstractmethod
from ibm_wos_utils.joblib.utils import constants
from ibm_wos_utils.joblib.utils.db_utils import DbUtils
from ibm_wos_utils.joblib.utils.db2_utils import DB2Utils
from ibm_wos_utils.joblib.utils.postgres_utils import POSTGRESUtils
from ibm_wos_utils.joblib.utils.param_utils import get
from ibm_wos_utils.joblib.utils.constants import JDBCDatabaseType

logger = logging.getLogger(__name__)


class Client(ABC):

    """
    Abstract class for all Spark job related actions
    """

    @abstractmethod
    def run_job(self, job_name, job_class, job_args, data_file_list=None, background=True, timeout=constants.SYNC_JOB_MAX_WAIT_TIME):
        '''
        - Upload data_file_list
        - Push entry job if it is not already pushed
        - compose job payload
        - run the job (Jobs will be available in wos_utils package
        '''
        pass

    @abstractmethod
    def get_job_status(self, job_id):
        pass

    @abstractmethod
    def get_file(self, file_path):
        pass

    @abstractmethod
    def get_exception(self, output_file_path):
        pass

    @abstractmethod
    def get_job_logs(self, job_id):
        pass

    @abstractmethod
    def delete_job_artifacts(self, job_id):
        pass

    @abstractmethod
    def kill_job(self, job_id):
        pass

    def __upload_job_artifacts(self, files_list, target_folder, overwrite=True):
        pass

    @abstractmethod
    def download_directory(self, directory_path):
        pass

    @abstractmethod
    def delete_directory(self, directory_path):
        pass

    @abstractmethod
    def upload_directory(self, directory_path, archive_directory_content):
        pass

    def create_table_job_post_processing_steps(self, table_info_json):
        db_client = None
        try:

            table_info_details = json.loads(
                get(table_info_json, "table_info_details"))
            jdbc_connection_details = {}

            if table_info_details:
                jdbc_connection_details = get(
                    table_info_json, "jdbc_connection_details")

            # Since the tables may have different JDBC connection, we need to check if the table has connection property
            # (e.g. explain_result has DB2 connection, and explain_queue has Postgres connection)
            for table_info in table_info_details:
                connection_details = get(table_info, "connection") or jdbc_connection_details
                db_client = self.__get_db_connection(connection_details)
                self.__alter_table_with_partition_index_primary_columns(db_client, table_info)

            logger.info(
                "Completed the post processing steps for create table job.")

        except Exception as e:
            logger.exception(
                "An error occurred while updating partition column {}".format(str(e)))
            pass

        finally:
            if db_client:
                db_client.delete_certificate_file()
                db_client.close_connection()

    def __get_db_connection(self, jdbc_connection_details):

        if not jdbc_connection_details:
            raise Exception(
                "jdbc connection details are not set in the partitions json.")

        certificate = get(jdbc_connection_details, "certificate")
        username = get(jdbc_connection_details, "user")
        password = get(jdbc_connection_details, "password")
        use_ssl = True if get(jdbc_connection_details,
                              "sslConnection") else False
        
        db_type, host_name, port, database_name = self._get_db_connection_from_jdbc_details(jdbc_connection_details)

        # Assign the utils class depending on the database type
        db_client = {
            JDBCDatabaseType.DB2.value: DB2Utils,
            JDBCDatabaseType.POSTGRESQL.value: POSTGRESUtils
        }[db_type](database_name, host_name, port,
                username, password, use_ssl, certificate)
        
        db_client.get_connection()
        
        return db_client

    def __alter_table_with_partition_index_primary_columns(self, db_client, table_info):
        try:
            schema_name = get(table_info, "schema_name")
            table_name = get(table_info, "table_name")

            partition_column_name = get(table_info, "partition_column")
            primary_key = get(table_info, "primary_key")
            index_column = get(table_info, "index_column")

            additional_index_columns = get(
                table_info, "additional_index_columns")
            additional_primary_keys = get(
                table_info, "additional_primary_keys")

            queries = []
            if partition_column_name:
                queries.append(db_client.generate_partition_column_query(
                    schema_name=schema_name,
                    table_name=table_name,
                    partition_column=partition_column_name))

            if primary_key:
                queries.append(db_client.generate_primary_keys_query(
                    schema_name=schema_name,
                    table_name=table_name,
                    primary_keys=[primary_key]))

            if additional_primary_keys:
                queries.append(db_client.generate_primary_keys_query(
                    schema_name=schema_name,
                    table_name=table_name,
                    primary_keys=additional_primary_keys))

            if index_column:
                queries.append(db_client.generate_index_columns_query(
                    schema_name=schema_name,
                    table_name=table_name,
                    index_columns=["{} DESC".format(index_column)]))

            if additional_index_columns:
                queries.append(db_client.generate_index_columns_query(
                    schema_name=schema_name,
                    table_name=table_name,
                    index_columns=additional_index_columns))

            logger.info("Alter table queries {}".format(queries))

            db_client.execute_queries(queries)
        except Exception as e:
            raise e

    def check_and_create_ssl_cert_files(self, job_args: dict):
        """
        Creates SSL certificate files for JDBC data sources if base64 encoded certificate is specified
        Arguments:
            job_args: The job arguments
        Returns:
            certificate_files: List of certificate file paths
        """
        certificate_files = []
        data_sources = job_args.get("tables", [])
        # If storage is common for all tables, generate certificate file using common storage details. Otherwise, generate a separate file for each table.
        if job_args.get("storage"):
            certificate_file = self.__check_and_create_ssl_cert_file(job_args)
            if certificate_file:
                certificate_files.append(certificate_file)
        else:
            for data_source in data_sources:
                certificate_file = self.__check_and_create_ssl_cert_file(
                    data_source)
                if certificate_file:
                    certificate_files.append(certificate_file)

        return certificate_files

    def __check_and_create_ssl_cert_file(self, data_source: dict):
        """
        Creates SSL certificate file for given JDBC data source if base64 encoded certificate is specified
        Arguments:
            data_source: The data source details
        Returns:
            certificate_file: certificate file path of generated SSL certificate
        """
        certificate_file = DbUtils.check_and_create_ssl_cert_file(data_source)
        if certificate_file:
            # Add certificate_file name to job parameters
            directory, file_name = os.path.split(certificate_file)
            data_source["storage"]["connection"]["ssl_cert_file_name"] = file_name

        return certificate_file
    
    def _get_db_connection_from_jdbc_details(self, jdbc_connection_details):
        jdbc_url = get(jdbc_connection_details, "url").split("//")
        db_type = jdbc_url[0].split(":")[1]
        host = jdbc_url[1].split(":")
        host_name = host[0]
        port = host[1].split("/")[0]
        database_name = host[1].split("/")[1]

        return db_type, host_name, port, database_name
