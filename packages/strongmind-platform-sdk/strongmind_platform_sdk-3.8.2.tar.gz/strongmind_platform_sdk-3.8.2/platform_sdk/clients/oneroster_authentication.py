from oneroster_client import ApiClient, Configuration

from platform_sdk.clients.identity_client import IdentityServerClient


class AuthenticatedConfig(Configuration):
    def auth_settings(self):
        """Gets Auth Settings dict for api client.

        :return: The Auth Settings information dict.
        """
        return {
            'OAuth2Security':
                {
                    'type': 'oauth2',
                    'in': 'header',
                    'key': 'Authorization',
                    'value': self.get_token_hook()
                },
        }


def get_authenticated_oneroster_client(base_url: str,
                                       identity_base_url: str,
                                       client_id: str,
                                       client_secret: str):
    id_server_client = IdentityServerClient({
        "baseurl": identity_base_url,
        "client_id": client_id,
        "client_secret": client_secret
    })
    return get_authenticated_oneroster_client_with_identity_server(base_url, id_server_client)


def get_authenticated_oneroster_client_with_identity_server(base_url: str,
                                                            id_server_client: IdentityServerClient):
    config = AuthenticatedConfig()
    config.get_token_hook = lambda: f"Bearer {id_server_client.get_token()}"
    config.host = base_url
    return ApiClient(config)
