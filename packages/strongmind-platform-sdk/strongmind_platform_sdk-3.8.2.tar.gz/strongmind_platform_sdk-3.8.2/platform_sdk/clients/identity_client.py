import base64
import datetime

import requests
from cryptography.hazmat.backends import default_backend
from cryptography.x509 import load_der_x509_certificate
from requests import HTTPError
from requests.auth import HTTPBasicAuth

from platform_sdk.helpers.exception_logger import raise_for_status_with_dependency_name
from platform_sdk.shared.constants import IDENTITY_SERVER


class IdentityNotFoundError(Exception):
    """Identity is not found in the Identity Server"""
    dependency_name = IDENTITY_SERVER

    def __init__(self, http_error: HTTPError = None):
        if http_error:
            self.response = http_error.response
            self.request = http_error.request


class IdentityClientError(Exception):
    """Identity Client Error"""
    dependency_name = IDENTITY_SERVER


class IdentityServerClient:
    def __init__(self, identity_server_secret):
        self.baseurl = identity_server_secret['baseurl']
        self.client_id = identity_server_secret['client_id']
        self.client_secret = identity_server_secret['client_secret']
        self.token = None

    def get_token(self):
        if self._token_expired():
            basic_auth = HTTPBasicAuth(username=self.client_id,
                                       password=self.client_secret)
            response = requests.post(f"{self.baseurl}/connect/token", auth=basic_auth,
                                     data={'grant_type': 'client_credentials'})
            raise_for_status_with_dependency_name(response, IDENTITY_SERVER)
            raise_identity_client_error_if_identity_error_page(response)

            self.token = response.json()
            self.token['timestamp'] = datetime.datetime.utcnow()

        return self.token['access_token']

    def _token_expired(self):
        if not self.token:
            return True

        expires_in = datetime.timedelta(
            seconds=int(self.token['expires_in']))
        expiry_time = self.token['timestamp'] + expires_in
        return expiry_time < datetime.datetime.utcnow() + datetime.timedelta(seconds=30)  # 30-second grace period

    def _headers(self):
        return {
            'Authorization': f"Bearer {self.get_token()}",
            'Accept': 'application/json'
        }

    def _get(self, url, raise_404: bool = True):
        headers = self._headers()
        response = requests.get(url, headers=headers)
        try:
            raise_for_status_with_dependency_name(response, IDENTITY_SERVER)
        except requests.HTTPError as http_error:
            handle_http_error(http_error, raise_404)

        raise_identity_client_error_if_identity_error_page(response)

        return response.json()

    def get_by_username(self, username):
        url = f"{self.baseurl}/api/accounts?username={username}"
        return self._get(url)

    def get_by_id(self, identity_id):
        url = f"{self.baseurl}/api/accounts/{identity_id}"
        return self._get(url)

    def get_by_external_id(self, provider, provider_id):
        url = f"{self.baseurl}/api/externalaccounts/{provider}/{provider_id}"
        return self._get(url)

    def get_by_source_system_id(self, source_system_id: str):
        url = f"{self.baseurl}/api/accounts/sourceSystemId/{source_system_id}"
        return self._get(url)

    def search(self, search: str, skip: int = 0, take: int = 100, include_inactive: bool = False):
        url = f"{self.baseurl}/api/accounts/search" \
              f"?search={search}&skip={skip}&take={take}&includeInactive={include_inactive}"
        return self._get(url, raise_404=False)

    def password_reset(self,
                       identity_id: str,
                       send_email: bool = False,
                       include_username: bool = False,
                       return_url: str = ""):
        headers = self._headers()
        url = f"{self.baseurl}/api/accounts/{identity_id}/PasswordReset?sendEmail={send_email}&includeUsername={include_username}&returnUrl={return_url}"
        response = requests.post(url, headers=headers)
        raise_for_status_with_dependency_name(response, IDENTITY_SERVER)
        raise_identity_client_error_if_identity_error_page(response)

        if len(response.text) > 0:
            return response.json()

    def update_account(self, identity_id, username=None, email=None, is_active=None):
        headers = self._headers()
        url = f"{self.baseurl}/api/accounts/{identity_id}"
        data = {}
        if username is not None:
            data["username"] = username
        if email is not None:
            data["email"] = email
        if is_active is not None:
            data["isActive"] = is_active
        response = requests.patch(url, headers=headers, json=data)
        raise_for_status_with_dependency_name(response, IDENTITY_SERVER)
        raise_identity_client_error_if_identity_error_page(response)

        if response.text:
            return response.json()

    def send_reminder_email(self, identity_id):
        headers = self._headers()
        url = f"{self.baseurl}/api/accounts/SendReminderEmail"
        response = requests.post(url, json=identity_id, headers=headers)
        raise_for_status_with_dependency_name(response, IDENTITY_SERVER)
        raise_identity_client_error_if_identity_error_page(response)

        if len(response.text) > 0:
            return response.json()

    def jwks_config(self):
        jwsk_url = f"{self.baseurl}/.well-known/openid-configuration/jwks"
        return self._get(jwsk_url)

    def public_key(self, jws_config=None):
        jwks_config = jws_config or self.jwks_config()
        x5c_val = jwks_config['keys'][0]['x5c'][0]
        return load_der_x509_certificate(base64.b64decode(x5c_val), default_backend()).public_key()


def handle_http_error(http_error, raise_404):
    if http_error.response.status_code == 404 and raise_404:
        raise IdentityNotFoundError(http_error)
    elif http_error.response.status_code != 404:
        raise http_error


def raise_identity_client_error_if_identity_error_page(response):
    if response.text and 'Error - Identity' in response.text:
        raise IdentityClientError(response.text)
