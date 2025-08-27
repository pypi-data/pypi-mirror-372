# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2021
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------
import numpy as np


class NumberUtil:

    @classmethod
    def is_number(cls, s):
        try:
            float(s)
            return True
        except ValueError:
            pass

        try:
            import unicodedata
            unicodedata.numeric(s)
            return True
        except (TypeError, ValueError):
            pass
        return False

    @classmethod
    def normalize_feature_weights(cls, weighted_features: list):
        feature_list = []
        weight_list = []

        for weighted_feature in weighted_features:
            feature_list.append(weighted_feature[0])
            weight_list.append(weighted_feature[1])

        normalizer = 1 / np.sum(np.absolute(weight_list))
        normalized_weight_list = []
        for weight in weight_list:
            normalized_weight_list.append(weight*normalizer)

        normalized_feature_weight_list = []
        for i in range(len(feature_list)):
            normalized_feature_weight_list.append(
                (feature_list[i], normalized_weight_list[i]))

        return normalized_feature_weight_list
