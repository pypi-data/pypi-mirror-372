import json
import unittest
from datetime import datetime

import requests
from expects import expect, equal
from faker import Faker
from mockito import when, mock, unstub, verifyStubbedInvocationsAreUsed, verify
from pydantic.json import pydantic_encoder
from requests import HTTPError

from platform_sdk.clients.identity_client import IdentityServerClient
from platform_sdk.clients.user_creation import UserCreationClient
from platform_sdk.models.user import User
from test.factories.user_factories import UserFactory
from test.helpers.test_helpers import create_http_error

fake = Faker()


class TestUserCreationClient(unittest.TestCase):
    def setUp(self) -> None:
        self.token = fake.word()
        self.url = f"https://{fake.domain_word()}"
        self.identity_server_client = mock(IdentityServerClient)
        when(self.identity_server_client).get_token().thenReturn(self.token)
        self.target = UserCreationClient(
            user_creation_service_url=self.url,
            identity_client=self.identity_server_client)

    def tearDown(self) -> None:
        unstub()

    def test_creates_user_with_hardcoded_date(self):
        """
        Client creates a user with hardcoded data
        """
        # Arrange
        user = User(
            Role="student",
            Username="jimmyt",
            GivenName="Jimmy",
            FamilyName="Thompson",
            Email="jimmy.thompson@test.strongmind.com",
            PartnerName="CoolSchool",
            IDs={
                "com.strongmind.identity.user.id": "405ffa29-844d-4b50-a360-a01bd063e90b"
            },
            ExternalProvider="Test",
            DateOfBirth=datetime.fromisoformat("2010-01-31"),
            SourceSystemId="83958c23-04e3-4755-b59c-d0a454cfc922"
        )
        response = mock({
            'status_code': 200
        }, spec=requests.Response)
        when(response).raise_for_status().thenReturn()
        when(requests).post(...).thenReturn(response)

        # Act
        self.target.create_user(user)

        # Assert
        verify(requests,
               times=1).post(self.url,
                             headers={
                                 'Authorization': f"Bearer {self.token}",
                                 'Content-Type': "application/json"
                             },
                             data='{"Role": "student", "Username": "jimmyt", "GivenName": "Jimmy", "FamilyName": '
                                  '"Thompson", "Email": "jimmy.thompson@test.strongmind.com", "PartnerName": '
                                  '"CoolSchool", "IDs": {"com.strongmind.identity.user.id": '
                                  '"405ffa29-844d-4b50-a360-a01bd063e90b"}, "ExternalProvider": "Test", '
                                  '"DateOfBirth": "2010-01-31", "SourceSystemId": '
                                  '"83958c23-04e3-4755-b59c-d0a454cfc922"}')
        verifyStubbedInvocationsAreUsed()

    def test_creates_user_with_factory_generated_data(self):
        """
        Client creates a user with factory generated data
        """
        # Arrange
        user = UserFactory()
        response = mock({
            'status_code': 200
        }, spec=requests.Response)
        when(response).raise_for_status().thenReturn()
        when(requests).post(...).thenReturn(response)

        # Act
        self.target.create_user(user)

        # Assert
        verify(requests,
               times=1).post(self.url,
                             headers={
                                 'Authorization': f"Bearer {self.token}",
                                 'Content-Type': "application/json"
                             },
                             data=json.dumps({
                                 "Role": user.role,
                                 "Username": user.username,
                                 "GivenName": user.given_name,
                                 "FamilyName": user.family_name,
                                 "Email": user.email,
                                 "PartnerName": user.partner_name,
                                 "IDs": user.ids,
                                 "ExternalProvider": user.external_provider,
                                 "DateOfBirth": user.dob,
                                 "SourceSystemId": user.source_system_id
                             }, default=pydantic_encoder))
        verifyStubbedInvocationsAreUsed()

    def test_creates_user_raises_http_error_with_dependency_name(self):
        """
        Client creates a user with factory generated data
        """
        # Arrange
        user = UserFactory()
        http_error = create_http_error(500)
        when(http_error.response).raise_for_status().thenRaise(http_error)
        when(requests).post(...).thenReturn(http_error.response)

        # Act
        with self.assertRaises(HTTPError) as context:
            self.target.create_user(user)

        # Assert
        expect(getattr(context.exception, 'dependency_name', None)).to(equal('UserCreation'))
        verifyStubbedInvocationsAreUsed()
