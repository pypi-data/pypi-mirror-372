# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# © Copyright IBM Corp. 2022  All Rights Reserved.
# US Government Users Restricted Rights -Use, duplication or disclosure restricted by 
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------
import pandas as pd
from functools import reduce


def convert_df_to_list(df:pd.DataFrame,features:list):
    """
        Method to convert pandas df to 2d array
    """
    if len(features) > 0:
        return df[features].values.tolist()
    else:
        return df.values.tolist()


def get(dictionary, keys:str,default=None):
    return reduce(lambda d, key: d.get(key, default) if isinstance(d, dict) else default, keys.split("."), dictionary)
    

def check_for_missing_features(df:pd.DataFrame,features:list):
    columns = list(df.columns)
    diff_cols = list(set(features)-set(columns))
    if len(diff_cols) > 0:
        raise Exception(f"Missing feature columns:{diff_cols} in input df")