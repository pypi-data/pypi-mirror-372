from __future__ import annotations

import ast
import datetime as dt
import json
import os

import importlib_resources
import pandas as pd
import requests

from tetsu.src import cloudant_helper


def workday_extraction(input_date: dt.datetime | str,
                       cloudant_doc: dict = None) -> str:
    """Extracts the workday from the epm workday calendar.
    Example:
        today = dt.datetime.now()
        wd = workday_extraction(today)

    :param input_date (str or timestamp): Expects a date as string or timestamp.
                                          When using a string, format like '03/01/25'
    :param cloudant_doc: Cloudant document for credentials retrieval
    :returns: workday
    """

    if cloudant_doc is None:
        cloudant_doc = ast.literal_eval(os.getenv("cloudant_document"))

    # ---- Extract JSON ----------------------------------------------------------------------------#
    creds = cloudant_helper.get_credentials(doc=cloudant_doc, creds={"api_key": ["workday_calendar_api_key"]})

    # Extract date
    if isinstance(input_date, str):
        input_date = dt.datetime.strptime(input_date, '%m/%d/%Y')
    input_year = input_date.year
    input_month = str(input_date.month).zfill(2)
    input_day = str(input_date.day).zfill(2)
    custom_dates_url = 'https://production.epm-web-platform.dal.app.cirrus.ibm.com/api/calendar/queryCustomDatesByDate?date='  # noqa: E501
    resources = importlib_resources.files("tetsu")

    try:
        raw_json = requests.get(
            custom_dates_url + f"{input_year}%2F{input_month}%2F{input_day}&key=" + creds["api_key"],
            timeout=600,
            verify=resources.joinpath("config", "root.pem"))
        if 'No custom date groups were found' in raw_json.content.decode("utf-8"):
            print(f"{input_date} is not a workday. Setting workday to NW.")
            return 'NW'
        raw_json.raise_for_status()

        # ---- Convert JSON to Dataframe ---------------------------------------------------------------#
        data = json.loads(raw_json.content)
        df = pd.DataFrame(data)
        # Convert String to Timestamp and Normalize time component
        workday = df['customDateName'].iloc[0]

        return workday

    except requests.exceptions.HTTPError as e:
        print(e)
