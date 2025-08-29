import factory

from platform_sdk.models.partner import Partner


class StandalonePartnerFactory(factory.Factory):
    class Meta:
        model = Partner

    id = factory.Faker('uuid4')
    name = factory.Faker('word')
    display_name = factory.Faker('word')
    canvas_domain = factory.Faker('domain_name')
    canvas_account = factory.Faker('random_int')
    powerschool_domain = None
    powerschool_dcid = None
    powerschool_school_number = None
    fuji_id = None
    default_grade = None
    canvas_account_uuid = factory.Faker('uuid4')
    clever_district_id = factory.Faker('uuid4')
    clever_school_id = factory.Faker('uuid4')
    group_label = factory.Faker('word')
    roster_source = factory.Faker('word', ext_word_list=['powerschool', 'canvas', 'clever'])
    feature_identity_emails = factory.Faker('boolean')
    canvas_authentication_provider_type = factory.Faker('word', ext_word_list=['openid_connect', 'cas', ''])
