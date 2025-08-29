from dataclasses import dataclass

@dataclass
class Domain:
    id: int
    name: str
    key: str
    secret: str
    token: str
    snap_token: str
    partner: str
    is_disabled: bool
