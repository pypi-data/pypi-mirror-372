# Box helper script

"""
This class will provide common functionalities with
the Box API specifically with the JWTAuth method

*** ---------------------- IMPORTANT ---------------------- ***

THIS CLASS REQUIRES THE LOG HELPER SCRIPT TO ALSO BE PRESENT IN YOUR PROJECT WRKDIR.
CHANGE THE IMPORT STATEMENT AS NEEDED TO CORRECTLY IMPORT LOG_HELPER OR REMOVE THE LOGGER
FROM THE CLASS
"""
import ast
import os
import pandas as pd
from boxsdk import Client, JWTAuth
from boxsdk.exception import BoxAPIException

from tetsu.src.log_helper import logger
from tetsu.src import cloudant_helper

logger = logger(name=__name__, handler="console")


class BoxHelper:
    def __init__(
            self,
            creds: dict = None,
            cloudant_doc=None,
            auth_filepath: str = None,
    ):
        """
        Initialization function for the BOXHelper class.
        You can authenticate using Cloudant, a local JSON file, or a creds dictionary. Pick 1 method only.
        :param cloudant_doc (optional): Name of the cloudant document to be retrieved
        :param creds (optional): A credentials dictionary can be optionally used to retrieve the desired DB2 credentials from the
                         cloudant document and override the default values
                         Example:
                        {"client_id": ["box", "client_id"],
                        "client_secret": ["box", "client_secret"],
                        "enterprise_id": ["box" "enterprise_id"],
                        "jwt_key_id": ["box", "db2", "jwt_key_id"],
                        "rsa_private_key_passphrase": ["box", "rsa_private_key_passphrase"],
                        "rsa_private_key_data": ["box", "rsa_private_key_data"]}
        :param auth_filepath (optional): The local path to the JWTAuth JSON file.
        """
        if cloudant_doc is None:
            self.cloudant_doc = ast.literal_eval(os.getenv("cloudant_document"))
        else:
            self.cloudant_doc = cloudant_doc

        if creds is None:
            self.creds = {
                "client_id": ["box", "clientID"],
                "client_secret": ["box", "clientSecret"],
                "enterprise_id": ["box", "enterpriseID"],
                "rsa_private_key_passphrase": ["box", "appAuth", "passphrase"],
                "rsa_private_key_data": ["box", "appAuth", "privateKey"],
                "jwt_key_id": ["box", "appAuth", "publicKeyID"],
            }
        else:
            self.creds = creds

        if auth_filepath is not None:
            try:
                self.client = Client(JWTAuth.from_settings_file(f"{auth_filepath}"))
                logger.info("Box instance has been authorized using a JWTAuth JSON file")
            except Exception as e:
                logger.exception(f"Could not authorize using JWTAuth method due to: {e}")
        else:
            try:
                self.creds = cloudant_helper.get_credentials(
                    doc=self.cloudant_doc, creds=self.creds
                )
                self.client = Client(
                    JWTAuth(
                        client_id=self.creds["client_id"],
                        client_secret=self.creds["client_secret"],
                        enterprise_id=self.creds["enterprise_id"],
                        jwt_key_id=self.creds["jwt_key_id"],
                        rsa_private_key_passphrase=self.creds[
                            "rsa_private_key_passphrase"
                        ],
                        rsa_private_key_data=self.creds["rsa_private_key_data"],
                    )
                )
                logger.info("Box instance has been authorized using Cloudant")
            except Exception as e:
                logger.exception(f"Could not authorize using Cloudant due to: {e}")

    def download_file(self, file_id: str, file_name: str) -> None:
        try:
            with open(file_name, "wb") as open_file:
                self.client.file(file_id).download_to(open_file)
                open_file.close()
        except Exception as e:
            logger.exception(f"Could not download file to local directory due to {e}")
        else:
            logger.info(
                f"{file_name} has successfully been downloaded to the local directory"
            )

    def download_file_as_df(
            self, file_id: str, file_type: str = "xlsx"
    ) -> pd.DataFrame:
        """
        Downloads a specified file from box. Currently, supports .xlsx, .csv, or .pkl
        :param file_id: A string of the ID of the file to be downloaded from box
        :param file_type: A string of the type of file. Currently, supports xlsx, csv, or pkl. Default = xlsx
        :return: The contents of the file
        """
        try:
            content = self.client.file(file_id=file_id).get_download_url()
        except Exception as e:
            logger.exception(f"Could not download file from box due to {e}")
        else:
            logger.info(f"File #{file_id} has been downloaded as a dataframe...")
            if file_type == "xlsx":
                return pd.read_excel(content)
            if file_type == "csv":
                return pd.read_csv(content)
            if file_type == "pkl":
                return pd.read_pickle(content)

    def upload_file(self, path: str, folder_id: str) -> None:
        """
        Uploads a specified file to a specified box folder

        :param path: A string of the local path to the file that will be uploaded
        :param folder_id: A string of the folder ID the file will be uploaded to
        """
        try:
            self.client.folder(folder_id).upload(path)
        except BoxAPIException as be:
            logger.exception(f"Could not upload file due to {be}")
        else:
            logger.info("File uploaded successfully...")

    def update_file(self, path: str, file_id: str) -> None:
        """
        Uploads a specified file to a specified box folder

        :param path: A string of the local path to the file that will be uploaded
        :param file_id: A string of the file ID for the updated file
        """
        try:
            self.client.file(file_id).update_contents(path)
        except BoxAPIException as be:
            logger.exception(f"Could not update file #{file_id} due to {be}")
        else:
            logger.info(f"File #{file_id} updated successfully...")

    def upload_df(
            self, data: pd.DataFrame, path: str, folder_id: str, file_type: str = "xlsx"
    ):
        """
        Uploads a specified pandas dataframe to a specified box folder

        :param data: The dataframe that will be uploaded
        :param path: A string with the path to the location where
                     the file should be saved *** MUST ALSO INCLUDE FILE NAME ***
        :param folder_id: A string with the folder ID for the specified box folder
        :param file_type: A string of the type of file the df should end up in.
                          Currently, supports xlsx, csv, or pkl. Default = xlsx
        """
        try:
            if file_type == "xlsx":
                data.to_excel(path)
            if file_type == "csv":
                data.to_csv(path)
            if file_type == "pkl":
                data.to_pickle(path)
        except BoxAPIException as be:
            logger.exception(
                f"Could not save data locally to initiate upload process due to {be}"
            )
        else:
            self.upload_file(path=path, folder_id=folder_id)
