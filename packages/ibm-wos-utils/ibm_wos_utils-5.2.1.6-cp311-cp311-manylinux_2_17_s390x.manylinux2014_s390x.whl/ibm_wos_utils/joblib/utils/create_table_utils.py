# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2022
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# -------------

import logging

from ibm_wos_utils.common.batch.jobs.create_remote_table_job import CreateRemoteTableJob
from ibm_wos_utils.joblib.clients.engine_client import EngineClient
from ibm_wos_utils.joblib.utils.python_utils import get

logger = logging.getLogger(__name__)

class CreateTableUtils:
    '''
    Utility class for creating table on remote database(Hive/db2)
    '''

    def __init__(self,  analytics_engine, tables, connection={}):
        self.connection = connection
        self.analytics_engine = analytics_engine
        self.tables = tables

    def get_tables_status(self):

        tables_status = []
        for table in self.tables:
            table_status = {
                "table_name": get(table, "table_name"),
                "state": "preparing"
                }
            tables_status.append(table_status)
        return tables_status

    def get_job_params(self):
        '''
        get the parameters needed for creating the remote spark job
        
        '''
        job_params = {
                        "spark_settings": get(self.analytics_engine, "parameters"),
                        "dependency_zip": [],
                        "arguments":{
                            "tables": self.tables
                        }
                    }
        if self.connection:
            connection_credentials = get(self.connection, "credentials")
            storage =  {
                                "type": get(self.connection, "type"),
                                "connection": get(self.connection, "connection"),
                                "credentials": connection_credentials
                            }
            job_params["arguments"]["storage"] = storage

        return job_params
                

    def create_remote_table(self):
        '''
        Creates the remote table in hive/db2
        based on the connection type
        '''
        tables_status = self.get_tables_status()
        engine_client = EngineClient(get(self.analytics_engine, "credentials"))
        logger.info("Started creating remote table on hive.")
    
        job_params = self.get_job_params()

        logger.info("Starting remote table creation job")
        job_response = engine_client.engine.run_job(job_name="create_remote_table", 
                                                job_class=CreateRemoteTableJob, job_args=job_params)

        logger.info("Create table job response {}".format(job_response))
        
        
        return self.format_response(job_id=get(job_response, "id"), \
                                        output_file_path=get(job_response, "output_file_path"), \
                                        state="preparing", \
                                        tables_status=tables_status)

    def format_response(self, job_id, output_file_path, state, tables_status):
        '''
        Format the response returned by hive/db2
        '''
        response = {}

        response["job_id"] = job_id
        response["output_file_path"] = output_file_path
        response["state"] = state
        response["tables_status"] = tables_status

        return response
