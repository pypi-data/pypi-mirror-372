from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Literal, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.borlengde_til_berg import BorlengdeTilBerg
    from ..models.identifikasjon import Identifikasjon
    from ..models.kombinasjon_sondering_data import KombinasjonSonderingData


T = TypeVar("T", bound="KombinasjonSondering")


@_attrs_define
class KombinasjonSondering:
    """kombinasjon av boremetodene dreietrykksondering og fjellkontrollboring som gjør det mulig å bore både i løsmasse og
    berg<engelsk>combination of the boring methods rotary pressure sounding and rock control boring which enables
    drilling in both soils and rock.</engelsk>

        Attributes:
            json_type (Union[Literal['KombinasjonSondering'], Unset]):
            identifikasjon (Union[Unset, Identifikasjon]): Unik identifikasjon av et objekt, ivaretatt av den ansvarlige
                produsent/forvalter, som kan benyttes av eksterne applikasjoner som referanse til objektet.

                NOTE1 Denne eksterne objektidentifikasjonen må ikke forveksles med en tematisk objektidentifikasjon, slik som
                f.eks bygningsnummer.

                NOTE 2 Denne unike identifikatoren vil ikke endres i løpet av objektets levetid.
            fra_borlengde (Union[Unset, float]):
            til_borlengde (Union[Unset, float]):
            torv_tykkelse (Union[Unset, float]):
            boret_lengde_i_berg (Union[Unset, float]):
            boret_lengde_til_berg (Union[Unset, BorlengdeTilBerg]): dybde til fjell som ikke er målt men basert på tolkning

                <engelsk>
                depth to bedrock based on interpretation
                </engelsk>
            maks_last (Union[Unset, float]):
            kombinasjon_sondering_observasjon (Union[Unset, list['KombinasjonSonderingData']]):
    """

    json_type: Union[Literal["KombinasjonSondering"], Unset] = UNSET
    identifikasjon: Union[Unset, "Identifikasjon"] = UNSET
    fra_borlengde: Union[Unset, float] = UNSET
    til_borlengde: Union[Unset, float] = UNSET
    torv_tykkelse: Union[Unset, float] = UNSET
    boret_lengde_i_berg: Union[Unset, float] = UNSET
    boret_lengde_til_berg: Union[Unset, "BorlengdeTilBerg"] = UNSET
    maks_last: Union[Unset, float] = UNSET
    kombinasjon_sondering_observasjon: Union[Unset, list["KombinasjonSonderingData"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        json_type = self.json_type

        identifikasjon: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.identifikasjon, Unset):
            identifikasjon = self.identifikasjon.to_dict()

        fra_borlengde = self.fra_borlengde

        til_borlengde = self.til_borlengde

        torv_tykkelse = self.torv_tykkelse

        boret_lengde_i_berg = self.boret_lengde_i_berg

        boret_lengde_til_berg: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.boret_lengde_til_berg, Unset):
            boret_lengde_til_berg = self.boret_lengde_til_berg.to_dict()

        maks_last = self.maks_last

        kombinasjon_sondering_observasjon: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.kombinasjon_sondering_observasjon, Unset):
            kombinasjon_sondering_observasjon = []
            for kombinasjon_sondering_observasjon_item_data in self.kombinasjon_sondering_observasjon:
                kombinasjon_sondering_observasjon_item = kombinasjon_sondering_observasjon_item_data.to_dict()
                kombinasjon_sondering_observasjon.append(kombinasjon_sondering_observasjon_item)

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
        if boret_lengde_i_berg is not UNSET:
            field_dict["boretLengdeIBerg"] = boret_lengde_i_berg
        if boret_lengde_til_berg is not UNSET:
            field_dict["boretLengdeTilBerg"] = boret_lengde_til_berg
        if maks_last is not UNSET:
            field_dict["maksLast"] = maks_last
        if kombinasjon_sondering_observasjon is not UNSET:
            field_dict["kombinasjonSonderingObservasjon"] = kombinasjon_sondering_observasjon

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.borlengde_til_berg import BorlengdeTilBerg
        from ..models.identifikasjon import Identifikasjon
        from ..models.kombinasjon_sondering_data import KombinasjonSonderingData

        d = dict(src_dict)
        json_type = cast(Union[Literal["KombinasjonSondering"], Unset], d.pop("jsonType", UNSET))
        if json_type != "KombinasjonSondering" and not isinstance(json_type, Unset):
            raise ValueError(f"jsonType must match const 'KombinasjonSondering', got '{json_type}'")

        _identifikasjon = d.pop("identifikasjon", UNSET)
        identifikasjon: Union[Unset, Identifikasjon]
        if isinstance(_identifikasjon, Unset):
            identifikasjon = UNSET
        else:
            identifikasjon = Identifikasjon.from_dict(_identifikasjon)

        fra_borlengde = d.pop("fraBorlengde", UNSET)

        til_borlengde = d.pop("tilBorlengde", UNSET)

        torv_tykkelse = d.pop("torvTykkelse", UNSET)

        boret_lengde_i_berg = d.pop("boretLengdeIBerg", UNSET)

        _boret_lengde_til_berg = d.pop("boretLengdeTilBerg", UNSET)
        boret_lengde_til_berg: Union[Unset, BorlengdeTilBerg]
        if isinstance(_boret_lengde_til_berg, Unset):
            boret_lengde_til_berg = UNSET
        else:
            boret_lengde_til_berg = BorlengdeTilBerg.from_dict(_boret_lengde_til_berg)

        maks_last = d.pop("maksLast", UNSET)

        kombinasjon_sondering_observasjon = []
        _kombinasjon_sondering_observasjon = d.pop("kombinasjonSonderingObservasjon", UNSET)
        for kombinasjon_sondering_observasjon_item_data in _kombinasjon_sondering_observasjon or []:
            kombinasjon_sondering_observasjon_item = KombinasjonSonderingData.from_dict(
                kombinasjon_sondering_observasjon_item_data
            )

            kombinasjon_sondering_observasjon.append(kombinasjon_sondering_observasjon_item)

        kombinasjon_sondering = cls(
            json_type=json_type,
            identifikasjon=identifikasjon,
            fra_borlengde=fra_borlengde,
            til_borlengde=til_borlengde,
            torv_tykkelse=torv_tykkelse,
            boret_lengde_i_berg=boret_lengde_i_berg,
            boret_lengde_til_berg=boret_lengde_til_berg,
            maks_last=maks_last,
            kombinasjon_sondering_observasjon=kombinasjon_sondering_observasjon,
        )

        kombinasjon_sondering.additional_properties = d
        return kombinasjon_sondering

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
