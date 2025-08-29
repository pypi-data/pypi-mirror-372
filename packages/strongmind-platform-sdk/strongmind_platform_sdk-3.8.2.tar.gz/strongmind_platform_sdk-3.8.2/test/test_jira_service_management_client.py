import unittest
import requests
from mockito import mock, unstub, verify, when, verifyStubbedInvocationsAreUsed
from faker import Faker
from requests import Response
from requests.auth import HTTPBasicAuth

from platform_sdk.clients.jira_service_management_client import JiraServiceManagementClient

fake = Faker()


class TestJiraServiceManagementClient(unittest.TestCase):
    def setUp(self):
        self.response = mock(Response)
        self.auth_api_key = fake.word()
        self.auth_email = fake.email()
        self.cloud_id = fake.uuid4()
        self.team_id = fake.uuid4()
        self.client = JiraServiceManagementClient(self.auth_api_key, self.auth_email, self.cloud_id, self.team_id)
        self.auth = HTTPBasicAuth(self.auth_email, self.auth_api_key)
        self.headers = {"Accept": "application/json"}

    def tearDown(self):
        unstub()

    def test_send_heartbeat(self):
        """
        Given we have a Jira Services key
        When we call 'send_heartbeat'
        Then the request should get made
        :return: response
        """
        # Arrange
        name = fake.word()
        url = f"https://api.atlassian.com/jsm/ops/api/{self.cloud_id}/v1/teams/{self.team_id}/heartbeats/ping?name={name}"
        when(self.response).raise_for_status(...)
        when(requests).get(url, headers=self.headers, auth=self.auth).thenReturn(self.response)
        # Act
        self.client.send_heartbeat(name)
        # Assert
        verify(requests, times=1).get(url, headers=self.headers, auth=self.auth)
        verifyStubbedInvocationsAreUsed()
