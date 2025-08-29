import logging

from oneroster_client import EnrollmentsManagementApi, ClassesManagementApi, AcademicSessionsManagementApi, \
    LineItemsManagementApi, ResultsManagementApi, UsersManagementApi, CoursesManagementApi, SingleEnrollmentType, \
    SingleUserType, SingleClassType, SingleCourseType, OrgsManagementApi, SingleOrgType, SingleAcademicSessionType, \
    SingleLineItemType, SingleResultType
from requests import HTTPError

from platform_sdk.clients import oneroster_authentication


def get_oneroster_object(api_fn, sourced_id, oneroster_type, raise_on_404=False):
    """
    Calls the oneroster function passed to it
    handles 404's by logging it and returning None
    """
    try:
        response = api_fn(sourced_id)
        return response
    except HTTPError as e:
        if e.response.status_code == 404:
            logging.warning(f"OneRoster {oneroster_type} was not found for: {sourced_id}")
            if raise_on_404:
                raise e
        else:
            raise e


class OneRosterClient:
    def __init__(self,
                 base_url: str,
                 identity_base_url: str,
                 identity_client_id: str,
                 identity_client_secret: str,
                 enrollments: EnrollmentsManagementApi = None,
                 classes: ClassesManagementApi = None,
                 academic_sessions: AcademicSessionsManagementApi = None,
                 line_items: LineItemsManagementApi = None,
                 results: ResultsManagementApi = None,
                 users: UsersManagementApi = None,
                 courses: CoursesManagementApi = None,
                 orgs: OrgsManagementApi = None,
                 raise_on_404=False):
        base_client = oneroster_authentication.get_authenticated_oneroster_client(
            base_url=base_url,
            identity_base_url=identity_base_url,
            client_id=identity_client_id,
            client_secret=identity_client_secret)

        self.enrollments = enrollments if enrollments else EnrollmentsManagementApi(base_client)
        self.classes = classes if classes else ClassesManagementApi(base_client)
        self.academic_sessions = academic_sessions if academic_sessions else AcademicSessionsManagementApi(base_client)
        self.line_items = line_items if line_items else LineItemsManagementApi(base_client)
        self.results = results if results else ResultsManagementApi(base_client)
        self.users = users if users else UsersManagementApi(base_client)
        self.courses = courses if courses else CoursesManagementApi(base_client)
        self.orgs = orgs if orgs else OrgsManagementApi(base_client)
        self.raise_on_404 = raise_on_404

    def get_enrollment_with_parents(self, enrollment_sourced_id: str) \
            -> SingleEnrollmentType or None:
        enrollment: SingleEnrollmentType = self.get_enrollment(enrollment_sourced_id)
        if not enrollment:
            return

        user: SingleUserType = self.get_user(enrollment.enrollment.user.sourced_id)
        if not user:
            return

        class_: SingleClassType = self.get_class(enrollment.enrollment._class.sourced_id)
        if not class_:
            return

        org: SingleOrgType = self.get_org(enrollment.enrollment.school.sourced_id)
        if not org:
            return

        enrollment.enrollment.user = user.user
        enrollment.enrollment._class = class_._class
        enrollment.enrollment.org = org.org
        return enrollment

    def get_enrollment_with_parents_and_course(self, enrollment_sourced_id: str) \
            -> SingleEnrollmentType or None:
        enrollment = self.get_enrollment_with_parents(enrollment_sourced_id)
        if not enrollment:
            return

        course: SingleCourseType = self.get_course(enrollment.enrollment._class.course.sourced_id)
        if not course:
            return

        enrollment.enrollment._class.course = course.course
        return enrollment

    def get_class_with_parents(self, class_sourced_id: str) \
            -> SingleClassType or None:
        class_: SingleClassType = self.get_class(class_sourced_id)
        if not class_:
            return

        course: SingleCourseType = self.get_course(class_._class.course.sourced_id)
        if not course:
            return

        org: SingleOrgType = self.get_org(class_._class.school.sourced_id)
        if not org:
            return

        academic_session: SingleAcademicSessionType = self.get_academic_session(class_._class.terms[0].sourced_id)
        if not academic_session:
            return

        class_._class.course = course.course
        class_._class.school = org.org
        class_._class.terms[0] = academic_session.academic_session
        return class_

    def get_one_roster_object(self, api_fn, sourced_id, oneroster_type):
        return get_oneroster_object(api_fn, sourced_id, oneroster_type, raise_on_404=self.raise_on_404)

    def get_enrollment(self, enrollment_sourced_id: str) -> SingleEnrollmentType or None:
        return self.get_one_roster_object(self.enrollments.get_enrollment,
                                    enrollment_sourced_id,
                                    'enrollment')

    def get_user(self, user_sourced_id: str) -> SingleUserType or None:
        return self.get_one_roster_object(self.users.get_user,
                                    user_sourced_id,
                                    'user')

    def get_class(self, class_sourced_id: str) -> SingleClassType or None:
        return self.get_one_roster_object(self.classes.get_class,
                                    class_sourced_id,
                                    'class')

    def get_course(self, course_sourced_id: str) -> SingleCourseType or None:
        return self.get_one_roster_object(self.courses.get_course,
                                    course_sourced_id,
                                    'course')

    def get_academic_session(self, academic_session_sourced_id: str) -> SingleAcademicSessionType or None:
        return self.get_one_roster_object(self.academic_sessions.get_academic_session,
                                    academic_session_sourced_id,
                                    'academic session')

    def get_line_item(self, line_item_sourced_id: str) -> SingleLineItemType or None:
        return self.get_one_roster_object(self.line_items.get_line_item,
                                    line_item_sourced_id,
                                    'line item')

    def get_result(self, result_sourced_id: str) -> SingleResultType or None:
        return self.get_one_roster_object(self.results.get_result,
                                    result_sourced_id,
                                    'result')

    def get_org(self, org_sourced_id: str) -> SingleOrgType or None:
        return self.get_one_roster_object(self.orgs.get_org,
                                    org_sourced_id,
                                    'org')
