from datetime import date
from enum import Enum
from typing import Optional, Dict

from pydantic import BaseModel, Field


class RoleEnum(str, Enum):
    administrator = 'administrator'
    aide = 'aide'
    guardian = 'guardian'
    parent = 'parent'
    proctor = 'proctor'
    relative = 'relative'
    student = 'student'
    teacher = 'teacher'


class User(BaseModel):
    """
    Contract for data needed to create a user in StrongMind's systems
    """
    role: Optional[RoleEnum] = Field(alias="Role")
    username: str = Field(alias="Username")
    given_name: str = Field(alias="GivenName")
    family_name: str = Field(alias="FamilyName")
    email: str = Field(alias="Email")
    partner_name: Optional[str] = Field(alias="PartnerName")
    ids: Dict = Field(alias="IDs")
    external_provider: Optional[str] = Field(alias="ExternalProvider")
    dob: Optional[date] = Field(alias="DateOfBirth")
    source_system_id: Optional[str] = Field(alias="SourceSystemId", default=None)
