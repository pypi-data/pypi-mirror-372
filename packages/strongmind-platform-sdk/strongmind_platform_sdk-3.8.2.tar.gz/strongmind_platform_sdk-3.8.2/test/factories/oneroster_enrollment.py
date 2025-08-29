from factory import Faker, LazyAttribute, Factory, SubFactory, List
from oneroster_client import SingleEnrollmentType, EnrollmentsType
from oneroster_client.models import EnrollmentType

from test.factories.oneroster_guidref import OneRosterGuidRefFactory


class OneRosterEnrollmentFactory(Factory):
    class Meta:
        model = EnrollmentType
        exclude = ('base_url')

    base_url = 'https://devapi.platform.strongmind.com/ims/oneroster/v1p1/'

    sourced_id = Faker('uuid4')
    status = Faker('word', ext_word_list=['active', 'tobedeleted'])
    date_last_modified = Faker('iso8601')
    metadata = None
    user = SubFactory(OneRosterGuidRefFactory,
                      href=LazyAttribute(lambda o: f'{o.factory_parent.base_url}users/{o.sourced_id}'),
                      sourced_id=Faker('uuid4'),
                      type='user'
                      )
    _class = SubFactory(OneRosterGuidRefFactory,
                        href=LazyAttribute(lambda o: f'{o.factory_parent.base_url}classes/{o.sourced_id}'),
                        sourced_id=Faker('uuid4'),
                        type='class'
                        )
    school = SubFactory(OneRosterGuidRefFactory,
                        href=LazyAttribute(lambda o: f'{o.factory_parent.base_url}orgs/{o.sourced_id}'),
                        sourced_id=Faker('uuid4'),
                        type='org'
                        )
    role = Faker('word', ext_word_list=['student'])
    primary = Faker('word', ext_word_list=['true', 'false'])
    begin_date = Faker('iso8601')
    end_date = Faker('iso8601')


class OneRosterSingleEnrollmentFactory(Factory):
    class Meta:
        model = SingleEnrollmentType

    enrollment = SubFactory(OneRosterEnrollmentFactory)


class OneRosterEnrollmentsFactory(Factory):
    class Meta:
        model = EnrollmentsType

    enrollments = List([
        SubFactory(OneRosterEnrollmentFactory),
        SubFactory(OneRosterEnrollmentFactory)
    ])
