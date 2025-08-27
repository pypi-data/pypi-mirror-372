from __future__ import annotations

from typing import Optional, List

from pydantic import BaseModel, Field
from sysnet_pyutils.models.general import LinkedType, MetadataTypeBase, MetadataType, LogItemType, \
    MetadataTypeEntry, ListTypeBase

from ippc_model.ippc_common import (
    IppcDocCodeEnum, IppcAdditionalTypeEnum, PermittingType, InspectionType, ReportType, ValidationType, ChangeOperator, MergeEquipment)


class DocumentTypeBase(BaseModel):
    doc_code: Optional[IppcDocCodeEnum] = Field(default=None, description='Kód dokumentu')
    additional_type: Optional[IppcAdditionalTypeEnum] = Field(default=None, description='Typ dodatečné informace, pokud je doc_code==additional')
    title: Optional[str] = Field(default=None, description='Úplný název dokumentu', examples=['Integrované povolení'])
    subject: Optional[str] = Field(default=None, description='Stručný název dokumentu', examples=['Integrované povolení'])
    version_ozo: Optional[str] = Field(default='1', description='Verze OZO???')
    annotation: Optional[str] = Field(default=None, description='Anotace (Většinou annotation RTF!!!)')
    content: Optional[str] = Field(default=None, description='Plný obsah (Většinou Body RTF!!!)')
    permitting: Optional[PermittingType] = Field(default=None, description='Povolovací řízení')
    inspection: Optional[InspectionType] = Field(default=None, description='Informace o kontrole')
    report: Optional[ReportType] = Field(default=None, description='Zpráva o plnění')
    validation: Optional[ValidationType] = Field(default=None, description='Informace o validaci')
    operator_change: Optional[ChangeOperator] = Field(default=None, description='Informace o změně provozovatele')
    equipment_merge: Optional[MergeEquipment] = Field(default=None, description='Informace o sloučení zařízení')
    expert: Optional[LinkedType] = Field(default=None, description='Odborně způsobilá osoba')
    additional: Optional[List[LinkedType]] = Field(default=None, description='Další propojené dokumenty')
    has_attachments: Optional[bool] = Field(default=False, description='Kontejner má/nemá přílohy')
    metadata: Optional[MetadataTypeBase] = Field(default=None, description='Metadata dokumentu')
    linked_list: Optional[List[LinkedType]] = Field(default=None, description='Propojené dokumenty')


class DocumentType(DocumentTypeBase):
    operator: Optional[LinkedType] = Field(default=None, description='Aktuální provozovatel')
    equipment: Optional[LinkedType] = Field(default=None, description='Aktuální zařízení')
    activity_main: Optional[str] = Field(default=None, description='Hlavní činnost')
    activity_other: Optional[list[str]] = Field(default=None, description='Ostatní činnosti')
    metadata: Optional[MetadataType] = Field(default=None, description='Metadata dokumentu')
    history: Optional[list[LogItemType]] = Field(default=None, description='Historie dokumentu')


class DocumentEntryType(BaseModel):
    doc_code: Optional[IppcDocCodeEnum] = Field(default=None, alias='data-code', description='Kód dokumentu')
    additional_type: Optional[IppcAdditionalTypeEnum] = Field(default=None, description='Typ dodatečné informace, pokud je doc_code==additional')
    title: Optional[str] = Field(default=None, description='Úplný název dokumentu', examples=['Integrované povolení'])
    subject: Optional[str] = Field(default=None, description='Stručný název dokumentu', examples=['Integrované povolení'])
    metadata: Optional[MetadataTypeEntry] = Field(default=None, description='Metadata dokumentu')


class DocumentListType(ListTypeBase):
    hits: Optional[int] = Field(default=0, description='Hits')
    entries: Optional[List[DocumentEntryType]] = Field(default=None, description='Seznam dokumentů')


