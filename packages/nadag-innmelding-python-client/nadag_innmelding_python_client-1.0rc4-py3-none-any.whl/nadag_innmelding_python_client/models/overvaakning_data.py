import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.akvifer_type import AkviferType
from ..types import UNSET, Unset

T = TypeVar("T", bound="OvervaakningData")


@_attrs_define
class OvervaakningData:
    """data fra overvåkning av setningsmåling, grunnvannsstand, poretrykk, rystelser eller andre
    overvåkningsdata<engelsk>data from supervision of settlements, groundwater table, pore pressure or any other
    supervision data</engelsk>

        Attributes:
            akvifer (Union[Unset, AkviferType]): oversikt over mulige akvifertyper for grunnvannsmålinger<engelsk>overview
                of possible aquifer types for ground water measurements</engelsk>
            m_å_le_tidspunkt (Union[Unset, datetime.datetime]):
            nedre_alarm_niv_å (Union[Unset, float]):
            ø_vre_alarm_niv_å (Union[Unset, float]):
            m_å_le_dato (Union[Unset, datetime.date]):
            observasjon_merknad (Union[Unset, str]):
    """

    akvifer: Union[Unset, AkviferType] = UNSET
    m_å_le_tidspunkt: Union[Unset, datetime.datetime] = UNSET
    nedre_alarm_niv_å: Union[Unset, float] = UNSET
    ø_vre_alarm_niv_å: Union[Unset, float] = UNSET
    m_å_le_dato: Union[Unset, datetime.date] = UNSET
    observasjon_merknad: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        akvifer: Union[Unset, str] = UNSET
        if not isinstance(self.akvifer, Unset):
            akvifer = self.akvifer.value

        m_å_le_tidspunkt: Union[Unset, str] = UNSET
        if not isinstance(self.m_å_le_tidspunkt, Unset):
            m_å_le_tidspunkt = self.m_å_le_tidspunkt.isoformat()

        nedre_alarm_niv_å = self.nedre_alarm_niv_å

        ø_vre_alarm_niv_å = self.ø_vre_alarm_niv_å

        m_å_le_dato: Union[Unset, str] = UNSET
        if not isinstance(self.m_å_le_dato, Unset):
            m_å_le_dato = self.m_å_le_dato.isoformat()

        observasjon_merknad = self.observasjon_merknad

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if akvifer is not UNSET:
            field_dict["akvifer"] = akvifer
        if m_å_le_tidspunkt is not UNSET:
            field_dict["måleTidspunkt"] = m_å_le_tidspunkt
        if nedre_alarm_niv_å is not UNSET:
            field_dict["nedreAlarmNivå"] = nedre_alarm_niv_å
        if ø_vre_alarm_niv_å is not UNSET:
            field_dict["ØvreAlarmNivå"] = ø_vre_alarm_niv_å
        if m_å_le_dato is not UNSET:
            field_dict["måleDato"] = m_å_le_dato
        if observasjon_merknad is not UNSET:
            field_dict["observasjonMerknad"] = observasjon_merknad

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        _akvifer = d.pop("akvifer", UNSET)
        akvifer: Union[Unset, AkviferType]
        if isinstance(_akvifer, Unset):
            akvifer = UNSET
        else:
            akvifer = AkviferType(_akvifer)

        _m_å_le_tidspunkt = d.pop("måleTidspunkt", UNSET)
        m_å_le_tidspunkt: Union[Unset, datetime.datetime]
        if isinstance(_m_å_le_tidspunkt, Unset):
            m_å_le_tidspunkt = UNSET
        else:
            m_å_le_tidspunkt = isoparse(_m_å_le_tidspunkt)

        nedre_alarm_niv_å = d.pop("nedreAlarmNivå", UNSET)

        ø_vre_alarm_niv_å = d.pop("ØvreAlarmNivå", UNSET)

        _m_å_le_dato = d.pop("måleDato", UNSET)
        m_å_le_dato: Union[Unset, datetime.date]
        if isinstance(_m_å_le_dato, Unset):
            m_å_le_dato = UNSET
        else:
            m_å_le_dato = isoparse(_m_å_le_dato).date()

        observasjon_merknad = d.pop("observasjonMerknad", UNSET)

        overvaakning_data = cls(
            akvifer=akvifer,
            m_å_le_tidspunkt=m_å_le_tidspunkt,
            nedre_alarm_niv_å=nedre_alarm_niv_å,
            ø_vre_alarm_niv_å=ø_vre_alarm_niv_å,
            m_å_le_dato=m_å_le_dato,
            observasjon_merknad=observasjon_merknad,
        )

        overvaakning_data.additional_properties = d
        return overvaakning_data

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
