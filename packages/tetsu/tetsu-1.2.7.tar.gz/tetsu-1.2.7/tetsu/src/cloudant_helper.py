"""
Facilitate communication with Cloudant
"""

import os
import json

from sys import platform
from base64 import b64decode, b64encode

from cloudant.client import Cloudant
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA
from cryptography.hazmat.backends import default_backend

from tetsu.src.log_helper import logger

logger = logger(name=__name__, handler="console")


def get_document(
    document_id: str,
    cloudant_api_key: str = os.getenv("CLOUDANT_IAM_API_KEY"),
    account: str = "848f0f0a-7ff0-4280-9a93-994725506313-bluemix",
    database: str = "epm-finance-dst",
    save_env: bool = True,
) -> dict:
    """
    Connects to cloudant and gets requested document.

    :param cloudant_api_key: Cloudant API key
    :param document_id: name of document in your cloudant database environment variables
    :param account: name of account you want to log in to
    :param database: name of database under the account you want to log in to
    :param save_env: If the cloudant document should be saved as an environment variable
    :return: cloudant document as json-like nested dictionary
    """
    try:
        client = Cloudant.iam(
            account_name=account, api_key=cloudant_api_key, connect=True
        )
        db = client[database]
        doc = json.loads(db[document_id].json())
        client.disconnect()
        logger.info(f"Successfully downloaded Cloudant document: {document_id}")
    except Exception as e:
        logger.exception(
            f"Could not download Cloudant document {document_id} due to: {e}"
        )
        raise e
    if save_env:
        os.environ["cloudant_doc"] = str(doc)
    return doc


def get_credentials(doc: dict, creds: dict) -> dict:
    """
    Get credentials from cloudant, if password, decrypt if necessary.
        example:
            doc = get_document(document_id="DOC_NAME",
                               cloudant_api_key=os.getenv('CLOUDANT_API_KEY'))

            params = {"bot_auth_token": ['slack-bots', "staging", "pricing-bot", 'bot_auth_token'],
                      "slack_app_token": ['slack-bots', "staging", "pricing-bot", 'slack_app_token']}

            slack_creds = get_credentials(doc=doc,
                                          creds=params)

        :param doc: The document object returned from the get_document function
        :param creds: A credentials dictionary with the name of the secret as the key and the path as the value in a list

        :return: creds_dict: A dictionary with the retrieved secret values
    """
    try:
        creds_dict = {}
        for key in creds:
            creds_dict[key] = get_field_value(doc, creds[key])
    except Exception as e:
        logger.exception(f"Could not retrieve credentials due to {e}")
        raise e
    else:
        logger.info("Credentials have been retrieved")
    return creds_dict


def get_field_value(dct: dict, keys: list):
    """
    Get password from cloudant, decrypt if necessary.
    example:
    some_dict = {
        "jdbc":{
            "staging":{
                "username":"epmtaxon",
                "password":{
                    "varname":"CLOUDANT_DECRYPTION_KEY",
                    "value":"some_password"}}}}
    > get_field_value(some_dict, 'jdbc', 'staging', 'username')
    'finds1'
    :param dct: dictionary containing the field value you want to find
    :param keys: the keys needed to traverse down the nested dict
    :return: value you wanted to find
    """
    field = safe_get(dct, keys)

    if isinstance(field, dict) and field["encrypted"] is not None:
        return decrypt_pw(field["value"])
    else:
        return field


def safe_get(dct: dict, keys: list):
    """
    Allows you to easily and safely get nested dictionary values
    EXAMPLE
    some_dict = {
    "jdbc":{
       "staging":{
          "username":"epmtaxon",
          "password":{
             "varname":"CLOUDANT_DECRYPTION_KEY",
             "value":"some_password"}}}}
    > safe_get(some_dict, 'jdbc', 'staging', 'username')
    'epmtaxon'
    > safe_get(some_dict, 'jdbc', 'staging', 'password')
    {'varname': 'CLOUDANT_DECRYPTION_KEY',
     'value': 'some_password'}
    :param dct: dictionary like data structure
    :param keys: comma separated fields
    :return:  value
    """
    for key in keys:
        try:
            dct = dct[key]
        except KeyError:
            return None
    return dct


def decrypt_pw(encrypted_val: str) -> str:
    """
    Decrypts a password using cloudant decryption key.
    :param encrypted_val: encrypted string
    :return: decrypted string
    """
    if platform == "win32" or platform == "darwin":
        rsa_key = RSA.importKey(open(os.path.join(r"config", r"id_rsa")).read())
    else:
        rsa_key = RSA.importKey(
            os.getenv("DST_CLOUDANT_DECRYPTION_KEY").replace(r"\n", "\n")
        )
    cipher = PKCS1_v1_5.new(rsa_key)
    raw_cipher_data = b64decode(encrypted_val)
    decrypt = cipher.decrypt(raw_cipher_data, default_backend())
    return decrypt.decode("utf-8")


def encrypt_pw(val: str) -> str:
    """
    Encrypts a password using cloudant public key.
    :param val: string
    :return: encrypted string
    """
    rsa_key = RSA.importKey(open(os.path.join(r"config", r"id_rsa.pub")).read())
    # rsa_key = RSA.importKey(os.getenv(PUBLIC).replace(r'\n', '\n'))
    cipher = PKCS1_v1_5.new(rsa_key)
    cipher_text = cipher.encrypt(val.encode())
    return b64encode(cipher_text).decode("utf-8")
