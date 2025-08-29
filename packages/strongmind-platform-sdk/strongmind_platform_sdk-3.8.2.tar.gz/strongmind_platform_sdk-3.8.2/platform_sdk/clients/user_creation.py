import json

import requests
from pydantic.json import pydantic_encoder

from platform_sdk.clients.identity_client import IdentityServerClient
from platform_sdk.helpers.exception_logger import raise_for_status_with_dependency_name
from platform_sdk.models.user import User
from platform_sdk.shared.constants import USER_CREATION


class UserCreationClient:
    def __init__(self,
                 user_creation_service_url: str,
                 identity_client: IdentityServerClient):
        self.url = user_creation_service_url
        self.token = identity_client.get_token()

    def _headers(self):
        return {
            'Authorization': f"Bearer {self.token}",
            'Content-Type': "application/json"
        }

    def create_user(self, user: User):
        headers = self._headers()
        payload = json.dumps(user.dict(by_alias=True), default=pydantic_encoder)
        response = requests.post(self.url, headers=headers, data=payload)
        raise_for_status_with_dependency_name(response, USER_CREATION)
        return response
