# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2021
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------
import json
import pandas as pd
import numpy as np
from lime.lime_tabular import LimeTabularExplainer


class Perturbations():
    """Generates perturbations for lime tabluar explainer."""

    def __init__(self, training_stats: json, problem_type: str, perturbations_count=10000, discretize_continuous=True, output_data_schema={}):
        """
        Arguments:
            training_stats:
                The Explainability training statistics
            problem_type:
                The problem type of the machine learning model. The value can be either regression, binary or multiclass
            perturbations_count:
                The number of pertubations to be generated
        """
        self.output_schema = self.__get_output_schema(output_data_schema)
        self.mode = "regression" if problem_type == "regression" else "classification"
        self.perturbations_count = perturbations_count
        if self.perturbations_count == 0:
            self.perturbations_count = 10000
        self.discretize_continuous = discretize_continuous
        self.training_stats = TrainingStatsReader(
            training_stats, features_schema=self.output_schema).training_stats
        self.__parse_training_stats()

    def __get_output_schema(self, output_data_schema):
        output_schema = {}
        if output_data_schema and output_data_schema.get("fields"):
            output_schema = {f.get("name"): f.get("type")
                             for f in output_data_schema.get("fields")}

        return output_schema

    def __parse_training_stats(self):
        self.feature_columns = self.training_stats.get("feature_columns")
        self.categorical_columns = self.training_stats.get(
            "categorical_columns")
        self.cat_features_indexes = [i for i, v in enumerate(
            self.feature_columns) if v in self.categorical_columns]
        self.cat_col_encoding_map = self.training_stats.get(
            "categorical_columns_encoding_mapping")
        self.data = pd.DataFrame(
            np.zeros((1, len(self.feature_columns))), columns=self.feature_columns).values
        self.stats = {
            "means": self.training_stats.get("d_means"),
            "mins": self.training_stats.get("d_mins"),
            "maxs": self.training_stats.get("d_maxs"),
            "stds": self.training_stats.get("d_stds"),
            "feature_values": self.training_stats.get("feature_values"),
            "feature_frequencies": self.training_stats.get("feature_frequencies")
        }

    def __get_data_row(self):
        data_row = [0] * len(self.feature_columns)

        base_values = self.training_stats.get("base_values")
        for i in range(len(self.feature_columns)):
            data_row[i] = base_values[i]

        for i in self.cat_features_indexes:
            data_row[i] = self.cat_col_encoding_map[i].index(data_row[i])

        return data_row

    def generate_perturbations(self):
        data_row = self.__get_data_row()
        lime_tabular = LimeTabularExplainer(self.data,
                                            feature_names=np.asarray(self.feature_columns), categorical_features=self.cat_features_indexes,
                                            categorical_names=self.cat_col_encoding_map,
                                            mode=self.mode,
                                            random_state=10,
                                            training_data_stats=self.stats,
                                            discretize_continuous=self.discretize_continuous)
        _, response = lime_tabular._LimeTabularExplainer__data_inverse(
            np.array(data_row), self.perturbations_count)
        df = pd.DataFrame(response, columns=self.feature_columns)
        return self.__get_decoded_df(df)

    def __get_decoded_df(self, df):
        for key, value in self.cat_col_encoding_map.items():
            feature_value = df[self.feature_columns[key]]
            feature_value_decoded = [value[int(x)] for x in feature_value]
            df[self.feature_columns[key]] = pd.Series(feature_value_decoded)

        if self.output_schema:
            numeric_features = [
                f for f in self.feature_columns if f not in self.categorical_columns]
            for f in numeric_features:
                feature_data_type = self.output_schema.get(f)
                if feature_data_type:
                    feature_data_type = feature_data_type.lower()
                    if any(i in feature_data_type for i in ["int", "integer", "long"]):
                        df[f] = df[f].astype(int)
        return df


class TrainingStatsReader():
    """Class used to read the training statistics json and perform the required transformations"""

    def __init__(self, training_stats, features_schema):
        self.features_schema = features_schema
        self.features = training_stats.get("feature_columns")
        self.categorical_features = training_stats.get("categorical_columns")
        self.training_stats = self.__transform_stats(training_stats)

    def __transform_stats(self, training_stats):
        transformed_stats = self.__convert_stats_keys(training_stats)
        self.__update_cat_cols_stats(transformed_stats)
        self.__update_class_labels(transformed_stats)

        return transformed_stats

    def __convert_stats_keys(self, training_stats):
        """Convert the required attributes in statistics dict from string to int and return"""
        updated_stats = {}

        # Convert string keys to int
        for k in list(training_stats.keys()):
            v = training_stats.get(k)
            if isinstance(v, list):
                new_value = v
            else:
                new_value = {}
                for k_in_v in v:
                    try:
                        new_value[int(k_in_v)] = v[k_in_v]
                    except ValueError:
                        new_value[k_in_v] = v[k_in_v]

            updated_stats[k] = new_value

        return updated_stats

    def __update_cat_cols_stats(self, stats):
        """This method will convert the categorical values to numbers/boolean if the feature datatype is not string.
        In statistics json, the column value keys in categorical counts are in string format.
        Incase the categorical column has numeric/boolean data type, this conversion is needed to make
        the data of keys in categorical counts, base values, encoding mapping to be in sync with the actual column data.
        """
        if not (self.features_schema and self.categorical_features):
            return

        updated_counts = stats.get("categorical_counts")
        updated_mapping = stats.get("categorical_columns_encoding_mapping")
        updated_base_values = stats.get("base_values")

        for feature in self.categorical_features:
            feature_type = self.features_schema.get(feature)
            col_index = self.features.index(feature)

            col_count = updated_counts.get(col_index)
            if feature_type in ["boolean", "bool"]:
                updated_base_values[col_index] = (
                    "true" == updated_base_values[col_index].lower())
                updated_mapping[col_index] = [
                    ("true" == val.lower()) for val in updated_mapping[col_index]]
                updated_counts[col_index] = {
                    ("true" == k.lower()): v for k, v in col_count.items()}
            elif feature_type is not None and feature_type not in ["string", "str"]:
                # Try for a type coversion and if it fails simply pass
                try:
                    col_count = {
                        int(k): v for k, v in col_count.items()}
                except ValueError:
                    try:
                        col_count = {
                            float(k): v for k, v in col_count.items()}
                    except ValueError:
                        pass
                except Exception:
                    pass
                updated_counts[col_index] = col_count

        stats["categorical_counts"] = updated_counts
        stats["base_values"] = updated_base_values
        stats["categorical_columns_encoding_mapping"] = updated_mapping

    def __update_class_labels(self, stats):
        labels = stats.get("class_labels")
        if labels:
            stats["class_labels"] = set([label.strip() if type(
                label) == str else label for label in labels])
