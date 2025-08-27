# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2021
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

import json

from ibm_wos_utils.explainability.utils.number_util import NumberUtil
from pyparsing import Word, Combine, Optional, nums, ParseException, SkipTo


class Object:
    pass


class RelationalExpr:
    LT = "<"
    LTE = "<="
    GT = ">"
    GTE = ">="

    def __init__(self, parse_result):
        self.left_operand = parse_result.get("left_operand")
        self.left_operator = parse_result.get("left_operator")
        self.feature_name = parse_result.get("feature_name").strip()
        self.right_operator = parse_result.get("right_operator")
        self.right_operand = parse_result.get("right_operand")

    def translate(self):
        feature_range = Object()

        if self.left_operator is not None and self.left_operator not in (self.LT, self.LTE):
            raise Exception(
                "An invalid operator was found in the feature importance expression for {0}".format(str(self.left_operator)))

        if self.right_operator not in (self.LT, self.LTE, self.GT, self.GTE):
            raise Exception(
                "An invalid operator was found in the feature importance expression for {0}".format(str(self.right_operator)))

        if self.left_operator in (self.LT, self.LTE):
            feature_range.min = self.left_operand
            feature_range.min_inclusive = (self.left_operator == self.LTE)

        if self.right_operator in (self.GT, self.GTE):
            feature_range.min = self.right_operand
            feature_range.min_inclusive = (self.right_operator == self.GTE)

        if self.left_operator in (self.GT, self.GTE):
            feature_range.max = self.left_operand
            feature_range.max_inclusive = (self.left_operator == self.GTE)

        if self.right_operator in (self.LT, self.LTE):
            feature_range.max = self.right_operand
            feature_range.max_inclusive = (self.right_operator == self.LTE)

        return self.feature_name, feature_range

    def __str__(self):
        return str({"left_operand": self.left_operand,
                    "left_operator": self.left_operator,
                    "feature_name": self.feature_name,
                    "right_operand": self.right_operand,
                    "right_operator": self.right_operator, })


class FeatureObjectParserUtil:

    @classmethod
    def get_feature_object(cls, weighted_feature: list, is_categorical: bool, discretize_continuous: bool):

        feature = Object()
        feature.weight = weighted_feature[1]

        if is_categorical:
            weighted_feature_split = str(weighted_feature[0]).split("=")
            feature.feature_name = weighted_feature_split[0].strip()
            feature.feature_value = weighted_feature_split[1]
            return feature

        # If discretize is false, weighted_feature[0] will have just the feature name.
        if not discretize_continuous:
            feature.feature_name = weighted_feature[0].strip()
            return feature
        # weighted_feature[0] would be of the following form
        # for categorical : [feature_name]=[value]
        # for numerical : [numeric_value][operator][feature_name][operator][numeric_value]
        relational_expr = cls.parse_feature_expr(weighted_feature[0])
        feature.feature_name, feature.feature_range = relational_expr.translate()

        return feature

    @classmethod
    def parse_feature_expr(cls, value: str):
        """
        Parse expressions of the form [numeric_value][operator][feature_name][operator][numeric_value] and [feature_name][operator][numeric_value] and create RelationalExpr object
        """
        number = Combine(Word(nums+"+-") + Optional("." + Word(nums+"eE+-")))
        operator = Word("<>=")
        expr1 = Optional(number.setResultsName("left_operand")
                         + operator.setResultsName("left_operator")) \
            + SkipTo(operator).setResultsName("feature_name") \
            + operator.setResultsName("right_operator") \
            + number.setResultsName("right_operand")
        expr2 = SkipTo(operator).setResultsName("feature_name") \
            + operator.setResultsName("right_operator") \
            + number.setResultsName("right_operand")

        try:
            return RelationalExpr(expr1.parseString(value))
        except ParseException as e:
            try:
                return RelationalExpr(expr2.parseString(value))
            except ParseException as e:
                raise Exception(
                    "An error occurred while computing feature importance for {0}".format(value))
