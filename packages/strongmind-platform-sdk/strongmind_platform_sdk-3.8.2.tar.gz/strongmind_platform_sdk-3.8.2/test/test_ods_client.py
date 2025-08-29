import unittest
import uuid

import requests
from faker import Faker
from mockito import when, mock, unstub, verifyStubbedInvocationsAreUsed, verify
from requests import HTTPError

from platform_sdk.clients.identity_client import IdentityServerClient
from platform_sdk.clients.ods_client import OneRosterDataStoreClient
from test.helpers.test_helpers import create_http_error

fake = Faker()


def setup_post():
    response = mock({'status_code': 200, 'text': 'Ok'})
    when(requests).post(...).thenReturn(response)

def setup_put():
    response = mock({'status_code': 200, 'text': 'Ok'})
    when(requests).put(...).thenReturn(response)

class TestCacheClient(unittest.TestCase):
    def tearDown(self) -> None:
        unstub()

    def setUp(self) -> None:
        self.key = fake.word()
        self.base_url = f"https://{fake.domain_name()}"
        self.bearer_token = fake.sha256()
        self.identity_client = mock(IdentityServerClient)
        when(self.identity_client).get_token().thenReturn(self.bearer_token)
        self.one_roster_central_client = OneRosterDataStoreClient(base_url=self.base_url,
                                                                  identity_client=self.identity_client)
        self.one_roster_legacy_client = OneRosterDataStoreClient(base_url=self.base_url, key=self.key)
        setup_post()

    def test_posts_enrollments_with_one_roster_legacy_client(self):
        """
        Client submits via HTTP with the x-functions-key header
        """
        # Arrange
        url = f"{self.base_url}/enrollments"
        payload = {fake.domain_word(): fake.random_int()}

        # Act
        self.one_roster_legacy_client.post_enrollment(payload)

        # Assert
        verify(requests).post(url, headers={'x-functions-key': self.key}, json=payload)

    def test_posts_enrollments_with_one_roster_central_client(self):
        """
        Client submits via HTTP with Bearer token auth
        """
        # Arrange
        url = f"{self.base_url}/enrollments"
        payload = {fake.domain_word(): fake.random_int()}

        # Act
        self.one_roster_central_client.post_enrollment(payload)

        # Assert
        verifyStubbedInvocationsAreUsed()
        verify(requests).post(url, headers={'Authorization': self.bearer_token}, json=payload)

    def test_posts_user_with_one_roster_legacy_client(self):
        """
        Client submits via HTTP with the x-functions-key header
        """
        # Arrange
        url = f"{self.base_url}/users"
        payload = {fake.domain_word(): fake.random_int()}

        # Act
        self.one_roster_legacy_client.post_user(payload)

        # Assert
        verify(requests).post(url, headers={'x-functions-key': self.key}, json=payload)

    def test_posts_user_with_one_roster_central_client(self):
        """
        Client submits via HTTP with Bearer token auth
        """
        # Arrange
        url = f"{self.base_url}/users"
        payload = {fake.domain_word(): fake.random_int()}

        # Act
        self.one_roster_central_client.post_user(payload)

        # Assert
        verifyStubbedInvocationsAreUsed()
        verify(requests).post(url, headers={'Authorization': self.bearer_token}, json=payload)

    def test_posts_demographic_with_one_roster_legacy_client(self):
        """
        Client submits via HTTP with the x-functions-key header
        """
        # Arrange
        url = f"{self.base_url}/demographics"
        payload = {fake.domain_word(): fake.random_int()}

        # Act
        self.one_roster_legacy_client.post_demographic(payload)

        # Assert
        verify(requests).post(url, headers={'x-functions-key': self.key}, json=payload)

    def test_posts_demographics_with_one_roster_central_client(self):
        """
         Client submits via HTTP with Bearer token auth
         """
        # Arrange
        url = f"{self.base_url}/demographics"
        payload = {fake.domain_word(): fake.random_int()}

        # Act
        self.one_roster_central_client.post_demographic(payload)

        # Assert
        verifyStubbedInvocationsAreUsed()
        verify(requests).post(url, headers={'Authorization': self.bearer_token}, json=payload)

    def test_deletes_with_one_roster_legacy_client(self):
        """
        Client deletes via HTTP with the right authentication header
        """
        # Arrange
        response = mock({'status_code': 204, 'text': ''})
        the_id = str(uuid.uuid4())
        url = f"{self.base_url}/enrollments/{the_id}"
        when(requests).delete(...).thenReturn(response)

        # Act
        self.one_roster_legacy_client.delete_enrollment(the_id)

        # Assert
        verify(requests).delete(url, headers={'x-functions-key': self.key})

    def test_deletes_with_one_roster_central_client(self):
        """
         Client submits via HTTP with Bearer token auth
         """
        # Arrange
        response = mock({'status_code': 204, 'text': ''})
        the_id = str(uuid.uuid4())
        url = f"{self.base_url}/enrollments/{the_id}"
        when(requests).delete(...).thenReturn(response)

        # Act
        self.one_roster_central_client.delete_enrollment(the_id)

        # Assert
        verify(requests).delete(url, headers={'Authorization': self.bearer_token})

    def test_posts_class_with_one_roster_legacy_client(self):
        """
        Client submits via HTTP with the x-functions-key header
        """
        # Arrange
        url = f"{self.base_url}/classes"
        payload = {fake.domain_word(): fake.random_int()}

        # Act
        self.one_roster_legacy_client.post_class(payload)
        verify(requests).post(url, headers={'x-functions-key': self.key}, json=payload)

    def test_posts_class_with_one_roster_central_client(self):
        """
        Client submits via HTTP with Bearer token auth
        """
        # Arrange
        url = f"{self.base_url}/classes"
        payload = {fake.domain_word(): fake.random_int()}

        # Act
        self.one_roster_central_client.post_class(payload)

        # Assert
        verifyStubbedInvocationsAreUsed()
        verify(requests).post(url, headers={'Authorization': self.bearer_token}, json=payload)

    def test_posts_courses_with_one_roster_legacy_client(self):
        """
        Client submits courses via HTTP with the x-functions-key header
        """
        # Arrange
        url = f"{self.base_url}/courses"
        payload = {fake.domain_word(): fake.random_int()}

        # Act
        self.one_roster_legacy_client.post_course(payload)

        # Assert
        verify(requests).post(url, headers={'x-functions-key': self.key}, json=payload)

    def test_posts_courses_with_one_roster_central_client(self):
        """
        Client submits courses via HTTP with Bearer token auth
        """
        # Arrange
        url = f"{self.base_url}/courses"
        payload = {fake.domain_word(): fake.random_int()}

        # Act
        self.one_roster_central_client.post_course(payload)

        # Assert
        verifyStubbedInvocationsAreUsed()
        verify(requests).post(url, headers={'Authorization': self.bearer_token}, json=payload)

    def test_posts_academic_sessions_with_one_roster_legacy_client(self):
        """
        Client submits courses via HTTP with the x-functions-key header
        """
        # Arrange
        url = f"{self.base_url}/academicSessions"
        payload = {fake.domain_word(): fake.random_int()}

        # Act
        self.one_roster_legacy_client.post_academic_session(payload)

        # Assert
        verify(requests).post(url, headers={'x-functions-key': self.key}, json=payload)

    def test_posts_academic_sessions_with_one_roster_central_client(self):
        """
        Client submits courses via HTTP with Bearer token auth
        """
        # Arrange
        url = f"{self.base_url}/academicSessions"
        payload = {fake.domain_word(): fake.random_int()}

        # Act
        self.one_roster_central_client.post_academic_session(payload)

        # Assert
        verifyStubbedInvocationsAreUsed()
        verify(requests).post(url, headers={'Authorization': self.bearer_token}, json=payload)

    def test_puts_results_with_one_roster_legacy_client(self):
        """
        Client submits courses via HTTP with the x-functions-key header
        """
        # Arrange
        setup_put()
        url = f"{self.base_url}/results"
        payload = {fake.domain_word(): fake.random_int()}

        # Act
        self.one_roster_legacy_client.put_result(payload)

        # Assert
        verify(requests).put(url, headers={'x-functions-key': self.key}, json=payload)

    def test_puts_results_with_one_roster_central_client(self):
        """
        Client submits courses via HTTP with Bearer token auth
        """
        # Arrange
        setup_put()
        url = f"{self.base_url}/results"
        payload = {fake.domain_word(): fake.random_int()}

        # Act
        self.one_roster_central_client.put_result(payload)

        # Assert
        verify(requests).put(url, headers={'Authorization': self.bearer_token}, json=payload)

    def test_posts_orgs_with_one_roster_legacy_client(self):
        """
        Client submits orgs via HTTP with the x-functions-key header
        """
        # Arrange
        url = f"{self.base_url}/orgs"
        payload = {fake.domain_word(): fake.random_int()}

        # Act
        self.one_roster_legacy_client.post_org(payload)

        # Assert
        verify(requests).post(url, headers={'x-functions-key': self.key}, json=payload)

    def test_posts_orgs_with_one_roster_central_client(self):
        """
        Client submits orgs via HTTP with Bearer token auth
        """
        # Arrange
        url = f"{self.base_url}/orgs"
        payload = {fake.domain_word(): fake.random_int()}

        # Act
        self.one_roster_central_client.post_org(payload)

        # Assert
        verifyStubbedInvocationsAreUsed()
        verify(requests).post(url, headers={'Authorization': self.bearer_token}, json=payload)

    def test_adds_dependency_name_to_post_exception_with_one_roster_legacy_client(self):
        """
        Legacy client raises an exception with the dependency name "OneRosterDataStore" when a post fails
        """
        # Arrange
        the_id = str(uuid.uuid4())
        url = f"{self.base_url}/enrollments/{the_id}"
        error = create_http_error(status_code=500, error_message='Internal Server Error', url=url, method='POST')
        payload = {fake.domain_word(): fake.random_int()}
        when(requests).post(...).thenReturn(error.response)
        when(error.response).raise_for_status().thenRaise(error)

        # Act
        with self.assertRaises(HTTPError) as context:
            self.one_roster_legacy_client.post_org(payload)

        # Assert
        self.assertEqual('OneRosterDataStore', context.exception.dependency_name)

    def test_adds_dependency_name_to_post_exception_with_one_roster_central_client(self):
        """
        Central client raises an exception with the dependency name "OneRosterDataStore" when a post
        """
        # Arrange
        the_id = str(uuid.uuid4())
        url = f"{self.base_url}/enrollments/{the_id}"
        error = create_http_error(status_code=500, error_message='Internal Server Error', url=url, method='POST')
        payload = {fake.domain_word(): fake.random_int()}
        when(requests).post(...).thenReturn(error.response)
        when(error.response).raise_for_status().thenRaise(error)

        # Act
        with self.assertRaises(HTTPError) as context:
            self.one_roster_central_client.post_org(payload)

        # Assert
        self.assertEqual('OneRosterDataStore', context.exception.dependency_name)

    def test_adds_dependency_name_to_delete_exception_with_one_roster_legacy_client(self):
        """
        Legacy client raises an exception with the dependency name "OneRosterDataStore" when a delete fails
        """
        # Arrange
        the_id = str(uuid.uuid4())
        url = f"{self.base_url}/enrollments/{the_id}"
        error = create_http_error(status_code=500, error_message='Internal Server Error', url=url, method='DELETE')
        when(requests).delete(...).thenReturn(error.response)
        when(error.response).raise_for_status().thenRaise(error)

        # Act
        with self.assertRaises(HTTPError) as context:
            self.one_roster_legacy_client.delete_enrollment(the_id)

        # Assert
        self.assertEqual('OneRosterDataStore', context.exception.dependency_name)

    def test_adds_dependency_name_to_delete_exception_with_one_roster_central_client(self):
        """
        Central client raises an exception with the dependency name "OneRosterDataStore" when a delete fails
        """
        # Arrange
        the_id = str(uuid.uuid4())
        url = f"{self.base_url}/enrollments/{the_id}"
        error = create_http_error(status_code=500, error_message='Internal Server Error', url=url, method='DELETE')
        when(requests).delete(...).thenReturn(error.response)
        when(error.response).raise_for_status().thenRaise(error)

        # Act
        with self.assertRaises(HTTPError) as context:
            self.one_roster_central_client.delete_enrollment(the_id)

        # Assert
        self.assertEqual('OneRosterDataStore', context.exception.dependency_name)

    def test_puts_line_items_with_one_roster_central_client(self):
        """
        Client submits line item via HTTP with Bearer token auth
        """
        # Arrange
        setup_put()
        url = f"{self.base_url}/lineItems"
        payload = {fake.domain_word(): fake.random_int()}

        # Act
        self.one_roster_central_client.put_line_item(payload)

        # Assert
        verify(requests).put(url, headers={'Authorization': self.bearer_token}, json=payload)

    def test_puts_result_with_sourced_id_with_one_roster_legacy_client(self):
        """
        Client submits result with sourced ID via HTTP with the x-functions-key header
        """
        # Arrange
        setup_put()
        sourced_id = str(uuid.uuid4())
        url = f"{self.base_url}/results/{sourced_id}"
        payload = {fake.domain_word(): fake.random_int()}

        # Act
        self.one_roster_legacy_client.put_result_with_sourced_id(payload, sourced_id)

        # Assert
        verify(requests).put(url, headers={'x-functions-key': self.key}, json=payload)

    def test_puts_result_with_sourced_id_with_one_roster_central_client(self):
        """
        Client submits result with sourced ID via HTTP with Bearer token auth
        """
        # Arrange
        setup_put()
        sourced_id = str(uuid.uuid4())
        url = f"{self.base_url}/results/{sourced_id}"
        payload = {fake.domain_word(): fake.random_int()}

        # Act
        self.one_roster_central_client.put_result_with_sourced_id(payload, sourced_id)

        # Assert
        verify(requests).put(url, headers={'Authorization': self.bearer_token}, json=payload)

    def test_puts_line_item_with_sourced_id_with_one_roster_legacy_client(self):
        """
        Client submits line item with sourced ID via HTTP with the x-functions-key header
        """
        # Arrange
        setup_put()
        sourced_id = str(uuid.uuid4())
        url = f"{self.base_url}/lineItems/{sourced_id}"
        payload = {fake.domain_word(): fake.random_int()}

        # Act
        self.one_roster_legacy_client.put_line_item_with_sourced_id(payload, sourced_id)

        # Assert
        verify(requests).put(url, headers={'x-functions-key': self.key}, json=payload)

    def test_puts_line_item_with_sourced_id_with_one_roster_central_client(self):
        """
        Client submits line item with sourced ID via HTTP with Bearer token auth
        """
        # Arrange
        setup_put()
        sourced_id = str(uuid.uuid4())
        url = f"{self.base_url}/lineItems/{sourced_id}"
        payload = {fake.domain_word(): fake.random_int()}

        # Act
        self.one_roster_central_client.put_line_item_with_sourced_id(payload, sourced_id)

        # Assert
        verify(requests).put(url, headers={'Authorization': self.bearer_token}, json=payload)
