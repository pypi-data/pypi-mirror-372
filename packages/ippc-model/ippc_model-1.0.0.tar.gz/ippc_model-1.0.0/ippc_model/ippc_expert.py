from __future__ import annotations

from datetime import datetime, date
from typing import Optional, List

from pydantic import Field, EmailStr, BaseModel
from sysnet_pyutils.models.general import (
    UserType, MetadataTypeBase, MetadataType, LogItemType, ListTypeBase, PersonCoreType)


class ExpertMigration(BaseModel):
    date_original_mod_time: Optional[datetime] = Field(default=None, description='OriginalModTime')
    pid_authority: Optional[str] = Field(default=None, description='PID_AUTHORITY')
    from_user: Optional[str] = Field(default=None, description='From')
    from_user_mail: Optional[EmailStr] = Field(default=None, description='From_userEmail')
    from_user_name: Optional[str] = Field(default=None, description='From_userName')
    from_person_name: Optional[str] = Field(default=None, description='From_orgName')
    from_person_uuid: Optional[str] = Field(default=None, description='From_orgUUID')
    is_authorized: Optional[bool] = Field(default=False, description='Authorized')
    annotation: Optional[str] = Field(default=None, description='Body')
    files: Optional[str] = Field(default=None, description='Body')

class ExpertTypeBase(PersonCoreType):
    email: Optional[List[EmailStr]] = Field(default=None, description='Email osoby')
    activity: Optional[List[str]] = Field(default=None, description='činnosti')
    date_validity: Optional[date] = Field(default=None, description='Platnost zápisu')
    contact: Optional[UserType] = Field(default=None, description='Kontaktní údaje')
    annotation: Optional[str] = Field(default=None, description='Anotace (Většinou annotation RTF!!!)')
    metadata: Optional[MetadataTypeBase] = Field(default=None, description='Metadata dokumentu')


class ExpertType(ExpertTypeBase):
    migration: Optional[ExpertMigration] = Field(default=None, description='Migrovaná data')
    metadata: Optional[MetadataType] = Field(default=None, description='Metadata dokumentu')
    history: Optional[list[LogItemType]] = Field(default=None, description='Historie dokumentu')


class ExpertListType(ListTypeBase):
    hits: Optional[int] = Field(default=0, description='Hits')
    entries: Optional[List[ExpertType]] = Field(default=None, description='')
