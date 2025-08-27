import json
from datetime import datetime
from enum import Enum
from typing import Optional, List, Union
from uuid import UUID

from pydantic import BaseModel, Field
from sysnet_pyutils.data_utils import get_dict_value_list, get_dict_value
from sysnet_pyutils.models.general import LinkedType, WorkflowType, RegionalValueType
from sysnet_pyutils.utils import is_valid_uuid


class IppcDocCodeEnum(Enum):
    REQUEST = 'request'
    SUMMARIZE = 'summarize'
    STATEMENT = 'statement'
    STATEMENT_CENIA = 'statement-cenia'
    DECISION = 'decision'
    APPEAL = 'appeal'
    APPDEC = 'appdec'
    RE_DECISION = 're-decision'
    MINORCHANGE = 'minorchange'
    CANCELED = 'canceled'
    CHANGE = 'change'
    ADDITIONAL = 'additional'
    TERMINATED = 'terminated'
    EXCEPTIONS = 'exceptions'
    APPEAL_RESULT = 'appeal-result'
    INTERRUPTED = 'interrupted'
    RESUMED = 'resumed'
    VALIDATE = 'validate'
    EXEMPTION = 'exemption'
    CLOSED = 'closed'

    REPORT_CONDITIONS = 'report-conditions'
    REPORT_REVIEW = 'report-review'
    REPORT_CHECK = 'report-check'
    REPORT_CHECK_SUPPLEMENT = 'report-check-supplement'
    XCHG_COMPANY = 'xchg-company'
    MERGED = 'merged'

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_


DOC_CREATES_CONTAINER = [IppcDocCodeEnum.REQUEST, IppcDocCodeEnum.CHANGE, IppcDocCodeEnum.EXCEPTIONS]

CONTAINER_TITLES = {
    IppcDocCodeEnum.REQUEST: 'Integrované povolení',
    IppcDocCodeEnum.CHANGE: 'Změna integrovaného povolení',
    IppcDocCodeEnum.EXCEPTIONS: 'Výjimky',

    IppcDocCodeEnum.REPORT_CONDITIONS: 'Dokumentace k zařízení',
    IppcDocCodeEnum.REPORT_REVIEW: 'Dokumentace k zařízení',
    IppcDocCodeEnum.REPORT_CHECK: 'Dokumentace k zařízení',
    IppcDocCodeEnum.REPORT_CHECK_SUPPLEMENT: 'Dokumentace k zařízení',
    IppcDocCodeEnum.XCHG_COMPANY: 'Dokumentace k zařízení'
}

DOC_PROCEEDING = [
    IppcDocCodeEnum.REQUEST, IppcDocCodeEnum.SUMMARIZE, IppcDocCodeEnum.STATEMENT, IppcDocCodeEnum.STATEMENT_CENIA,
    IppcDocCodeEnum.DECISION, IppcDocCodeEnum.APPEAL, IppcDocCodeEnum.APPDEC, IppcDocCodeEnum.RE_DECISION,
    IppcDocCodeEnum.MINORCHANGE, IppcDocCodeEnum.VALIDATE, IppcDocCodeEnum.CANCELED,
    IppcDocCodeEnum.CHANGE,
    IppcDocCodeEnum.INTERRUPTED, IppcDocCodeEnum.RESUMED, IppcDocCodeEnum.ADDITIONAL, IppcDocCodeEnum.TERMINATED,
    IppcDocCodeEnum.EXEMPTION, IppcDocCodeEnum.EXCEPTIONS, IppcDocCodeEnum.APPEAL_RESULT, IppcDocCodeEnum.CLOSED,
    IppcDocCodeEnum.MERGED]

DOC_DOCUMENTATION = [
    IppcDocCodeEnum.REPORT_CONDITIONS, IppcDocCodeEnum.REPORT_REVIEW,
    IppcDocCodeEnum.REPORT_CHECK, IppcDocCodeEnum.REPORT_CHECK_SUPPLEMENT,
    IppcDocCodeEnum.XCHG_COMPANY]


class IppcAdditionalTypeEnum(Enum):
    DOKUMENT = 'dokument'
    KORESPONDENCE = 'korespondence'
    ZPRAVA = 'zpráva'
    ZAPIS = 'zápis'
    NAVRH = 'návrh'
    ROZHODNUTI = 'rozhodnutí'
    JINA_INFORMACE = 'jiná informace'

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_


class ReviewTypeEnum(Enum):
    # 'Typ přezkumu (Plánovaná kontrola|P, Neplánovaná kontrola|U)'
    PLANNED = 'P'
    UNPLANNED = 'U'

class DataObjectsEnum(Enum):
    ACTIVITY = 'activity'
    EQUIPMENT = 'equipment'
    EXPERT = 'expert'

class DataFormatEnum(Enum):
    CSV = 'csv'
    DDA = 'dda'

class IppcStatusEnum(Enum):
    STATUS_0 = '0 - Neautorizováno'
    STATUS_1 = '1 - Publikováno'
    STATUS_2 = '2 - Stručné shrnutí publikováno'
    STATUS_3 = '3 - Stručné shrnutí staženo'
    STATUS_4 = '4 - Vyjádření OZO publikováno'
    STATUS_5 = '5 - Vyjádření OZO staženo'
    STATUS_6 = '6 - Rozhodnuto'
    STATUS_7 = '7 - Uloženo'
    STATUS_8 = '8 - Rozhodnuto (vyjádření nestaženo)'
    STATUS_9 = '9 - Řízení zastaveno'
    STATUS_A = 'A - Dokumentace uložena'
    STATUS_B = 'B - Odvolání'
    STATUS_D = 'D - IP zrušeno'
    STATUS_M = 'M - Řízení sloučeno'
    STATUS_P = 'P - Řízení přerušeno'
    STATUS_Z = 'Z - Provoz ukončen'
    STATUS_Z1 = 'Z1 - Vyňato z režimu'
    STATUS_X = 'X - Bez stavu'

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_


class PermittingType(BaseModel):
    date_initiated: Optional[datetime] = Field(
        default=None,
        description='Datum zahájení řízení',
        examples=['2024-05-04T00:00:00Z'])
    date_expired: Optional[datetime] = Field(
        default=None,
        description='Datum stažení dokumentu',
        examples=['2024-05-04T00:00:00Z'])
    date_legal: Optional[datetime] = Field(
        default=None,
        description='Datum nabytí právní moci (date_legal, date_legalized)',
        examples=['2024-05-04T00:00:00Z'])
    date_executed: Optional[datetime] = Field(
        default=None,
        description='Datum provedení změny (date_change). Sem patří data typu date_decided, date_merged, ...',
        examples=['2024-05-04T00:00:00Z'])
    date_decided: Optional[datetime] = Field(
        default=None,
        description='Datum zastavení řízení - zapisovat do date_executed',
        examples=['2024-05-04T00:00:00Z'])
    date_exempted: Optional[datetime] = Field(
        default=None,
        description='Datum vynětí z režimu - zapisovat do date_executed',
        examples=['2024-05-04T00:00:00Z'],
    )
    date_exception: Optional[datetime] = Field(
        default=None,
        description='Datum zadání výjimek - zapisovat do date_executed',
        examples=['2024-05-04T00:00:00Z'],
    )
    date_appealed: Optional[datetime] = Field(
        default=None,
        description='Datum odvolání - zapisovat do date_executed',
        examples=['2024-05-04T00:00:00Z'],
    )
    date_interrupted: Optional[datetime] = Field(
        default=None,
        description='Datum přerušení řízení - zapisovat do date_executed',
        examples=['2024-05-04T00:00:00Z'],
    )
    date_resumed: Optional[datetime] = Field(
        default=None,
        description='Datum obnovení řízení - zapisovat do date_executed',
        examples=['2024-05-04T00:00:00Z'],
    )
    date_appeal_result: Optional[datetime] = Field(
        default=None,
        description='Právní moc odvolání - zapisovat do date_legal',
        examples=['2024-05-04T00:00:00Z'],
    )
    date_closed: Optional[datetime] = Field(
        default=None,
        description='Datum ukončení provozu zařízení',
        examples=['2024-05-04T00:00:00Z'],
    )
    published: Optional[bool] = Field(default=False, description='Dokument publikován (publikuje se autorizací, stahuje uplynutím času' )
    source: Optional[str] = Field(default=None, description='Originál žádosti k nahlédnutí')
    bat_id: Optional[str] = Field(default=None, description='Identifikace BAT')
    processor: Optional[str] = Field(default=None, description='Zpracovatel žádosti')
    unabridged: Optional[bool] = Field(default=False, description='Plné znění')
    eia: Optional[bool] = Field(default=False, description='Posouzení podle zákona o posuzování vlivů na životní prostředí')
    eia_id: Optional[str] = Field(default=None, description='Identifikace záměru v informačním systému EIA')
    permitted: Optional[bool] = Field(default=None, description='Integrované povolení uděleno/neuděleno')
    status_resumed: Optional[IppcStatusEnum] = Field(default=None, description='Stav obnovení')

class PermittingItemType(PermittingType):
    documents: Optional[List[LinkedType]] = Field(default=None, description='Seznam dokumentů řízení')


class InspectionType(BaseModel):
    date_check_start: Optional[datetime] = Field(
        default=None,
        description='Termín přezkumu nebo kontroly - zahájení',
        examples=['2024-05-04T00:00:00Z'],
    )
    date_check_end: Optional[datetime] = Field(
        default=None,
        description='Termín přezkumu nebo kontroly - ukončení',
        examples=['2024-05-04T00:00:00Z'],
    )
    check_type: Optional[ReviewTypeEnum] = Field(
        default=None,
        description='Typ přezkumu (Plánovaná kontrola, Neplánovaná kontrola)')
    check_office: Optional[str] = Field(
        default=None,
        description='Identifikace kontrolní instituce [identOfficeCheck] (ČIŽP, KHS)',
    )
    finished: Optional[bool] = Field(default=None, description='Zpráva o kontrole (isFinished)')
    check_subject: Optional[str] = Field(default=None, description='Rozsah kontroly a kontrolní období')

class InspectionItemType(InspectionType):
    document: Optional[LinkedType] = Field(default=None, description='Propojený dokument')


class ReportType(BaseModel):
    date_published: Optional[datetime] = Field(
        default=None, description='Datum podání zprávy', examples=['2024-05-04T00:00:00Z']
    )
    date_period_start: Optional[datetime] = Field(
        default=None,
        description='Období, za které je zpráva podávána (period_start)- zahájení',
        examples=['2024-05-04T00:00:00Z'],
    )
    date_period_end: Optional[datetime] = Field(
        default=None,
        description='Období, za které je zpráva podávána (period_end) - ukončení',
        examples=['2024-05-04T00:00:00Z'],
    )
    complied: Optional[bool] = Field(default=None, description='Podmínky jsou plněny (isComplied)', examples=[True])

class ReportItemType(ReportType):
    document: Optional[LinkedType] = Field(default=None, description='Propojený dokument')


class ValidationType(BaseModel):
    delivered: Optional[bool] = Field(default=None, description='Dokument doručen MŽP', examples=[False])
    date_delivered: Optional[datetime] = Field(default=None, description='Datum doručení na MŽP')
    id_no: Optional[str] = Field(default=None, description='Čj. MŘP')
    archive_file: Optional[str] = Field(default=None, description='Archivační box', examples=['IPPC/EH/21/01/JCK'])
    comment: Optional[str] = Field(default=None, description='Poznámka')

class ValidationItemType(ValidationType):
    document: Optional[LinkedType] = Field(default=None, description='Provázaný dokument')


class ChangeOperator(BaseModel):
    date_changed: Optional[datetime] = Field(default=None, description='Datum změny (Date_Changed)')
    date_changed_legal: Optional[datetime] = Field(default=None,
                                                   description='Datum účinnosti změny (Date_Operation_Changed)')
    operator_from: Optional[LinkedType] = Field(default=None, description='Původní provozovatel')
    operator_to: Optional[LinkedType] = Field(default=None, description='Následný provozovatel')


class MergeEquipment(BaseModel):
    date_merged: Optional[datetime] = Field(
        default=None,
        description='Datum sloučení IP - zapisovat do date_executed',
        examples=['2024-05-04T00:00:00Z'])
    date_merged_legal: Optional[datetime] = Field(
        default=None,
        description='Datum právní moci sloučení IP - zapisovat do date_legal',
        examples=['2024-05-04T00:00:00Z'])
    equipment_source: Optional[LinkedType] = Field(default=None, description='Zdrojové zařízení (PID_Appliance)')
    equipment_target: Optional[LinkedType] = Field(default=None, description='Cílové zařízení (PID_Appliance_Merged)')
    equipment_merged: Optional[LinkedType] = Field(default=None, description='Sloučené zařízení (PID_Appliance_Merged)')


class IppcContainerEnum(Enum):
    PROCEEDING = 'proceeding'  # Řízení
    DOCUMENTATION = 'documentation'  # Dokumentace
    OTHER = 'other'  # Jiný

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_

class ActivityStatusEnum(Enum):
    AC_NEW = '0 - nová'
    AC_ACTIVE = '1 - aktivní'
    AC_EXCLUDED = '9 - vyřazená'

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_


class EquipmentStatusEnum(Enum):
    EQ_NEW = '0 - nové'
    EQ_AUTHORIZED = '1 - autorizováno'
    EQ_ACTIVE = '2 - aktivní'
    EQ_MERGED = 'M - sloučené'
    EQ_CLOSED = 'Z - Provoz ukončen'
    EQ_EXCLUDED = 'Z1 - Vyňato z režimu'

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_


PROCEEDING_TRANSITION = {
    IppcDocCodeEnum.REQUEST: {'node_name': 'Autorizace žádosti o IP', 'status_to': IppcStatusEnum.STATUS_1.value},
    IppcDocCodeEnum.SUMMARIZE: {'node_name': 'Autorizace stručného shrnutí', 'status_to': IppcStatusEnum.STATUS_2.value},
    IppcDocCodeEnum.STATEMENT: {'node_name': 'Autorizace vyjádření OZO', 'status_to': IppcStatusEnum.STATUS_4.value},
    IppcDocCodeEnum.STATEMENT_CENIA: {'node_name': 'Autorizace vyjádření CENIA', 'status_to': IppcStatusEnum.STATUS_4.value},
    IppcDocCodeEnum.DECISION: {'node_name': None, 'status_to': None},
    IppcDocCodeEnum.APPEAL: {'node_name': None, 'status_to': None},
    IppcDocCodeEnum.APPDEC: {'node_name': None, 'status_to': None},
    IppcDocCodeEnum.RE_DECISION: {'node_name': None, 'status_to': None},
    IppcDocCodeEnum.MINORCHANGE: {'node_name': None, 'status_to': None},
    IppcDocCodeEnum.VALIDATE: {'node_name': None, 'status_to': None},
    IppcDocCodeEnum.CANCELED: {'node_name': None, 'status_to': None},
    IppcDocCodeEnum.CHANGE: {'node_name': 'Autorizace podstatné změny IP', 'status_to': IppcStatusEnum.STATUS_1.value},
    IppcDocCodeEnum.INTERRUPTED: {'node_name': None, 'status_to': None},
    IppcDocCodeEnum.RESUMED: {'node_name': None, 'status_to': None},
    IppcDocCodeEnum.ADDITIONAL: {'node_name': None, 'status_to': None},
    IppcDocCodeEnum.TERMINATED: {'node_name': None, 'status_to': None},
    IppcDocCodeEnum.EXEMPTION: {'node_name': None, 'status_to': None},
    IppcDocCodeEnum.EXCEPTIONS: {'node_name': 'Autorizace výjimek z IP', 'status_to': IppcStatusEnum.STATUS_1.value},
    IppcDocCodeEnum.APPEAL_RESULT: {'node_name': None, 'status_to': None},
    IppcDocCodeEnum.CLOSED: {'node_name': None, 'status_to': None},

}


class IppcWorkflowType(WorkflowType):
    status_from: Optional[IppcStatusEnum] = Field(default=None, description='Předchozí stav')
    status_to: Optional[IppcStatusEnum] = Field(default=None, description='Následný stav')


def get_dict_value_regional(data: dict, item_name: str) -> Union[List[RegionalValueType], None]:
    v = get_dict_value_list(data=data, item_name=item_name)
    if not bool(v):
        return None
    out = []
    for item in v:
        x = RegionalValueType(value=item)
        out.append(x)
    return out

def get_dict_value_uuid(data: dict, item_name: str) -> Union[str, None]:
    v = get_dict_value(data=data, item_name=item_name)
    if not bool(v):
        return None
    if is_valid_uuid(v):
        return str(UUID(v))
    return None

def get_dict_value_rtf(data: dict, item_name: str) -> Union[str, None]:
    v = get_dict_value(data=data, item_name=item_name)
    if not bool(v):
        return None
    out = json.dumps(v)
    return out
