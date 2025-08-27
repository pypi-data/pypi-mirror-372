from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="VingeboringData")


@_attrs_define
class VingeboringData:
    """data fra utførelse og tolkning av vingeboring<engelsk>data from performance and interpretation of vane
    tests</engelsk>

        Attributes:
            boret_dybde (Union[Unset, float]):
            effektiv_densitet (Union[Unset, float]):
            korrigert_skj_æ_rfasthet (Union[Unset, float]):
            observasjon_kode (Union[Unset, str]):
            observasjon_merknad (Union[Unset, str]):
            omr_ø_rt_skj_æ_rfasthet (Union[Unset, float]):
            omr_ø_rt_torsjon_moment (Union[Unset, float]):
            sensitivitet (Union[Unset, float]):
            uomr_ø_rt_skj_æ_rfasthet (Union[Unset, float]):
            uomr_ø_rt_torsjon_moment (Union[Unset, float]):
            boret_lengde (Union[Unset, float]):
            plastisitet_indeks (Union[Unset, float]):
    """

    boret_dybde: Union[Unset, float] = UNSET
    effektiv_densitet: Union[Unset, float] = UNSET
    korrigert_skj_æ_rfasthet: Union[Unset, float] = UNSET
    observasjon_kode: Union[Unset, str] = UNSET
    observasjon_merknad: Union[Unset, str] = UNSET
    omr_ø_rt_skj_æ_rfasthet: Union[Unset, float] = UNSET
    omr_ø_rt_torsjon_moment: Union[Unset, float] = UNSET
    sensitivitet: Union[Unset, float] = UNSET
    uomr_ø_rt_skj_æ_rfasthet: Union[Unset, float] = UNSET
    uomr_ø_rt_torsjon_moment: Union[Unset, float] = UNSET
    boret_lengde: Union[Unset, float] = UNSET
    plastisitet_indeks: Union[Unset, float] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        boret_dybde = self.boret_dybde

        effektiv_densitet = self.effektiv_densitet

        korrigert_skj_æ_rfasthet = self.korrigert_skj_æ_rfasthet

        observasjon_kode = self.observasjon_kode

        observasjon_merknad = self.observasjon_merknad

        omr_ø_rt_skj_æ_rfasthet = self.omr_ø_rt_skj_æ_rfasthet

        omr_ø_rt_torsjon_moment = self.omr_ø_rt_torsjon_moment

        sensitivitet = self.sensitivitet

        uomr_ø_rt_skj_æ_rfasthet = self.uomr_ø_rt_skj_æ_rfasthet

        uomr_ø_rt_torsjon_moment = self.uomr_ø_rt_torsjon_moment

        boret_lengde = self.boret_lengde

        plastisitet_indeks = self.plastisitet_indeks

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if boret_dybde is not UNSET:
            field_dict["boretDybde"] = boret_dybde
        if effektiv_densitet is not UNSET:
            field_dict["effektivDensitet"] = effektiv_densitet
        if korrigert_skj_æ_rfasthet is not UNSET:
            field_dict["korrigertSkjærfasthet"] = korrigert_skj_æ_rfasthet
        if observasjon_kode is not UNSET:
            field_dict["observasjonKode"] = observasjon_kode
        if observasjon_merknad is not UNSET:
            field_dict["observasjonMerknad"] = observasjon_merknad
        if omr_ø_rt_skj_æ_rfasthet is not UNSET:
            field_dict["omrørtSkjærfasthet"] = omr_ø_rt_skj_æ_rfasthet
        if omr_ø_rt_torsjon_moment is not UNSET:
            field_dict["omrørtTorsjonMoment"] = omr_ø_rt_torsjon_moment
        if sensitivitet is not UNSET:
            field_dict["sensitivitet"] = sensitivitet
        if uomr_ø_rt_skj_æ_rfasthet is not UNSET:
            field_dict["uomrørtSkjærfasthet"] = uomr_ø_rt_skj_æ_rfasthet
        if uomr_ø_rt_torsjon_moment is not UNSET:
            field_dict["uomrørtTorsjonMoment"] = uomr_ø_rt_torsjon_moment
        if boret_lengde is not UNSET:
            field_dict["boretLengde"] = boret_lengde
        if plastisitet_indeks is not UNSET:
            field_dict["plastisitetIndeks"] = plastisitet_indeks

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        boret_dybde = d.pop("boretDybde", UNSET)

        effektiv_densitet = d.pop("effektivDensitet", UNSET)

        korrigert_skj_æ_rfasthet = d.pop("korrigertSkjærfasthet", UNSET)

        observasjon_kode = d.pop("observasjonKode", UNSET)

        observasjon_merknad = d.pop("observasjonMerknad", UNSET)

        omr_ø_rt_skj_æ_rfasthet = d.pop("omrørtSkjærfasthet", UNSET)

        omr_ø_rt_torsjon_moment = d.pop("omrørtTorsjonMoment", UNSET)

        sensitivitet = d.pop("sensitivitet", UNSET)

        uomr_ø_rt_skj_æ_rfasthet = d.pop("uomrørtSkjærfasthet", UNSET)

        uomr_ø_rt_torsjon_moment = d.pop("uomrørtTorsjonMoment", UNSET)

        boret_lengde = d.pop("boretLengde", UNSET)

        plastisitet_indeks = d.pop("plastisitetIndeks", UNSET)

        vingeboring_data = cls(
            boret_dybde=boret_dybde,
            effektiv_densitet=effektiv_densitet,
            korrigert_skj_æ_rfasthet=korrigert_skj_æ_rfasthet,
            observasjon_kode=observasjon_kode,
            observasjon_merknad=observasjon_merknad,
            omr_ø_rt_skj_æ_rfasthet=omr_ø_rt_skj_æ_rfasthet,
            omr_ø_rt_torsjon_moment=omr_ø_rt_torsjon_moment,
            sensitivitet=sensitivitet,
            uomr_ø_rt_skj_æ_rfasthet=uomr_ø_rt_skj_æ_rfasthet,
            uomr_ø_rt_torsjon_moment=uomr_ø_rt_torsjon_moment,
            boret_lengde=boret_lengde,
            plastisitet_indeks=plastisitet_indeks,
        )

        vingeboring_data.additional_properties = d
        return vingeboring_data

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
