from factory import Factory, Faker, DictFactory, SubFactory

from platform_sdk.models.user import User


class UserIDsFactory(DictFactory):
    Key1 = Faker("uuid4")
    Key2 = Faker("uuid4")


class UserFactory(Factory):
    class Meta:
        model = User

    Role = Faker('word', ext_word_list=['administrator', 'aide', 'guardian', 'parent', 'proctor', 'relative', 'student',
                                        'teacher', ])
    Username = Faker("first_name")
    GivenName = Faker("first_name")
    FamilyName = Faker("last_name")
    Email = Faker("email")
    PartnerName = Faker("domain_word")
    IDs = SubFactory(UserIDsFactory)
    ExternalProvider = Faker("domain_word")
    DateOfBirth = Faker("date")
