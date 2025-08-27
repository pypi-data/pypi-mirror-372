# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2020, 2021
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

import uuid
import json
import os

class DriftModelSerializer(object):
    def __init__(self, spark, model):
        self.spark = spark
        self.input_directory = os.getcwd() + "/drift_model_{}".format(uuid.uuid4())
        self.model_stages = model.stages

        # TODO Figure out a way to save this if worker node does not have write permissions
        model.save("file://" + self.input_directory)

        self.valid_names = [
            self.input_directory,
            "stages",
            "metadata",
            "treesMetadata",
            "data"]

        # These directories have json files in them
        self.json_dirs = ["metadata"]

        # These directories have parquet files in them
        self.parquet_dirs = ["data", "treesMetadata"]

    def is_valid_stage_name(self, name):
        return name.endswith(tuple([stage.uid for stage in self.model_stages]))

    def get_model_as_dict(self, dirname=None, root=None):
        """Get Pyspark Model as a dict (recursively)

        Keyword Arguments:
            dirname {str} --  Directory to convert as dictionary (default: {None})
            root {str} -- Path traversed so far (default: {None})

        Returns:
            dict -- Model as a dict
        """
        if not dirname:
            dirname = self.input_directory
        result = {}
        if (dirname in self.valid_names) or self.is_valid_stage_name(dirname):
            dirpath = (root + "/" + dirname) if root else dirname
            for child in os.listdir(dirpath):
                cwd = dirpath + "/" + child
                if not os.path.isdir(cwd):
                    continue

                if child in self.json_dirs:
                    for file in os.listdir(cwd):
                        # For files starting with part* in json dirs, read the
                        # file as json and append to result
                        if os.path.isfile(
                                cwd + "/" + file) and file.startswith("part"):
                            with open(cwd + "/" + file, "r") as fp:
                                result[child] = {
                                    "type": "json",
                                    "name": file,
                                    "content": json.load(fp)
                                }
                elif child in self.parquet_dirs:
                    # For parquet directories, read the data as spark
                    # dataframe.
                    temp_df = self.spark.read.parquet("file://" + cwd)

                    # Dump the dataframe as json in a subdirectory
                    temp_df.write.json("file://" + cwd + "/json")
                    content = []
                    for fname in os.listdir(cwd + "/json"):
                        if fname.endswith("json"):
                            # Spark dumps as multi-line json files. Each line
                            # has to be loaded separately as a json.
                            with open(cwd + "/json/" + fname, "r") as fp:
                                for line in fp:
                                    content.append(json.loads(line))
                        result[child] = {
                            "type": "parquet",
                            "schema": temp_df.schema.jsonValue(),
                            "content": content
                        }
                else:
                    result[child] = self.get_model_as_dict(child, dirpath)
        return result
