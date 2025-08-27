from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.lag_posisjon import LagPosisjon
from ..types import UNSET, Unset

T = TypeVar("T", bound="GeotekniskProeveseriedelData")


@_attrs_define
class GeotekniskProeveseriedelData:
    """Data som tilhører en geoteknisk prøveseriedel

    Attributes:
        lag_posisjon (Union[Unset, LagPosisjon]): kodeliste som brukes for å fortelle i hvilken del av prøvedelen som
            det er gjort undersøkelser
        pr_ø_ve_metode (Union[Unset, str]):
        aksiel_deformasjon (Union[Unset, float]):
        skj_æ_rfasthet_udrenert (Union[Unset, float]):
        detaljert_lag_sammensetning (Union[Unset, str]):
        skj_æ_rfasthet_omr_ø_rt (Union[Unset, float]):
        densitet_pr_ø_vetaking (Union[Unset, float]):
        er_omr_ø_rt (Union[Unset, bool]):
        lab_analyse (Union[Unset, bool]):
        flyte_grense (Union[Unset, float]):
        gl_ø_de_tap (Union[Unset, float]):
        plastitets_grense (Union[Unset, float]):
        sensitivitet (Union[Unset, float]):
        skj_æ_rfasthet_uforstyrret (Union[Unset, float]):
        boret_lengde (Union[Unset, float]):
        vanninnhold (Union[Unset, float]):
        observasjon_kode (Union[Unset, str]):
        observasjon_merknad (Union[Unset, str]):
    """

    lag_posisjon: Union[Unset, LagPosisjon] = UNSET
    pr_ø_ve_metode: Union[Unset, str] = UNSET
    aksiel_deformasjon: Union[Unset, float] = UNSET
    skj_æ_rfasthet_udrenert: Union[Unset, float] = UNSET
    detaljert_lag_sammensetning: Union[Unset, str] = UNSET
    skj_æ_rfasthet_omr_ø_rt: Union[Unset, float] = UNSET
    densitet_pr_ø_vetaking: Union[Unset, float] = UNSET
    er_omr_ø_rt: Union[Unset, bool] = UNSET
    lab_analyse: Union[Unset, bool] = UNSET
    flyte_grense: Union[Unset, float] = UNSET
    gl_ø_de_tap: Union[Unset, float] = UNSET
    plastitets_grense: Union[Unset, float] = UNSET
    sensitivitet: Union[Unset, float] = UNSET
    skj_æ_rfasthet_uforstyrret: Union[Unset, float] = UNSET
    boret_lengde: Union[Unset, float] = UNSET
    vanninnhold: Union[Unset, float] = UNSET
    observasjon_kode: Union[Unset, str] = UNSET
    observasjon_merknad: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        lag_posisjon: Union[Unset, str] = UNSET
        if not isinstance(self.lag_posisjon, Unset):
            lag_posisjon = self.lag_posisjon.value

        pr_ø_ve_metode = self.pr_ø_ve_metode

        aksiel_deformasjon = self.aksiel_deformasjon

        skj_æ_rfasthet_udrenert = self.skj_æ_rfasthet_udrenert

        detaljert_lag_sammensetning = self.detaljert_lag_sammensetning

        skj_æ_rfasthet_omr_ø_rt = self.skj_æ_rfasthet_omr_ø_rt

        densitet_pr_ø_vetaking = self.densitet_pr_ø_vetaking

        er_omr_ø_rt = self.er_omr_ø_rt

        lab_analyse = self.lab_analyse

        flyte_grense = self.flyte_grense

        gl_ø_de_tap = self.gl_ø_de_tap

        plastitets_grense = self.plastitets_grense

        sensitivitet = self.sensitivitet

        skj_æ_rfasthet_uforstyrret = self.skj_æ_rfasthet_uforstyrret

        boret_lengde = self.boret_lengde

        vanninnhold = self.vanninnhold

        observasjon_kode = self.observasjon_kode

        observasjon_merknad = self.observasjon_merknad

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if lag_posisjon is not UNSET:
            field_dict["lagPosisjon"] = lag_posisjon
        if pr_ø_ve_metode is not UNSET:
            field_dict["prøveMetode"] = pr_ø_ve_metode
        if aksiel_deformasjon is not UNSET:
            field_dict["aksielDeformasjon"] = aksiel_deformasjon
        if skj_æ_rfasthet_udrenert is not UNSET:
            field_dict["skjærfasthetUdrenert"] = skj_æ_rfasthet_udrenert
        if detaljert_lag_sammensetning is not UNSET:
            field_dict["detaljertLagSammensetning"] = detaljert_lag_sammensetning
        if skj_æ_rfasthet_omr_ø_rt is not UNSET:
            field_dict["skjærfasthetOmrørt"] = skj_æ_rfasthet_omr_ø_rt
        if densitet_pr_ø_vetaking is not UNSET:
            field_dict["densitetPrøvetaking"] = densitet_pr_ø_vetaking
        if er_omr_ø_rt is not UNSET:
            field_dict["erOmrørt"] = er_omr_ø_rt
        if lab_analyse is not UNSET:
            field_dict["labAnalyse"] = lab_analyse
        if flyte_grense is not UNSET:
            field_dict["flyteGrense"] = flyte_grense
        if gl_ø_de_tap is not UNSET:
            field_dict["glødeTap"] = gl_ø_de_tap
        if plastitets_grense is not UNSET:
            field_dict["plastitetsGrense"] = plastitets_grense
        if sensitivitet is not UNSET:
            field_dict["sensitivitet"] = sensitivitet
        if skj_æ_rfasthet_uforstyrret is not UNSET:
            field_dict["skjærfasthetUforstyrret"] = skj_æ_rfasthet_uforstyrret
        if boret_lengde is not UNSET:
            field_dict["boretLengde"] = boret_lengde
        if vanninnhold is not UNSET:
            field_dict["vanninnhold"] = vanninnhold
        if observasjon_kode is not UNSET:
            field_dict["observasjonKode"] = observasjon_kode
        if observasjon_merknad is not UNSET:
            field_dict["observasjonMerknad"] = observasjon_merknad

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        _lag_posisjon = d.pop("lagPosisjon", UNSET)
        lag_posisjon: Union[Unset, LagPosisjon]
        if isinstance(_lag_posisjon, Unset):
            lag_posisjon = UNSET
        else:
            lag_posisjon = LagPosisjon(_lag_posisjon)

        pr_ø_ve_metode = d.pop("prøveMetode", UNSET)

        aksiel_deformasjon = d.pop("aksielDeformasjon", UNSET)

        skj_æ_rfasthet_udrenert = d.pop("skjærfasthetUdrenert", UNSET)

        detaljert_lag_sammensetning = d.pop("detaljertLagSammensetning", UNSET)

        skj_æ_rfasthet_omr_ø_rt = d.pop("skjærfasthetOmrørt", UNSET)

        densitet_pr_ø_vetaking = d.pop("densitetPrøvetaking", UNSET)

        er_omr_ø_rt = d.pop("erOmrørt", UNSET)

        lab_analyse = d.pop("labAnalyse", UNSET)

        flyte_grense = d.pop("flyteGrense", UNSET)

        gl_ø_de_tap = d.pop("glødeTap", UNSET)

        plastitets_grense = d.pop("plastitetsGrense", UNSET)

        sensitivitet = d.pop("sensitivitet", UNSET)

        skj_æ_rfasthet_uforstyrret = d.pop("skjærfasthetUforstyrret", UNSET)

        boret_lengde = d.pop("boretLengde", UNSET)

        vanninnhold = d.pop("vanninnhold", UNSET)

        observasjon_kode = d.pop("observasjonKode", UNSET)

        observasjon_merknad = d.pop("observasjonMerknad", UNSET)

        geoteknisk_proeveseriedel_data = cls(
            lag_posisjon=lag_posisjon,
            pr_ø_ve_metode=pr_ø_ve_metode,
            aksiel_deformasjon=aksiel_deformasjon,
            skj_æ_rfasthet_udrenert=skj_æ_rfasthet_udrenert,
            detaljert_lag_sammensetning=detaljert_lag_sammensetning,
            skj_æ_rfasthet_omr_ø_rt=skj_æ_rfasthet_omr_ø_rt,
            densitet_pr_ø_vetaking=densitet_pr_ø_vetaking,
            er_omr_ø_rt=er_omr_ø_rt,
            lab_analyse=lab_analyse,
            flyte_grense=flyte_grense,
            gl_ø_de_tap=gl_ø_de_tap,
            plastitets_grense=plastitets_grense,
            sensitivitet=sensitivitet,
            skj_æ_rfasthet_uforstyrret=skj_æ_rfasthet_uforstyrret,
            boret_lengde=boret_lengde,
            vanninnhold=vanninnhold,
            observasjon_kode=observasjon_kode,
            observasjon_merknad=observasjon_merknad,
        )

        geoteknisk_proeveseriedel_data.additional_properties = d
        return geoteknisk_proeveseriedel_data

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
