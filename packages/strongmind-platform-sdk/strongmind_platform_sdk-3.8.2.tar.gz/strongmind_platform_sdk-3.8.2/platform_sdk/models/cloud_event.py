from datetime import datetime
from typing import Optional, Any

from pydantic.dataclasses import dataclass


@dataclass
class CloudEvent:
    """
    Contract supporting the Cloud Event schema at https://github.com/cloudevents/spec/blob/master/spec.json
    """
    id: str
    type: str
    source: str
    time: datetime
    subject: str
    dataschema: Optional[str]
    datacontenttype: Optional[str]
    data: Optional[Any]
    specversion: str = "1.0"

