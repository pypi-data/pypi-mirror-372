import unittest

import requests
from expects import *
from faker import Faker
from mockito import mock, when, unstub, captor
from oneroster_client import ApiClient
from requests import Response
from requests.structures import CaseInsensitiveDict

from platform_sdk.clients.identity_client import IdentityServerClient
from platform_sdk.clients.oneroster_authentication import get_authenticated_oneroster_client_with_identity_server, \
    AuthenticatedConfig

fake = Faker()


class TestOneRosterAuthentication(unittest.TestCase):
    def setUp(self) -> None:
        self.token = fake.word()
        self.id_server_client = mock(IdentityServerClient)

    def tearDown(self) -> None:
        unstub()

    def setup_mock_request_response(self):
        self.mock_response = mock(Response)
        self.mock_response.status_code = 200
        self.mock_response.headers = CaseInsensitiveDict({})
        when(self.mock_response).raise_for_status()

        self.header_captor = captor()

        when(requests).request(any, any, params=any, json=any, headers=self.header_captor, timeout=any) \
            .thenReturn(self.mock_response)

    def test_gets_authenticated_client(self):
        # Arrange
        when(self.id_server_client).get_token().thenReturn(self.token)
        base_url = f"https://{fake.domain_word()}"

        # Act
        client = get_authenticated_oneroster_client_with_identity_server(
            base_url,
            self.id_server_client
        )

        # Assert
        expect(client).to(be_a(ApiClient))
        expect(client.configuration.host).to(equal(base_url))

    def test_calls_api_with_correct_auth_header(self):
        # Arrange
        self.setup_mock_request_response()
        when(self.id_server_client).get_token().thenReturn(self.token)
        base_url = f"https://{fake.domain_word()}"
        client = get_authenticated_oneroster_client_with_identity_server(
            base_url,
            self.id_server_client
        )

        # Act
        client.call_api("/", "GET", auth_settings=['OAuth2Security'])

        # Assert
        expect(self.header_captor.value).not_to(be_none)
        expect(self.header_captor.value).to(have_key("Authorization"))
        expect(self.header_captor.value["Authorization"]).to(equal(f"Bearer {self.token}"))

    def test_token_hook_is_called_on_every_request(self):
        """Make sure we check for a new token on every request"""
        # Arrange
        config = AuthenticatedConfig()
        self.number_of_tokens = 0

        def get_token():
            self.number_of_tokens += 1
            return f"Bearer {self.number_of_tokens}"

        config.get_token_hook = get_token
        client = ApiClient(config)
        self.setup_mock_request_response()

        for i in range(1, 9):
            # Act
            client.call_api("/", "GET", auth_settings=['OAuth2Security'])

            # Assert
            expect(self.header_captor.value).not_to(be_none)
            expect(self.header_captor.value).to(have_key("Authorization"))
            expect(self.header_captor.value["Authorization"]).to(equal(f"Bearer {i}"))


if __name__ == '__main__':
    unittest.main()
