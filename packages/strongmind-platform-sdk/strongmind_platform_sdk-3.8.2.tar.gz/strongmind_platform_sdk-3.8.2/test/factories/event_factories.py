from datetime import datetime

from factory import Dict, Faker, LazyAttribute, SelfAttribute, Factory

from platform_sdk.models.cloud_event import CloudEvent


class PowerSchoolEventFactory(Factory):
    class Meta:
        model = CloudEvent
        exclude = 'powerschool_domain', 'recordid', 'api_name'

    specversion = "1.0"
    dataschema = None
    api_name = "section_enrollment"
    recordid = Faker("random_int")
    id = Faker("uuid4")
    type = "PowerSchool.WebHook"
    subject = "CC"
    powerschool_domain = Faker("domain_word")
    source = LazyAttribute(lambda o: f"https://{o.powerschool_domain}/ws/v1/{o.api_name}/{o.recordid}")
    time = datetime.utcnow().isoformat()
    datacontenttype = "application/json"
    data = Dict({
        "ref": SelfAttribute("..source"),
        "event_type": "INSERT",
        "id": SelfAttribute("..recordid"),
        "entity": SelfAttribute("..subject"),
        "timestamp": SelfAttribute("..time")
    })
