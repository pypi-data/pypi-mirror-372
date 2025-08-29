from typing import Dict

import requests

from platform_sdk.clients.identity_client import IdentityServerClient
from platform_sdk.helpers.exception_logger import raise_for_status_with_dependency_name
from platform_sdk.shared.constants import STRONGMIND_CENTRAL


class CentralClient:
    def __init__(self, base_url: str, identity_server_client: IdentityServerClient):
        self.base_url = base_url
        self.identity_client = identity_server_client

    @property
    def headers(self):
        return {
            'Authorization': self.identity_client.get_token()
        }

    def _post_data(self, data: Dict, data_type: str):
        url = f"{self.base_url}/{data_type}"
        response = requests.post(url, headers=self.headers, json=data)
        raise_for_status_with_dependency_name(response, STRONGMIND_CENTRAL)

    def post_guardians(self, user_uid: str, guardians: list):
        """Send the guardians data for the user by
        sending a POST to the Central API"""
        self._post_data(self.build_guardian_payload(guardians), f"api/users/{user_uid}/guardians")

    def build_guardian_payload(self, guardians: list):
        return {
            "guardians": [
                {
                    "uid": guardian["uid"],
                    "relationship": guardian["relationship"],
                    "primary": guardian["primary"]
                }
                for guardian in guardians
            ]
        }

