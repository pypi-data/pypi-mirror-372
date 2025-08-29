from factory import Factory, Faker

from platform_sdk.models.domain import Domain


class DomainFactory(Factory):
    class Meta:
        model = Domain

    id = Faker('random_int')
    name = Faker('domain_name')
    key = Faker('word')
    secret = Faker('word')
    token = Faker('word')
    snap_token = Faker('word')
    partner = Faker('word')
    is_disabled = False
