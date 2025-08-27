from __future__ import annotations

from typing import Optional, List

from pydantic import BaseModel, Field
from sysnet_pyutils.models.general import LinkedType, ListTypeBase, LogItemType

from ippc_model.ippc_common import (
    IppcContainerEnum, IppcStatusEnum, PermittingItemType, InspectionItemType,
    ReportItemType, ValidationItemType, ChangeOperator, MergeEquipment, IppcWorkflowType)


class ContainerTypeSuperBase(BaseModel):
    # Kontejner dokumentů IPPC (jedno řízení) [základ]
    name: Optional[str] = Field(
        default=None, description="Název kontejneru", examples=['Výroba obuvnických podešví (PUR-PLASTICS s.r.o.)'])
    content_type: Optional[IppcContainerEnum] = Field(
        default=IppcContainerEnum.PROCEEDING, description='Typ obsahu kontejneru (řízení/dokumentace/jiný)')
    international: Optional[bool] = Field(default=False, description='Mezinárodní mechanismus')


class ContainerTypeBase(ContainerTypeSuperBase):
    # Kontejner dokumentů IPPC (jedno řízení) [zápis dat]
    equipment: Optional[LinkedType] = Field(default=None, description='Zařízení (identifikátor/název)')
    operator: Optional[LinkedType] = Field(default=None, description='Provozovatel (identifikátor/název)')
    has_attachments: Optional[bool] = Field(default=False, description='Kontejner má/nemá přílohy')


class ContainerTypeListItem(ContainerTypeBase):
    # Kontejner dokumentů IPPC lehký (jedno řízení)
    identifier: Optional[str] = Field(default=None, description="UUID kontejneru (model 46)")
    locked: Optional[bool] = Field(default=False, description='Zámek kontejneru')
    status: Optional[IppcStatusEnum] = Field(default=None, description='Stav řízení v kontejneru (model 47)')
    status_saved: Optional[IppcStatusEnum] = Field(default=None, description='Předchozí stav řízení v kontejneru')
    activity_main: Optional[str] = Field(default=None, description='Hlavní činnost')


class ContainerTypeLight(ContainerTypeListItem):
    # Kontejner dokumentů IPPC lehký (jedno řízení)
    activity_other: Optional[list[str]] = Field(default=None, description='Ostatní činnosti')


class ContainerListType(ListTypeBase):
    hits: Optional[int] = Field(default=0, description='Hits')
    entries: Optional[List[ContainerTypeListItem]] = Field(default=None, description='')


class ContainerType(ContainerTypeLight):
    # Kontejner dokumentů IPPC plný (jedno řízení)
    permitting: Optional[PermittingItemType] = Field(default=None, description='Povolovací řízení')
    inspection: Optional[List[InspectionItemType]] = Field(default=None, description='Informace o kontrole')
    report: Optional[List[ReportItemType]] = Field(default=None, description='Zpráva o plnění')
    validation: Optional[List[ValidationItemType]] = Field(default=None, description='Informace o validaci')
    operator_change: Optional[List[ChangeOperator]] = Field(default=None, description='Informace o změně provozovatele')
    equipment_merge: Optional[List[MergeEquipment]] = Field(default=None, description='Informace o sloučení zařízení')
    expert: Optional[LinkedType] = Field(default=None, description='Odborně způsobilá osoba')
    workflow: Optional[list[IppcWorkflowType]] = Field(default=None, description='Záznam životního cyklu')
    history: Optional[list[LogItemType]] = Field(default=None, description='Historie životního cyklu kontejneru')


