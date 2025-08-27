# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2020, 2021
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

import json
import uuid

from ibm_wos_utils.joblib.jobs.aios_spark_job import AIOSBaseJob


class SampleJobWithKHive(AIOSBaseJob):

    def run_job(self):

        self.logger.info(
            "===================== This is Sample Job interacting with Kerberized hive(Demo) =================")

        self.logger.debug(
            '############################# debug message #############################')
        self.logger.info(
            '############################# info message #############################')
        self.logger.warn(
            '############################# warn message #############################')
        self.logger.error(
            '############################# error message  #############################')

        self.logger.info("Parameter Dict :")
        self.logger.info(json.dumps(self.arguments, indent=2))

        output_path = self.arguments.get("output_file_path")
        self.logger.info("Data filepath: " +
                         self.arguments.get('data_file_path'))

        sql_df1 = self.spark.sql("show tables")
        sql_df1.show()

        sql_df2 = self.spark.sql(
            "Select count(*) from ppm_data.gcr_payload_100k;")
        sql_df2.show()

        data_json = {
            'output_json': [
                {
                    "counts": {
                        "Age": {
                            "minority": {
                                "[18, 25]": {
                                    "fav_count": 110,
                                    "total_count": 190
                                },
                                "[71, 90]": {
                                    "fav_count": 5,
                                    "total_count": 6
                                },
                                "[56, 59]": {
                                    "fav_count": 14,
                                    "total_count": 20
                                }
                            },
                            "majority": {
                                "[60, 70]": {
                                    "fav_count": 33,
                                    "total_count": 45
                                },
                                "[26, 55]": {
                                    "fav_count": 538,
                                    "total_count": 739
                                }
                            }
                        },
                        "Sex": {
                            "minority": {
                                "female": {
                                    "fav_count": 201,
                                    "total_count": 310
                                }
                            },
                            "majority": {
                                "male": {
                                    "fav_count": 499,
                                    "total_count": 690
                                }
                            }
                        }
                    },
                    "time_taken": "57.491331338882446",
                    "data_source": "payload"
                }
            ]
        }
        data_json = {key: value for key,
                     value in data_json.items() if value is not None}
        df = self.spark.createDataFrame([data_json])
        path = "{}/sample_output.json".format(output_path)
        df.coalesce(1).write.json(path, mode='overwrite')
        import time
        time.sleep(5)
        print('reading the file content from hdfs...')
        df = self.spark.read.json(path)
        df.printSchema()
        df.show()
