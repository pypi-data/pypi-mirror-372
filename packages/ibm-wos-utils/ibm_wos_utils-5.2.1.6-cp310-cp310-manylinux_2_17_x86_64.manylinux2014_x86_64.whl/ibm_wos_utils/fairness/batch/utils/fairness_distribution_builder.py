# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2021
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

"""
The fairness data distribution builder.
"""

try:
    from pyspark.sql.dataframe import DataFrame
except ImportError as ie:
    pass

from ibm_wos_utils.fairness.batch.utils.constants import CATEGORICAL_DATA_TYPES, NUMERICAL_DATA_TYPES
from ibm_wos_utils.fairness.batch.utils.date_util import DateUtil
from ibm_wos_utils.fairness.batch.utils.python_util import get
from ibm_wos_utils.fairness.batch.utils.sql_utils import SQLUtils

class FairnessDistributionBuilder():

    def __init__(self, fairness_parameters: dict, training_df):
        """
        Constructor for the class.
        :parameters: The fairness parameters.
        :training_df: The training data in a spark data frame. (from pyspark.sql.dataframe import DataFrame)
        """
        self.parameters = fairness_parameters
        self.training_df = training_df
    
    def build(self) -> dict:
        """
        Builds the fairness data distribution as per the given parameters.

        :returns: The fairness data distribution.
        """
        start_time = DateUtil.current_milli_time()

        # Validating the fairness parameters
        self._validate_parameters()

        # Generating the training data distribution
        data_distribution = self.generate_distribution()

        time_taken = DateUtil.current_milli_time() - start_time
        print("Time taken to build the fairness data distribution for {} rows was {} seconds.".format(get(data_distribution, "total_rows_count"), time_taken/1000))
        return data_distribution
    
    def generate_distribution(self):
        """
        Generates and returns the training data distribution.

        :returns: The training data distribution and the total rows count.
        """
        distribution = None
        rows_count = 0

        # Generating the distribution values
        distribution_values = []

        # Getting the model type
        model_type = get(self.parameters, "model_type")
        is_classification = False if model_type == "regression" else True

        for feature in get(self.parameters, "features"):
            fairness_attribute = get(feature, "feature")
            data_type = get(feature, "data_type")
            is_categorical = True if data_type in CATEGORICAL_DATA_TYPES else False
            attribute_row_count = 0
            
            # Generating the distribution for majority groups
            maj_dist_values, maj_total_count = self.get_group_distribution(fairness_attribute, get(feature, "majority"), "reference", is_categorical, is_classification)
            distribution_values.extend(maj_dist_values)
            attribute_row_count += maj_total_count

            # Generating the distribution for minority groups
            min_dist_values, min_total_count = self.get_group_distribution(fairness_attribute, get(feature, "minority"), "monitored", is_categorical, is_classification)
            distribution_values.extend(min_dist_values)
            attribute_row_count += min_total_count

            # Updating the total rows count
            rows_count = max(rows_count, attribute_row_count)
        

        # Building the distribution
        distribution = {
            "fields": [
                "feature",
                "feature_value",
                "label",
                "count",
                "is_favourable",
                "group"
            ],
            "values": distribution_values,
            "total_rows_count": rows_count
        }

        return distribution
    
    def get_group_distribution(self, fairness_attribute: str, group_vals: list, group_type: str, is_categorical: bool, is_classification: bool):
        """
        Generates the distribution for the given attribute for the given group classes/ranges.

        :fairness_attribute: The feature to which the groups belong.
        :group_vals: The values/ranges in the feature in which the distribution is to be calculated.
        :group_type: The type of the group.

        :returns: The distribution values for the given group and total row count.
        """

        dist_vals = []
        group_row_count = 0

        # Getting all label groups
        fav_labels = get(self.parameters, "favourable_class")
        unfav_labels = get(self.parameters, "unfavourable_class")
        all_labels = fav_labels + unfav_labels

        for group in group_vals:
            # Getting the group df
            
            # Buiding the group query
            if is_categorical:
                group_query = SQLUtils.get_cat_filter_query(fairness_attribute, "==", [group])
            else:
                group_query = SQLUtils.get_num_filter_query(fairness_attribute, [group])
            
            group_df = self.training_df.filter(group_query)
            
            # Getting the counts for each label
            for label in all_labels:
                label_count = self.get_label_count(fairness_attribute, group_df, label, is_classification)
                group_row_count += label_count
                dist_vals.append([
                    fairness_attribute,
                    group,
                    label,
                    label_count,
                    True if label in fav_labels else False,
                    group_type
                ])

        return dist_vals, group_row_count
    
    def get_label_count(self, fairness_attribute: str, group_df, label, is_classification: bool) -> int:
        """
        Returns the number of rows with the given group in the given fairness attribute with the given label in the label column.

        :fairness_attribute: The fairness attribute.
        :group_df: The data frame with rows of group for which the rows are to be counted. (from pyspark.sql.dataframe import DataFrame)
        :label: The label whose rows are to be counted. [Would be a string in case of classification model and a list in case of regression models.]
        :is_classification: Boolean flag indicating whether the model deployment is a classification model or regression.

        :returns: The row count.
        """
        label_count = None

        # Building the label query
        label_column = get(self.parameters, "class_label")
        if is_classification:
            label_query = SQLUtils.get_cat_filter_query(label_column, "==", [label])
        else:
            label_query = SQLUtils.get_num_filter_query(label_column, [label])

        label_count = group_df.filter(label_query).count()

        return label_count
    
    def _validate_parameters(self) -> None:
        """
        Validates the fairness parameters set in the class object.

        :returns: None
        """

        # Validating the first level keys
        first_level_keys = [
            "features",
            "class_label",
            "favourable_class",
            "unfavourable_class",
            "model_type",
            "min_records"
        ]
        for key in first_level_keys:
            if key not in self.parameters and key != "min_records":
                raise Exception("Mandatory field {} not provided in the parameters.".format(key))
        
        # Validating the min_records if present
        if "min_records" in self.parameters:
            min_records = get(self.parameters, "min_records")
            if not isinstance(min_records, int):
                raise Exception("Minimum records needed for fairness calculation must be an integer.")
        
        # Validating fav/unfav classes
        fav_classes = get(self.parameters, "favourable_class")
        if not isinstance(fav_classes, list):
            raise Exception("Favourable classes must be provided in a list.")
        unfav_classes = get(self.parameters, "unfavourable_class")
        if not isinstance(unfav_classes, list):
            raise Exception("Unfavourable classes must be provided in a list.")

        # Validating the class label
        class_label = get(self.parameters, "class_label")
        if not isinstance(class_label, str):
            raise Exception("The name of the label column must be a string.")

        # Validating the model type
        model_type = get(self.parameters, "model_type")
        if not isinstance(model_type, str):
            raise Exception("The model type must be a string.")

        # Validating the features
        features = get(self.parameters, "features")
        if not isinstance(features, list):
            raise Exception("The feature details should be given in a list.")

        feature_details = [
            "data_type",
            "feature",
            "majority",
            "minority",
            "threshold"
        ]
        for feature in features:
            for detail in feature_details:
                if detail not in feature and detail != "threshold":
                    raise Exception("Mandatory feature detail {} not provided.".format(detail))
                if detail == "data_type":
                    given_type = get(feature, detail)
                    supported_types = CATEGORICAL_DATA_TYPES + NUMERICAL_DATA_TYPES
                    if given_type not in supported_types:
                        raise Exception("The supported data types are {}.".format(supported_types))
            
            # Validating the threshold
            if "threshold" in feature:
                threshold = get(feature, "threshold")
                if not isinstance(threshold, float) or threshold < 0.0 or threshold > 1.0:
                    raise Exception("Threshold should be a float number between 0 and 1.")
            
            # Validating the attribute name
            fairness_attribute = get(feature, "feature")
            if not isinstance(fairness_attribute, str):
                raise Exception("The feature name which is to be monitored must be a string.")

            # Validating the majority and minority
            majority = get(feature, "majority")
            minority = get(feature, "minority")
            if not isinstance(majority, list):
                raise Exception("The majority groups must be provided in a list.")
            if not isinstance(minority, list):
                raise Exception("The minority groups must be provided in a list.")

        return