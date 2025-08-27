from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="KjerneBoringData")


@_attrs_define
class KjerneBoringData:
    """Data som tilhører en Kjerneboring

    Attributes:
        boret_lengde (Union[Unset, float]):
        forvitringsgrad (Union[Unset, str]):
        geologisk_material_tekst (Union[Unset, str]):
        geologisk_material_type (Union[Unset, str]):
        kjerne_opptak_prosent (Union[Unset, int]):
        material_struktur (Union[Unset, str]):
        observasjon_kode (Union[Unset, str]):
        observasjon_merknad (Union[Unset, str]):
        opptrekk (Union[Unset, str]):
        q_verdi_ja (Union[Unset, float]):
        q_verdi_jn (Union[Unset, float]):
        q_verdi_jr (Union[Unset, float]):
        q_verdi_jw (Union[Unset, float]):
        q_verdi_q (Union[Unset, float]):
        q_verdi_q_er_beregnet (Union[Unset, bool]):
        q_verdi_rqd (Union[Unset, float]):
        q_verdi_srf (Union[Unset, float]):
        rock_mass_rating (Union[Unset, int]):
        ruhetsindeks (Union[Unset, int]):
        sprekke_frekvens (Union[Unset, float]):
        sprekke_material_tekst (Union[Unset, str]):
        sprekke_material_type (Union[Unset, str]):
        str_ø_k_fall_fall (Union[Unset, int]):
        str_ø_k_fall_str_ø_k (Union[Unset, int]):
    """

    boret_lengde: Union[Unset, float] = UNSET
    forvitringsgrad: Union[Unset, str] = UNSET
    geologisk_material_tekst: Union[Unset, str] = UNSET
    geologisk_material_type: Union[Unset, str] = UNSET
    kjerne_opptak_prosent: Union[Unset, int] = UNSET
    material_struktur: Union[Unset, str] = UNSET
    observasjon_kode: Union[Unset, str] = UNSET
    observasjon_merknad: Union[Unset, str] = UNSET
    opptrekk: Union[Unset, str] = UNSET
    q_verdi_ja: Union[Unset, float] = UNSET
    q_verdi_jn: Union[Unset, float] = UNSET
    q_verdi_jr: Union[Unset, float] = UNSET
    q_verdi_jw: Union[Unset, float] = UNSET
    q_verdi_q: Union[Unset, float] = UNSET
    q_verdi_q_er_beregnet: Union[Unset, bool] = UNSET
    q_verdi_rqd: Union[Unset, float] = UNSET
    q_verdi_srf: Union[Unset, float] = UNSET
    rock_mass_rating: Union[Unset, int] = UNSET
    ruhetsindeks: Union[Unset, int] = UNSET
    sprekke_frekvens: Union[Unset, float] = UNSET
    sprekke_material_tekst: Union[Unset, str] = UNSET
    sprekke_material_type: Union[Unset, str] = UNSET
    str_ø_k_fall_fall: Union[Unset, int] = UNSET
    str_ø_k_fall_str_ø_k: Union[Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        boret_lengde = self.boret_lengde

        forvitringsgrad = self.forvitringsgrad

        geologisk_material_tekst = self.geologisk_material_tekst

        geologisk_material_type = self.geologisk_material_type

        kjerne_opptak_prosent = self.kjerne_opptak_prosent

        material_struktur = self.material_struktur

        observasjon_kode = self.observasjon_kode

        observasjon_merknad = self.observasjon_merknad

        opptrekk = self.opptrekk

        q_verdi_ja = self.q_verdi_ja

        q_verdi_jn = self.q_verdi_jn

        q_verdi_jr = self.q_verdi_jr

        q_verdi_jw = self.q_verdi_jw

        q_verdi_q = self.q_verdi_q

        q_verdi_q_er_beregnet = self.q_verdi_q_er_beregnet

        q_verdi_rqd = self.q_verdi_rqd

        q_verdi_srf = self.q_verdi_srf

        rock_mass_rating = self.rock_mass_rating

        ruhetsindeks = self.ruhetsindeks

        sprekke_frekvens = self.sprekke_frekvens

        sprekke_material_tekst = self.sprekke_material_tekst

        sprekke_material_type = self.sprekke_material_type

        str_ø_k_fall_fall = self.str_ø_k_fall_fall

        str_ø_k_fall_str_ø_k = self.str_ø_k_fall_str_ø_k

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if boret_lengde is not UNSET:
            field_dict["boretLengde"] = boret_lengde
        if forvitringsgrad is not UNSET:
            field_dict["forvitringsgrad"] = forvitringsgrad
        if geologisk_material_tekst is not UNSET:
            field_dict["geologiskMaterialTekst"] = geologisk_material_tekst
        if geologisk_material_type is not UNSET:
            field_dict["geologiskMaterialType"] = geologisk_material_type
        if kjerne_opptak_prosent is not UNSET:
            field_dict["kjerneOpptak_Prosent"] = kjerne_opptak_prosent
        if material_struktur is not UNSET:
            field_dict["materialStruktur"] = material_struktur
        if observasjon_kode is not UNSET:
            field_dict["observasjonKode"] = observasjon_kode
        if observasjon_merknad is not UNSET:
            field_dict["observasjonMerknad"] = observasjon_merknad
        if opptrekk is not UNSET:
            field_dict["opptrekk"] = opptrekk
        if q_verdi_ja is not UNSET:
            field_dict["QVerdi_Ja"] = q_verdi_ja
        if q_verdi_jn is not UNSET:
            field_dict["QVerdi_Jn"] = q_verdi_jn
        if q_verdi_jr is not UNSET:
            field_dict["QVerdi_Jr"] = q_verdi_jr
        if q_verdi_jw is not UNSET:
            field_dict["QVerdi_Jw"] = q_verdi_jw
        if q_verdi_q is not UNSET:
            field_dict["QVerdi_Q"] = q_verdi_q
        if q_verdi_q_er_beregnet is not UNSET:
            field_dict["QVerdi_QErBeregnet"] = q_verdi_q_er_beregnet
        if q_verdi_rqd is not UNSET:
            field_dict["QVerdi_RQD"] = q_verdi_rqd
        if q_verdi_srf is not UNSET:
            field_dict["QVerdi_SRF"] = q_verdi_srf
        if rock_mass_rating is not UNSET:
            field_dict["RockMassRating"] = rock_mass_rating
        if ruhetsindeks is not UNSET:
            field_dict["ruhetsindeks"] = ruhetsindeks
        if sprekke_frekvens is not UNSET:
            field_dict["sprekkeFrekvens"] = sprekke_frekvens
        if sprekke_material_tekst is not UNSET:
            field_dict["sprekkeMaterialTekst"] = sprekke_material_tekst
        if sprekke_material_type is not UNSET:
            field_dict["sprekkeMaterialType"] = sprekke_material_type
        if str_ø_k_fall_fall is not UNSET:
            field_dict["strøkFall_Fall"] = str_ø_k_fall_fall
        if str_ø_k_fall_str_ø_k is not UNSET:
            field_dict["strøkFall_Strøk"] = str_ø_k_fall_str_ø_k

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        boret_lengde = d.pop("boretLengde", UNSET)

        forvitringsgrad = d.pop("forvitringsgrad", UNSET)

        geologisk_material_tekst = d.pop("geologiskMaterialTekst", UNSET)

        geologisk_material_type = d.pop("geologiskMaterialType", UNSET)

        kjerne_opptak_prosent = d.pop("kjerneOpptak_Prosent", UNSET)

        material_struktur = d.pop("materialStruktur", UNSET)

        observasjon_kode = d.pop("observasjonKode", UNSET)

        observasjon_merknad = d.pop("observasjonMerknad", UNSET)

        opptrekk = d.pop("opptrekk", UNSET)

        q_verdi_ja = d.pop("QVerdi_Ja", UNSET)

        q_verdi_jn = d.pop("QVerdi_Jn", UNSET)

        q_verdi_jr = d.pop("QVerdi_Jr", UNSET)

        q_verdi_jw = d.pop("QVerdi_Jw", UNSET)

        q_verdi_q = d.pop("QVerdi_Q", UNSET)

        q_verdi_q_er_beregnet = d.pop("QVerdi_QErBeregnet", UNSET)

        q_verdi_rqd = d.pop("QVerdi_RQD", UNSET)

        q_verdi_srf = d.pop("QVerdi_SRF", UNSET)

        rock_mass_rating = d.pop("RockMassRating", UNSET)

        ruhetsindeks = d.pop("ruhetsindeks", UNSET)

        sprekke_frekvens = d.pop("sprekkeFrekvens", UNSET)

        sprekke_material_tekst = d.pop("sprekkeMaterialTekst", UNSET)

        sprekke_material_type = d.pop("sprekkeMaterialType", UNSET)

        str_ø_k_fall_fall = d.pop("strøkFall_Fall", UNSET)

        str_ø_k_fall_str_ø_k = d.pop("strøkFall_Strøk", UNSET)

        kjerne_boring_data = cls(
            boret_lengde=boret_lengde,
            forvitringsgrad=forvitringsgrad,
            geologisk_material_tekst=geologisk_material_tekst,
            geologisk_material_type=geologisk_material_type,
            kjerne_opptak_prosent=kjerne_opptak_prosent,
            material_struktur=material_struktur,
            observasjon_kode=observasjon_kode,
            observasjon_merknad=observasjon_merknad,
            opptrekk=opptrekk,
            q_verdi_ja=q_verdi_ja,
            q_verdi_jn=q_verdi_jn,
            q_verdi_jr=q_verdi_jr,
            q_verdi_jw=q_verdi_jw,
            q_verdi_q=q_verdi_q,
            q_verdi_q_er_beregnet=q_verdi_q_er_beregnet,
            q_verdi_rqd=q_verdi_rqd,
            q_verdi_srf=q_verdi_srf,
            rock_mass_rating=rock_mass_rating,
            ruhetsindeks=ruhetsindeks,
            sprekke_frekvens=sprekke_frekvens,
            sprekke_material_tekst=sprekke_material_tekst,
            sprekke_material_type=sprekke_material_type,
            str_ø_k_fall_fall=str_ø_k_fall_fall,
            str_ø_k_fall_str_ø_k=str_ø_k_fall_str_ø_k,
        )

        kjerne_boring_data.additional_properties = d
        return kjerne_boring_data

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
