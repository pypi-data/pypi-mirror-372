from factory import Factory, Faker, SubFactory, LazyAttribute, List
from oneroster_client import ResultType, SingleResultType, ResultsType

from test.factories.oneroster_guidref import OneRosterGuidRefFactory


class OneRosterResultFactory(Factory):
    class Meta:
        model = ResultType
        exclude = ('base_url')

    base_url = 'https://devapi.platform.strongmind.com/ims/oneroster/v1p1/'

    sourced_id = Faker('uuid4')
    status = Faker('word', ext_word_list=['active', 'tobedeleted'])
    date_last_modified = Faker('iso8601')
    metadata = None

    line_item = SubFactory(OneRosterGuidRefFactory,
                           href=LazyAttribute(lambda o: f'{o.factory_parent.base_url}lineItems/{o.sourced_id}'),
                           sourced_id=Faker('uuid4'),
                           type='lineItem'
                           )

    student = SubFactory(OneRosterGuidRefFactory,
                         href=LazyAttribute(lambda o: f'{o.factory_parent.base_url}users/{o.sourced_id}'),
                         sourced_id=Faker('uuid4'),
                         type='user'
                         )

    score_status = Faker('word', ext_word_list=['exempt', 'fully graded', 'partially graded', 'submitted'])

    score = Faker('random_int', min=0, max=100)
    score_date = Faker('date')
    comment = Faker('word')


class OneRosterSingleResultFactory(Factory):
    class Meta:
        model = SingleResultType

    result = SubFactory(OneRosterResultFactory)


class OneRosterResultsFactory(Factory):
    class Meta:
        model = ResultsType
        exclude = "line_item_uuid", "student_uuid", "result_uuid"

    line_item_uuid = Faker("uuid4")
    student_uuid = Faker("uuid4")
    result_uuid = Faker("uuid4")

    results = List([
        SubFactory(OneRosterResultFactory,
                   sourced_id=LazyAttribute(lambda o: o.factory_parent.factory_parent.result_uuid),
                   line_item__sourced_id=line_item_uuid,
                   student__sourced_id=student_uuid)
    ])
