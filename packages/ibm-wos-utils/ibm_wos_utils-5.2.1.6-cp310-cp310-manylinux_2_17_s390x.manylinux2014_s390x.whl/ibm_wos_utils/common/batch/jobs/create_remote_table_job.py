# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2021
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------
import json
try:
    from pyspark.sql import SQLContext
except ImportError as e:
    pass
from ibm_wos_utils.joblib.jobs.aios_spark_job import AIOSBaseJob
from ibm_wos_utils.joblib.utils.constants import *
from ibm_wos_utils.joblib.utils.table_utils import TableUtils



class CreateRemoteTableJob(AIOSBaseJob):
    """Spark job to get the explanations from hive"""

    def run_job(self):
        self.logger.info("Starting the table creation job")
        self.logger.info(self.arguments)
        table_utils = TableUtils(spark=self.spark, sql_context=self.sc, arguments=self.arguments, 
                                    storage_type=self.storage_type, location_type=self.location_type,
                                    jdbc_connection_properties=self.jdbc_connection_properties, 
                                    location_type_map=self.location_type_map, jdbc_connection_properties_map=self.jdbc_connection_properties_map)
        tables_status, table_info_json, error_msg = {}, {}, None
        try:
             tables_status, table_info_json, error_msg = table_utils.create_table()
             if error_msg:
                 raise Exception(error_msg)
        finally:
            self.save_data(self.arguments.get("output_file_path") +
                            "/tables_status.json", {"tables_status":tables_status})
            if table_info_json:
                self.save_data(self.arguments.get("output_file_path") +
                            "/table_info.json", table_info_json)
            if error_msg:
                self.save_data(self.arguments.get("output_file_path") +
                            "/exception.json", {"error_msg": error_msg})
            self.logger.info("completed create/validate table job execution.")