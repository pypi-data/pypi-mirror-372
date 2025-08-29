from factory import Factory, Faker, SubFactory, LazyAttribute, List
from oneroster_client import LineItemType, SingleLineItemType, LineItemsType

from platform_sdk.shared.constants import GUID_ONEROSTER_CURRENT_GRADE_CATEGORY_ID, \
    GUID_ONEROSTER_FINAL_GRADE_CATEGORY_ID
from test.factories.oneroster_guidref import OneRosterGuidRefFactory


class OneRosterLineItemFactory(Factory):
    class Meta:
        model = LineItemType
        exclude = ('base_url')

    base_url = 'https://devapi.platform.strongmind.com/ims/oneroster/v1p1/'

    sourced_id = Faker("uuid4")
    status = "active"
    date_last_modified = Faker("date")
    title = Faker("sentence")
    assign_date = Faker("past_date")
    due_date = Faker("future_date")

    _class = SubFactory(OneRosterGuidRefFactory,
                        href=LazyAttribute(lambda o: f'{o.factory_parent.base_url}classes/{o.sourced_id}'),
                        sourced_id=Faker('uuid4'),
                        type='class'
                        )

    category = SubFactory(OneRosterGuidRefFactory,
                          href=LazyAttribute(lambda o: f'{o.factory_parent.base_url}categories/{o.sourced_id}'),
                          sourced_id=Faker('uuid4'),
                          type='category'
                          )

    grading_period = SubFactory(OneRosterGuidRefFactory,
                                href=LazyAttribute(
                                    lambda o: f'{o.factory_parent.base_url}academicSessions/{o.sourced_id}'),
                                sourced_id=Faker('uuid4'),
                                type='academicSession'
                                )

    result_value_min = 0
    result_value_max = 100


class OneRosterSingleLineItemFactory(Factory):
    class Meta:
        model = SingleLineItemType

    line_item = SubFactory(OneRosterLineItemFactory)


class OneRosterLineItemsFactory(Factory):
    class Meta:
        model = LineItemsType
        exclude = "class_uuid"

    class_uuid = Faker("uuid4")

    line_items = List([
        SubFactory(OneRosterLineItemFactory, _class__sourced_id=class_uuid,
                   category__sourced_id=GUID_ONEROSTER_CURRENT_GRADE_CATEGORY_ID),
        SubFactory(OneRosterLineItemFactory, _class__sourced_id=class_uuid,
                   category__sourced_id=GUID_ONEROSTER_FINAL_GRADE_CATEGORY_ID)
    ])
