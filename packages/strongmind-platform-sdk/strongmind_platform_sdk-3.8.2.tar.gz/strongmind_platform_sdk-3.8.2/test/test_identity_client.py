import unittest
import uuid
from datetime import datetime, timedelta

import requests
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
from expects import *
from faker import Faker
from freezegun import freeze_time
from mockito import when, mock, unstub, verify, verifyStubbedInvocationsAreUsed
from requests import HTTPError
from requests.auth import HTTPBasicAuth

from platform_sdk.clients.identity_client import IdentityServerClient, IdentityNotFoundError, IdentityClientError
from test.helpers.test_helpers import create_http_error

fake = Faker()


class TestIdentityTokenRetrieval(unittest.TestCase):
    def setUp(self) -> None:
        self.identity_server_domain = fake.hostname()
        self.identity_server_secret = {
            "baseurl": f"https://{self.identity_server_domain}", "client_id": fake.hostname(),
            "client_secret": str(uuid.uuid4())}
        self.id_server_client = IdentityServerClient(self.identity_server_secret)

        self.jwks_config = {
            "keys": [{"kty": "RSA", "use": "sig", "kid": "B11BEF00378B154EE50987E40CC61A860E7B73A0RS256",
                      "x5t": "sRvvADeLFU7lCYfkDMYahg57c6A", "e": "AQAB",
                      "n": "oq3G2h0uHltYQDE0ybLqAd1A4kOmL9CHRVhIYVSleFIpYwh8hZpDL6ZOxW6vIEYgzKoTY_WUKnu0QBGaerPeHZQ4Aj1XDx-TceOzyQO1XQMIQRENoiXZY-gLpdB3_I9Sx7-Nt1Xa4HeZYKoOrtJ4iKs-rpj8k7zdGitdIYSvl41vbIJ-F_x7NaIlIj1tnLnbj3Kwldb8ZPW6aUIJtBw0Ei0_bVKFQIZysjP0WG2hxUHfpNvhapTrR0v8TRZer4q1SFxoz3frjOVB4VOSqvRyI2nsGn_tyoh1EH8TLKe_D1KKmp-68qCaaRXfSa1y1coKtGHMhzdRHakQ0GR5UWJJwgwK4jd4QxQVpWr0eV0gvPBp9UoRXTk0NiKb1-svCnnb2I1VQDEdXFi8cMFZmDmsJ4gmhy-yDydqHbWcwQX7TE_eGsnfgh4tayMZRnrJ5SFPT-dEdxkYYc1ikAT_0LF_w7QtfGOXRvu8coN1pcAjTiGZrs8bQZJ4xk6GJE1-TyjdNO9RAxa2SgKspzfdXxfdJ6iO-LUMR8aEe8MAd8RcEHA6fghPa5hYopJXUa4p-vd8T6SV2SRtsjWlITsDxUhKIVIdFXZoY4-AH66f1V5oODAy-r9HxP5AJdBcmFKUE-ZLep5tPw_8YQZVox2EEODlt0yyidSWySf77xveUcGLGw8",
                      "x5c": [
                          "MIIFMjCCAxqgAwIBAgIQHcyK71MjS1G7mst8V\u002B5S5TANBgkqhkiG9w0BAQsFADAWMRQwEgYDVQQDEwtEZXZJZGVudGl0eTAeFw0yMDAxMTMxNjA0MDlaFw0zMDAxMTMxNjE0MDlaMBYxFDASBgNVBAMTC0RldklkZW50aXR5MIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEAoq3G2h0uHltYQDE0ybLqAd1A4kOmL9CHRVhIYVSleFIpYwh8hZpDL6ZOxW6vIEYgzKoTY/WUKnu0QBGaerPeHZQ4Aj1XDx\u002BTceOzyQO1XQMIQRENoiXZY\u002BgLpdB3/I9Sx7\u002BNt1Xa4HeZYKoOrtJ4iKs\u002Brpj8k7zdGitdIYSvl41vbIJ\u002BF/x7NaIlIj1tnLnbj3Kwldb8ZPW6aUIJtBw0Ei0/bVKFQIZysjP0WG2hxUHfpNvhapTrR0v8TRZer4q1SFxoz3frjOVB4VOSqvRyI2nsGn/tyoh1EH8TLKe/D1KKmp\u002B68qCaaRXfSa1y1coKtGHMhzdRHakQ0GR5UWJJwgwK4jd4QxQVpWr0eV0gvPBp9UoRXTk0NiKb1\u002BsvCnnb2I1VQDEdXFi8cMFZmDmsJ4gmhy\u002ByDydqHbWcwQX7TE/eGsnfgh4tayMZRnrJ5SFPT\u002BdEdxkYYc1ikAT/0LF/w7QtfGOXRvu8coN1pcAjTiGZrs8bQZJ4xk6GJE1\u002BTyjdNO9RAxa2SgKspzfdXxfdJ6iO\u002BLUMR8aEe8MAd8RcEHA6fghPa5hYopJXUa4p\u002Bvd8T6SV2SRtsjWlITsDxUhKIVIdFXZoY4\u002BAH66f1V5oODAy\u002Br9HxP5AJdBcmFKUE\u002BZLep5tPw/8YQZVox2EEODlt0yyidSWySf77xveUcGLGw8CAwEAAaN8MHowDgYDVR0PAQH/BAQDAgWgMAkGA1UdEwQCMAAwHQYDVR0lBBYwFAYIKwYBBQUHAwEGCCsGAQUFBwMCMB8GA1UdIwQYMBaAFPZF1aUGMikPeBrUdEYpJ0/I7/UbMB0GA1UdDgQWBBT2RdWlBjIpD3ga1HRGKSdPyO/1GzANBgkqhkiG9w0BAQsFAAOCAgEATLwtq5qkMrWblZD/\u002B/\u002ByqrJOomHU0qOJaVbqi/oWMDm5cltk3mRj2YV5n4EuWMoKlKShnWjHoDWF8ZHYOMbTAGOUB6aLcikEPWMPKkkDuo/6pwo\u002BZsBUKzi6mGq3tDnpL46hk//bN33zQ3m4Llzwos1685WzpzhfO8QoZ0NB0h0v\u002Bh7hWmnSJVPoMnHuVraQLtNzUF6snyCtChoSGn/fh3dWEhEY9U7zC9HMuBLNGkhM4UVh\u002Bb1hCg9VFREn0ThF4xKvKVXli2Hioxz2XwlZ1BzJ4so1brYbnEotDj46JRQ7GAnY3/IYdtlYgsc8Jh920K5SS\u002BSKHKCTkhFXadTW\u002BWNVMNnwn4QRPiiYfyOG5c0wedegchHk/oG58ISuqgkhh9ehOfmMVHeUHDJ\u002B7s\u002BKsxbG4nzfO6Y8wrcO/93m0P56Len5xfz1FZ8qYGBAhG7fEge0xIeI5qLo18rP8oUmItdH\u002BteA4RWn7Ol\u002BLn\u002B2d8bQfkiRmSKsMVuqXsmPTMCJJfF6EKdyR2iaYOCckutGSktr7iWahRUibm0uJm0lMUEM7H7U5/inuJnjAj8LxnPmUqKJn8ggSbdtf0AOA2PVHkeyNvWU/pZ2mmRY5QoVOobFDcQX2a7R3LE9ZBp14z29yyPllHVblfdKblKs/xvtl1eOZPeo4vSnOR/MxppvdpU="],
                      "alg": "RS256"}]}

    def tearDown(self) -> None:
        unstub()

    def mock_token_retrieval(self, response):
        when(requests).post(
            f"https://{self.identity_server_domain}/connect/token",
            auth=HTTPBasicAuth(
                username=self.identity_server_secret["client_id"],
                password=self.identity_server_secret["client_secret"]),
            data={'grant_type': 'client_credentials'}).thenReturn(response)

    def test_update_account_raises_identity_client_error_on_page_error(self):
        identity_id = fake.uuid4()
        url = f"https://{self.identity_server_domain}/api/accounts/{identity_id}"
        headers = {'header': 'token'}
        data = {'username': fake.word()}
        response_text = '<html><head><title>Error - Identity</title>'
        mock_response = mock({'text': response_text})
        when(self.id_server_client)._headers().thenReturn(headers)
        when(requests).patch(url, headers=headers, json=data).thenReturn(mock_response)
        with self.assertRaises(IdentityClientError) as assert_error:
            self.id_server_client.update_account(identity_id, username=data['username'])
        expect(str(assert_error.exception)).to(equal(response_text))

    def test_send_reminder_email_raises_identity_client_error_on_page_error(self):
        identity_id = fake.uuid4()
        url = f"https://{self.identity_server_domain}/api/accounts/SendReminderEmail"
        headers = {'header': 'token'}
        response_text = '<html><head><title>Error - Identity</title>'
        mock_response = mock({'text': response_text})
        when(self.id_server_client)._headers().thenReturn(headers)
        when(requests).post(url, json=identity_id, headers=headers).thenReturn(mock_response)
        with self.assertRaises(IdentityClientError) as assert_error:
            self.id_server_client.send_reminder_email(identity_id)
        expect(str(assert_error.exception)).to(equal(response_text))

    def test_password_reset_raises_identity_client_error_on_page_error(self):
        identity_id = fake.uuid4()
        url = f"https://{self.identity_server_domain}/api/accounts/{identity_id}" \
              f"/PasswordReset?sendEmail=False&includeUsername=False&returnUrl="
        headers = {'header': 'token'}
        response_text = '<html><head><title>Error - Identity</title>'
        mock_response = mock({'text': response_text})
        when(self.id_server_client)._headers().thenReturn(headers)
        when(requests).post(url, headers=headers).thenReturn(mock_response)
        with self.assertRaises(IdentityClientError) as assert_error:
            self.id_server_client.password_reset(identity_id)
        expect(str(assert_error.exception)).to(equal(response_text))

    def test_get_token_raises_identity_client_error_on_page_error(self):
        response_text = '<html><head><title>Error - Identity</title>'
        mock_response = mock({'text': response_text})
        basic_auth = HTTPBasicAuth(username=self.id_server_client.client_id,
                                   password=self.id_server_client.client_secret)
        when(requests).post(
            f"{self.id_server_client.baseurl}/connect/token", auth=basic_auth, data={'grant_type': 'client_credentials'}
        ).thenReturn(mock_response)
        with self.assertRaises(IdentityClientError) as assert_error:
            self.id_server_client.get_token()
        expect(str(assert_error.exception)).to(equal(response_text))

    def test_get_raises_identity_client_error_on_page_error(self):
        url = f"https://{self.identity_server_domain}/api/accounts/{fake.uuid4()}"
        headers = {'header': 'token'}
        response_text = '<html><head><title>Error - Identity</title>'
        mock_response = mock({'text': response_text})
        when(self.id_server_client)._headers().thenReturn(headers)
        when(requests).get(url, headers=headers).thenReturn(mock_response)
        with self.assertRaises(IdentityClientError) as assert_error:
            self.id_server_client._get(url)
        expect(str(assert_error.exception)).to(equal(response_text))

    @freeze_time("2020-07-31")
    def test_identity_client_issues_new_token_when_none_exists(self):
        """When there is no token, we should get a new one so that we can have access"""
        expected_token = fake.word()
        response = mock({'status_code': 200, 'json': lambda: {"access_token": expected_token, "expires_in": 3600}})
        response.text = fake.word()
        self.mock_token_retrieval(response)
        token = self.id_server_client.get_token()
        expect(token).to(equal(expected_token))
        verifyStubbedInvocationsAreUsed()

    @freeze_time("2020-07-31")
    def test_identity_client_issues_new_token_when_token_expired(self):
        """When the token is expired, we should get a new one so that we can have access"""
        stale_token = fake.word()
        expected_token = fake.word()
        self.id_server_client.token = {"access_token": stale_token, "expires_in": 3600,
                                       "timestamp": datetime.utcnow() - timedelta(days=1)}
        response = mock({'status_code': 200, 'json': lambda: {"access_token": expected_token, "expires_in": 3600}})
        response.text = fake.word()
        self.mock_token_retrieval(response)
        token = self.id_server_client.get_token()
        expect(token).to(equal(expected_token))
        verifyStubbedInvocationsAreUsed()

    @freeze_time("2020-07-31")
    def test_identity_client_issues_new_token_when_token_is_about_to_expire(self):
        """
        When the token is within a 30 second period from expring
        Then should get a new one so that we can have access
        So that tokens do not expire while we are using them
        """
        stale_token = fake.word()
        expected_token = fake.word()
        self.id_server_client.token = {"access_token": stale_token, "expires_in": 3600,
                                       "timestamp": datetime.utcnow() - timedelta(minutes=59, seconds=45)}
        response = mock({'status_code': 200, 'json': lambda: {"access_token": expected_token, "expires_in": 3600}})
        response.text = fake.word()
        self.mock_token_retrieval(response)
        token = self.id_server_client.get_token()
        expect(token).to(equal(expected_token))
        verifyStubbedInvocationsAreUsed()

    @freeze_time("2020-07-31")
    def test_identity_client_issues_same_token_when_one_exists(self):
        """
        When there is a token that is not expired,
        we should reuse it so that we can have access and we aren't getting tokens all the time
        """
        expected_token = fake.word()
        self.id_server_client.token = {"access_token": expected_token, "expires_in": 3600,
                                       "timestamp": datetime.utcnow() - timedelta(minutes=1)}

        token = self.id_server_client.get_token()
        expect(token).to(equal(expected_token))
        verifyStubbedInvocationsAreUsed()

    def test_gets_identity_by_username(self):
        """
        Client should be able to get an identity by username, using the identity server API
        """
        # Arrange
        self.id_server_client.token = {"access_token": "blah", "expires_in": 3600,
                                       "timestamp": datetime.utcnow() - timedelta(minutes=1)}
        username = fake.name()
        response = mock({
            'status_code': 200
        }, spec=requests.Response)
        response.text = fake.word()
        when(response).raise_for_status().thenReturn()
        when(response).json().thenReturn({"username": username})

        when(requests).get(
            f"https://{self.identity_server_domain}/api/accounts?username={username}",
            headers={"Authorization": "Bearer blah", "Accept": "application/json"}).thenReturn(response)

        # Act
        identity = self.id_server_client.get_by_username(username)

        # Assert
        expect(identity["username"]).to(equal(username))

    def test_gets_identity_by_external_account_id(self):
        """
        Client should be able to get an identity by external account id, using the identity server API
        """
        # Arrange
        self.id_server_client.token = {"access_token": "blah", "expires_in": 3600,
                                       "timestamp": datetime.utcnow() - timedelta(minutes=1)}
        id = fake.uuid4()
        provider = fake.domain_word()
        account_external_id = fake.uuid4()
        response = mock({
            'status_code': 200
        }, spec=requests.Response)
        response.text = fake.word()
        when(response).raise_for_status().thenReturn()
        when(response).json().thenReturn({"id": id})

        when(requests).get(
            f"https://{self.identity_server_domain}/api/externalaccounts/{provider}/{account_external_id}",
            headers={"Authorization": "Bearer blah", "Accept": "application/json"}).thenReturn(response)

        # Act
        identity = self.id_server_client.get_by_external_id(provider, account_external_id)

        # Assert
        expect(identity["id"]).to(equal(id))

    def test_raises_identity_not_found_if_identity_by_username_does_not_exist(self):
        """
        Client should return an IdentityNotFoundError if the identity is not found by username
        """
        # Arrange
        self.id_server_client.token = {"access_token": "blah", "expires_in": 3600,
                                       "timestamp": datetime.utcnow() - timedelta(minutes=1)}
        username = fake.name()
        response = mock({
            'status_code': 404
        }, spec=requests.Response)
        when(response).raise_for_status().thenRaise(requests.HTTPError(response=response))

        when(requests).get(
            f"https://{self.identity_server_domain}/api/accounts?username={username}",
            headers={"Authorization": "Bearer blah", "Accept": "application/json"}).thenReturn(response)

        # Act/Assert
        with self.assertRaises(IdentityNotFoundError):
            self.id_server_client.get_by_username(username)

    def test_gets_identity_by_id(self):
        """
        Client should be able to get an identity by ID, using the identity server API
        """
        # Arrange
        self.id_server_client.token = {"access_token": "blah", "expires_in": 3600,
                                       "timestamp": datetime.utcnow() - timedelta(minutes=1)}
        identity_id = fake.uuid4()
        response = mock({
            'status_code': 200
        }, spec=requests.Response)
        response.text = fake.word()
        when(response).raise_for_status().thenReturn()
        when(response).json().thenReturn({"id": identity_id})

        when(requests).get(
            f"https://{self.identity_server_domain}/api/accounts/{identity_id}",
            headers={"Authorization": "Bearer blah", "Accept": "application/json"}).thenReturn(response)

        # Act
        identity = self.id_server_client.get_by_id(identity_id)

        # Assert
        expect(identity["id"]).to(equal(identity_id))

    def test_raises_identity_not_found_if_identity_by_id_does_not_exist(self):
        """
        Client should return an IdentityNotFoundError if the identity is not found by id
        """
        # Arrange
        self.id_server_client.token = {"access_token": "blah", "expires_in": 3600,
                                       "timestamp": datetime.utcnow() - timedelta(minutes=1)}
        identity_id = fake.uuid4()
        response = mock({
            'status_code': 404
        }, spec=requests.Response)
        when(response).raise_for_status().thenRaise(requests.HTTPError(response=response))

        when(requests).get(
            f"https://{self.identity_server_domain}/api/accounts/{identity_id}",
            headers={"Authorization": "Bearer blah", "Accept": "application/json"}).thenReturn(response)

        # Act/Assert
        with self.assertRaises(IdentityNotFoundError):
            self.id_server_client.get_by_id(identity_id)

    def test_get_identities_with_search(self):
        """
        Client should be able to get n identities with an email/username/name/id like the search param
        """
        # Arrange
        self.id_server_client.token = {"access_token": "blah", "expires_in": 3600,
                                       "timestamp": datetime.utcnow() - timedelta(minutes=1)}
        identity_id_1 = fake.uuid4()
        identity_id_2 = fake.uuid4()
        response = mock({
            'status_code': 200
        }, spec=requests.Response)
        response.text = fake.word()
        when(response).raise_for_status().thenReturn()
        when(response).json().thenReturn(
            {
                "results": [
                    {
                        "id": identity_id_1
                    },
                    {
                        "id": identity_id_2
                    }
                ]
            })

        search_param = fake.email()
        skip = 2
        take = 101
        include_inactive = True

        when(requests).get(
            f"https://{self.identity_server_domain}/api/accounts/search"
            f"?search={search_param}&skip={skip}&take={take}&includeInactive={include_inactive}",
            headers={"Authorization": "Bearer blah", "Accept": "application/json"}).thenReturn(response)

        # Act
        result = self.id_server_client.search(search_param, skip, take, include_inactive)

        # Assert
        expect(result['results']).to(be_a(list))
        expect(result['results'][0]['id']).to(equal(identity_id_1))
        expect(result['results'][1]['id']).to(equal(identity_id_2))

    def test_search_raises_identity_not_found(self):
        """
        Client should catch 404 exceptions and still return the response json
        The response json should contain an empty list for results
        """
        # Arrange
        self.id_server_client.token = {"access_token": "blah", "expires_in": 3600,
                                       "timestamp": datetime.utcnow() - timedelta(minutes=1)}
        response = mock({
            'status_code': 404
        }, spec=requests.Response)
        response.text = fake.word()
        when(response).raise_for_status().thenRaise(requests.HTTPError(response=response))
        when(response).json().thenReturn({"results": []})

        search_param = fake.email()

        when(requests).get(
            f"https://{self.identity_server_domain}/api/accounts/search"
            f"?search={search_param}&skip=0&take=100&includeInactive=False",
            headers={"Authorization": "Bearer blah", "Accept": "application/json"}).thenReturn(response)

        # Act
        result = self.id_server_client.search(search_param)

        # Assert
        expect(result['results']).to(be_empty)

    def test_search_raises_non_404_error(self):
        """
        Client should catch 404 exceptions and still return the response json
        The response json should contain an empty list for results
        """
        # Arrange
        self.id_server_client.token = {"access_token": "blah", "expires_in": 3600,
                                       "timestamp": datetime.utcnow() - timedelta(minutes=1)}
        response = mock({
            'status_code': 500
        }, spec=requests.Response)
        when(response).raise_for_status().thenRaise(requests.HTTPError(response=response))

        search_param = fake.email()

        when(requests).get(
            f"https://{self.identity_server_domain}/api/accounts/search"
            f"?search={search_param}&skip=0&take=100&includeInactive=False",
            headers={"Authorization": "Bearer blah", "Accept": "application/json"}).thenReturn(response)

        # Act/Assert
        with self.assertRaises(HTTPError) as context:
            self.id_server_client.search(search_param)

        expect(context.exception.dependency_name).to(equal('IdentityServer'))

    def test_initiates_password_resets_with_email(self):
        """
        Client should be able to initiate password resets with email
        """
        # Arrange
        send_email = True
        include_username = fake.boolean()
        return_url = fake.url()
        self.id_server_client.token = {"access_token": "blah", "expires_in": 3600,
                                       "timestamp": datetime.utcnow() - timedelta(minutes=1)}
        identity_id = fake.uuid4()
        response = mock({
            'status_code': 200,
            'text': ""
        }, spec=requests.Response)
        when(response).raise_for_status().thenReturn()
        # when(response).json().thenRaise(JSONDecodeError)

        when(requests).post(
            f"https://{self.identity_server_domain}/api/accounts/{identity_id}/PasswordReset?sendEmail={send_email}&includeUsername={include_username}&returnUrl={return_url}",
            headers={"Authorization": "Bearer blah", "Accept": "application/json"}).thenReturn(response)

        # Act
        self.id_server_client.password_reset(identity_id, send_email, include_username, return_url)

        # Assert
        verifyStubbedInvocationsAreUsed()
        verify(requests).post(
            f"https://{self.identity_server_domain}/api/accounts/{identity_id}/PasswordReset?sendEmail={send_email}&includeUsername={include_username}&returnUrl={return_url}",
            headers={"Authorization": "Bearer blah", "Accept": "application/json"})

    def test_initiates_password_resets_without_email(self):
        """
        Client should be able to initiate password resets without email
        """
        # Arrange
        send_email = False
        include_username = fake.boolean()
        return_url = fake.url()
        self.id_server_client.token = {"access_token": "blah", "expires_in": 3600,
                                       "timestamp": datetime.utcnow() - timedelta(minutes=1)}
        identity_id = fake.uuid4()
        response_dict = {
            'accountId': identity_id,
            'url': '',
            'expiresDateTime': ''
        }
        response = mock({
            'status_code': 200,
            'text': str(response_dict)
        }, spec=requests.Response)
        when(response).raise_for_status().thenReturn()
        when(response).json().thenReturn(response_dict)

        when(requests).post(
            f"https://{self.identity_server_domain}/api/accounts/{identity_id}/PasswordReset?sendEmail={send_email}&includeUsername={include_username}&returnUrl={return_url}",
            headers={"Authorization": "Bearer blah", "Accept": "application/json"}).thenReturn(response)

        # Act
        self.id_server_client.password_reset(identity_id, send_email, include_username, return_url)

        # Assert
        verifyStubbedInvocationsAreUsed()
        verify(requests).post(
            f"https://{self.identity_server_domain}/api/accounts/{identity_id}/PasswordReset?sendEmail={send_email}&includeUsername={include_username}&returnUrl={return_url}",
            headers={"Authorization": "Bearer blah", "Accept": "application/json"})

    def test_updates_account_username(self):
        """
        Client should be able to update the username on an account
        """
        # Arrange
        self.id_server_client.token = {"access_token": "blah", "expires_in": 3600,
                                       "timestamp": datetime.utcnow() - timedelta(minutes=1)}
        identity_id = fake.uuid4()
        username = fake.sentence()

        response = mock({
            'status_code': 200,
            'text': ''
        }, spec=requests.Response)
        when(response).raise_for_status().thenReturn()

        when(requests).patch(
            f"https://{self.identity_server_domain}/api/accounts/{identity_id}",
            json={"username": username},
            headers={"Authorization": "Bearer blah", "Accept": "application/json"}).thenReturn(response)

        # Act
        self.id_server_client.update_account(identity_id,
                                             username=username)

        # Assert
        verifyStubbedInvocationsAreUsed()

    def test_updates_account_email(self):
        """
        Client should be able to update the email on an account
        """
        # Arrange
        self.id_server_client.token = {"access_token": "blah", "expires_in": 3600,
                                       "timestamp": datetime.utcnow() - timedelta(minutes=1)}
        identity_id = fake.uuid4()
        email = f"{fake.word()}@test.com"

        response = mock({
            'status_code': 200,
            'text': ''
        }, spec=requests.Response)
        when(response).raise_for_status().thenReturn()

        when(requests).patch(
            f"https://{self.identity_server_domain}/api/accounts/{identity_id}",
            json={"email": email},
            headers={"Authorization": "Bearer blah", "Accept": "application/json"}).thenReturn(response)

        # Act
        self.id_server_client.update_account(identity_id,
                                             email=email)

        # Assert
        verifyStubbedInvocationsAreUsed()

    def test_updates_account_active(self):
        """
        Client should be able to update the active flag on an account
        """
        # Arrange
        self.id_server_client.token = {"access_token": "blah", "expires_in": 3600,
                                       "timestamp": datetime.utcnow() - timedelta(minutes=1)}
        identity_id = fake.uuid4()
        is_active = fake.boolean()

        response = mock({
            'status_code': 200,
            'text': ''
        }, spec=requests.Response)
        when(response).raise_for_status().thenReturn()

        when(requests).patch(
            f"https://{self.identity_server_domain}/api/accounts/{identity_id}",
            json={"isActive": is_active},
            headers={"Authorization": "Bearer blah", "Accept": "application/json"}).thenReturn(response)

        # Act
        self.id_server_client.update_account(identity_id,
                                             is_active=is_active)

        # Assert
        verifyStubbedInvocationsAreUsed()

    def test_gets_identity_by_source_system_id(self):
        """
        Client should be able to get an identity by Source System ID, using the identity server API
        """
        # Arrange
        self.id_server_client.token = {"access_token": "blah", "expires_in": 3600,
                                       "timestamp": datetime.utcnow() - timedelta(minutes=1)}
        source_system_id = fake.uuid4()
        identity_id = fake.uuid4()
        response = mock({
            'status_code': 200
        }, spec=requests.Response)
        response.text = fake.word()
        when(response).raise_for_status().thenReturn()
        when(response).json().thenReturn({"id": identity_id, "sourceSystemId": source_system_id})

        when(requests).get(
            f"https://{self.identity_server_domain}/api/accounts/sourceSystemId/{source_system_id}",
            headers={"Authorization": "Bearer blah", "Accept": "application/json"}).thenReturn(response)

        # Act
        identity = self.id_server_client.get_by_source_system_id(source_system_id)

        # Assert
        expect(identity["id"]).to(equal(identity_id))
        expect(identity["sourceSystemId"]).to(equal(source_system_id))

    def test_raises_identity_not_found_if_identity_by_source_id_does_not_exist(self):
        """
        Client should return an IdentityNotFoundError if the identity is not found by source system id
        """
        # Arrange
        self.id_server_client.token = {"access_token": "blah", "expires_in": 3600,
                                       "timestamp": datetime.utcnow() - timedelta(minutes=1)}
        source_system_id = fake.uuid4()
        response = mock({
            'status_code': 404
        }, spec=requests.Response)
        when(response).raise_for_status().thenRaise(requests.HTTPError(response=response))

        when(requests).get(
            f"https://{self.identity_server_domain}/api/accounts/sourceSystemId/{source_system_id}",
            headers={"Authorization": "Bearer blah", "Accept": "application/json"}).thenReturn(response)

        # Act/Assert
        with self.assertRaises(IdentityNotFoundError):
            self.id_server_client.get_by_source_system_id(source_system_id)

    def test_posts_user_to_send_reminder_email_endpoint(self):
        """
        Client should be able to post to the /accounts/SendReminderEmail endpoint with the given user id
        """
        # Arrange
        identity_id = fake.uuid4()
        self.id_server_client.token = {"access_token": "blah", "expires_in": 3600,
                                       "timestamp": datetime.utcnow() - timedelta(minutes=1)}
        response = mock({
            'status_code': 202,
            'text': ""
        }, spec=requests.Response)
        when(response).raise_for_status().thenReturn()
        # when(response).json().thenRaise(JSONDecodeError)

        when(requests).post(
            f"https://{self.identity_server_domain}/api/accounts/SendReminderEmail",
            json=str(identity_id),
            headers={"Authorization": "Bearer blah", "Accept": "application/json"}).thenReturn(response)

        # Act
        self.id_server_client.send_reminder_email(identity_id)

        # Assert
        verifyStubbedInvocationsAreUsed()
        verify(requests).post(
            f"https://{self.identity_server_domain}/api/accounts/SendReminderEmail",
            json=str(identity_id),
            headers={"Authorization": "Bearer blah", "Accept": "application/json"})

    def test_it_raises_identity_not_found_with_http_info(self):
        # Arrange
        self.id_server_client.token = {"access_token": "blah", "expires_in": 3600,
                                       "timestamp": datetime.utcnow() - timedelta(minutes=1)}
        url = fake.url()
        http_error = create_http_error(404, url=url)
        when(requests).get(...).thenReturn(http_error.response)
        when(http_error.response).raise_for_status().thenRaise(http_error)

        # Act
        with self.assertRaises(IdentityNotFoundError) as context:
            self.id_server_client._get(url)

        expect(context.exception.response).to(equal(http_error.response))
        expect(context.exception.request).to(equal(http_error.request))
        expect(context.exception.dependency_name).to(equal('IdentityServer'))

    def test_send_reminder_email_raises_http_error_with_dependency_name(self):
        # Arrange
        self.id_server_client.token = {"access_token": "blah", "expires_in": 3600,
                                       "timestamp": datetime.utcnow() - timedelta(minutes=1)}
        identity_id = fake.uuid4()
        http_error = create_http_error(500)
        when(requests).post(...).thenReturn(http_error.response)
        when(http_error.response).raise_for_status().thenRaise(http_error)

        # Act/Assert
        with self.assertRaises(HTTPError) as context:
            self.id_server_client.send_reminder_email(identity_id)

        verify(requests).post(
            f"https://{self.identity_server_domain}/api/accounts/SendReminderEmail",
            json=str(identity_id),
            headers={"Authorization": "Bearer blah", "Accept": "application/json"})

        expect(context.exception.dependency_name).to(equal('IdentityServer'))

    def test_update_account_raises_http_error_with_dependency_name(self):
        # Arrange
        self.id_server_client.token = {"access_token": "blah", "expires_in": 3600,
                                       "timestamp": datetime.utcnow() - timedelta(minutes=1)}
        username = fake.word()
        identity_id = fake.uuid4()
        http_error = create_http_error(500)
        when(requests).patch(...).thenReturn(http_error.response)
        when(http_error.response).raise_for_status().thenRaise(http_error)

        # Act/Assert
        with self.assertRaises(HTTPError) as context:
            self.id_server_client.update_account(identity_id, username)

        verify(requests).patch(
            f"https://{self.identity_server_domain}/api/accounts/{identity_id}",
            json={"username": username},
            headers={"Authorization": "Bearer blah", "Accept": "application/json"})

        expect(context.exception.dependency_name).to(equal('IdentityServer'))

    def test_password_reset_raises_http_error_with_dependency_name(self):
        # Arrange
        self.id_server_client.token = {"access_token": "blah", "expires_in": 3600,
                                       "timestamp": datetime.utcnow() - timedelta(minutes=1)}
        identity_id = fake.uuid4()
        send_email = False
        include_username = fake.boolean()
        return_url = fake.url()
        http_error = create_http_error(500)
        when(requests).post(...).thenReturn(http_error.response)
        when(http_error.response).raise_for_status().thenRaise(http_error)

        # Act/Assert
        with self.assertRaises(HTTPError) as context:
            self.id_server_client.password_reset(identity_id, send_email, include_username, return_url)

        verify(requests).post(
            f"https://{self.identity_server_domain}/api/accounts/{identity_id}/PasswordReset?sendEmail={send_email}&includeUsername={include_username}&returnUrl={return_url}",
            headers={"Authorization": "Bearer blah", "Accept": "application/json"})

        expect(context.exception.dependency_name).to(equal('IdentityServer'))

    def test_get_token_raises_http_error_with_dependency_name(self):
        # Arrange
        http_error = create_http_error(500)
        when(requests).post(...).thenReturn(http_error.response)
        when(http_error.response).raise_for_status().thenRaise(http_error)

        # Act/Assert
        with self.assertRaises(HTTPError) as context:
            self.id_server_client.get_token()

        expect(context.exception.dependency_name).to(equal('IdentityServer'))

    def test_get_raises_http_error_with_dependency_name(self):
        # Arrange
        http_error = create_http_error(500)
        when(requests).get(...).thenReturn(http_error.response)
        when(http_error.response).raise_for_status().thenRaise(http_error)
        when(self.id_server_client).get_token()

        # Act/Assert
        with self.assertRaises(HTTPError) as context:
            self.id_server_client._get(fake.url())

        expect(context.exception.dependency_name).to(equal('IdentityServer'))

    def test_get_doesnt_raise_404_http_errors_with_flag(self):
        # Arrange
        http_error = create_http_error(404)
        when(requests).get(...).thenReturn(http_error.response)
        when(http_error.response).raise_for_status().thenRaise(http_error)
        when(http_error.response).json()
        when(self.id_server_client).get_token()

        # Act/Assert
        self.id_server_client._get(fake.url(), raise_404=False)

    def test_jwks_config(self):
        # Arrange
        self.id_server_client.token = {"access_token": "blah", "expires_in": 3600,
                                       "timestamp": datetime.utcnow() - timedelta(minutes=1)}
        response = mock({
            'status_code': 200
        }, spec=requests.Response)
        response.text = fake.word()
        when(response).raise_for_status().thenReturn()
        when(response).json().thenReturn(self.jwks_config)

        when(requests).get(
            f"https://{self.identity_server_domain}/.well-known/openid-configuration/jwks",
            headers={"Authorization": "Bearer blah", "Accept": "application/json"}).thenReturn(response)

        # Act
        result = self.id_server_client.jwks_config()

        # Assert
        expect(result).to(equal(self.jwks_config))

    def test_public_key_without_argument(self):
        # Arrange
        when(self.id_server_client).jwks_config().thenReturn(self.jwks_config)

        # Act
        result = self.id_server_client.public_key()

        # Assert
        expect(result).to(be_a(RSAPublicKey))

    def test_public_key_with_jws_config_argument(self):
        # Act
        result = self.id_server_client.public_key(self.jwks_config)

        # Assert
        expect(result).to(be_a(RSAPublicKey))


if __name__ == '__main__':
    unittest.main()
