from __future__ import annotations

from datetime import datetime, date
from typing import Optional, List

from pydantic import BaseModel, Field, EmailStr
from sysnet_pyutils.models.general import (
    RegionalValueType, GeoPointType, CodeValueType, LocationType, MetadataTypeBase, LinkedType,
    MetadataType, LogItemType, TimeLimitedType, ListTypeBase)

from ippc_model.ippc_common import EquipmentStatusEnum


class EquipmentOtherInfo(BaseModel):
    # Další relevantní informace k zařízení
    eprtr: Optional[list[RegionalValueType]] = Field(default=None, description="E-PRTR")
    irz: Optional[list[RegionalValueType]] = Field(default=None, description='Seznam navázaných provozoven IRZ')
    chmu_source: Optional[list[RegionalValueType]] = Field(default=None, description='ČHMÚ - zdroje znečišťování')
    chmu_incinerator: Optional[list[RegionalValueType]] = Field(default=None, description='ČHMÚ - spalovny')
    rlcp: Optional[list[RegionalValueType]] = Field(default=None, description='Reporting LCP')
    isoh: Optional[list[RegionalValueType]] = Field(default=None, description='ISOH')


class EquipmentReportingBase(BaseModel):
    # Údaje pro reporting do EK (jen zadávané)
    inspire_id: Optional[str] = Field(default=None, description='Inspire ID')
    bat_conclusion_value: Optional[str] = Field(default=None, description='BAT Conclusion Value')
    other_relevant_chapters: Optional[str] = Field(default=None, description='Other Relevant Chapters')
    baseline_report_value: Optional[str] = Field(default=None, description='Baseline Report Value')
    permit_reconsidered: Optional[str] = Field(default=None, description='Permit Reconsidered')
    permit_updated: Optional[datetime] = Field(default=None, description='Permit Updated')
    remarks: Optional[str] = Field(default=None, description='Remarks')
    production_facility_local_id: Optional[str] = Field(default=None, description='Production Facility Local ID')


class EquipmentReporting(EquipmentReportingBase):
    # Údaje pro reporting do EK (vypočítávané)
    thematic_id: Optional[str] = Field(default=None, description='Thematic ID (výpočet =PID)')
    point_geometry: Optional[GeoPointType] = Field(default=None, description='Point geometry (výpočet se z lokality)')
    condition_of_facility_value: Optional[str] = Field(default=None, description='Condition of facility value (výpočet)')
    title: Optional[str] = Field(default=None, description='Title (výpočet z title)')
    competent_authority_permits: Optional[str] = Field(default=None, description='Competent authority permits (výpočet)')
    competent_authority_inspections: Optional[list[str]] = Field(default=None, description='Competent authority inspections (výpočet)')
    ied_annex_i_activity_value_main: Optional[str] = Field(default=None, description='IED annex i activity value (main activity) (výpočet)')
    ied_annex_i_activity_value_other: Optional[list[str]] = Field(default=None, description='IED annex i activity value (other activity) (výpočet)')
    permit_granted: Optional[bool] = Field(default=None, description='Permit granted (výpočet)')
    bat_derogation_indicator: Optional[bool] = Field(default=None, description='BAT Derogation Indicator (výpočet)')
    site_visit_number: Optional[List[str]] = Field(default=None, description='Site Visit Number (výpočet)')


class EquipmentMigration(BaseModel):
    date_merged: Optional[date] = Field(default=None, description='Date_Merged')
    date_data_valid: Optional[date] = Field(default=None, description='PLATNOST_DAT')
    pid_merged: Optional[str] = Field(default=None, description='PID_Appliance_Merged')
    pid_authority: Optional[str] = Field(default=None, description='PID_AUTHORITY')
    pid_import: Optional[str] = Field(default=None, description='PID_Import')
    pid_state: Optional[str] = Field(default=None, description='PID_STATE')
    from_user: Optional[str] = Field(default=None, description='From')
    from_user_mail: Optional[EmailStr] = Field(default=None, description='From_userEmail')
    from_user_id: Optional[str] = Field(default=None, description='From_userEmail')
    from_user_name: Optional[str] = Field(default=None, description='From_userName')
    from_person_name: Optional[str] = Field(default=None, description='From_orgName')
    from_person_uuid: Optional[str] = Field(default=None, description='From_orgUUID')
    is_authorized: Optional[bool] = Field(default=False, description='Authorized')
    is_closed: Optional[bool] = Field(default=False, description='isClosed')
    is_compiled: Optional[bool] = Field(default=False, description='isComplied')
    is_eia: Optional[bool] = Field(default=False, description='isEIA')
    is_exempted: Optional[bool] = Field(default=False, description='isExempted')
    is_finished: Optional[bool] = Field(default=False, description='isFinished')
    is_merged: Optional[bool] = Field(default=False, description='isMerged')
    is_updated: Optional[bool] = Field(default=False, description='isUpdated')
    is_verified: Optional[bool] = Field(default=False, description='isVerified')
    rec_no: Optional[int] = Field(default=None, description='REC_NO')
    remarks: Optional[str] = Field(default=None, description='remarks')
    shape: Optional[str] = Field(default=None, description='SHAPE')
    history_status: Optional[List[str]] = Field(default=None, description='StatusHistory')
    history_admin: Optional[List[str]] = Field(default=None, description='AdminLog')
    history_logs: Optional[List[str]] = Field(default=None, description='Log')
    history_events: Optional[List[str]] = Field(default=None, description='LogEvents')

    @property
    def status(self) -> EquipmentStatusEnum:
        out = EquipmentStatusEnum.EQ_NEW
        if self.is_authorized:
            out = EquipmentStatusEnum.EQ_ACTIVE
        if self.is_merged:
            out = EquipmentStatusEnum.EQ_MERGED
        if self.is_closed:
            out = EquipmentStatusEnum.EQ_CLOSED
        if self.is_exempted:
            out = EquipmentStatusEnum.EQ_EXCLUDED
        return out


class EquipmentTypeBase(BaseModel):
    title: Optional[str] = Field(
        default=None,
        description='Úplný název zařízení',
        examples=['Výroba gumových obuvnických podešví'])
    name: Optional[str] = Field(default=None, description='Stručný název zařízení', examples=['Výroba obuvnických podešví'])
    operator: Optional[LinkedType] = Field(default=None, description='Aktuální provozovatel')
    location: Optional[LocationType] = Field(default=None, description='Umístění zařízení')
    activity_main: Optional[str] = Field(default=None, description='Hlavní činnost')
    activity_other: Optional[List[str]] = Field(default=None, description='Ostatní činnosti')
    international: Optional[bool] = Field(default=False, description='Mezinárodní mechanismus')
    office_check: Optional[list[CodeValueType]] = Field(default=None, description='Kontrolní orgán')
    waste_water_disposal: Optional[str] = Field(default=None, description='Vypouštění odpadních vod')
    other: Optional[EquipmentOtherInfo] = Field(default=None, description='Další relevantní informace k zařízení ')
    reporting: Optional[EquipmentReportingBase] = Field(default=None, description='Reporting pro EK - zadávané hodnoty')
    metadata: Optional[MetadataTypeBase] = Field(default=None, description='Metadata dokumentu')


class EquipmentType(EquipmentTypeBase):
    reporting: Optional[EquipmentReporting] = Field(default=None, description='Reporting pro EK - všechny hodnoty')
    merged: Optional[bool] = Field(default=False, description='Zařízení bylo sloučeno se jiným zařízením')
    equipment_merged: Optional[LinkedType] = Field(default=None, description='Sloučené zařízení (PID_Appliance_Merged)')
    authorized: Optional[bool] = Field(default=False, description='Dokument byl autorizován')
    status: Optional[EquipmentStatusEnum] = Field(default=None, description='Stav zařízení')
    metadata: Optional[MetadataType] = Field(default=None, description='Metadata dokumentu')
    history: Optional[list[LogItemType]] = Field(default=None, description='Historie životního cyklu dokumentu')
    operator_history: Optional[list[TimeLimitedType]] = Field(default=None, description='Historie provozovatelů')
    migration: Optional[EquipmentMigration] = Field(default=None, description='Neurčená migrovaná data')


class EquipmentListType(ListTypeBase):
    hits: Optional[int] = Field(default=0, description='Hits')
    entries: Optional[List[EquipmentType]] = Field(default=None, description='')


