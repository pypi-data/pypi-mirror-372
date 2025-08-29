from factory import Factory, Faker
from oneroster_client.models.user_id_type import UserIdType


class OneRosterUserIdFactory(Factory):
    class Meta:
        model = UserIdType

    type = Faker('word')
    identifier = Faker('uuid4')
