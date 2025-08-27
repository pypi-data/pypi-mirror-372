import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.deformasjon_observasjon_kode import DeformasjonObservasjonKode
from ..types import UNSET, Unset

T = TypeVar("T", bound="DeformasjonMaaleData")


@_attrs_define
class DeformasjonMaaleData:
    """data fra måling av setning ved angitt måletidspunkt<engelsk>data from measurements of settlements at a given
    time</engelsk>

        Attributes:
            m_å_le_dato (Union[Unset, datetime.date]):
            m_å_le_tidspunkt (Union[Unset, datetime.datetime]):
            deformasjon_observasjon_kode (Union[Unset, DeformasjonObservasjonKode]): Kodeliste for å angi
                deformasjonsobservasjon
            observasjon_merknad (Union[Unset, str]):
            setning (Union[Unset, float]):
            deformasjon_x (Union[Unset, float]):
            deformasjon_y (Union[Unset, float]):
            deformasjon_z (Union[Unset, float]):
            er_gyldig (Union[Unset, bool]):
            boret_lengde (Union[Unset, float]):
            observasjon_kode (Union[Unset, str]):
    """

    m_å_le_dato: Union[Unset, datetime.date] = UNSET
    m_å_le_tidspunkt: Union[Unset, datetime.datetime] = UNSET
    deformasjon_observasjon_kode: Union[Unset, DeformasjonObservasjonKode] = UNSET
    observasjon_merknad: Union[Unset, str] = UNSET
    setning: Union[Unset, float] = UNSET
    deformasjon_x: Union[Unset, float] = UNSET
    deformasjon_y: Union[Unset, float] = UNSET
    deformasjon_z: Union[Unset, float] = UNSET
    er_gyldig: Union[Unset, bool] = UNSET
    boret_lengde: Union[Unset, float] = UNSET
    observasjon_kode: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        m_å_le_dato: Union[Unset, str] = UNSET
        if not isinstance(self.m_å_le_dato, Unset):
            m_å_le_dato = self.m_å_le_dato.isoformat()

        m_å_le_tidspunkt: Union[Unset, str] = UNSET
        if not isinstance(self.m_å_le_tidspunkt, Unset):
            m_å_le_tidspunkt = self.m_å_le_tidspunkt.isoformat()

        deformasjon_observasjon_kode: Union[Unset, str] = UNSET
        if not isinstance(self.deformasjon_observasjon_kode, Unset):
            deformasjon_observasjon_kode = self.deformasjon_observasjon_kode.value

        observasjon_merknad = self.observasjon_merknad

        setning = self.setning

        deformasjon_x = self.deformasjon_x

        deformasjon_y = self.deformasjon_y

        deformasjon_z = self.deformasjon_z

        er_gyldig = self.er_gyldig

        boret_lengde = self.boret_lengde

        observasjon_kode = self.observasjon_kode

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if m_å_le_dato is not UNSET:
            field_dict["måleDato"] = m_å_le_dato
        if m_å_le_tidspunkt is not UNSET:
            field_dict["måleTidspunkt"] = m_å_le_tidspunkt
        if deformasjon_observasjon_kode is not UNSET:
            field_dict["deformasjonObservasjonKode"] = deformasjon_observasjon_kode
        if observasjon_merknad is not UNSET:
            field_dict["observasjonMerknad"] = observasjon_merknad
        if setning is not UNSET:
            field_dict["setning"] = setning
        if deformasjon_x is not UNSET:
            field_dict["deformasjonX"] = deformasjon_x
        if deformasjon_y is not UNSET:
            field_dict["deformasjonY"] = deformasjon_y
        if deformasjon_z is not UNSET:
            field_dict["deformasjonZ"] = deformasjon_z
        if er_gyldig is not UNSET:
            field_dict["erGyldig"] = er_gyldig
        if boret_lengde is not UNSET:
            field_dict["boretLengde"] = boret_lengde
        if observasjon_kode is not UNSET:
            field_dict["observasjonKode"] = observasjon_kode

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
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

        _deformasjon_observasjon_kode = d.pop("deformasjonObservasjonKode", UNSET)
        deformasjon_observasjon_kode: Union[Unset, DeformasjonObservasjonKode]
        if isinstance(_deformasjon_observasjon_kode, Unset):
            deformasjon_observasjon_kode = UNSET
        else:
            deformasjon_observasjon_kode = DeformasjonObservasjonKode(_deformasjon_observasjon_kode)

        observasjon_merknad = d.pop("observasjonMerknad", UNSET)

        setning = d.pop("setning", UNSET)

        deformasjon_x = d.pop("deformasjonX", UNSET)

        deformasjon_y = d.pop("deformasjonY", UNSET)

        deformasjon_z = d.pop("deformasjonZ", UNSET)

        er_gyldig = d.pop("erGyldig", UNSET)

        boret_lengde = d.pop("boretLengde", UNSET)

        observasjon_kode = d.pop("observasjonKode", UNSET)

        deformasjon_maale_data = cls(
            m_å_le_dato=m_å_le_dato,
            m_å_le_tidspunkt=m_å_le_tidspunkt,
            deformasjon_observasjon_kode=deformasjon_observasjon_kode,
            observasjon_merknad=observasjon_merknad,
            setning=setning,
            deformasjon_x=deformasjon_x,
            deformasjon_y=deformasjon_y,
            deformasjon_z=deformasjon_z,
            er_gyldig=er_gyldig,
            boret_lengde=boret_lengde,
            observasjon_kode=observasjon_kode,
        )

        deformasjon_maale_data.additional_properties = d
        return deformasjon_maale_data

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
