# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2021
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

try:
    from pyspark.sql import SparkSession
    from pyspark.sql.dataframe import DataFrame
except ImportError as ie:
    pass

import math
from ibm_wos_utils.fairness.batch.utils import constants
from ibm_wos_utils.fairness.batch.utils.date_util import DateUtil
from ibm_wos_utils.fairness.batch.utils.indirect_bias.correlated_attr_distribution_utils import CorrelatedAttrDistributionUtils
from ibm_wos_utils.fairness.batch.utils.python_util import get
from ibm_wos_utils.fairness.batch.utils.sql_utils import SQLUtils
from ibm_wos_utils.joblib.utils.db_utils import DbUtils


class BatchUtils():

    @classmethod
    def get_group_counts(cls, data, col_name: str, group_vals: list, fav_label_query: str, data_type, group_counts: dict=None, correlated_attr_group_vals: list=None) -> dict:
        """
        Returns the counts of the given group with it"s given classes counts.
        :data: The data on which the counts are to be counted. (from pyspark.sql.dataframe import DataFrame)
        :col_name: The column on which the counts are to be done.
        :group_vals: The group values/ranges for which the counts are to be made.
        :fav_label_query: The favourable label query.
        :data_type: The data type of the column
        :group_counts: [Optional] Dictionary containing counts for each group in `group_vals` of the given `col_name`. This if given, optimises the DI calculation.
        :correlated_attr_group_vals: [Optional] The correlated majority/minority group values if col_name is a protected attribute.
            Example,
                If col_name = "age"
                and, group_vals = [
                    [18, 25],
                    [70, 90]
                ] then,
                group_counts = {
                    "[18, 25]": 120,
                    "[70, 90]": 180
                }
                or if col_name = "gender"
                and, group_vals = [
                    "female",
                    "others"
                ] then,
                group_counts = {
                    "female": 80,
                    "others": 50
                }

        :returns: The favourable and total counts for the given group.
        """
        count_dict = {}
        # Getting the group rows
        if data_type in constants.CATEGORICAL_DATA_TYPES:
            all_groups_query = SQLUtils.get_cat_filter_query(
                col_name, "==", group_vals)
        elif data_type in constants.NUMERICAL_DATA_TYPES:
            all_groups_query = SQLUtils.get_num_filter_query(
                col_name, group_vals)
        else:
            raise ValueError(
                "Unknown data type {} encountered for {} column.".format(data_type, col_name))
        all_groups_df = data.filter(all_groups_query)

        # Getting the group counts
        for group in group_vals:
            group_query = ""
            # Getting the query for the current group
            if data_type in constants.CATEGORICAL_DATA_TYPES:
                group_query = SQLUtils.get_cat_filter_query(
                    col_name, "==", [group])
            elif data_type in constants.NUMERICAL_DATA_TYPES:
                group_query = SQLUtils.get_num_filter_query(col_name, [group])
            else:
                raise ValueError(
                    "Unknown data type {} encountered for {} column.".format(data_type, col_name))

            # Getting applying filter to get current group rows
            group_df = all_groups_df.filter(group_query)
            group_fav_df = group_df.filter(fav_label_query)
            group_fav_count = group_fav_df.count()
            group_count = group_df.count() if group_counts is None or str(group) not in group_counts else group_counts[str(group)]
            count_dict[str(group)] = {
                "fav_count": group_fav_count,
                "total_count": group_count
            }
            # If the col_name is a protected attribute, compute correlated attributes group counts using the correlation information.
            if correlated_attr_group_vals:
                correlated_attr_group_counts = {}
                group_correlations = cls.get_correlations_for_maj_min_group(correlated_attr_group_vals, group)
                if group_count > 0 and group_correlations:
                    correlated_attr_group_counts = CorrelatedAttrDistributionUtils.get_correlated_attr_group_counts(group, group_correlations, group_df, group_fav_df, group_count, group_fav_count)
                count_dict[str(group)]["correlated_attr_group_counts"] = correlated_attr_group_counts
        return count_dict

    @classmethod
    def calculate_di_variables(cls, data, fairness_attribute: str, inputs: dict, data_type, model_type: str, group_counts: dict=None) -> dict:
        """
        Calculates the variables needed for disparate impact calculation on the given fairness attribute.
        :data: The data on which the variables are to be calculated. (from pyspark.sql.dataframe import DataFrame)
        :fairness_attribute: The fairness attribute on which the variables are to be calculated.
        :inputs: The inputs dictionary.
        :data_type: The data type of the fairness attribute column.
        :group_counts: [Optional] Dictionary containing counts for each group of the given fairness attributes present in the fairness configuration. This if given, optimises the DI calculation.
            Example,
                If inputs = {
                    "fairness_attributes": ["age", "gender"],
                    "majority": {
                        "age": [[18, 25]],
                        "gender": ["male"]
                    },
                    "minority": {
                        "age": [[26, 90]],
                        "gender": ["female]
                    }...
                }
                and, fairness_attribute = "age" then,
                group_counts = {
                    "[18, 25]": 120,
                    "[26, 90]": 180
                }
                or if fairness_attribute = "gender" then,
                group_counts = {
                    "male": 220,
                    "female": 80
                }

        :returns: The DI variables for the given inputs.
        """
        di_vars = {
            "majority": {},
            "minority": {}
        }
        # Getting the majority and minority groups
        majority = inputs.get("majority", {}).get(fairness_attribute, None)
        minority = inputs.get("minority", {}).get(fairness_attribute, None)
        # Getting the label column and favourable outcomes
        label_column = get(inputs, "class_label")
        fav_classes = get(inputs, "favourable_class")

        # Getting the query for favourable outcome rows
        favorable_count_query = None
        if model_type == constants.REGRESSION_MODEL_TYPE:
            favorable_count_query = SQLUtils.get_num_filter_query(
                label_column, fav_classes)
        else:
            favorable_count_query = SQLUtils.get_cat_filter_query(
                label_column, "==", fav_classes)

        # If it is a protected attribute, use correlation information from inputs to compute correlated attributes distribution counts
        correlated_majority = None
        correlated_minority = None
        is_protected_attribute = fairness_attribute in inputs.get("protected_attributes", [])
        if is_protected_attribute:
            correlated_attributes = inputs.get("correlated_attributes", {}).get(fairness_attribute, None)
            if correlated_attributes:
                correlated_majority = inputs.get("correlated_majority", {}).get(fairness_attribute, None)
                correlated_minority = inputs.get("correlated_minority", {}).get(fairness_attribute, None)

        # Getting the counts for majority
        maj_group_total_counts = {str(x): group_counts[str(x)] for x in majority} if group_counts is not None else None
        di_vars["majority"] = cls.get_group_counts(
            data, fairness_attribute, majority, favorable_count_query, data_type, maj_group_total_counts, correlated_attr_group_vals=correlated_majority)

        # Getting the counts for minorities
        mino_group_total_counts = {str(x): group_counts[str(x)] for x in minority} if group_counts is not None else None
        di_vars["minority"] = cls.get_group_counts(
            data, fairness_attribute, minority, favorable_count_query, data_type, mino_group_total_counts, correlated_attr_group_vals=correlated_minority)
        return di_vars

    @classmethod
    def calculate_di_dict(cls, data, inputs: dict, data_types: dict, model_type: str, total_group_counts: dict=None) -> dict:
        """
        Returns a dictionary with disparate impact variables for the given data for all fairness attributes in the given inputs.
        :data: The data on which the disparate impact variables are to be calculated. (from pyspark.sql.dataframe import DataFrame)
        :inputs: The inputs dictionary.
        :data_types: The data types of the fairness attributes.
        :model_type: The model type.
        :total_group_counts: [Optional] Dictionary containing counts for each group of all fairness attributes present in the fairness configuration. This if given, optimises the DI calculation.
            Example,
                If inputs = {
                    "fairness_attributes": ["age", "gender"],
                    "majority": {
                        "age": [[18, 25]],
                        "gender": ["male"]
                    },
                    "minority": {
                        "age": [[26, 90]],
                        "gender": ["female]
                    }...
                } then,
                total_group_counts = {
                    "age": {
                        "[18, 25]": 120,
                        "[26, 90]": 180
                    },
                    "gender": {
                        "male": 220,
                        "female": 80
                    }
                }

        :returns: Dictionary containing DI values for the given fairness configuration.
        """
        di_dict = {}

        # Getting all labels
        all_labels = get(inputs, "favourable_class") + get(inputs, "unfavourable_class")
        label_column = get(inputs, "class_label")

        # Filtering unused label rows
        if model_type == constants.REGRESSION_MODEL_TYPE:
            all_label_query = SQLUtils.get_num_filter_query(label_column, all_labels)
        else:
            all_label_query = SQLUtils.get_cat_filter_query(label_column, "==", all_labels)
        
        # Applying the query
        data = data.filter(all_label_query)

        for fairness_attribute in inputs["fairness_attributes"]:
            data_type = data_types[fairness_attribute] if fairness_attribute in data_types else None
            # Calculating the DI variables on the given data
            fair_att_group_counts = total_group_counts[fairness_attribute] if total_group_counts is not None and fairness_attribute in total_group_counts else None
            di_dict[fairness_attribute] = cls.calculate_di_variables(
                data, fairness_attribute, inputs, data_type, model_type, fair_att_group_counts)
        # Add rows analyzed
        di_dict = cls.add_rows_analyzed(di_dict, data, inputs, data_types)
        return di_dict

    @classmethod
    def get_inputs_from_monitor_instance(cls, monitor_instance: dict) -> dict:
        """
        Converts the given fairness configuration into the inputs dictionary.
        :monitor_instance: The fairness configuration dictionary.

        :returns: The inputs object from the given monitor instance.
        """
        inputs = {}
        parameters = get(monitor_instance, "entity.parameters")
        inputs["class_label"] = get(parameters, "class_label")
        inputs["favourable_class"] = get(parameters, "favourable_class")
        inputs["unfavourable_class"] = get(parameters, "unfavourable_class")
        inputs["min_records"] = get(parameters, "min_records")
        majority = {}
        minority = {}
        fairness_attributes = []
        threshold = []
        protected_attributes = []
        correlated_attributes = {}
        correlated_majority = {}
        correlated_minority = {}
        features = get(parameters, "features")
        if features is not None:
            for feature_details in features:
                feature = get(feature_details, "feature")
                if feature is not None:
                    fairness_attributes.append(feature)
                    threshold.append(get(feature_details, "threshold"))
                    majority[feature] = get(feature_details, "majority")
                    minority[feature] = get(feature_details, "minority")
                    # For protected attributes, add correlation information to inputs
                    is_protected_attribute = feature_details.get("is_protected_attribute")
                    if is_protected_attribute is not None and is_protected_attribute is True:
                        protected_attributes.append(feature)
                        if "correlated_attributes" in feature_details:
                            correlated_attributes[feature] = feature_details.get("correlated_attributes")
                        if "correlated_majority" in feature_details:
                            correlated_majority[feature] = feature_details.get("correlated_majority")
                        if "correlated_minority" in feature_details:
                            correlated_minority[feature] = feature_details.get("correlated_minority")
        inputs["majority"] = majority
        inputs["minority"] = minority
        inputs["threshold"] = threshold
        inputs["fairness_attributes"] = fairness_attributes
        inputs["protected_attributes"] = protected_attributes
        inputs["correlated_attributes"] = correlated_attributes
        inputs["correlated_majority"] = correlated_majority
        inputs["correlated_minority"] = correlated_minority
        return inputs

    @classmethod
    def get_data_source_from_subscription(cls, subscription: dict, data_source_type: str) -> dict:
        """
        Parses the subscription and returns the given data source type.
        :subscription: The subscription JSON.
        :data_source_type: The data source type to be returned.

        :returns: The data source of the type from the given subscription.
        """
        data_source = None
        data_sources = get(subscription, "entity.data_sources")
        if data_sources is not None and isinstance(data_sources, list):
            for ds in data_sources:
                if ds["type"] == data_source_type:
                    data_source = ds
                    break
        return data_source

    @classmethod
    def get_data_types(cls, subscription: dict, fairness_attributes: list) -> dict:
        """
        Parses the subscription JSON and returns the data types of the given fairness attribute.
        :subscription: The subscription JSON.
        :fairness_attributes: The list of fairness attributes.

        :returns: The data types of the fairness attributes as per the output data schema in the subscription.
        """
        data_types = {}

        # Getting the fields array from the output data schema
        fields = get(
            subscription, "entity.asset_properties.output_data_schema.fields")
        for field in fields:
            field_name = field["name"]
            if field_name in fairness_attributes:
                data_types[field_name] = field["type"]

        return data_types

    @classmethod
    def check_if_modeling_role_present(cls, modeling_role: str, schema: dict) -> bool:
        """
        Checks if the given modeling role is present in the given schema.
        :modeling_role: The modeling role to be checked.
        :schema: The schema in which the modeling role is to be searched.

        :returns: The boolean flag indicating if the given modeling role present in the schema.
        """
        is_present = False

        for field in schema["fields"]:
            field_modeling_role = get(field, "metadata.modeling_role")
            is_deleted_field = get(field, "metadata.deleted")
            if field_modeling_role and field_modeling_role == modeling_role and not is_deleted_field:
                is_present = True
                break
        return is_present

    @classmethod
    def get_name_with_modeling_role(cls, modeling_role: str, schema: dict) -> str:
        """
        Returns the name of the column with the given modeling role in the given schema.
        :modeling_role: The modeling role to be checked.
        :schema: The schema in which the column name is to be searched.

        :returns: The column name with the given modeling role in the schema.
        """
        col_name = None

        for field in schema["fields"]:
            field_modeling_role = get(field, "metadata.modeling_role")
            is_deleted_field = get(field, "metadata.deleted")
            if field_modeling_role and field_modeling_role == modeling_role and not is_deleted_field:
                col_name = field["name"]
                break
        
        return col_name
    
    @classmethod
    def get_names_with_modeling_role(cls, modeling_role: str, schema: dict) -> list:
        """
        Returns the names of the column with the given modeling role in the given schema.
        :modeling_role: The modeling role to be checked.
        :schema: The schema in which the column name is to be searched.

        :returns: The list of column names with the given modeling role in the schema.
        """
        col_names = list()

        for field in schema["fields"]:
            field_modeling_role = get(field, "metadata.modeling_role")
            is_deleted_field = get(field, "metadata.deleted")
            if field_modeling_role and field_modeling_role == modeling_role and not is_deleted_field:
                col_name = field["name"]
                col_names.append(col_name)
        
        return col_names

    @classmethod
    def add_rows_analyzed(cls, di_dict: dict, data, inputs: dict, data_types: dict) -> dict:
        """
        Calculates and adds rows analyzed from the DI variable values.
        :di_dict: The DI dictionary.
        :data: The data on which the disparate impact variables are calculated. (from pyspark.sql.dataframe import DataFrame)
        :inputs: The inputs dictionary.
        :data_types: The data types of the fairness attributes.

        :returns: The DI dictionary with global rows analyzed and for each fairness attribute.
        """
        global_rows_analyzed = None

        # Figuring out the attribute with highest rows analyzed
        max_row_fair_att = None
        max_rows_analyzed = None
        for fairness_attribute in di_dict:
            fa_di_dict = di_dict[fairness_attribute]
            # Calcuating the rows analyzed for this fairness attribute
            fa_rows_analyzed = 0

            # Adding the minority counts
            min_dict = fa_di_dict["minority"]
            for min_group in min_dict:
                fa_rows_analyzed += min_dict[min_group]["total_count"]

            # Adding the majority counts
            maj_dict = fa_di_dict["majority"]
            for maj_group in maj_dict:
                fa_rows_analyzed += maj_dict[maj_group]["total_count"]

            # Adding rows analyzed for the fairness attribute
            fa_di_dict["rows_analyzed"] = fa_rows_analyzed

            # Updating the max rows fairness attribute
            if max_row_fair_att is None:
                max_row_fair_att = fairness_attribute
                max_rows_analyzed = fa_rows_analyzed
            else:
                if fa_rows_analyzed > max_rows_analyzed:
                    max_row_fair_att = fairness_attribute
                    max_rows_analyzed = fa_rows_analyzed
        
        # Calculating the global rows analyzed #20703
        # Getting the count of unused groups for this attribute
        data_type = data_types[max_row_fair_att]
        all_used_groups = inputs.get("majority", {}).get(max_row_fair_att, "") + inputs.get("minority", {}).get(max_row_fair_att, "")
        if data_type in constants.CATEGORICAL_DATA_TYPES:
            # The attribute is categorical
            unused_group_query = SQLUtils.get_cat_filter_query(max_row_fair_att, "!=", all_used_groups, concat_operator="and")
            unused_rows_fair_att = data.filter(unused_group_query).count()
        else:
            # The attribute is numerical
            unused_group_query = SQLUtils.get_num_filter_query(max_row_fair_att, all_used_groups, include=False, concat_operator="and")
            unused_rows_fair_att = data.filter(unused_group_query).count()
        
        print("Unused rows for max rows analyzed fairness attribute were found to be {}".format(unused_rows_fair_att))
        global_rows_analyzed = max_rows_analyzed + unused_rows_fair_att
        print("Global rows analyzed is {}".format(global_rows_analyzed))

        # Adding the global rows analyzed
        di_dict["rows_analyzed"] = global_rows_analyzed
        return di_dict

    @classmethod
    def merge_di_dicts(cls, di_dict_1: dict, di_dict_2: dict) -> dict:
        """
        Adds up the numbers from the given DI dictionaries and returns a combined one.
        :di_dict_1: The first DI dictionary.
        :di_dict_2: The second DI dictionary.

        :returns: The merged DI dictionary with added counts for each group.
        """
        di_dict = {}

        # Adding the numbers for each of the fairness attributes given
        for key in di_dict_1:
            if key == "rows_analyzed":
                di_dict["rows_analyzed"] = di_dict_1["rows_analyzed"] + \
                    di_dict_2["rows_analyzed"]
            else:
                # Calculating the summed majority
                summed_majority = {}
                for maj in di_dict_1[key]["majority"]:
                    summed_majority[maj] = {
                        "fav_count": di_dict_1[key]["majority"][maj]["fav_count"] + di_dict_2[key]["majority"][maj]["fav_count"],
                        "total_count": di_dict_1[key]["majority"][maj]["total_count"] + di_dict_2[key]["majority"][maj]["total_count"]
                    }
                # Calculating the summed minority
                summed_minority = {}
                for mino in di_dict_2[key]["minority"]:
                    summed_minority[mino] = {
                        "fav_count": di_dict_1[key]["minority"][mino]["fav_count"] + di_dict_2[key]["minority"][mino]["fav_count"],
                        "total_count": di_dict_1[key]["minority"][mino]["total_count"] + di_dict_2[key]["minority"][mino]["total_count"]
                    }
                di_dict[key] = {
                    "majority": summed_majority,
                    "minority": summed_minority,
                    "rows_analyzed": di_dict_1[key]["rows_analyzed"] + di_dict_2[key]["rows_analyzed"]
                }

        return di_dict
    
    @classmethod
    def merge_group_counts_dicts(cls, group_counts_dict_1: dict, group_counts_dict_2: dict) -> dict:
        """
        Adds up the numbers for the given two group count dictionaries.
        :group_counts_dict_1: The first group counts dictionary.
        :group_counts_dict_2: The second group counts dictionary.
            Example,
                If inputs = {
                    "fairness_attributes": ["age", "gender"],
                    "majority": {
                        "age": [[18, 25]],
                        "gender": ["male"]
                    },
                    "minority": {
                        "age": [[26, 90]],
                        "gender": ["female]
                    }...
                } then,
                group_counts_dict = {
                    "age": {
                        "[18, 25]": 120,
                        "[26, 90]": 180
                    },
                    "gender": {
                        "male": 220,
                        "female": 80
                    }
                }

        :returns: The group counts dictionary with added numbers.
        """
        group_counts = {x: dict() for x in group_counts_dict_1}

        for column_name in group_counts_dict_1:
            for group in group_counts_dict_1[column_name]:
                group_count_1 = group_counts_dict_1.get(column_name, {}).get(group, 0)
                group_count_2 = group_counts_dict_2.get(column_name, {}).get(group, 0)
                group_counts[column_name][group] = group_count_1 + group_count_2

        return group_counts
    
    @classmethod
    def get_batch_data_distribution(cls, data_counts: dict, monitor_instance: dict) -> dict:
        """
        Generates the distribution (fav/unfav counts only) for the given counts.

        :data_counts: the counts for the given data.
        :monitor_instance: The monitor instance object.

        :returns: The tuple containing distribution and correlated attributes distribution(if exists) objects.
        """
        data_distribution = None
        correlated_attr_distribution = None

        # Generating the values
        values = []
        corr_attr_dist_values = []

        for feature in get(monitor_instance, "entity.parameters.features"):
            fairness_attribute = get(feature, "feature")
            is_protected_attribute = get(feature, "is_protected_attribute", default=False)

            # Getting the counts for the fairness attribute
            att_counts = data_counts.get("counts", {}).get(fairness_attribute, {})

            # Adding the majority counts
            majority = get(feature, "majority")
            maj_counts = get(att_counts, "majority")
            for maj in majority:
                # Getting the counts
                fav_count = maj_counts.get(str(maj), {}).get("fav_count", 0)
                total_count = maj_counts.get(str(maj), {}).get("total_count", 0)
                unfav_count = total_count - fav_count
                
                values.append([
                    fairness_attribute,
                    maj,
                    fav_count,
                    unfav_count,
                    "reference"
                ])
            
                # If attribute is a protected attribute, generate correlated attribute distribution if counts for the correlated attribute values exist.
                if is_protected_attribute:
                    corr_attr_dist_counts = maj_counts.get(str(maj), {}).get("correlated_attr_group_counts", None)
                    if corr_attr_dist_counts is not None:
                        corr_dist_values = CorrelatedAttrDistributionUtils.get_correlated_attr_dist_values(fairness_attribute, maj, corr_attr_dist_counts, "reference")
                        corr_attr_dist_values.extend(corr_dist_values)

            # Adding the minority counts
            minority = get(feature, "minority")
            mino_counts = get(att_counts, "minority")
            for mino in minority:
                # Getting the counts
                fav_count = mino_counts.get(str(mino), {}).get("fav_count", 0)
                total_count = mino_counts.get(str(mino), {}).get("total_count", 0)
                unfav_count = total_count - fav_count

                values.append([
                    fairness_attribute,
                    mino,
                    fav_count,
                    unfav_count,
                    "monitored"
                ])

                # If attribute is a protected attribute, generate correlated attribute distribution if counts for the correlated attribute values exist.
                if is_protected_attribute:
                    corr_attr_dist_counts = mino_counts.get(str(mino), {}).get("correlated_attr_group_counts", None)
                    if corr_attr_dist_counts is not None:
                        corr_dist_values = CorrelatedAttrDistributionUtils.get_correlated_attr_dist_values(fairness_attribute, mino, corr_attr_dist_counts, "monitored")
                        corr_attr_dist_values.extend(corr_dist_values)

        data_distribution = {
            "fields": [
                "feature",
                "feature_value",
                "fav_count",
                "unfav_count",
                "group"
            ],
            "values": values
        }

        # Constructing correlated attribute distribution if corr_attr_dist_values are generated
        if len(corr_attr_dist_values) > 0:
            correlated_attr_distribution = {
                "fields": [
                    "feature",
                    "feature_value",
                    "correlated_feature",
                    "correlated_feature_value",
                    "fav_count",
                    "unfav_count",
                    "total_rows_percent",
                    "group"
                ],
                "values": corr_attr_dist_values
            }

        return data_distribution, correlated_attr_distribution
    
    @classmethod
    def get_spark_settings_from_subscription(cls, subscription: dict) -> dict:
        """
        Returns the spark settings from the given subscription object.
        :subscription: The subscription object.

        :returns: The spark settings from the given subscription.
        """
        spark_settings = None
        spark_settings = get(
            subscription, "entity.analytics_engine.parameters")
        return spark_settings
    
    @classmethod
    def read_stratified_samples(
        cls,
        sample_size_percent: int,
        inputs: dict,
        data_types: dict,
        spark, # SparkSession
        location_type: str,
        db_name: str,
        table_name: str,
        columns_to_map: list,
        columns_to_filter: list,
        model_type: str,
        all_labels: list,
        schema_name: str=None,
        jdbc_connection_properties: dict=None,
        record_timestamp_column: str=None,
        start_time: str=None,
        end_time: str=None,
        probability_column: str=None,
        order_by_timestamp_desc: bool=None,
        partition_column: str=None,
        num_partitions: int=None
    ): # (DataFrame, dict)
        """
        Reads the data from Hive table with stratified samples as per the fairness configuration.
        :sample_size_percent: The sample size in terms of percentage.
        :inputs: The inputs dictionary.
        :data_types: The data types of each of the fairness attributes.
        :spark: The Spark session.
        :location_type: The location type (hive or jdbc).
        :db_name: The database name.
        :table_name: The table name.
        :columns_to_map: The columns to map.
        :columns_to_filter: The columns to filter.
        :model_type: The model type.
        :all_labels: All the known labels (or ranges) for the prediction.
        :schema_name: The schema name. [Optional]
        :jdbc_connection_properties: The JDBC connection properties. [Optional]
        :record_timestamp_column: The record timestamp column. [Optional]
        :start_time: The start time for the data. [Optional]
        :end_time: The end time for the data. [Optional]
        :probability_column: The probability column name in the data. [Optional]
        :order_by_timestamp_desc: Whether the data should be sorted based on timestamp column in decreasing order. [Optional]
        :parititon_column: The column on which the table is partitioned on. [Optional]
        :num_partitions: The number of partitions. [Optional]

        :returns: The final dataframe with all samples combined along with total counts for each group.
        """
        spark_df = None
        total_group_counts = dict()

        # Generating the all label query
        for_sql = False if location_type == "metastore" else True
        label_column = get(inputs, "class_label")
        if model_type == constants.REGRESSION_MODEL_TYPE:
            all_label_query = SQLUtils.get_num_filter_query(label_column, all_labels, include=True, for_sql=for_sql)
        else:
            operator = "==" if location_type == "metastore" else "="
            all_label_query = SQLUtils.get_cat_filter_query(label_column, operator, all_labels, for_sql=for_sql)

        for fairness_attribute in inputs["fairness_attributes"]:
            total_group_counts[fairness_attribute] = dict()
            # Reading for minority groups
            for mino in inputs["minority"][fairness_attribute]:
                # Building the SQL queries
                group_df, sample_size = cls.get_stratified_sample(
                    column_name=fairness_attribute,
                    groups=[mino],
                    data_type=data_types[fairness_attribute],
                    sample_size_percent=sample_size_percent,
                    spark=spark,
                    location_type=location_type,
                    db_name=db_name,
                    table_name=table_name,
                    columns_to_map=columns_to_map,
                    columns_to_filter=columns_to_filter,
                    all_label_query=all_label_query,
                    schema_name=schema_name,
                    jdbc_connection_properties=jdbc_connection_properties,
                    record_timestamp_column=record_timestamp_column,
                    start_time=start_time,
                    end_time=end_time,
                    probability_column=probability_column,
                    order_by_timestamp_desc=order_by_timestamp_desc,
                    partition_column=partition_column,
                    num_partitions=num_partitions
                )
                spark_df = spark_df.unionByName(group_df) if spark_df is not None else group_df
                total_group_counts[fairness_attribute][str(mino)] = sample_size
            
            # Reading for majority groups
            for maj in inputs["majority"][fairness_attribute]:
                maj_df, sample_size = cls.get_stratified_sample(
                    column_name=fairness_attribute,
                    groups=[maj],
                    data_type=data_types[fairness_attribute],
                    sample_size_percent=sample_size_percent,
                    spark=spark,
                    location_type=location_type,
                    db_name=db_name,
                    table_name=table_name,
                    columns_to_map=columns_to_map,
                    columns_to_filter=columns_to_filter,
                    all_label_query=all_label_query,
                    schema_name=schema_name,
                    jdbc_connection_properties=jdbc_connection_properties,
                    record_timestamp_column=record_timestamp_column,
                    start_time=start_time,
                    end_time=end_time,
                    probability_column=probability_column,
                    order_by_timestamp_desc=order_by_timestamp_desc,
                    partition_column=partition_column,
                    num_partitions=num_partitions
                )
                spark_df = spark_df.unionByName(maj_df) if spark_df is not None else maj_df
                total_group_counts[fairness_attribute][str(maj)] = sample_size

        return spark_df, total_group_counts
    
    @classmethod
    def get_stratified_sample(
        cls,
        column_name: str,
        groups: list,
        data_type: str,
        sample_size_percent: int,
        spark, # SparkSession
        location_type: str,
        db_name: str,
        table_name: str,
        columns_to_map: list,
        columns_to_filter: list,
        all_label_query: str,
        schema_name: str=None,
        jdbc_connection_properties: dict=None,
        record_timestamp_column: str=None,
        start_time: str=None,
        end_time: str=None,
        probability_column: str=None,
        order_by_timestamp_desc: bool=None,
        partition_column: str=None,
        num_partitions: int=None
    ): # (DataFrame, int)
        """
        Reads the stratified sample for the given group.
        :column_name: The column on which the sampling is to be performed.
        :groups: The group which is to be sampled. [List of strings in case of categorical column, list of ranges (list) otherwise.]
        :data_type: The data type of the column.
        :sample_size_percent: The sample size in terms of percentage.
        :spark: The Spark session.
        :location_type: The location type (hive or jdbc).
        :db_name: The database name.
        :table_name: The table name.
        :columns_to_map: The columns to map.
        :columns_to_filter: The columns to filter.
        :all_label_query: The filter query for all known labels (or ranges).
        :schema_name: The schema name. [Optional]
        :jdbc_connection_properties: The JDBC connection properties. [Optional]
        :record_timestamp_column: The record timestamp column. [Optional]
        :start_time: The start time for the data. [Optional]
        :end_time: The end time for the data. [Optional]
        :probability_column: The probability column name in the data. [Optional]
        :order_by_timestamp_desc: Whether the data should be sorted based on timestamp column in decreasing order. [Optional]
        :parititon_column: The column on which the table is partitioned on. [Optional]
        :num_partitions: The number of partitions. [Optional]

        :returns: The dataframe containing sample for the given group and the sample size read.
        """
        group_df = None

        # Getting the size of the group
        for_sql = False if location_type == "metastore" else True
        if data_type == "string":
            operator = "==" if location_type == "metastore" else "="
            group_filter = SQLUtils.get_cat_filter_query(column_name, operator, values=groups, for_sql=for_sql)
        else:
            group_filter = SQLUtils.get_num_filter_query(column_name, groups, include=True, for_sql=for_sql)
        
        # Appending the known label query with group filter
        group_filter = SQLUtils.concat_query(group_filter, "and", all_label_query)
        
        if location_type == "metastore":
            size_query = "select count(\"{}\") as COUNT from {}.{} where {}".format(column_name, db_name, table_name, group_filter)
        else:
            size_query = "select count(\"{}\") as COUNT from \"{}\".\"{}\" where {}".format(column_name, schema_name, table_name, group_filter)

        size_query = size_query.replace("``", "`")
        size_query = size_query.replace("\"`", "\"")
        size_query = size_query.replace("`\"", "\"")
        
        count_df = DbUtils.get_table_as_dataframe(
            spark=spark,
            location_type=location_type,
            database_name=db_name,
            table_name=table_name,
            schema_name=schema_name,
            connection_properties=jdbc_connection_properties,
            sql_query=size_query
        )
        data_size = count_df.first()["COUNT"] if "COUNT" in count_df.first() else count_df.first()["count"]
        sample_size = (data_size * sample_size_percent) // 100

        # Getting the sampled data
        if location_type == "metastore":
            data_query = "select * from {}.{} where {} distribute by rand() sort by rand() limit {}".format(db_name, table_name, group_filter, sample_size)
        else:
            if "postgresql" in str(jdbc_connection_properties):
                data_query = "select * from \"{}\".\"{}\" where {} order by random() limit {}".format(schema_name, table_name, group_filter, sample_size)
            else:
                data_query = "select * from \"{}\".\"{}\" where {} order by rand() limit {}".format(schema_name, table_name, group_filter, sample_size)
        
        data_query = data_query.replace("``", "`")
        data_query = data_query.replace("\"`", "\"")
        data_query = data_query.replace("`\"", "\"")
        
        group_df = DbUtils.get_table_as_dataframe(
            spark=spark,
            location_type=location_type,
            database_name=db_name,
            table_name=table_name,
            schema_name=schema_name,
            connection_properties=jdbc_connection_properties,
            sql_query=data_query,
            columns_to_map=columns_to_map,
            columns_to_filter=columns_to_filter,
            record_timestamp_column=record_timestamp_column,
            start_time=start_time,
            end_time=end_time,
            probability_column=probability_column,
            order_by_timestamp_desc=order_by_timestamp_desc,
            partition_column=partition_column,
            num_partitions=num_partitions
        )

        return group_df, sample_size

    @classmethod
    def get_feature_details_from_config(cls, fairness_config: dict, feature_name: str):
        """
        Fetches the feature details from  fairness configuration
        Arguments:
            :fairness_config: The fairness configuration.
            :feature_name: The name of feature whose details need to be fetched.
        Returns:
            :The details of feature like majority, minority, threshold, etc.
        """
        features = get(fairness_config, "parameters.features")
        for feature in features:
            if feature.get("feature") == feature_name:
                return feature
        # Return none if not found
        return None

    @classmethod
    def should_skip_perturbation_for_prot_attr(cls, inputs: dict, protected_attribute: str):
        """
        Checks if a protected attribute has correlated attributes and determines whether to skip perturbation.
        Arguments:
            :inputs: The inputs dictionary containing feature details.
            :protected_attribute: The name of the protected attribute.
        Returns:
            :Boolean flag to indicate whether to skip perturbation for the protected_attribute.
        """
        correlated_attributes = inputs.get("correlated_attributes", {}).get(protected_attribute, None)
        if correlated_attributes is None or len(correlated_attributes) == 0:
            return True
        return False

    @classmethod
    def get_correlations_for_maj_min_group(cls, correlated_maj_min: list, to_group):
        """
        Fetches correlation details for the specified majority/minority group of the protected attribute
        Arguments:
            :correlated_maj_min: The correlated majority/minority
            :to_group: The majority/minority group for which correlation map is to be found. It can be string or a list(numerical range)
        Returns:
            : The correlation details for the specified majority/minority group. 
        """
        correlations = None
        for val in correlated_maj_min:
            if to_group == val.get("feature_value"):
                correlations = val.get("correlations")
                break
        return correlations
    
    @classmethod
    def get_class_labels_from_prediction_metadata(cls, output_data_schema: dict) -> list:
        """
        Reads the class_labels from the prediction modeling role object from the output data schema (https://github.ibm.com/aiopenscale/tracker/issues/28078#issuecomment-49115177).
        :output_data_schema: The output data schema object.

        :returns: The class label fields.
        """
        class_labels = list()

        for field in output_data_schema["fields"]:
            field_modeling_role = get(field, "metadata.modeling_role")
            if field_modeling_role is not None and field_modeling_role == constants.PREDICTION_MODELING_ROLE:
                class_labels = get(field, "metadata.class_labels", default=list())
                break

        return class_labels

    @classmethod
    def get_time_windows(cls, run_parameters: dict, monitor_instance: dict) -> list:
        """
        Computes time windows for fairness evaluation based on start time and end time specified in run parameters.
        - If start time and end time are not specified, it is usual flow where start time is last_processed_ts, end time is none.
        - If start time, end time and N compute_windows are specified, divide the total interval in compute_windows to find the N evaluation windows.
        - If start time, end time are specified with evalute_using_schedule option, use the schedule information to find the evaluation windows.
        - If only start time, end time are specified, consider it entire interval as single window.
        
        Arguments:
            :run_parameters: The monitoring run parameters
            :monitor_instance: The monitor instance containing all details.
        Returns:
            : The time windows for fairness evaluation.
        """
        time_windows = []

        if not run_parameters or "start_time" not in run_parameters or "end_time" not in run_parameters:
            # Usual flow
            start_time = get(monitor_instance, "entity.parameters.last_processed_ts")
            time_windows.append([start_time, None])
            return time_windows
        else:
            # Historical run
            start_time = get(run_parameters, "start_time")
            end_time = get(run_parameters, "end_time")
            compute_windows = get(run_parameters, "compute_windows")
            evaluate_using_schedule = get(run_parameters, "evaluate_using_schedule")

            if compute_windows is not None and int(compute_windows) > 0:
                # Split the total interval using compute_windows
                compute_windows = int(compute_windows)
                if compute_windows == 1:
                    time_windows.append([start_time, end_time])
                    return time_windows
    
                time_diff_in_seconds = DateUtil.get_time_diff_in_seconds(
                    from_time=start_time, to_time=end_time)
                seconds_per_window = time_diff_in_seconds / compute_windows
                # Compute time windows for the interval based on seconds_per_window and window count
                time_windows = cls.get_time_windows_for_interval(start_time, end_time, compute_windows, seconds_per_window)
                
            elif evaluate_using_schedule is not None and str(evaluate_using_schedule).lower() == "true":
                # Split the total interval using schedule's frequency
                repeat_type = get(monitor_instance, "entity.schedule.repeat_type")
                repeat_interval = get(monitor_instance, "entity.schedule.repeat_interval")
                time_diff_in_seconds = DateUtil.get_time_diff_in_seconds(
                    from_time=start_time, to_time=end_time)
                seconds_per_window = cls.get_schedule_interval_in_seconds(repeat_type, repeat_interval)
                # Calculating the total compute windows based on schedule frequency
                compute_windows = math.ceil(time_diff_in_seconds / seconds_per_window)
                # Compute time windows for the interval based on seconds_per_window and window count
                time_windows = cls.get_time_windows_for_interval(start_time, end_time, compute_windows, seconds_per_window)
            else:
                # Return single window for complete interval
                time_windows.append([start_time, end_time])
                return time_windows

        return time_windows

    @classmethod
    def get_time_windows_for_interval(cls, start_time: str, end_time: str, windows_count: int, seconds_per_window: int) -> list:
        """
        Computes time windows for given interval using windows_count and seconds_per_window

        Arguments:
            :start_time: The start time of the interval.
            :end_time: The end time of the interval.
            :windows_count: The number of evaluation windows to be generated.
            :seconds_per_window: The duration in seconds for each window.
        Returns:
            : The time windows for given interval.
        """
        time_windows = []
        window_start_time = None
        window_end_time = None

        for _ in range(windows_count):
            if not window_start_time: # First window
                window_start_time = start_time
            else:
                window_start_time = DateUtil.get_datetime_with_time_delta(
                    time=window_end_time, unit="microsecond", count=1)

            window_end_time = DateUtil.get_datetime_with_time_delta(
                time=window_start_time, unit="second", count=seconds_per_window)
            if DateUtil.get_datetime_str_as_time(window_end_time) > DateUtil.get_datetime_str_as_time(end_time):
                # This is for last window where the calculated end time can be greater than the end of the interval
                window_end_time = end_time

            time_windows.append([window_start_time, window_end_time])

        return time_windows
        
    @classmethod
    def get_schedule_interval_in_seconds(cls, repeat_type: str, repeat_interval: int) -> int:
        """
        Computes schedule interval in seconds.

        Arguments:
            :repeat_type: The repeat type of schedule
            :repeat_interval: The repeat interval of schedule.
        Returns:
            : The schedule interval in seconds.
        """
        interval_in_seconds = 1
        if repeat_type == "week":
            interval_in_seconds = 7 * 24 * 60 * 60
        elif repeat_type == "day":
            interval_in_seconds = 24 * 60 * 60
        elif repeat_type == "hour":
            interval_in_seconds = 60 * 60
        elif repeat_type == "minute":
            interval_in_seconds = 60
        else:
            raise Exception("Unsupported repeat type for the schedule {}. Supported repeat types are {}".format(repeat_type, ["week", "day", "hour", "minute"]))

        return repeat_interval * interval_in_seconds
