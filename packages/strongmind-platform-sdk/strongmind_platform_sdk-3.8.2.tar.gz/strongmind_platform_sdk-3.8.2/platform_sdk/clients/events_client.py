import json

import requests
from pydantic.json import pydantic_encoder

from platform_sdk.clients.identity_client import IdentityServerClient
from platform_sdk.helpers.exception_logger import raise_for_status_with_dependency_name
from platform_sdk.models.cloud_event import CloudEvent
from platform_sdk.shared.constants import EVENTS_API


class EventPlatformClient:
    def __init__(self, url, identity_client: IdentityServerClient):
        self.url = url
        self.identity_client = identity_client

    def send_event(self, event: CloudEvent):
        return self._send_message(json.dumps(event, default=pydantic_encoder))

    def _send_message(self, message: str):
        headers = {
            'Authorization': f"Bearer {self.identity_client.get_token()}",
            'Content-Type': "application/cloudevents+json; charset=utf-8"
        }
        response = requests.post(self.url, headers=headers, data=message)
        raise_for_status_with_dependency_name(response, EVENTS_API)
        return response
