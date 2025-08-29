from dataclasses import fields
from typing import List, Dict, Any

import requests
from requests import HTTPError

from platform_sdk.models.domain import Domain
from platform_sdk.models.partner import Partner
from platform_sdk.shared.exceptions import IdentifierMapperError, PairNotFoundError, PartnerNotFoundError


class IDMapperClient:
    def __init__(self, secret: Dict):
        self.token = secret['token']
        self.domain = secret['domain']

    def _headers(self):
        headers = {'Authorization': f'Token {self.token}'}
        return headers

    def _get(self, url, params=None, partner_api: bool = False):
        response = requests.get(url, headers=self._headers(), params=params)
        try:
            response.raise_for_status()
        except requests.HTTPError as http_error:
            handle_http_error(http_error, partner_api=partner_api)
        return response

    def _put(self, url, payload):
        response = requests.put(url, headers=self._headers(), json=payload)
        return self._verify_response(response)

    def _post(self, url, payload):
        response = requests.post(url, headers=self._headers(), json=payload)
        return self._verify_response(response)

    @staticmethod
    def _verify_response(response):
        try:
            response.raise_for_status()
        except requests.HTTPError as http_error:
            raise IdentifierMapperError(http_error)
        return response

    def get_pairs(self, service, value):
        url = f"https://{self.domain}/api/v1/pairs/"
        params = {service: value}
        return self._get(url, params).json()

    def get_pair_by_guid(self, guid):
        url = f"https://{self.domain}/api/v1/pairs/{guid}"
        if not guid.startswith('strongmind.guid://'):
            url += '/'

        return self._get(url).json()

    def get_partner_by_name(self, partner_name) -> Partner:
        url = f"https://{self.domain}/api/v1/partners/{partner_name}/"
        responded_partner = self._get(url, partner_api=True).json()
        return json_to_model(Partner, responded_partner)

    def get_partner_by_id(self, partner_id: str) -> Partner:
        url = f"https://{self.domain}/api/v1/partners/{partner_id}/"
        responded_partner = self._get(url, partner_api=True).json()
        return json_to_model(Partner, responded_partner)

    def get_partners_by_fields(self, **kwargs) -> List[Partner]:
        url = f"https://{self.domain}/api/v1/partners/"
        response = self._get(url, params=kwargs, partner_api=True)
        responded_partners = response.json()
        if not responded_partners:
            raise PartnerNotFoundError(HTTPError(response=response, request=response.request))

        return json_list_to_model_list(Partner, responded_partners)

    # CAUTION: This should only be used if you know what you're doing
    def put_partner(self, **kwargs):
        partner_name = kwargs.get('name')
        if not partner_name:
            raise PartnerNotFoundError()

        url = f"https://{self.domain}/api/v1/partners/{partner_name}/"
        return self._put(url, kwargs)

    def submit_pairs(self, payload):
        """Send the payload as a bunch of pairs to the Identifier Mapper by
        sending a POST to the Pairs API"""
        url = f"https://{self.domain}/api/v1/pairs/"
        response = requests.post(url, headers=self._headers(), json=payload)

        try:
            response.raise_for_status()
        except requests.HTTPError as http_error:
            raise IdentifierMapperError(http_error)

    def delete_pair(self, guid):
        url = f"https://{self.domain}/api/v1/pairs/{guid}"
        headers = {
            'Authorization': f'Token {self.token}'
        }

        response = requests.delete(url, headers=headers)

        try:
            response.raise_for_status()
        except requests.HTTPError as http_error:
            if http_error.response.status_code == 404:
                pass
            raise IdentifierMapperError(http_error)

    def get_or_create_uuid(self, key: str) -> str:
        """Send a GET request to the id mapper uuid route and receive a UUID string"""
        url = f"https://{self.domain}/api/v1/uuid/{key}/"
        return self._get(url).json()

    def get_domains(self) -> List[Domain]:
        """
        Send a GET request to the id mapper domain route and receive a list of all domain objects
        """
        url = f"https://{self.domain}/api/v1/domains/"
        domain_list = self._get(url).json()
        return json_list_to_model_list(Domain, domain_list)

    def get_domains_by_fields(self, **kwargs) -> List[Domain]:
        """
        Send a GET request to the id mapper domain route with filter and receive a filtered list of domain objects
        """
        url = f"https://{self.domain}/api/v1/domains/"
        domain_list = self._get(url, params=kwargs).json()
        return json_list_to_model_list(Domain, domain_list)

    def get_domain(self, domain_name) -> Domain:
        """
        Send a GET request to the id mapper domain route and receive a domain object
        """
        url = f"https://{self.domain}/api/v1/domains/{domain_name}/"
        domain_dict = self._get(url).json()
        return json_to_model(Domain, domain_dict)

    def post_domain(self, payload):
        """
        Send a POST request to the id mapper domain route and create a domain object and receive a 200
        """
        url = f"https://{self.domain}/api/v1/domains/"
        return self._post(url, payload)

    def put_domain(self, domain_name, payload):
        """
        Send a PUT request to the id mapper Domain route and update a domain object and receive a 200
        """
        url = f"https://{self.domain}/api/v1/domains/{domain_name}/"
        return self._put(url, payload)

    @staticmethod
    def generate_linker_key(partner_name: str, link_type: str, id: str):
        """
        link_types: user, class, course, academicSession, enrollment, result,
                    currentLineItem, finalLineItem, courseProgressLineItem
        """
        return f'{partner_name}-{link_type}-{id}'

    @staticmethod
    def generate_strongmind_guid(service, partner_name, id):
        return f'strongmind.guid://{service}/{partner_name}/{id}'


def json_to_model(model, json: Dict[str, Any]):
    model_fields = {field.name: field.type for field in fields(model)}
    attributes = {attribute: value for attribute, value in json.items() if attribute in model_fields}
    return model(**attributes)


def json_list_to_model_list(model, json_list: List[Dict[str, Any]]):
    return [json_to_model(model, json) for json in json_list]


def handle_http_error(http_error, partner_api: bool = False):
    if http_error.response.status_code == 404:
        if partner_api:
            raise PartnerNotFoundError(http_error)
        else:
            raise PairNotFoundError(http_error)
    raise IdentifierMapperError(http_error)
