# TM1 Helper

import os
import ast
import math
import TM1py
import numpy as np
import pandas as pd

from collections import Counter

from tetsu.src import cloudant_helper
from tetsu.src import log_helper

logger = log_helper.logger(name=__name__, handler="console")


def tm1_pull(
    cube: str,
    environment: str,
    mdx_query: str,
    skip_zeros: bool = False,
    include_attributes: bool = False,
    creds: dict = None,
    cloudant_doc: dict = None,
) -> pd.DataFrame:
    """
    Load in a local SQL file for easy data pulls

    :param cube: The cube to access
    :param environment: The environment (production, staging)
    :param mdx_query: location of mdx txt file
    :param skip_zeros: True/False to suppress zeros in data pull. True = suppress zeros. False = keep zeros
    :param include_attributes: True/False to include member attribute columns in returned dataframe or not
    :param creds: Credentials dictionary for retrieval
    :param cloudant_doc: Cloudant document for credentials retrieval

    :return: A pandas dataframe with the retrieved data
    """
    if cloudant_doc is None:
        cloudant_doc = ast.literal_eval(os.getenv("cloudant_document"))
    if creds is None:
        creds = {
            "hostname": ["cubes", cube, environment, "hostname"],
            "port": ["cubes", cube, environment, "port"],
            "username": ["w3", "username"],
            "password": ["w3", "password"]
        }

    creds = cloudant_helper.get_credentials(doc=cloudant_doc, creds=creds)
    tm1_object = TM1py.TM1Service(address=creds["hostname"],
                                  port=creds["port"],
                                  user=creds["username"],
                                  password=creds["password"],
                                  ssl='true',
                                  namespace='IBMIntranet')
    try:
        cellset_id = tm1_object.cubes.cells.create_cellset(mdx_query)
        extract_df = tm1_object.cubes.cells.extract_cellset_dataframe(
            cellset_id, skip_zeros=skip_zeros, include_attributes=include_attributes
        )
        extract_df["Value"] = extract_df["Value"].fillna(0)
    except Exception as error:
        raise Exception("TM1pyError" + repr(error))
    return extract_df


def tm1_push(
    cube: str, environment: str, df: pd.DataFrame, creds=None, cloudant_doc=None
) -> None:
    """
    Push data to the cube

    :param cube: The cube to access
    :param environment: The environment (production, staging)
    :param df: The dataframe to be pushed to the cube
    :param creds: Credentials dictionary for retrieval
    :param cloudant_doc: Cloudant document for credentials retrieval
    """
    if cloudant_doc is None:
        cloudant_doc = ast.literal_eval(os.getenv("cloudant_document"))
    if creds is None:
        creds = {
            "hostname": ["cubes", cube, environment, "hostname"],
            "port": ["cubes", cube, environment, "port"],
            "username": ["w3", "username"],
            "password": ["w3", "password"]
        }

    creds = cloudant_helper.get_credentials(doc=cloudant_doc, creds=creds)
    tm1_object = TM1py.TM1Service(address=creds["hostname"],
                                  port=creds["port"],
                                  user=creds["username"],
                                  password=creds["password"],
                                  ssl='true',
                                  namespace='IBMIntranet')
    # check if table exists in the cube
    if not tm1_object.cubes.exists(cube):
        raise Exception(f"{cube} does not exist")
    correct_names = tm1_object.cubes.get_dimension_names(cube)

    # check if dataframe has a column labeled value
    if "value" not in df.columns:
        raise Exception("Dataframe needs a column called 'value'")
    upload_value_name = "value"

    # TM1py soft rule to keep uploads under 1000 records; break into smaller dataframes
    breakout = math.ceil((df.count()[1] / 1000))
    model_df_list = np.array_split(df, breakout)

    for dataframe in model_df_list:
        upload_dimensions = dataframe.drop([upload_value_name], axis="columns")
        upload_values = dataframe[[upload_value_name]]

        upload_dimensions_list = [tuple(x) for x in upload_dimensions.values]
        upload_values_list = list(upload_values[upload_value_name])
        dictionary = dict(zip(upload_dimensions_list, upload_values_list))

        dimension_names = upload_dimensions.columns.tolist()
        # check if there are too many/too few dimensions
        if len(correct_names) != len(dimension_names):
            raise Exception(
                f"{set(dimension_names) - set(correct_names)} is not a valid dimension in {cube}"
            )

        # check if the names of the dimensions are correct/incorrect
        if not (Counter(correct_names) == Counter(dimension_names)):
            raise KeyError(
                f"The missing {cube} dimensions are {set(correct_names) - set(dimension_names)}. "
                f"The additional dimensions from model_df are {set(dimension_names) - set(correct_names)}"
            )

        try:
            tm1_object.cells.write_values(cube, dictionary, dimension_names)
        except Exception as error:
            raise Exception("TM1pyError" + repr(error))
