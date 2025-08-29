from factory import List, Faker, LazyAttribute, Factory, SubFactory
from oneroster_client import SingleClassType
from oneroster_client.models import ClassType

from test.factories.oneroster_guidref import OneRosterGuidRefFactory


class OneRosterClassFactory(Factory):
    class Meta:
        model = ClassType
        exclude = 'base_url'

    base_url = 'https://devapi.platform.strongmind.com/ims/oneroster/v1p1/'

    sourced_id = Faker('uuid4')
    status = Faker('word', ext_word_list=['active', 'tobedeleted'])
    date_last_modified = Faker('iso8601')
    metadata = None
    title = Faker('word')
    class_code = Faker('word')
    class_type = Faker('word', ext_word_list=['homeroom', 'scheduled'])
    location = Faker('word')
    grades = List([
        Faker('word',
              ext_word_list=['IT', 'PR', 'PK', 'TK', 'KG', '01', '02', '03', '04', '05', '06', '07', '08', '09',
                             '10',
                             '11', '12', '13', 'PS', 'UG', 'Other'])
    ])
    subjects = List([
        Faker('word'),
        Faker('word'),
        Faker('word'),
    ])

    course = SubFactory(OneRosterGuidRefFactory,
                        href=LazyAttribute(lambda o: f'{o.factory_parent.base_url}courses/{o.sourced_id}'),
                        sourced_id=Faker('uuid4'),
                        type='course'
                        )
    school = SubFactory(OneRosterGuidRefFactory,
                        href=LazyAttribute(lambda o: f'{o.factory_parent.base_url}orgs/{o.sourced_id}'),
                        sourced_id=Faker('uuid4'),
                        type='org'
                        )
    terms = List([
        SubFactory(OneRosterGuidRefFactory,
                   href=LazyAttribute(lambda o: f'{o.factory_parent.factory_parent.base_url}terms/{o.sourced_id}'),
                   sourced_id=Faker('uuid4'),
                   type='term'
                   ),
    ])

    subject_codes = List([
        Faker('random_int'),
        Faker('random_int'),
        Faker('random_int'),
    ])

    periods = List([
        Faker('random_int'),
        Faker('random_int'),
        Faker('random_int'),
    ])

    resources = List([
        SubFactory(OneRosterGuidRefFactory,
                   href=LazyAttribute(lambda o: f'{o.factory_parent.factory_parent.base_url}resources/{o.sourced_id}'),
                   sourced_id=Faker('uuid4'),
                   type='resource'
                   )
    ])


class OneRosterSingleClassFactory(Factory):
    class Meta:
        model = SingleClassType

    _class = SubFactory(OneRosterClassFactory)
