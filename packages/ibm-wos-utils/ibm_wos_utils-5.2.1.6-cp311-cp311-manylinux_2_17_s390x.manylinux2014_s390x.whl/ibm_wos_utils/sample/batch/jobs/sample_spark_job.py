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

from ibm_wos_utils.sample.batch.utils.subtraction import Subtraction
from ibm_wos_utils.sample.batch.utils.addition import Addition
from ibm_wos_utils.joblib.utils.db_utils import DbUtils
from ibm_wos_utils.joblib.utils.joblib_utils import JoblibUtils
from ibm_wos_utils.joblib.utils.param_utils import get_dict_from_param_list
from ibm_wos_utils.joblib.jobs.aios_spark_job import AIOSBaseJob


class SampleJob(AIOSBaseJob):

    def run_job(self):

        self.logger.info(
            "===================== This is Monitor Job (Demo) =================")

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

        # Try accessing the data sources, if specified in job parameters
        data_sources = self.arguments.get("tables", [])
        for data_source in data_sources:
            self.logger.info("Reading data from "+ data_source.get("table"))
            data_source_type = data_source.get("type")
            probability_column = JoblibUtils.get_column_by_modeling_role(data_source.get("columns"), "probability") if data_source.get("columns") else None
            # Check if location type and connection properties exist in map. If not found, try to get it from common storage
            location_type = self.location_type_map.get(data_source_type) if self.location_type_map.get(data_source_type) else self.location_type
            connection_properties=self.jdbc_connection_properties_map.get(data_source_type) if self.jdbc_connection_properties_map.get(data_source_type) else self.jdbc_connection_properties

            df = DbUtils.get_table_as_dataframe(
                self.spark,
                location_type,
                data_source.get("database"),
                data_source.get("table"),
                data_source.get("schema"),
                connection_properties=connection_properties,
                probability_column=probability_column
                )
            df.printSchema()
            df.show()

        output_path = self.arguments.get("output_file_path")
        self.logger.info("Data filepath: " +
                         self.arguments.get('data_file_path'))

        data = {
            'accuracy': 0.805,
            'true_positive_rate': 0.576,
            'recall': 0.576,
            'precision': 0.7422680412371134,
            'false_positive_rate': 0.09090909090909091,
            'area_under_roc': 0.7425454545454546,
            'area_under_pr': 0.6511572164948454,
            'f1_measure': 0.6486486486486486,
            'confusion_matrix': [[250.0, 25.0], [53.0, 72.0]]
        }

        data = {
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

        path = output_path + "/output.json"
        # Save my output data to output.json
        self.logger.info("Saving my output data to file")
        super().save_data(path=path, data_json=data)

        s = Subtraction()
        a = Addition()
        self.logger.info(' Sum of 9 and 5 is ' + str(a.add(9, 5)))
        self.logger.info(' Diff between 9 and 5 is ' + str(s.subtract(9, 5)))

        self.logger.info(" Save the stacktrace")

        try:
            unknown_class.add(9, 9)
        except Exception as ex:
            self.logger.info(
                "Exception thrown so that we can save the stacktrace, Error: '{}'".format(str(ex)))
            super().save_exception_trace(error_msg=str(ex))

        self.logger.info(
            "================== FINISHED JOB =========================")
        self.logger.error(
            '############################# JOB FINISHED   #############################')
