import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.hydraulisk_konduktivitet import HydrauliskKonduktivitet
from ..types import UNSET, Unset

T = TypeVar("T", bound="HydrauliskeData")


@_attrs_define
class HydrauliskeData:
    """data fra måling av vannstrømning, vannhastighetsbestemmelse og hydraulisk splitting i felt.
    <engelsk>data from measurements of water flow, water velocity, pumping tests and hydraulic splitting in the field.
    </engelsk>

        Attributes:
            m_å_le_dato (Union[Unset, datetime.date]):
            m_å_le_tidspunkt (Union[Unset, datetime.datetime]):
            observasjon_merknad (Union[Unset, str]):
            hydraulisk_konduktivitet (Union[Unset, HydrauliskKonduktivitet]): proporsjonalitetskonstant som relaterer
                vannstrømningsrate gjennom et medium til gradienten

                Merknad: Kalles også hydraulisk ledningsevne og avhenger av både vannets og mediets egenskaper.

                <engelsk>proportionality constant which relates water permeability through a medium with the gradient</engelsk>
            dybde_grunnvannstand (Union[Unset, float]):
    """

    m_å_le_dato: Union[Unset, datetime.date] = UNSET
    m_å_le_tidspunkt: Union[Unset, datetime.datetime] = UNSET
    observasjon_merknad: Union[Unset, str] = UNSET
    hydraulisk_konduktivitet: Union[Unset, HydrauliskKonduktivitet] = UNSET
    dybde_grunnvannstand: Union[Unset, float] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        m_å_le_dato: Union[Unset, str] = UNSET
        if not isinstance(self.m_å_le_dato, Unset):
            m_å_le_dato = self.m_å_le_dato.isoformat()

        m_å_le_tidspunkt: Union[Unset, str] = UNSET
        if not isinstance(self.m_å_le_tidspunkt, Unset):
            m_å_le_tidspunkt = self.m_å_le_tidspunkt.isoformat()

        observasjon_merknad = self.observasjon_merknad

        hydraulisk_konduktivitet: Union[Unset, str] = UNSET
        if not isinstance(self.hydraulisk_konduktivitet, Unset):
            hydraulisk_konduktivitet = self.hydraulisk_konduktivitet.value

        dybde_grunnvannstand = self.dybde_grunnvannstand

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if m_å_le_dato is not UNSET:
            field_dict["måleDato"] = m_å_le_dato
        if m_å_le_tidspunkt is not UNSET:
            field_dict["måleTidspunkt"] = m_å_le_tidspunkt
        if observasjon_merknad is not UNSET:
            field_dict["observasjonMerknad"] = observasjon_merknad
        if hydraulisk_konduktivitet is not UNSET:
            field_dict["hydrauliskKonduktivitet"] = hydraulisk_konduktivitet
        if dybde_grunnvannstand is not UNSET:
            field_dict["dybdeGrunnvannstand"] = dybde_grunnvannstand

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

        observasjon_merknad = d.pop("observasjonMerknad", UNSET)

        _hydraulisk_konduktivitet = d.pop("hydrauliskKonduktivitet", UNSET)
        hydraulisk_konduktivitet: Union[Unset, HydrauliskKonduktivitet]
        if isinstance(_hydraulisk_konduktivitet, Unset):
            hydraulisk_konduktivitet = UNSET
        else:
            hydraulisk_konduktivitet = HydrauliskKonduktivitet(_hydraulisk_konduktivitet)

        dybde_grunnvannstand = d.pop("dybdeGrunnvannstand", UNSET)

        hydrauliske_data = cls(
            m_å_le_dato=m_å_le_dato,
            m_å_le_tidspunkt=m_å_le_tidspunkt,
            observasjon_merknad=observasjon_merknad,
            hydraulisk_konduktivitet=hydraulisk_konduktivitet,
            dybde_grunnvannstand=dybde_grunnvannstand,
        )

        hydrauliske_data.additional_properties = d
        return hydrauliske_data

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
