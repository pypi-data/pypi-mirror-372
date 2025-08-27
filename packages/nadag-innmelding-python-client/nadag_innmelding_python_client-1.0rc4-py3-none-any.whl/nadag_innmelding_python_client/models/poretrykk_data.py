import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="PoretrykkData")


@_attrs_define
class PoretrykkData:
    """data fra måling av poretrykk <engelsk>data from measurements of pore pressure</engelsk>

    Attributes:
        avlesing_0_kontroll (Union[Unset, float]):
        avlesing_etter_0_kontroll (Union[Unset, float]):
        avlesing_fø_r_0_kontroll (Union[Unset, float]):
        avstand_manometer_filterspiss (Union[Unset, float]):
        avstand_topp_slange_til_vannstand (Union[Unset, float]):
        barometer_trykk (Union[Unset, float]):
        dybde_grunnvannstand (Union[Unset, float]):
        m_å_le_dato (Union[Unset, datetime.date]):
        m_å_le_tidspunkt (Union[Unset, datetime.datetime]):
        observasjon_kode (Union[Unset, str]):
        observasjon_merknad (Union[Unset, str]):
        poretrykk (Union[Unset, float]):
        trykkhøyde (Union[Unset, float]):
    """

    avlesing_0_kontroll: Union[Unset, float] = UNSET
    avlesing_etter_0_kontroll: Union[Unset, float] = UNSET
    avlesing_fø_r_0_kontroll: Union[Unset, float] = UNSET
    avstand_manometer_filterspiss: Union[Unset, float] = UNSET
    avstand_topp_slange_til_vannstand: Union[Unset, float] = UNSET
    barometer_trykk: Union[Unset, float] = UNSET
    dybde_grunnvannstand: Union[Unset, float] = UNSET
    m_å_le_dato: Union[Unset, datetime.date] = UNSET
    m_å_le_tidspunkt: Union[Unset, datetime.datetime] = UNSET
    observasjon_kode: Union[Unset, str] = UNSET
    observasjon_merknad: Union[Unset, str] = UNSET
    poretrykk: Union[Unset, float] = UNSET
    trykkhøyde: Union[Unset, float] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        avlesing_0_kontroll = self.avlesing_0_kontroll

        avlesing_etter_0_kontroll = self.avlesing_etter_0_kontroll

        avlesing_fø_r_0_kontroll = self.avlesing_fø_r_0_kontroll

        avstand_manometer_filterspiss = self.avstand_manometer_filterspiss

        avstand_topp_slange_til_vannstand = self.avstand_topp_slange_til_vannstand

        barometer_trykk = self.barometer_trykk

        dybde_grunnvannstand = self.dybde_grunnvannstand

        m_å_le_dato: Union[Unset, str] = UNSET
        if not isinstance(self.m_å_le_dato, Unset):
            m_å_le_dato = self.m_å_le_dato.isoformat()

        m_å_le_tidspunkt: Union[Unset, str] = UNSET
        if not isinstance(self.m_å_le_tidspunkt, Unset):
            m_å_le_tidspunkt = self.m_å_le_tidspunkt.isoformat()

        observasjon_kode = self.observasjon_kode

        observasjon_merknad = self.observasjon_merknad

        poretrykk = self.poretrykk

        trykkhøyde = self.trykkhøyde

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if avlesing_0_kontroll is not UNSET:
            field_dict["avlesing0Kontroll"] = avlesing_0_kontroll
        if avlesing_etter_0_kontroll is not UNSET:
            field_dict["avlesingEtter0Kontroll"] = avlesing_etter_0_kontroll
        if avlesing_fø_r_0_kontroll is not UNSET:
            field_dict["avlesingFør0Kontroll"] = avlesing_fø_r_0_kontroll
        if avstand_manometer_filterspiss is not UNSET:
            field_dict["avstandManometerFilterspiss"] = avstand_manometer_filterspiss
        if avstand_topp_slange_til_vannstand is not UNSET:
            field_dict["avstandToppSlangeTilVannstand"] = avstand_topp_slange_til_vannstand
        if barometer_trykk is not UNSET:
            field_dict["barometerTrykk"] = barometer_trykk
        if dybde_grunnvannstand is not UNSET:
            field_dict["dybdeGrunnvannstand"] = dybde_grunnvannstand
        if m_å_le_dato is not UNSET:
            field_dict["måleDato"] = m_å_le_dato
        if m_å_le_tidspunkt is not UNSET:
            field_dict["måleTidspunkt"] = m_å_le_tidspunkt
        if observasjon_kode is not UNSET:
            field_dict["observasjonKode"] = observasjon_kode
        if observasjon_merknad is not UNSET:
            field_dict["observasjonMerknad"] = observasjon_merknad
        if poretrykk is not UNSET:
            field_dict["poretrykk"] = poretrykk
        if trykkhøyde is not UNSET:
            field_dict["trykkhøyde"] = trykkhøyde

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        avlesing_0_kontroll = d.pop("avlesing0Kontroll", UNSET)

        avlesing_etter_0_kontroll = d.pop("avlesingEtter0Kontroll", UNSET)

        avlesing_fø_r_0_kontroll = d.pop("avlesingFør0Kontroll", UNSET)

        avstand_manometer_filterspiss = d.pop("avstandManometerFilterspiss", UNSET)

        avstand_topp_slange_til_vannstand = d.pop("avstandToppSlangeTilVannstand", UNSET)

        barometer_trykk = d.pop("barometerTrykk", UNSET)

        dybde_grunnvannstand = d.pop("dybdeGrunnvannstand", UNSET)

        _m_å_le_dato = d.pop("måleDato", UNSET)
        m_å_le_dato: Union[Unset, datetime.date]
        if isinstance(_m_å_le_dato, Unset):
            m_å_le_dato = UNSET
        else:
            m_å_le_dato = isoparse(_m_å_le_dato).date()

        _m_å_le_tidspunkt = d.pop("måleTidspunkt", UNSET)
        m_å_le_tidspunkt: Union[Unset, datetime.datetime]
        if isinstance(_m_å_le_tidspunkt, Unset):
            m_å_le_tidspunkt = UNSET
        else:
            m_å_le_tidspunkt = isoparse(_m_å_le_tidspunkt)

        observasjon_kode = d.pop("observasjonKode", UNSET)

        observasjon_merknad = d.pop("observasjonMerknad", UNSET)

        poretrykk = d.pop("poretrykk", UNSET)

        trykkhøyde = d.pop("trykkhøyde", UNSET)

        poretrykk_data = cls(
            avlesing_0_kontroll=avlesing_0_kontroll,
            avlesing_etter_0_kontroll=avlesing_etter_0_kontroll,
            avlesing_fø_r_0_kontroll=avlesing_fø_r_0_kontroll,
            avstand_manometer_filterspiss=avstand_manometer_filterspiss,
            avstand_topp_slange_til_vannstand=avstand_topp_slange_til_vannstand,
            barometer_trykk=barometer_trykk,
            dybde_grunnvannstand=dybde_grunnvannstand,
            m_å_le_dato=m_å_le_dato,
            m_å_le_tidspunkt=m_å_le_tidspunkt,
            observasjon_kode=observasjon_kode,
            observasjon_merknad=observasjon_merknad,
            poretrykk=poretrykk,
            trykkhøyde=trykkhøyde,
        )

        poretrykk_data.additional_properties = d
        return poretrykk_data

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
