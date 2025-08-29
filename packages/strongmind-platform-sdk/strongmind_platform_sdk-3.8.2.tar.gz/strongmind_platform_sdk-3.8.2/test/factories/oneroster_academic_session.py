from factory import Factory, List, Faker, SubFactory, LazyAttribute
from oneroster_client.models import SingleAcademicSessionType, AcademicSessionType

from test.factories.oneroster_guidref import OneRosterGuidRefFactory


class OneRosterAcademicSessionFactory(Factory):
    class Meta:
        model = AcademicSessionType
        exclude = ('base_url')

    base_url = 'https://devapi.platform.strongmind.com/ims/oneroster/v1p1/'

    sourced_id = Faker('uuid4')
    status = 'active'
    date_last_modified = Faker('iso8601')
    metadata = None
    title = Faker('word')
    start_date = Faker('iso8601')
    end_date = Faker('iso8601')
    type = Faker('word', ext_word_list=['gradingPeriod', 'semester', 'schoolYear', 'term'])
    parent = SubFactory(OneRosterGuidRefFactory,
                        href=LazyAttribute(lambda o: f'{o.factory_parent.base_url}terms/{o.sourced_id}'),
                        sourced_id=Faker('uuid4'),
                        type='term')
    children = List([
        SubFactory(OneRosterGuidRefFactory,
                   href=LazyAttribute(lambda o: f'{o.factory_parent.factory_parent.base_url}terms/{o.sourced_id}'),
                   sourced_id=Faker('uuid4'),
                   type='term'),
    ])
    school_year = Faker('year')


class OneRosterSingleAcademicSessionFactory(Factory):
    class Meta:
        model = SingleAcademicSessionType

    academic_session = SubFactory(OneRosterAcademicSessionFactory)
