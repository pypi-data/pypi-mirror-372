# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2021
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

import logging
import random
import secrets

try:
    from pyspark.sql import SparkSession, Window
    from pyspark.sql.dataframe import DataFrame
    from pyspark.sql.functions import array, explode, lit, monotonically_increasing_id, row_number, udf, col
    from pyspark.sql.types import ArrayType, FloatType, IntegerType, LongType, StringType, StructField, StructType
except ImportError as ie:
    pass

from ibm_wos_utils.fairness.batch.utils.batch_utils import BatchUtils
from ibm_wos_utils.fairness.batch.utils.date_util import DateUtil
from ibm_wos_utils.fairness.batch.utils.python_util import get
from ibm_wos_utils.fairness.batch.utils.sql_utils import SQLUtils

logger = logging.getLogger(__name__)

class PerturbationUtils():

    @classmethod
    def perform_perturbation(cls, data, column_to_perturb: str, from_group, to_groups: list, spark, numerical_perturb_count_per_row: int=2, float_decimal_place_precision: int=None, numerical_perturb_seed: int=0, from_group_count: int=None, correlation_info: dict=None): # (DataFrame, dict)
        """
        Performs perturbation on the given Spark data-frame (transformations) and returns the perturbed data frame.
        :data: The Spark data frame containing the data to be perturbed.
        :column_to_perturb: The column name on which perturbation is to be performed.
        :from_group: The group on which the perturbation is to be performed. [String in case of categorical columns and list (containing the range) in case of numerical columns.]
        :to_groups: The list of groups to which the perturbation is to be performed. [List of strings in case of categorical columns and list of lists (containing the ranges) in case of numerical columns.]
        :spark: The SparkSession object.
        :numerical_perturb_count_per_row: [Optional] The number of perturbed rows to be generated per row for numerical perturbation.
        :float_decimal_place_precision: [Optional] The decimal place precision to be used for numerical perturbation when data is float.
        :numerical_perturb_seed: [Optional] The seed to be used for numerical perturbation while picking up random values.
        :from_group_count: [Optional] The number of rows belonging to `from_group`. [Optimises numerical perturbation.]
        :correlation_info: [Optional] The correlation information of the protected attribute to be used for perturbation of correlated attributes.
        
        :returns: A data-frame containing the perturbed records of all `to_groups` and the count of perturbed rows generated for each `to_group`.
            Example,
                If to_groups = [
                    [18, 25],
                    [70, 90]
                ] then,
                pert_to_groups_count = {
                    "[18, 25]": 120,
                    "[70, 90]": 80
                }
                or if to_groups = ["female", "others"] then,
                pert_to_groups_count = {
                    "female": 220,
                    "others": 80
                }
        """
        perturbed_df = pert_to_groups_count = None

        # Checking of the column is categorical or numerical
        is_categorical = isinstance(data.schema[column_to_perturb].dataType, StringType)

        if is_categorical:
            # Performing the categorical perturbation
            perturbed_df, pert_to_groups_count = cls._categorical_perturbation(data, column_to_perturb, from_group, to_groups, spark, from_group_count=from_group_count, correlation_info=correlation_info)
        else:
            # Performing the numerical perturbation
            perturbed_df, pert_to_groups_count = cls._numerical_perturbation(data, column_to_perturb, from_group, to_groups, numerical_perturb_count_per_row, float_decimal_place_precision, numerical_perturb_seed, spark, from_group_count=from_group_count, correlation_info=correlation_info)

        return perturbed_df, pert_to_groups_count
    
    @classmethod
    def _categorical_perturbation(cls, data, column_to_perturb: str, from_group: str, to_groups: list, spark, from_group_count: int, correlation_info: dict=None): # (DataFrame, dict)
        """
        Performs the categorical perturbation on the given Spark data-frame (transformations) and returns the perturbed data frame.
        :data: The Spark data frame containing the data to be perturbed.
        :column_to_perturb: The column name on which perturbation is to be performed.
        :from_group: The group name (string) on which the perturbation is to be performed.
        :to_groups: The list of group names (string) to which the perturbation is to be performed.
        :from_group_count: The number of rows belonging to `from_group`.
        :spark: The SparkSession object.
        :from_group_count: [Optional] The number of rows belonging to `from_group`. [Optimises perturbation.]
        :correlation_info: [Optional] The correlation information of the protected attribute to be used for perturbation of correlated attributes.
        
        :returns: A data-frame containing the perturbed records of all `to_groups` and the count of perturbed rows generated for each `to_group`.
            Example,
                If to_groups = ["female", "others"] then,
                pert_to_groups_count = {
                    "female": 220,
                    "others": 80
                }
        """
        perturbed_df = pert_to_groups_count = None
        start_time = DateUtil.current_milli_time()

        # Initialising the perturbed data-frame
        perturbed_df = spark.createDataFrame([], data.schema)

        # Taking the rows that belong to the `from_group`
        from_group_query = SQLUtils.get_cat_filter_query(
            col_name=column_to_perturb,
            operator="==",
            values=[from_group]
        )
        print("Query filter used for the from group {} is: {}".format(from_group, from_group_query))
        from_group_df = data.where(from_group_query)

        # If from_group_count is not specified, get it from the from_group_df
        if from_group_count is None:
            from_group_count = from_group_df.count()
        
        # If there are no rows in data belonging to the specified group, not performing perturbation for the group.
        if from_group_count == 0:
            logger.warning("There are no rows in the sample data which belong to the group {}, hence not performing perturbation.".format(from_group))
            # Setting pert_to_groups_count to 0 as no perturbed rows generated
            pert_to_groups_count = {x: 0 for x in to_groups}
        else:
            # Performing perturbation (transformations) for each `to_group`
            perturbed_df = from_group_df.withColumn(column_to_perturb, explode(array([lit(to_group) for to_group in to_groups])))

            # Calculating the number of perturbed rows generated
            pert_to_groups_count = {x: from_group_count for x in to_groups}

            # Perturbing correlated attributes if protected attribute is being perturbed
            if correlation_info is not None and correlation_info.get("correlated_maj_min"):
                perturbed_df = cls._correlated_attr_perturbation(perturbed_df, column_to_perturb, to_groups, spark, correlation_info, pert_to_groups_count)
        
        end_time = DateUtil.current_milli_time()
        print("Time taken for categorical perturbation of {} column was {} milliseconds.".format(column_to_perturb, end_time - start_time))

        return perturbed_df, pert_to_groups_count
    
    @classmethod
    def _numerical_perturbation(cls, data, column_to_perturb: str, from_group: list, to_groups: list, numerical_perturb_count_per_row: int, float_decimal_place_precision: int, numerical_perturb_seed: int, spark, from_group_count: int=None, correlation_info: dict=None): # NOSONAR
        """
        Performs the categorical perturbation on the given Spark data-frame (transformations) and returns the perturbed data frame.
        :data: The Spark data frame containing the data to be perturbed.
        :column_to_perturb: The column name on which perturbation is to be performed.
        :from_group: The group range on which the perturbation is to be performed.
        :to_groups: The list of group ranges to which the perturbation is to be performed.
        :numerical_perturb_count_per_row: The number of perturbed rows to be generated per row for numerical perturbation.
        :float_decimal_place_precision: The decimal place precision to be used for numerical perturbation when data is float.
        :numerical_perturb_seed: The seed to be used for numerical perturbation while picking up random values.
        :spark: The SparkSession object.
        :from_group_count: [Optional] The number of rows belonging to `from_group`. [Optimises perturbation.]
        :correlation_info: [Optional] The correlation information of the protected attribute to be used for perturbation of correlated attributes.

        :returns: A data-frame containing the perturbed records of all `to_groups` and the count of perturbed rows generated for each `to_group`.
            Example,
                If to_groups = [
                    [18, 25],
                    [70, 90]
                ] then,
                pert_to_groups_count = {
                    "[18, 25]": 120,
                    "[70, 90]": 80
                }
        """
        perturbed_df = pert_to_groups_count = None
        start_time = DateUtil.current_milli_time()

        # Checking if the column is integer type or not
        is_int = isinstance(data.schema[column_to_perturb].dataType, IntegerType) or isinstance(data.schema[column_to_perturb].dataType, LongType)

        if from_group_count is None:
            # Taking the rows that belong to the `from_group`
            from_group_query = SQLUtils.get_num_filter_query(
                col_name=column_to_perturb,
                ranges=[from_group],
                include=True
            )
            print("Query filter used for the from group {} is: {}".format(from_group, from_group_query))
            from_group_df = data.where(from_group_query)
            from_group_count = from_group_df.count()

        # If there are no rows in data belonging to the specified group, not performing perturbation for the group.
        if from_group_count == 0:
            logger.warning("There are no rows in the sample data which belong to the group {}, hence not performing perturbation.".format(from_group))
            perturbed_df = spark.createDataFrame([], data.schema)
            # Setting pert_to_groups_count to 0 as no perturbed rows generated
            pert_to_groups_count = {str(x): 0 for x in to_groups}
        else:
            # Calculating the total number of perturbations per row
            total_num_perturbations_per_row = len(to_groups) * numerical_perturb_count_per_row

            # Calculating the total number of perturbations to be generated
            pert_to_groups_count = {str(x): numerical_perturb_count_per_row * from_group_count for x in to_groups}

            # Creating the duplicate rows to be perturbed
            n_to_array = udf(lambda n : [n] * total_num_perturbations_per_row, ArrayType(IntegerType() if is_int else FloatType()))
            if "." in column_to_perturb:
                column_to_perturb = "`{}`".format(column_to_perturb)
            perturbed_df = data.withColumn(column_to_perturb if "." not in column_to_perturb else column_to_perturb[1:-1], n_to_array(data[column_to_perturb]))
            perturbed_df = perturbed_df.withColumn(column_to_perturb if "." not in column_to_perturb else column_to_perturb[1:-1], explode(perturbed_df[column_to_perturb]))
            if "." in column_to_perturb:
                column_to_perturb = column_to_perturb[1:-1]

            # Generating the perturbed values
            perturbed_values = []
            # Setting the random seed. We cannot remove the use of seed here since it is user input.
            random.seed(numerical_perturb_seed) # NOSONAR
            for _1 in range(from_group_count):
                # For each row in `from_group` generating the perturbed value using random values from `to_group`
                for to_group in to_groups:
                    for _2 in range(numerical_perturb_count_per_row):
                        if is_int:
                            perturbed_value = random.randint(to_group[0], to_group[1]) # NOSONAR
                        else:
                            perturbed_value = random.uniform(to_group[0], to_group[1]) # NOSONAR
                            if float_decimal_place_precision is not None:
                                perturbed_value = perturbed_value.__round__(float_decimal_place_precision)
                        
                        perturbed_values.append(perturbed_value)

            # Adding the perturbed values generated to the perturbed data frame
            # Convert list to a dataframe
            pert = "{}_pert"
            pert_col_name = pert.format(column_to_perturb)
            pert_val_df = spark.createDataFrame([(l,) for l in perturbed_values], [pert_col_name])

            # Add 'sequential' index and join both dataframe to get the final result
            perturbed_df = perturbed_df.withColumn("row_idx", row_number().over(Window.partitionBy(lit(0)).orderBy(monotonically_increasing_id())))
            pert_val_df = pert_val_df.withColumn("row_idx", row_number().over(Window.partitionBy(lit(0)).orderBy(monotonically_increasing_id())))

            # Joining the perturbed value data from with perturbed data frame and replacing the column to be perturbed
            perturbed_df = perturbed_df.join(pert_val_df, perturbed_df["row_idx"] == pert_val_df["row_idx"]).drop("row_idx").drop(column_to_perturb).withColumnRenamed(pert_col_name, column_to_perturb)

            # Perturbing correlated attributes if protected attribute is being perturbed
            if correlation_info is not None and correlation_info.get("correlated_maj_min"):
                perturbed_df = cls._correlated_attr_perturbation(perturbed_df, column_to_perturb, to_groups, spark, correlation_info, pert_to_groups_count)

        end_time = DateUtil.current_milli_time()
        print("Time taken for numerical perturbation of {} column was {} milliseconds.".format(column_to_perturb, end_time - start_time))

        return perturbed_df, pert_to_groups_count

    @classmethod
    def _correlated_attr_perturbation(cls, data, protected_attribute: str, to_groups: list, spark, correlation_info: dict, pert_to_groups_count: dict, float_decimal_place_precision: int=None): # NOSONAR
        """
        Perturbs correlated attributes of a protected attribute using correlation map.
        - for each correlated attribute, fetch relative weights from correlation map and generate perturbated values
        by generating weighted random values using the relative weights.
        - Update these values in the perturbed dataframe.
        Arguments:
            :data: The dataframe containing perturbed protected attribute values.
            :protected_attribute: The name of the protected attribute.
            :to_groups: The list of groups to which the protected attribute is perturbed.
            :spark: The sparkSession object.
            :correlation_info: The correlation information of the protected attribute to be used for perturbation of correlated attributes
            :pert_to_groups_count: The count of perturbed rows generated for each `to_group`
        Returns:
            :Dataframe where all correlated attributes of given protected attribute are perturbed.
        """
        logger.info("Performing perturbation of correlated attributes for the protected attribute {}".format(protected_attribute))
        start_time = DateUtil.current_milli_time()

        correlated_attributes = correlation_info.get("correlated_attributes")
        correlated_attr_cols = [correlated_attr.get("feature") for correlated_attr in correlated_attributes]
        correlated_maj_min = correlation_info.get("correlated_maj_min")
        
        # Add row index to the dataframe which is required when updating the perturbed values
        df_schema = StructType(
                        data.schema.fields # original schema
                        + [StructField("row_idx", LongType(),True)] # index column
                    )
        df = spark.createDataFrame(data.rdd.zipWithIndex().map(lambda r:(list(r[0])+[r[1]])), df_schema)

        dtypes_dict = dict(data.dtypes)
        is_categorical_prot_attr = dtypes_dict.get(protected_attribute) in ["string", "boolean"]

        # Perturb dataframe which combines perturbed rows generated for correlated attributes for each to_group value of the protected attribute
        agg_pert_df = None
        # Find the perturbed values for correlated attributes for each to_group value of the protected attribute
        for to_group in to_groups:
            # Fetch correlations for current to_group
            correlations = BatchUtils.get_correlations_for_maj_min_group(correlated_maj_min, to_group)
            if correlations is None or len(correlations) == 0:
                continue
            # Find the subset of rows for each to_group value of the protected attribute
            if is_categorical_prot_attr:
                group_filter_query = SQLUtils.get_cat_filter_query(protected_attribute, "==", [to_group])
            else:
                group_filter_query = SQLUtils.get_num_filter_query(protected_attribute, [to_group])
            selected_cols = [protected_attribute, 'row_idx']
            group_df = df.select(selected_cols).filter(group_filter_query)

            # Get perturbed values for each correlated attribute
            sample_size = pert_to_groups_count.get(str(to_group))
            if sample_size is None:
                sample_size = group_df.count()
            if sample_size == 0:
                continue

            # Add a temporary index column which is needed while updating perturbed values of correlated attributes
            group_df = group_df.withColumn("idx", row_number().over(Window.partitionBy(lit(0)).orderBy(monotonically_increasing_id())))

            # Generate perturbed values for each correlated attribute based on the correlation map for the to_group
            for correlated_attr_details in correlations:
                correlated_attr = correlated_attr_details.get("feature")
                data_type = dtypes_dict.get(correlated_attr)

                # Generate sample_size number of perturbed values
                perturbed_values = cls.get_corr_attr_perturbed_values(correlated_attr_details, sample_size, data_type, float_decimal_place_precision=float_decimal_place_precision)
    
                # Create dataframe with perturbed values for the current correlated attribute
                pert_col_name = "{}_pert".format(correlated_attr)
                corr_attr_pert_df = spark.createDataFrame([(l,) for l in perturbed_values], [pert_col_name])

                # Add 'sequential' index and join the dataframe with group_df
                corr_attr_pert_df = corr_attr_pert_df.withColumn("idx", row_number().over(Window.partitionBy(lit(0)).orderBy(monotonically_increasing_id())))                    
                group_df = group_df.join(corr_attr_pert_df, ["idx"])

            # Drop the temporary index and protected_attribute as original data already has it
            group_df = group_df.drop("idx").drop(protected_attribute)

            # Now the group_df contains peturbed values for all the correlated attributes for current to_group
            # Add the rows to the aggregate perturb dataframe
            if agg_pert_df is None:
                agg_pert_df = group_df
            else:
                agg_pert_df = agg_pert_df.union(group_df)

        # Now constructing the final perturbed dataframe by replacing correlated attribute values from the agg_pert_df
        # This is done by joining input data with agg_pert_df on row_idx column
        final_pert_df = df.join(agg_pert_df, ["row_idx"]).drop("row_idx")

        # Drop the correlated attribute columns and rename perturbed columns to become the correlated attribute columns
        final_pert_df = final_pert_df.drop(*correlated_attr_cols)
        col_name_mapping = {"{}_pert".format(col_name): col_name for col_name in correlated_attr_cols}
        modified_col_names = [col_name_mapping.get(col_name, col_name) for col_name in final_pert_df.columns]
        final_pert_df = final_pert_df.toDF(*modified_col_names)
        
        time_taken = DateUtil.current_milli_time() - start_time
        logger.info("Time taken for perturbation of correlated attributes for the protected attribute {} is {} seconds.".format(protected_attribute, time_taken/1000))
        return final_pert_df

    @classmethod
    def get_corr_attr_perturbed_values(cls, correlated_attr_details: dict, sample_size: int, data_type: str, float_decimal_place_precision: int=None):
        """
        Generates sample_size number of perturbed values for the specified correlated attribute of a protected attribute using correlation map
        Arguments:
            :correlated_attr_details: The correlation details for the majority/minority group of the protected attribute
            :sample_size: The number of perturbed values to be generated
            :data_type: The data type of the correlated attribute column
            :float_decimal_place_precision[Optional]: The decimal place precision to be used for numerical perturbation when data is float.
        Returns:
            : The pertubed values specified correlated attribute based on relative weights. 
        """
        perturbed_values = []
        attr_values = []
        relative_weights = []
        for attr_val_dict in correlated_attr_details.get("values"):
            attr_values.append(attr_val_dict.get("feature_value"))
            relative_weights.append(attr_val_dict.get("relative_weight"))
        if not attr_values or not relative_weights:
            return []
        # Generating weighted random values using relative_weights
        perturbed_values = random.choices(attr_values, weights=relative_weights, k=sample_size) # NOSONAR
        secrets_random_generator = secrets.SystemRandom()        
        # For numerical correlated attribute, select random values from the selected range
        is_categorical = data_type in ["string", "boolean"]        
        if not is_categorical:
            num_perturbed_values = []
            is_int = data_type in ["int", "long"]
            for val in perturbed_values:
                if is_int:
                    perturbed_value = secrets_random_generator.randint(val[0], val[1])
                else:
                    perturbed_value = secrets_random_generator.uniform(val[0], val[1])
                    if float_decimal_place_precision is not None:
                        perturbed_value = perturbed_value.__round__(float_decimal_place_precision)
                num_perturbed_values.append(perturbed_value)
            perturbed_values = num_perturbed_values
        return perturbed_values

