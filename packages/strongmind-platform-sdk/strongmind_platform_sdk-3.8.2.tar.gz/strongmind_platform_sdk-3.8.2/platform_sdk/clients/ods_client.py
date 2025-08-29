from typing import Dict

import requests

from platform_sdk.helpers.exception_logger import raise_for_status_with_dependency_name
from platform_sdk.shared.constants import ONEROSTER_DATA_STORE
from platform_sdk.shared.utilities import get_plural_oneroster_type, identity_server_client


class OneRosterDataStoreClient:
    def __init__(self, base_url: str, key=None, identity_client=None):
        self.base_url = base_url
        self.key = key
        if not self.key:
            self.identity_client = identity_client or identity_server_client()

    @property
    def headers(self):
        if self.key:
            return {
                'x-functions-key': self.key
            }

        return {
            'Authorization': self.identity_client.get_token()
        }

    def _post_data(self, data: Dict, data_type: str):
        url = f"{self.base_url}/{data_type}"
        response = requests.post(url, headers=self.headers, json=data)
        raise_for_status_with_dependency_name(response, ONEROSTER_DATA_STORE)

    def _put_data(self, data: Dict, data_type: str):
        url = f"{self.base_url}/{data_type}"
        response = requests.put(url, headers=self.headers, json=data)
        raise_for_status_with_dependency_name(response, ONEROSTER_DATA_STORE)

    def _put_data_with_id(self, data: Dict, data_type: str, sourced_id: str):
        """PUT data with sourcedId in the URL path (required by Azure Functions)"""
        url = f"{self.base_url}/{data_type}/{sourced_id}"
        response = requests.put(url, headers=self.headers, json=data)
        raise_for_status_with_dependency_name(response, ONEROSTER_DATA_STORE)

    def _delete(self, uuid: str, data_type: str):
        url = f"{self.base_url}/{data_type}/{uuid}"
        response = requests.delete(url, headers=self.headers)
        raise_for_status_with_dependency_name(response, ONEROSTER_DATA_STORE)

    def get_data_as_dict(self, sourced_id: str, data_type: str):
        url = f"{self.base_url}/{get_plural_oneroster_type(data_type)}/{sourced_id}"
        response = requests.get(url=url, headers=self.headers)
        raise_for_status_with_dependency_name(response, ONEROSTER_DATA_STORE)

        return response.json().get(data_type)

    def post_enrollment(self, enrollment: Dict):
        """Send the enrollment data to the cache by
        sending a POST to the OneRoster Cache API"""
        self._post_data(enrollment, "enrollments")

    def delete_enrollment(self, enrollment_id: str):
        """Soft delete the enrollment by
        sending a DELETE to the OneRoster Cache API"""
        self._delete(enrollment_id, "enrollments")

    def post_user(self, user: Dict):
        """Send the user data to the cache by
        sending a POST to the OneRoster Cache API"""
        self._post_data(user, "users")

    def delete_user(self, user_id: str):
        """Soft delete the enrollment by
        sending a DELETE to the OneRoster Cache API"""
        self._delete(user_id, "users")

    def post_demographic(self, demographic: Dict):
        """Send the demographic data to the cache by
        sending a POST to the OneRoster Cache API"""
        self._post_data(demographic, "demographics")

    def post_course(self, course: Dict):
        """Send the course data to the cache by
        sending a POST to the OneRoster Cache API"""
        self._post_data(course, "courses")

    def delete_course(self, course_id: str):
        """Soft delete the course by
        sending a DELETE to the OneRoster Cache API"""
        self._delete(course_id, "courses")

    def post_class(self, oneroster_class: Dict):
        """Send the class data to the cache by
        sending a POST to the OneRoster Cache API"""
        self._post_data(oneroster_class, "classes")

    def delete_class(self, class_id: str):
        """Soft delete the class by
        sending a DELETE to the OneRoster Cache API"""
        self._delete(class_id, "classes")

    def post_academic_session(self, data: Dict):
        """Send the course data to the cache by
        sending a POST to the OneRoster Cache API"""
        self._post_data(data, "academicSessions")

    def put_result(self, result: Dict):
        """Send the result data to the cache by
        sending a PUT to the OneRoster Cache API"""
        self._put_data(result, "results")

    def put_result_with_sourced_id(self, result: Dict, sourced_id: str):
        """Send the result data to the cache by
        sending a PUT to the OneRoster Cache API with sourcedId in URL path"""
        self._put_data_with_id(result, "results", sourced_id)

    def post_org(self, org: Dict):
        """Send the course data to the cache by
        sending a POST to the OneRoster Cache API"""
        self._post_data(org, "orgs")

    def put_line_item(self, data: Dict):
        """Send the line items data to the cache by
        sending a POST to the OneRoster Cache API"""
        self._put_data(data, "lineItems")

    def put_line_item_with_sourced_id(self, data: Dict, sourced_id: str):
        """Send the line items data to the cache by
        sending a PUT to the OneRoster Cache API with sourcedId in URL path"""
        self._put_data_with_id(data, "lineItems", sourced_id)
