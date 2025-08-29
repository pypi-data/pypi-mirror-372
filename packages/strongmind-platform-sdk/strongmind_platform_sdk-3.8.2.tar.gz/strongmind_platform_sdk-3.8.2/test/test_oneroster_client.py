import copy
import logging
import unittest

import pytest
from expects import *
from faker import Faker
from mockito import unstub, patch, mock, when, verify
from oneroster_client import EnrollmentsManagementApi, ClassesManagementApi, AcademicSessionsManagementApi, \
    LineItemsManagementApi, ResultsManagementApi, UsersManagementApi, CoursesManagementApi, OrgsManagementApi
from requests import HTTPError, Response

from platform_sdk.clients import oneroster_authentication
from platform_sdk.clients.oneroster_client import OneRosterClient, get_oneroster_object
from test.factories.oneroster_academic_session import OneRosterAcademicSessionFactory, \
    OneRosterSingleAcademicSessionFactory
from test.factories.oneroster_class import OneRosterClassFactory, OneRosterSingleClassFactory
from test.factories.oneroster_course import OneRosterCourseFactory, OneRosterSingleCourseFactory
from test.factories.oneroster_enrollment import OneRosterSingleEnrollmentFactory, OneRosterEnrollmentFactory
from test.factories.oneroster_lineitem import OneRosterLineItemFactory, OneRosterSingleLineItemFactory
from test.factories.oneroster_org_factory import OneRosterSingleOrgFactory, OneRosterOrgFactory
from test.factories.oneroster_result import OneRosterResultFactory, OneRosterSingleResultFactory
from test.factories.oneroster_user import OneRosterUserFactory, OneRosterSingleUserFactory

fake = Faker()


class TestOneRosterClient(unittest.TestCase):
    def setUp(self) -> None:
        self.setup_mocks()
        self.setup_data()

    def setup_mocks(self):
        self.enrollments_api = mock(EnrollmentsManagementApi)
        self.classes_api = mock(ClassesManagementApi)
        self.academic_sessions_api = mock(AcademicSessionsManagementApi)
        self.line_items_api = mock(LineItemsManagementApi)
        self.results_api = mock(ResultsManagementApi)
        self.users_api = mock(UsersManagementApi)
        self.courses_api = mock(CoursesManagementApi)
        self.orgs_api = mock(OrgsManagementApi)
        patch(oneroster_authentication.get_authenticated_oneroster_client,
              lambda base_url, identity_base_url, client_id, client_secret: None)
        self.target = OneRosterClient(base_url=fake.url(),
                                      identity_base_url=fake.url(),
                                      identity_client_id=fake.url(),
                                      identity_client_secret=fake.url(),
                                      enrollments=self.enrollments_api,
                                      classes=self.classes_api,
                                      academic_sessions=self.academic_sessions_api,
                                      line_items=self.line_items_api,
                                      results=self.results_api,
                                      users=self.users_api,
                                      courses=self.courses_api,
                                      orgs=self.orgs_api)

    def setup_data(self):
        self.enrollment_sourced_id = fake.uuid4()
        self.class_sourced_id = fake.uuid4()
        self.user_sourced_id = fake.uuid4()
        self.course_sourced_id = fake.uuid4()
        self.academic_session_sourced_id = fake.uuid4()
        self.line_item_sourced_id = fake.uuid4()
        self.result_sourced_id = fake.uuid4()
        self.org_sourced_id = fake.uuid4()

        self.enrollment = OneRosterEnrollmentFactory(sourced_id=self.enrollment_sourced_id,
                                                     user__sourced_id=self.user_sourced_id,
                                                     _class__sourced_id=self.class_sourced_id,
                                                     school__sourced_id=self.org_sourced_id,
                                                     )
        self.single_enrollment = OneRosterSingleEnrollmentFactory(enrollment=self.enrollment)

        self.user = OneRosterUserFactory(sourced_id=self.user_sourced_id,
                                         orgs__0__sourced_id=self.org_sourced_id)
        self.single_user = OneRosterSingleUserFactory(user=self.user)

        self.class_ = OneRosterClassFactory(sourced_id=self.class_sourced_id,
                                            course__sourced_id=self.course_sourced_id,
                                            school__sourced_id=self.org_sourced_id,
                                            terms__0__sourced_id=self.academic_session_sourced_id)
        self.single_class = OneRosterSingleClassFactory(_class=self.class_)

        self.course = OneRosterCourseFactory(sourced_id=self.course_sourced_id,
                                             school_year__sourced_id=self.academic_session_sourced_id,
                                             org__sourced_id=self.org_sourced_id)
        self.single_course = OneRosterSingleCourseFactory(course=self.course)

        self.academic_session = OneRosterAcademicSessionFactory(sourced_id=self.academic_session_sourced_id)
        self.single_academic_session = OneRosterSingleAcademicSessionFactory(academic_session=self.academic_session)

        self.line_item = OneRosterLineItemFactory(sourced_id=self.line_item_sourced_id,
                                                  _class__sourced_id=self.class_sourced_id,
                                                  grading_period__sourced_id=self.academic_session_sourced_id)
        self.single_line_item = OneRosterSingleLineItemFactory(line_item=self.line_item)

        self.result = OneRosterResultFactory(sourced_id=self.result_sourced_id,
                                             student__sourced_id=self.user_sourced_id)
        self.single_result = OneRosterSingleResultFactory(result=self.result)

        self.org = OneRosterOrgFactory(sourced_id=self.org_sourced_id)
        self.single_org = OneRosterSingleOrgFactory(org=self.org)

    def tearDown(self) -> None:
        unstub()

    def test_get_oneroster_object_404(self):
        """
        When a 404 is raised when trying to get a OneRoster object
        Then we should catch the 404, log, and return None
        """
        # Arrange
        response = mock(Response)
        response.status_code = 404
        http_error = HTTPError()
        http_error.response = response
        sourced_id = fake.uuid4()
        obj_type = 'object type'
        when(self.users_api).get_user(sourced_id).thenRaise(http_error)
        func = self.users_api.get_user
        when(logging).warning(...)

        # Act
        result = get_oneroster_object(func, sourced_id, obj_type)

        # Assert
        verify(self.users_api, times=1).get_user(sourced_id)
        verify(logging, times=1).warning(f"OneRoster {obj_type} was not found for: {sourced_id}")

    def test_get_oneroster_object_404_with_404_error_enabled(self):
        """
        When a 404 is raised when trying to get a OneRoster object
        Then we should catch the 404, log, and return None
        """
        # Arrange
        response = mock(Response)
        response.status_code = 404
        http_error = HTTPError()
        http_error.response = response
        sourced_id = fake.uuid4()
        obj_type = 'object type'
        when(self.users_api).get_user(sourced_id).thenRaise(http_error)
        func = self.users_api.get_user
        when(logging).warning(...)

        # Act
        with pytest.raises(HTTPError):
            result = get_oneroster_object(func, sourced_id, obj_type, raise_on_404=True)

            # Assert
            verify(self.users_api, times=1).get_user(sourced_id)
            verify(logging, times=1).warning(f"OneRoster {obj_type} was not found for: {sourced_id}")

    def test_get_enrollments_with_parents(self):
        """
        Given an enrollment sourced id
        Then we should return a OneRoster SingleEnrollmentType
        Where the user, class, and school/org types associated with the enrollment
        are on the enrollment object
        """
        # Arrange
        when(self.enrollments_api).get_enrollment(self.enrollment_sourced_id).thenReturn(self.single_enrollment)
        when(self.classes_api).get_class(self.class_sourced_id).thenReturn(self.single_class)
        when(self.users_api).get_user(self.user_sourced_id).thenReturn(self.single_user)
        when(self.orgs_api).get_org(self.org_sourced_id).thenReturn(self.single_org)
        expected_enrollment = copy.deepcopy(self.enrollment)
        expected_enrollment.user = self.user
        expected_enrollment._class = self.class_
        expected_enrollment.org = self.org

        # Act
        enrollment_result = self.target.get_enrollment_with_parents(self.enrollment_sourced_id)

        # Assert
        expect(enrollment_result.enrollment).to(equal(expected_enrollment))

    def test_get_enrollments_with_parents_and_course(self):
        """
        Given an enrollment sourced id
        Then we should return a OneRoster SingleEnrollmentType
        Where the user, class, and school/org types associated with the enrollment
        are on the enrollment object and the course associated with the class is on the
        class object nested within the enrollment object
        """
        # Arrange
        when(self.enrollments_api).get_enrollment(self.enrollment_sourced_id).thenReturn(self.single_enrollment)
        when(self.classes_api).get_class(self.class_sourced_id).thenReturn(self.single_class)
        when(self.users_api).get_user(self.user_sourced_id).thenReturn(self.single_user)
        when(self.orgs_api).get_org(self.org_sourced_id).thenReturn(self.single_org)
        when(self.courses_api).get_course(self.course_sourced_id).thenReturn(self.single_course)
        expected_enrollment = copy.deepcopy(self.enrollment)
        expected_enrollment.user = self.user
        expected_class = copy.deepcopy(self.class_)
        expected_class.course = self.course
        expected_enrollment._class = expected_class
        expected_enrollment.org = self.org

        # Act
        enrollment_result = self.target.get_enrollment_with_parents_and_course(self.enrollment_sourced_id)

        # Assert
        expect(enrollment_result.enrollment).to(equal(expected_enrollment))

    def test_get_class_with_parents(self):
        """
        Given a class sourced id
        Then we should return a OneRoster SingleClassType
        where the course, org, and academic session objects associated with the class
        are on the class object
        """
        # Arrange
        when(self.classes_api).get_class(self.class_sourced_id).thenReturn(self.single_class)
        when(self.courses_api).get_course(self.course_sourced_id).thenReturn(self.single_course)
        when(self.orgs_api).get_org(self.org_sourced_id).thenReturn(self.single_org)
        when(self.academic_sessions_api).get_academic_session(self.academic_session_sourced_id) \
            .thenReturn(self.single_academic_session)
        expected_class = copy.deepcopy(self.class_)
        expected_class.course = self.course
        expected_class.school = self.org
        expected_class.terms[0] = self.academic_session

        # Act
        class_result = self.target.get_class_with_parents(self.class_sourced_id)

        # Assert
        expect(class_result._class).to(equal(expected_class))
