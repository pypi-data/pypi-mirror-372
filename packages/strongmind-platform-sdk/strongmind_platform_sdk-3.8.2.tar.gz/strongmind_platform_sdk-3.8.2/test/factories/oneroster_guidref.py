from factory import Faker, Factory
from oneroster_client import GUIDRefType


class OneRosterGuidRefFactory(Factory):
    class Meta:
        model = GUIDRefType

    href = Faker('word')
    sourced_id = Faker('uuid4')
    type = Faker('word', ext_word_list=['academicSession', 'category', 'class', 'course', 'demographics',
                                        'enrollment', 'lineItem', 'org', 'resource', 'result', 'student',
                                        'teacher', 'user', 'term', 'gradingPeriod'])
