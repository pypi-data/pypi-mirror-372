import requests
from requests.auth import HTTPBasicAuth


class JiraServiceManagementClient:
    def __init__(self, auth_api_key, auth_email, cloud_id, team_id):
        self.auth_api_key = auth_api_key
        self.auth_email = auth_email
        self.cloud_id = cloud_id
        self.team_id = team_id
        self.auth = HTTPBasicAuth(self.auth_email, self.auth_api_key)
        self.headers = { "Accept": "application/json" }


    def send_heartbeat(self, name):
        url = f"https://api.atlassian.com/jsm/ops/api/{self.cloud_id}/v1/teams/{self.team_id}/heartbeats/ping?name={name}"
        response = requests.get(url, headers=self.headers, auth=self.auth)
        response.raise_for_status()
        return response
