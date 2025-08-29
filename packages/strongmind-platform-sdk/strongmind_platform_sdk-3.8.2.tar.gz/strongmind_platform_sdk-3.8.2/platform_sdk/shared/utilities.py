from oneroster_client import ApiClient
from typing import Optional
import logging
import json
import os

from platform_sdk.clients.central_client import CentralClient
from platform_sdk.clients.identity_client import IdentityServerClient
from platform_sdk.clients.oneroster_authentication import get_authenticated_oneroster_client_with_identity_server
from platform_sdk.shared.constants import ONEROSTER_SINGLE_TYPE_NAME_CLASS

base_one_roster_client: Optional[ApiClient] = None
base_central_client: Optional[ApiClient] = None
base_identity_server_client: Optional[IdentityServerClient] = None


def get_plural_oneroster_type(oneroster_type: str) -> str:
    es_plurals = [ONEROSTER_SINGLE_TYPE_NAME_CLASS]
    suffix = 's' if oneroster_type not in es_plurals else 'es'
    return oneroster_type + suffix


def identity_server_client():
    global base_identity_server_client
    log_out = {
        'cache_hit': True
    }

    if not base_identity_server_client:
        log_out['cache_hit'] = False
        base_identity_server_client = IdentityServerClient({
            "baseurl": os.getenv("IDENTITY_SERVER_BASEURL") or os.getenv("IDENTITY_SERVER_BASE_URL"),
            "client_id": os.getenv("IDENTITY_SERVER_CLIENT_ID"),
            "client_secret": os.getenv("IDENTITY_SERVER_CLIENT_SECRET")
        })
    logging.info(json.dumps(log_out))
    return base_identity_server_client


def authenticated_oneroster_client():
    global base_one_roster_client
    log_out = {
        'cache_hit': True
    }
    if not base_one_roster_client:
        log_out['cache_hit'] = False
        base_one_roster_client = get_authenticated_oneroster_client_with_identity_server(
            base_url=os.getenv("ONEROSTER_BASE_URL"),
            id_server_client=identity_server_client()
        )
    logging.info(json.dumps(log_out))
    return base_one_roster_client


def authenticated_central_client():
    global base_central_client
    log_out = {
        'cache_hit': True
    }
    if not base_central_client:
        log_out['cache_hit'] = False
        base_url = os.getenv("CENTRAL_BASE_URL")
        base_central_client = CentralClient(base_url, identity_server_client())
    logging.info(json.dumps(log_out))
    return base_central_client
