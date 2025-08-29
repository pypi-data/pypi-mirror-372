from dataclasses import dataclass


@dataclass
class Partner:
    id: str
    name: str
    display_name: str
    canvas_domain: str
    canvas_account: int
    powerschool_domain: str
    powerschool_dcid: int
    powerschool_school_number: int
    fuji_id: int
    default_grade: str
    canvas_account_uuid: str
    clever_district_id: str
    clever_school_id: str
    group_label: str
    roster_source: str
    feature_identity_emails: bool
    canvas_authentication_provider_type: str
