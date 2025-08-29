from factory import Factory, Faker, LazyAttribute, SubFactory, List
from oneroster_client import UsersType
from oneroster_client.models.single_user_type import SingleUserType
from oneroster_client.models.user_type import UserType

from test.factories.oneroster_guidref import OneRosterGuidRefFactory
from test.factories.oneroster_user_id import OneRosterUserIdFactory


class OneRosterUserFactory(Factory):
    class Meta:
        model = UserType
        exclude = 'base_url', 'identity_id', 'canvas_user_id', 'org_sourced_id'

    # Excluded Variable
    org_sourced_id = Faker('uuid4')
    base_url = 'https://devapi.platform.strongmind.com/ims/oneroster/v1p1/'
    identity_id = Faker('uuid4')
    canvas_user_id = Faker('random_int')

    # Included Variable
    sourced_id = Faker('uuid4')
    status = Faker('word', ext_word_list=['active', 'tobedeleted'])
    date_last_modified = Faker('iso8601')
    metadata = None
    username = LazyAttribute(lambda o: f'{o.given_name}{o.family_name}')
    user_ids = List([
        SubFactory(OneRosterUserIdFactory,
                   type='canvas_user_id',
                   identifier=LazyAttribute(lambda o: o.factory_parent.factory_parent.canvas_user_id)
                   ),
        SubFactory(OneRosterUserIdFactory,
                   type='identity_id',
                   identifier=LazyAttribute(lambda o: o.factory_parent.factory_parent.identity_id)
                   ),
    ])
    enabled_user = Faker('word', ext_word_list=['True', 'False'])
    given_name = Faker('first_name')
    family_name = Faker('last_name')
    middle_name = Faker('first_name')
    role = Faker('word', ext_word_list=['administrator', 'aide', 'guardian', 'parent', 'proctor', 'relative', 'student',
                                        'teacher'])
    identifier = Faker('random_int')
    email = LazyAttribute(lambda o: f'{o.given_name}{o.family_name}@notarealboy.com')
    sms = Faker("msisdn")
    phone = Faker("msisdn")
    agents = List([
        SubFactory(OneRosterGuidRefFactory),
        SubFactory(OneRosterGuidRefFactory)
    ])
    orgs = List([
        SubFactory(OneRosterGuidRefFactory,
                   href=LazyAttribute(lambda
                                          o: f'{o.factory_parent.factory_parent.base_url}orgs/{o.factory_parent.factory_parent.org_sourced_id}'),
                   sourced_id=Faker('uuid4'),
                   type='org'
                   )
    ])
    grades = List([Faker('word',
                         ext_word_list=['IT', 'PR', 'PK', 'TK', 'KG', '01', '02', '03', '04', '05', '06', '07', '08',
                                        '09',
                                        '10', '11', '12', '13', 'PS', 'UG', 'Other'])])
    password = None


class OneRosterSingleUserFactory(Factory):
    class Meta:
        model = SingleUserType

    user = SubFactory(OneRosterUserFactory)


class OneRosterUsersFactory(Factory):
    class Meta:
        model = UsersType

    users = List([
        SubFactory(OneRosterUserFactory),
        SubFactory(OneRosterUserFactory)
    ])
