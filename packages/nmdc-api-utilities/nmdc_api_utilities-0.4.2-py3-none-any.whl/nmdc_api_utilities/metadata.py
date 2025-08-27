# -*- coding: utf-8 -*-
from nmdc_api_utilities.nmdc_search import NMDCSearch
import requests
import logging
import json
from nmdc_api_utilities.auth import NMDCAuth
from nmdc_api_utilities.decorators import requires_auth

logger = logging.getLogger(__name__)


class Metadata(NMDCSearch):
    """
    Class to interact with the NMDC API metadata endpoints. These deal mostly with metadata management, including validation and submission.

    Parameters
    ----------
    auth : NMDCAuth
        An instance of the NMDCAuth class for authentication.
    """

    def __init__(self, env="prod", auth: NMDCAuth = None):
        self.env = env
        self.auth = auth or NMDCAuth()
        super().__init__(env=env)

    def validate_json(self, json_records: list[dict] | str) -> int:
        """
        Validates a json file using the NMDC json validate endpoint.

        If the validation passes, the method returns without any side effects.

        Parameters
        ----------
        json_records : list[dict] | str
            The json records to be validated. Can be passed in as a file path or list of dictionaries.

        Returns
        -------
        int
            The HTTP status code of the validation request.

        Raises
        ------
        Exception
            If the validation fails.
        """
        if isinstance(json_records, str):
            with open(json_records, "r") as f:
                data = json.load(f)
        else:
            data = json_records

        # Check that the term "placeholder" is not present anywhere in the json
        if "placeholder" in json.dumps(data):
            raise Exception("Placeholder values found in json!")

        url = f"{self.base_url}/metadata/json:validate"
        headers = {"accept": "application/json", "Content-Type": "application/json"}
        response = requests.post(url, headers=headers, json=data)
        if response.text != '{"result":"All Okay!"}' or response.status_code != 200:
            logging.error(f"Validation failed.")
            raise Exception(
                f"Validation failed with the following information:\n"
                f"Status Code: {response.status_code}\n"
                f"Response: {response.text}"
            )
        else:
            logging.info("Validation passed!")

        return response.status_code

    @requires_auth
    def submit_json(self, json_records: list[dict] | str) -> int:
        """
        Submits a json file to the NMDC API metadata.

        Parameters
        ----------
        json_records : list[dict] | str
            The json records to be submitted. Can be passed in as a file path or list of dictionaries.

        Returns
        -------
        int
            The HTTP status code of the submission request.

        Raises
        ------
        Exception
            If the submission fails.

        """
        # if a file is passed in, load the json
        if isinstance(json_records, str):
            with open(json_records, "r") as f:
                json_records = json.load(f)

        token = self.auth.get_token()

        # api request
        url = f"{self.base_url}/metadata/json:submit"
        headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }
        response = requests.post(url, headers=headers, json=json_records)

        # error handling
        if response.status_code != 200:
            logging.error(f"Request failed with response {response.text}")
            raise Exception(
                "Submission failed with the following information:\n"
                f"Status Code: {response.status_code}\n"
                f"Response: {response.text}"
            )
        else:
            logging.info("Submission passed!")

        return response.status_code
