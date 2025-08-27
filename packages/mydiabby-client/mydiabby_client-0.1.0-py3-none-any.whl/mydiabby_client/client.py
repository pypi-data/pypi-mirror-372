"""
Created on Tues August 26 15:49:43 2025
@author: nfontaine
"""

import requests
import logging
from .exceptions import AuthenticationError, APIError
from json.decoder import JSONDecodeError
from typing import Any, Union

logger = logging.getLogger(__name__)

#---------------------------------------------------------------------------
#       Class that fetches data from the MyDiabby API
#---------------------------------------------------------------------------

class MyDiabbyClient:

    def __init__(self,
                 username: str,
                 password: str,
                 base_url: str ="https://app.mydiabby.com/api"
                 ) -> None:
        
        self.username = username
        self.password = password
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json, text/plain, */*"
        })
        self.token = None

        self._authenticate()


    def _authenticate(self) -> None:
        """
        Authenticates with MyDiabby and stores the Bearer token."""
        
        url = f"{self.base_url}/getToken"
        payload = {"username": self.username,
                   "password": self.password,
                   "platform": "dt"}

        resp = self.session.post(url, json=payload)
        if resp.status_code != 200:
            raise AuthenticationError(f"Failed to authenticate: {resp.text}")

        try:
            data = resp.json()
        except (ValueError, JSONDecodeError):
            raise AuthenticationError("Invalid JSON response")

        self.token = data.get("token")
        if not self.token:
            raise AuthenticationError("No token in response")

        self.session.headers.update({"Authorization": f"Bearer {self.token}"})


    def _request(self,
                 method: str,
                 endpoint: str, **kwargs) -> Any:
        """
        Helper function that makes the necessary requests.
        If a 401 error code occurs, it will re-authenticate and retry once.
        """
        url = f"{self.base_url}{endpoint}"
        resp = self.session.request(method, url, **kwargs)

        if resp.status_code == 401:
            # re-authenticate and retry once
            self._authenticate()
            resp = self.session.request(method, url, **kwargs)

        if not resp.ok:
            try:
                err = resp.json()
            except Exception:
                err = resp.text
            raise APIError(f"API error {resp.status_code}: {err}")

        try:
            response = resp.json()
        except (ValueError, JSONDecodeError):
            raise APIError("Invalid JSON response")

        return response


    def get_account(self) -> dict:
        """
        Fetch info about the user, as a json.
        """
        return self._request("GET", "/account")


    def get_data(self) -> Union[dict, list]:
        """
        Fetch all CGM and pump data, as a json.
        """
        return self._request("GET", "/data")
