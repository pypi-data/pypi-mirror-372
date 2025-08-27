"""
This module is responsible for loading environment variables from the environment file.
"""
from dotenv import load_dotenv
from pathlib import Path
import os

load_dotenv()

def _check_all_environment_variables_are_set():
    environment_variables = ["ODS_API_KEY",
                             "ODS_DOMAIN",
                             "ODS_API_TYPE"]

    for environment_variable in environment_variables:
        ev = os.getenv(environment_variable)
        if not ev:
            raise ValueError(f"{environment_variable} not found in the .env file. "
                             f"Please define it as '{environment_variable}'.")
        if ev == "your_" + environment_variable.lower():
            raise ValueError(f"Please define the environment variable '{environment_variable}' in the .env file.")


def get_base_url() -> str:
    return _get_ods_url()

def _get_ods_url() -> str:
    """
    Constructs the ODS (Open Data Service) API URL based on environment variables.

    Returns:
        str: The constructed ODS API URL **without** trailing slash ('/'): https://<ODS_DOMAIN>/api/<ODS_API_TYPE>
    """
    _ods_domain = os.getenv('ODS_DOMAIN')
    _ods_api_type = os.getenv('ODS_API_TYPE')
    _url_no_prefix = f"{_ods_domain}/api/{_ods_api_type}".replace("//", "/")
    _url = "https://" + _url_no_prefix
    return _url

def _get_headers():
    _api_key = os.getenv('ODS_API_KEY')
    _headers = {'Authorization': f'apikey {_api_key}'}
    return _headers
