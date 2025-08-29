import factory

from platform_sdk.models.partner import Partner
from test.factories.standalone_partner import StandalonePartnerFactory


class PartnerFactory(StandalonePartnerFactory):
    class Meta:
        model = Partner

    name = factory.Faker('word')
    powerschool_domain = factory.Faker('domain_name')
    powerschool_dcid = factory.Faker('random_int')
    powerschool_school_number = factory.Faker('random_int')
    fuji_id = factory.Faker('random_int')
    default_grade = factory.Faker('random_element', elements=['06', '07', '08', '09', '10', '11', '12'])
    canvas_authentication_provider_type = factory.Faker('random_element', elements=['openid_connect', 'cas', ''])
