import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.geoteknisk_grunnvann_observasjon_kode import GeotekniskGrunnvannObservasjonKode
from ..types import UNSET, Unset

T = TypeVar("T", bound="GrunnvannData")


@_attrs_define
class GrunnvannData:
    """data fra måling av grunnvannstand, med observasjonskoder, kommentarer og tidsstempel for angitt
    måletidspunkt<engelsk>data from measurement of ground water level, with observation codes, comments and time for
    measurements</engelsk>

        Attributes:
            m_å_le_dato (Union[Unset, datetime.date]):
            dybde_grunnvannstand (Union[Unset, float]):
            m_å_le_tidspunkt (Union[Unset, datetime.datetime]):
            observasjon_kode (Union[Unset, str]):
            observasjon_merknad (Union[Unset, str]):
            p_h (Union[Unset, float]):
            ledningsevne (Union[Unset, float]):
            oksygen_innhold (Union[Unset, float]):
            temperatur (Union[Unset, float]):
            redoks (Union[Unset, float]):
            turbiditet (Union[Unset, float]):
            boret_lengde (Union[Unset, float]):
            grunnvann_observasjon_kode (Union[Unset, GeotekniskGrunnvannObservasjonKode]): oversikt over observasjonskoder
                for grunnvann
            er_gyldig (Union[Unset, bool]):
    """

    m_å_le_dato: Union[Unset, datetime.date] = UNSET
    dybde_grunnvannstand: Union[Unset, float] = UNSET
    m_å_le_tidspunkt: Union[Unset, datetime.datetime] = UNSET
    observasjon_kode: Union[Unset, str] = UNSET
    observasjon_merknad: Union[Unset, str] = UNSET
    p_h: Union[Unset, float] = UNSET
    ledningsevne: Union[Unset, float] = UNSET
    oksygen_innhold: Union[Unset, float] = UNSET
    temperatur: Union[Unset, float] = UNSET
    redoks: Union[Unset, float] = UNSET
    turbiditet: Union[Unset, float] = UNSET
    boret_lengde: Union[Unset, float] = UNSET
    grunnvann_observasjon_kode: Union[Unset, GeotekniskGrunnvannObservasjonKode] = UNSET
    er_gyldig: Union[Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        m_å_le_dato: Union[Unset, str] = UNSET
        if not isinstance(self.m_å_le_dato, Unset):
            m_å_le_dato = self.m_å_le_dato.isoformat()

        dybde_grunnvannstand = self.dybde_grunnvannstand

        m_å_le_tidspunkt: Union[Unset, str] = UNSET
        if not isinstance(self.m_å_le_tidspunkt, Unset):
            m_å_le_tidspunkt = self.m_å_le_tidspunkt.isoformat()

        observasjon_kode = self.observasjon_kode

        observasjon_merknad = self.observasjon_merknad

        p_h = self.p_h

        ledningsevne = self.ledningsevne

        oksygen_innhold = self.oksygen_innhold

        temperatur = self.temperatur

        redoks = self.redoks

        turbiditet = self.turbiditet

        boret_lengde = self.boret_lengde

        grunnvann_observasjon_kode: Union[Unset, str] = UNSET
        if not isinstance(self.grunnvann_observasjon_kode, Unset):
            grunnvann_observasjon_kode = self.grunnvann_observasjon_kode.value

        er_gyldig = self.er_gyldig

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if m_å_le_dato is not UNSET:
            field_dict["måleDato"] = m_å_le_dato
        if dybde_grunnvannstand is not UNSET:
            field_dict["dybdeGrunnvannstand"] = dybde_grunnvannstand
        if m_å_le_tidspunkt is not UNSET:
            field_dict["måleTidspunkt"] = m_å_le_tidspunkt
        if observasjon_kode is not UNSET:
            field_dict["observasjonKode"] = observasjon_kode
        if observasjon_merknad is not UNSET:
            field_dict["observasjonMerknad"] = observasjon_merknad
        if p_h is not UNSET:
            field_dict["pH"] = p_h
        if ledningsevne is not UNSET:
            field_dict["ledningsevne"] = ledningsevne
        if oksygen_innhold is not UNSET:
            field_dict["oksygenInnhold"] = oksygen_innhold
        if temperatur is not UNSET:
            field_dict["temperatur"] = temperatur
        if redoks is not UNSET:
            field_dict["redoks"] = redoks
        if turbiditet is not UNSET:
            field_dict["turbiditet"] = turbiditet
        if boret_lengde is not UNSET:
            field_dict["boretLengde"] = boret_lengde
        if grunnvann_observasjon_kode is not UNSET:
            field_dict["grunnvannObservasjonKode"] = grunnvann_observasjon_kode
        if er_gyldig is not UNSET:
            field_dict["erGyldig"] = er_gyldig

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

        dybde_grunnvannstand = d.pop("dybdeGrunnvannstand", UNSET)

        _m_å_le_tidspunkt = d.pop("måleTidspunkt", UNSET)
        m_å_le_tidspunkt: Union[Unset, datetime.datetime]
        if isinstance(_m_å_le_tidspunkt, Unset):
            m_å_le_tidspunkt = UNSET
        else:
            m_å_le_tidspunkt = isoparse(_m_å_le_tidspunkt)

        observasjon_kode = d.pop("observasjonKode", UNSET)

        observasjon_merknad = d.pop("observasjonMerknad", UNSET)

        p_h = d.pop("pH", UNSET)

        ledningsevne = d.pop("ledningsevne", UNSET)

        oksygen_innhold = d.pop("oksygenInnhold", UNSET)

        temperatur = d.pop("temperatur", UNSET)

        redoks = d.pop("redoks", UNSET)

        turbiditet = d.pop("turbiditet", UNSET)

        boret_lengde = d.pop("boretLengde", UNSET)

        _grunnvann_observasjon_kode = d.pop("grunnvannObservasjonKode", UNSET)
        grunnvann_observasjon_kode: Union[Unset, GeotekniskGrunnvannObservasjonKode]
        if isinstance(_grunnvann_observasjon_kode, Unset):
            grunnvann_observasjon_kode = UNSET
        else:
            grunnvann_observasjon_kode = GeotekniskGrunnvannObservasjonKode(_grunnvann_observasjon_kode)

        er_gyldig = d.pop("erGyldig", UNSET)

        grunnvann_data = cls(
            m_å_le_dato=m_å_le_dato,
            dybde_grunnvannstand=dybde_grunnvannstand,
            m_å_le_tidspunkt=m_å_le_tidspunkt,
            observasjon_kode=observasjon_kode,
            observasjon_merknad=observasjon_merknad,
            p_h=p_h,
            ledningsevne=ledningsevne,
            oksygen_innhold=oksygen_innhold,
            temperatur=temperatur,
            redoks=redoks,
            turbiditet=turbiditet,
            boret_lengde=boret_lengde,
            grunnvann_observasjon_kode=grunnvann_observasjon_kode,
            er_gyldig=er_gyldig,
        )

        grunnvann_data.additional_properties = d
        return grunnvann_data

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
