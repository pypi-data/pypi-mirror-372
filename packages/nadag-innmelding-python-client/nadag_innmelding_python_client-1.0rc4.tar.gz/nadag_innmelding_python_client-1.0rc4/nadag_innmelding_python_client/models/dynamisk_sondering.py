from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Literal, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.dynamisk_sondering_data import DynamiskSonderingData
    from ..models.identifikasjon import Identifikasjon


T = TypeVar("T", bound="DynamiskSondering")


@_attrs_define
class DynamiskSondering:
    """sondering som benytter slag på borstrengen ved penetrasjon, benevnes også som ramsondering, flere liknende metoder
    aktuelle<engelsk>sounding using strokes on the drill string during penetration, several similar methods are
    applicable</engelsk>

        Attributes:
            json_type (Union[Literal['DynamiskSondering'], Unset]):
            identifikasjon (Union[Unset, Identifikasjon]): Unik identifikasjon av et objekt, ivaretatt av den ansvarlige
                produsent/forvalter, som kan benyttes av eksterne applikasjoner som referanse til objektet.

                NOTE1 Denne eksterne objektidentifikasjonen må ikke forveksles med en tematisk objektidentifikasjon, slik som
                f.eks bygningsnummer.

                NOTE 2 Denne unike identifikatoren vil ikke endres i løpet av objektets levetid.
            fra_borlengde (Union[Unset, float]):
            til_borlengde (Union[Unset, float]):
            torv_tykkelse (Union[Unset, float]):
            ant_pr_ø_veuttak_forstyrret_matr (Union[Unset, int]):
            dynamisk_sondering_observasjon (Union[Unset, list['DynamiskSonderingData']]):
    """

    json_type: Union[Literal["DynamiskSondering"], Unset] = UNSET
    identifikasjon: Union[Unset, "Identifikasjon"] = UNSET
    fra_borlengde: Union[Unset, float] = UNSET
    til_borlengde: Union[Unset, float] = UNSET
    torv_tykkelse: Union[Unset, float] = UNSET
    ant_pr_ø_veuttak_forstyrret_matr: Union[Unset, int] = UNSET
    dynamisk_sondering_observasjon: Union[Unset, list["DynamiskSonderingData"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        json_type = self.json_type

        identifikasjon: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.identifikasjon, Unset):
            identifikasjon = self.identifikasjon.to_dict()

        fra_borlengde = self.fra_borlengde

        til_borlengde = self.til_borlengde

        torv_tykkelse = self.torv_tykkelse

        ant_pr_ø_veuttak_forstyrret_matr = self.ant_pr_ø_veuttak_forstyrret_matr

        dynamisk_sondering_observasjon: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.dynamisk_sondering_observasjon, Unset):
            dynamisk_sondering_observasjon = []
            for dynamisk_sondering_observasjon_item_data in self.dynamisk_sondering_observasjon:
                dynamisk_sondering_observasjon_item = dynamisk_sondering_observasjon_item_data.to_dict()
                dynamisk_sondering_observasjon.append(dynamisk_sondering_observasjon_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if json_type is not UNSET:
            field_dict["jsonType"] = json_type
        if identifikasjon is not UNSET:
            field_dict["identifikasjon"] = identifikasjon
        if fra_borlengde is not UNSET:
            field_dict["fraBorlengde"] = fra_borlengde
        if til_borlengde is not UNSET:
            field_dict["tilBorlengde"] = til_borlengde
        if torv_tykkelse is not UNSET:
            field_dict["torvTykkelse"] = torv_tykkelse
        if ant_pr_ø_veuttak_forstyrret_matr is not UNSET:
            field_dict["antPrøveuttakForstyrretMatr"] = ant_pr_ø_veuttak_forstyrret_matr
        if dynamisk_sondering_observasjon is not UNSET:
            field_dict["dynamiskSonderingObservasjon"] = dynamisk_sondering_observasjon

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.dynamisk_sondering_data import DynamiskSonderingData
        from ..models.identifikasjon import Identifikasjon

        d = dict(src_dict)
        json_type = cast(Union[Literal["DynamiskSondering"], Unset], d.pop("jsonType", UNSET))
        if json_type != "DynamiskSondering" and not isinstance(json_type, Unset):
            raise ValueError(f"jsonType must match const 'DynamiskSondering', got '{json_type}'")

        _identifikasjon = d.pop("identifikasjon", UNSET)
        identifikasjon: Union[Unset, Identifikasjon]
        if isinstance(_identifikasjon, Unset):
            identifikasjon = UNSET
        else:
            identifikasjon = Identifikasjon.from_dict(_identifikasjon)

        fra_borlengde = d.pop("fraBorlengde", UNSET)

        til_borlengde = d.pop("tilBorlengde", UNSET)

        torv_tykkelse = d.pop("torvTykkelse", UNSET)

        ant_pr_ø_veuttak_forstyrret_matr = d.pop("antPrøveuttakForstyrretMatr", UNSET)

        dynamisk_sondering_observasjon = []
        _dynamisk_sondering_observasjon = d.pop("dynamiskSonderingObservasjon", UNSET)
        for dynamisk_sondering_observasjon_item_data in _dynamisk_sondering_observasjon or []:
            dynamisk_sondering_observasjon_item = DynamiskSonderingData.from_dict(
                dynamisk_sondering_observasjon_item_data
            )

            dynamisk_sondering_observasjon.append(dynamisk_sondering_observasjon_item)

        dynamisk_sondering = cls(
            json_type=json_type,
            identifikasjon=identifikasjon,
            fra_borlengde=fra_borlengde,
            til_borlengde=til_borlengde,
            torv_tykkelse=torv_tykkelse,
            ant_pr_ø_veuttak_forstyrret_matr=ant_pr_ø_veuttak_forstyrret_matr,
            dynamisk_sondering_observasjon=dynamisk_sondering_observasjon,
        )

        dynamisk_sondering.additional_properties = d
        return dynamisk_sondering

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
