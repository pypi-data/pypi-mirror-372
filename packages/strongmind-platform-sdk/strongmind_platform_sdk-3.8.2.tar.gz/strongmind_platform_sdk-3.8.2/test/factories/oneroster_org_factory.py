from factory import Faker, LazyAttribute, Factory, DictFactory, SubFactory, Dict
from oneroster_client import OrgType, SingleOrgType


class OrgMetadataFactory(DictFactory):
    canvas_domain = Faker('domain_name')
    canvas_account = Faker('random_int')
    canvas_account_uuid = Faker('uuid4')

    powerschool_domain = Faker('domain_name')
    powerschool_dcid = Faker('random_int')
    powerschool_school_number = Faker('random_int')

    clever_district_id = Faker('hexify', text='^' * 24)
    clever_school_id = Faker('hexify', text='^' * 24)

    fuji_id = Faker('random_int')
    default_grade = Faker('random_int')
    group_label = Faker('word')

    roster_source = Faker('word', ext_word_list=['powerschool', 'canvas', 'clever'])


class OneRosterOrgFactory(Factory):
    class Meta:
        model = OrgType

    # Required
    sourced_id = Faker('uuid4')
    status = Faker('word', ext_word_list=['active', 'tobedeleted'])
    date_last_modified = Faker('iso8601')
    metadata = Dict({"StrongMind": SubFactory(OrgMetadataFactory)})
    name = Faker('word')
    type = Faker('word', ext_word_list=['department', 'school', 'district', 'local', 'state', 'national'])
    identifier = LazyAttribute(lambda o: o.name)

    # Not required
    parent = None
    children = None


class OneRosterSingleOrgFactory(Factory):
    class Meta:
        model = SingleOrgType

    org = SubFactory(OneRosterOrgFactory)
