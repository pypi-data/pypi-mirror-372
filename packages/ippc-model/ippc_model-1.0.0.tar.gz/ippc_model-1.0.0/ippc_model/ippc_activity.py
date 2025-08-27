from __future__ import annotations

from typing import Optional, List

from pydantic import BaseModel, Field
from sysnet_pyutils.models.general import MetadataTypeBase, MetadataType, LogItemType, ListTypeBase

from ippc_model.ippc_common import ActivityStatusEnum


# Činnost (kategorie) IPPC [Kategorie zařízení. Příloha č. 1 zákona č. 76/2002 Sb.]


class ActivityTypeBase(BaseModel):
    category: Optional[str] = Field(default=None, description='Kategorie zařízení (Equipment_Class)')
    code: Optional[str] = Field(default=None, description='Číslo (Equipment_Categories)')
    value_cz: Optional[str] = Field(default=None, description='Popis (Equipment_Categories_Text)')
    value_en: Optional[str] = Field(default=None, description='Popis - Reporting EK (Equipment_Categories_Text_EK)')
    hidden: Optional[bool] = Field(default=False, description='Skrýt kategorii v pohledech (Equipment_Class_Hide)')
    comment: Optional[str] = Field(default=None, description='Poznámka (Comment)')
    metadata: Optional[MetadataTypeBase] = Field(default=None, description='Metadata dokumentu')


class ActivityType(ActivityTypeBase):
    status: Optional[ActivityStatusEnum] = Field(default=ActivityStatusEnum.AC_NEW, description='Stav položky činnosti')
    metadata: Optional[MetadataType] = Field(default=None, description='')
    history: Optional[list[LogItemType]] = Field(default=None, description='Historie dokumentu')


class ActivityListType(ListTypeBase):
    hits: Optional[int] = Field(default=0, description='Hits')
    entries: Optional[List[ActivityType]] = Field(default=None, description='')


class ActivityViewItemType(BaseModel):
    hidden: Optional[bool] = Field(default=False, description='Skrýt kategorii v pohledech (Equipment_Class_Hide)')
    category: Optional[str] = Field(default=None, description='Kategorie zařízení (Equipment_Class)')
    code: Optional[str] = Field(default=None, description='Číslo (Equipment_Categories)')
    value_cz: Optional[str] = Field(default=None, description='Popis (Equipment_Categories_Text)')
    value_en: Optional[str] = Field(default=None, description='Popis - Reporting EK (Equipment_Categories_Text_EK)')
    count_container: Optional[int] = Field(default=0, description='Počet IP')
    count_equipment: Optional[int] = Field(default=0, description='Počet zařízení')
    count_expert: Optional[int] = Field(default=0, description='Počet OZO')


