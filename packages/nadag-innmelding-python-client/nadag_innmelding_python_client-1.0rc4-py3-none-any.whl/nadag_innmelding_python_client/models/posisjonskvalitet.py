from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.maalemetode import Maalemetode
from ..models.maalemetode_hoeyde import MaalemetodeHoeyde
from ..models.synbarhet import Synbarhet
from ..types import UNSET, Unset

T = TypeVar("T", bound="Posisjonskvalitet")


@_attrs_define
class Posisjonskvalitet:
    """beskrivelse av kvaliteten på stedfestingen

    Attributes:
        målemetode (Maalemetode): metode som ligger til grunn for registrering av posisjon


            -- Definition - -
            method on which registration of position is based
        nøyaktighet (Union[Unset, int]):
        synbarhet (Union[Unset, Synbarhet]): hvor godt den kartlagte detalj var synbar ved kartleggingen
        m_å_lemetode_hø_yde (Union[Unset, MaalemetodeHoeyde]): metode for å måle objekttypens høydeverdi
        n_ø_yaktighet_hø_yde (Union[Unset, int]):
        maksimalt_avvik (Union[Unset, int]):
    """

    målemetode: Maalemetode
    nøyaktighet: Union[Unset, int] = UNSET
    synbarhet: Union[Unset, Synbarhet] = UNSET
    m_å_lemetode_hø_yde: Union[Unset, MaalemetodeHoeyde] = UNSET
    n_ø_yaktighet_hø_yde: Union[Unset, int] = UNSET
    maksimalt_avvik: Union[Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        målemetode = self.målemetode.value

        nøyaktighet = self.nøyaktighet

        synbarhet: Union[Unset, str] = UNSET
        if not isinstance(self.synbarhet, Unset):
            synbarhet = self.synbarhet.value

        m_å_lemetode_hø_yde: Union[Unset, str] = UNSET
        if not isinstance(self.m_å_lemetode_hø_yde, Unset):
            m_å_lemetode_hø_yde = self.m_å_lemetode_hø_yde.value

        n_ø_yaktighet_hø_yde = self.n_ø_yaktighet_hø_yde

        maksimalt_avvik = self.maksimalt_avvik

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "målemetode": målemetode,
            }
        )
        if nøyaktighet is not UNSET:
            field_dict["nøyaktighet"] = nøyaktighet
        if synbarhet is not UNSET:
            field_dict["synbarhet"] = synbarhet
        if m_å_lemetode_hø_yde is not UNSET:
            field_dict["målemetodeHøyde"] = m_å_lemetode_hø_yde
        if n_ø_yaktighet_hø_yde is not UNSET:
            field_dict["nøyaktighetHøyde"] = n_ø_yaktighet_hø_yde
        if maksimalt_avvik is not UNSET:
            field_dict["maksimaltAvvik"] = maksimalt_avvik

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        målemetode = Maalemetode(d.pop("målemetode"))

        nøyaktighet = d.pop("nøyaktighet", UNSET)

        _synbarhet = d.pop("synbarhet", UNSET)
        synbarhet: Union[Unset, Synbarhet]
        if isinstance(_synbarhet, Unset):
            synbarhet = UNSET
        else:
            synbarhet = Synbarhet(_synbarhet)

        _m_å_lemetode_hø_yde = d.pop("målemetodeHøyde", UNSET)
        m_å_lemetode_hø_yde: Union[Unset, MaalemetodeHoeyde]
        if isinstance(_m_å_lemetode_hø_yde, Unset):
            m_å_lemetode_hø_yde = UNSET
        else:
            m_å_lemetode_hø_yde = MaalemetodeHoeyde(_m_å_lemetode_hø_yde)

        n_ø_yaktighet_hø_yde = d.pop("nøyaktighetHøyde", UNSET)

        maksimalt_avvik = d.pop("maksimaltAvvik", UNSET)

        posisjonskvalitet = cls(
            målemetode=målemetode,
            nøyaktighet=nøyaktighet,
            synbarhet=synbarhet,
            m_å_lemetode_hø_yde=m_å_lemetode_hø_yde,
            n_ø_yaktighet_hø_yde=n_ø_yaktighet_hø_yde,
            maksimalt_avvik=maksimalt_avvik,
        )

        posisjonskvalitet.additional_properties = d
        return posisjonskvalitet

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
