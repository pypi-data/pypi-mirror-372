import json
import unittest
from datetime import datetime

import requests
from expects import expect, equal
from faker import Faker
from freezegun import freeze_time
from mockito import when, mock, unstub, verifyStubbedInvocationsAreUsed
from pydantic.json import pydantic_encoder
from requests import HTTPError

from platform_sdk.clients.events_client import EventPlatformClient
from platform_sdk.clients.identity_client import IdentityServerClient
from test.factories.event_factories import PowerSchoolEventFactory
from test.helpers.test_helpers import create_http_error

fake = Faker()


class TestEventPipelineClient(unittest.TestCase):
    def setUp(self) -> None:
        self.url = f"https://{fake.domain_name()}"
        self.token = fake.word()
        self.identity_client = mock(IdentityServerClient)
        self.target = EventPlatformClient(url=self.url,
                                          identity_client=self.identity_client)
        when(self.identity_client).get_token().thenReturn(self.token)

    def tearDown(self) -> None:
        unstub()

    @freeze_time("2021-03-24 11:34:25")
    def test_sends_hardcoded_event(self):
        """
        Client sends a hardcoded event via HTTP with the auth and content type headers
        """
        # Arrange
        payload = {
            "type": "PowerSchool.WebHook",
            "subject": "CC",
            "source": self.url,
            "time": datetime.utcnow().isoformat(),
            "datacontenttype": "application/json",
            "data": {
                "ref": self.url,
                "event_type": "UPDATE",
                "id": "blahblah",
                "entity": "CC",
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        response = mock({'status_code': 200, 'text': 'Ok'})

        when(requests).post(self.url, headers={
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/cloudevents+json; charset=utf-8"
        }, data=json.dumps(payload, default=pydantic_encoder)).thenReturn(response)

        # Act
        self.target.send_event(payload)

        # Assert
        verifyStubbedInvocationsAreUsed()

    def test_sends_factory_generated_event(self):
        """
        Client send a generated event via HTTP with the auth and content type headers
        """
        # Arrange
        payload = PowerSchoolEventFactory()
        response = mock({'status_code': 200, 'text': 'Ok'})

        when(requests).post(self.url, headers={
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/cloudevents+json; charset=utf-8"
        }, data=json.dumps(payload, default=pydantic_encoder)).thenReturn(response)

        # Act
        self.target.send_event(payload)

        # Assert
        verifyStubbedInvocationsAreUsed()

    def test_creates_user_raises_http_error_with_dependency_name(self):
        """
        Client creates a user with factory generated data
        """
        # Arrange
        payload = PowerSchoolEventFactory()
        http_error = create_http_error(500)
        when(http_error.response).raise_for_status().thenRaise(http_error)
        when(requests).post(...).thenReturn(http_error.response)

        # Act
        with self.assertRaises(HTTPError) as context:
            self.target.send_event(payload)

        # Assert
        expect(getattr(context.exception, 'dependency_name', None)).to(equal('EventsApi'))
        verifyStubbedInvocationsAreUsed()
