from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.maalemetode import Maalemetode
from ..models.maalemetode_hoeyde import MaalemetodeHoeyde
from ..types import UNSET, Unset

T = TypeVar("T", bound="PosisjonskvalitetNADAG")


@_attrs_define
class PosisjonskvalitetNADAG:
    """Posisjonskvalitet slik den brukes i NADAG (Nasjonal Database for Grunnundersøkelser).
    (En realisering av den generelle Posisjonskvalitet)

        Attributes:
            målemetode (Maalemetode): metode som ligger til grunn for registrering av posisjon


                -- Definition - -
                method on which registration of position is based
            m_å_lemetode_hø_yde (Union[Unset, MaalemetodeHoeyde]): metode for å måle objekttypens høydeverdi
            nøyaktighet (Union[Unset, int]):
            n_ø_yaktighet_hø_yde (Union[Unset, int]):
    """

    målemetode: Maalemetode
    m_å_lemetode_hø_yde: Union[Unset, MaalemetodeHoeyde] = UNSET
    nøyaktighet: Union[Unset, int] = UNSET
    n_ø_yaktighet_hø_yde: Union[Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        målemetode = self.målemetode.value

        m_å_lemetode_hø_yde: Union[Unset, str] = UNSET
        if not isinstance(self.m_å_lemetode_hø_yde, Unset):
            m_å_lemetode_hø_yde = self.m_å_lemetode_hø_yde.value

        nøyaktighet = self.nøyaktighet

        n_ø_yaktighet_hø_yde = self.n_ø_yaktighet_hø_yde

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "målemetode": målemetode,
            }
        )
        if m_å_lemetode_hø_yde is not UNSET:
            field_dict["målemetodeHøyde"] = m_å_lemetode_hø_yde
        if nøyaktighet is not UNSET:
            field_dict["nøyaktighet"] = nøyaktighet
        if n_ø_yaktighet_hø_yde is not UNSET:
            field_dict["nøyaktighetHøyde"] = n_ø_yaktighet_hø_yde

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        målemetode = Maalemetode(d.pop("målemetode"))

        _m_å_lemetode_hø_yde = d.pop("målemetodeHøyde", UNSET)
        m_å_lemetode_hø_yde: Union[Unset, MaalemetodeHoeyde]
        if isinstance(_m_å_lemetode_hø_yde, Unset):
            m_å_lemetode_hø_yde = UNSET
        else:
            m_å_lemetode_hø_yde = MaalemetodeHoeyde(_m_å_lemetode_hø_yde)

        nøyaktighet = d.pop("nøyaktighet", UNSET)

        n_ø_yaktighet_hø_yde = d.pop("nøyaktighetHøyde", UNSET)

        posisjonskvalitet_nadag = cls(
            målemetode=målemetode,
            m_å_lemetode_hø_yde=m_å_lemetode_hø_yde,
            nøyaktighet=nøyaktighet,
            n_ø_yaktighet_hø_yde=n_ø_yaktighet_hø_yde,
        )

        posisjonskvalitet_nadag.additional_properties = d
        return posisjonskvalitet_nadag

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
