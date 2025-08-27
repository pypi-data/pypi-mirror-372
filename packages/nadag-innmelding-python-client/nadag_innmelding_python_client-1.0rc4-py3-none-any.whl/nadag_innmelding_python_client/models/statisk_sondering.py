from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Literal, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.identifikasjon import Identifikasjon
    from ..models.statisk_sondering_data import StatiskSonderingData


T = TypeVar("T", bound="StatiskSondering")


@_attrs_define
class StatiskSondering:
    """sonderingstype som brukes for å bestemme lagdeling i løsmasser og dybde til fast grunn, og utføres med en konstant
    nedpressingshastighet og rotasjonshatighet.<engelsk>sounding method used for identification of soil stratification
    and depth to firm layers, performed with constant penetration and rotation rate</engelsk>

        Attributes:
            json_type (Union[Literal['StatiskSondering'], Unset]):
            identifikasjon (Union[Unset, Identifikasjon]): Unik identifikasjon av et objekt, ivaretatt av den ansvarlige
                produsent/forvalter, som kan benyttes av eksterne applikasjoner som referanse til objektet.

                NOTE1 Denne eksterne objektidentifikasjonen må ikke forveksles med en tematisk objektidentifikasjon, slik som
                f.eks bygningsnummer.

                NOTE 2 Denne unike identifikatoren vil ikke endres i løpet av objektets levetid.
            fra_borlengde (Union[Unset, float]):
            til_borlengde (Union[Unset, float]):
            torv_tykkelse (Union[Unset, float]):
            telenivå (Union[Unset, float]):
            statisk_sondering_observasjon (Union[Unset, list['StatiskSonderingData']]):
    """

    json_type: Union[Literal["StatiskSondering"], Unset] = UNSET
    identifikasjon: Union[Unset, "Identifikasjon"] = UNSET
    fra_borlengde: Union[Unset, float] = UNSET
    til_borlengde: Union[Unset, float] = UNSET
    torv_tykkelse: Union[Unset, float] = UNSET
    telenivå: Union[Unset, float] = UNSET
    statisk_sondering_observasjon: Union[Unset, list["StatiskSonderingData"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        json_type = self.json_type

        identifikasjon: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.identifikasjon, Unset):
            identifikasjon = self.identifikasjon.to_dict()

        fra_borlengde = self.fra_borlengde

        til_borlengde = self.til_borlengde

        torv_tykkelse = self.torv_tykkelse

        telenivå = self.telenivå

        statisk_sondering_observasjon: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.statisk_sondering_observasjon, Unset):
            statisk_sondering_observasjon = []
            for statisk_sondering_observasjon_item_data in self.statisk_sondering_observasjon:
                statisk_sondering_observasjon_item = statisk_sondering_observasjon_item_data.to_dict()
                statisk_sondering_observasjon.append(statisk_sondering_observasjon_item)

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
        if telenivå is not UNSET:
            field_dict["telenivå"] = telenivå
        if statisk_sondering_observasjon is not UNSET:
            field_dict["statiskSonderingObservasjon"] = statisk_sondering_observasjon

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.identifikasjon import Identifikasjon
        from ..models.statisk_sondering_data import StatiskSonderingData

        d = dict(src_dict)
        json_type = cast(Union[Literal["StatiskSondering"], Unset], d.pop("jsonType", UNSET))
        if json_type != "StatiskSondering" and not isinstance(json_type, Unset):
            raise ValueError(f"jsonType must match const 'StatiskSondering', got '{json_type}'")

        _identifikasjon = d.pop("identifikasjon", UNSET)
        identifikasjon: Union[Unset, Identifikasjon]
        if isinstance(_identifikasjon, Unset):
            identifikasjon = UNSET
        else:
            identifikasjon = Identifikasjon.from_dict(_identifikasjon)

        fra_borlengde = d.pop("fraBorlengde", UNSET)

        til_borlengde = d.pop("tilBorlengde", UNSET)

        torv_tykkelse = d.pop("torvTykkelse", UNSET)

        telenivå = d.pop("telenivå", UNSET)

        statisk_sondering_observasjon = []
        _statisk_sondering_observasjon = d.pop("statiskSonderingObservasjon", UNSET)
        for statisk_sondering_observasjon_item_data in _statisk_sondering_observasjon or []:
            statisk_sondering_observasjon_item = StatiskSonderingData.from_dict(statisk_sondering_observasjon_item_data)

            statisk_sondering_observasjon.append(statisk_sondering_observasjon_item)

        statisk_sondering = cls(
            json_type=json_type,
            identifikasjon=identifikasjon,
            fra_borlengde=fra_borlengde,
            til_borlengde=til_borlengde,
            torv_tykkelse=torv_tykkelse,
            telenivå=telenivå,
            statisk_sondering_observasjon=statisk_sondering_observasjon,
        )

        statisk_sondering.additional_properties = d
        return statisk_sondering

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
