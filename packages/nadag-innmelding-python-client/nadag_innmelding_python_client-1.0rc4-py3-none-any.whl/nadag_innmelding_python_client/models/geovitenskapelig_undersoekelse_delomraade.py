import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.identifikasjon import Identifikasjon
    from ..models.polygon import Polygon


T = TypeVar("T", bound="GeovitenskapeligUndersoekelseDelomraade")


@_attrs_define
class GeovitenskapeligUndersoekelseDelomraade:
    """del av et undersøkelsesområde hvor det pågår, skal gjøres eller er gjort geovitenskapelige undersøkelser

    Merknad: Typisk brukt offshore hvor et undersøkelsesområde er delt i flere mindre lokaliteter.

    <engelsk> area where geoscientific investigations are planned, in progress or performed. Note: This feature is
    typically used offshore where an investigation is split into smaller parts</engelsk>

        Attributes:
            identifikasjon (Union[Unset, Identifikasjon]): Unik identifikasjon av et objekt, ivaretatt av den ansvarlige
                produsent/forvalter, som kan benyttes av eksterne applikasjoner som referanse til objektet.

                NOTE1 Denne eksterne objektidentifikasjonen må ikke forveksles med en tematisk objektidentifikasjon, slik som
                f.eks bygningsnummer.

                NOTE 2 Denne unike identifikatoren vil ikke endres i løpet av objektets levetid.
            oppdateringsdato (Union[Unset, datetime.datetime]):
            beskrivelse (Union[Unset, str]):
            område (Union[Unset, Polygon]):
    """

    identifikasjon: Union[Unset, "Identifikasjon"] = UNSET
    oppdateringsdato: Union[Unset, datetime.datetime] = UNSET
    beskrivelse: Union[Unset, str] = UNSET
    område: Union[Unset, "Polygon"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        identifikasjon: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.identifikasjon, Unset):
            identifikasjon = self.identifikasjon.to_dict()

        oppdateringsdato: Union[Unset, str] = UNSET
        if not isinstance(self.oppdateringsdato, Unset):
            oppdateringsdato = self.oppdateringsdato.isoformat()

        beskrivelse = self.beskrivelse

        område: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.område, Unset):
            område = self.område.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if identifikasjon is not UNSET:
            field_dict["identifikasjon"] = identifikasjon
        if oppdateringsdato is not UNSET:
            field_dict["oppdateringsdato"] = oppdateringsdato
        if beskrivelse is not UNSET:
            field_dict["beskrivelse"] = beskrivelse
        if område is not UNSET:
            field_dict["område"] = område

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.identifikasjon import Identifikasjon
        from ..models.polygon import Polygon

        d = dict(src_dict)
        _identifikasjon = d.pop("identifikasjon", UNSET)
        identifikasjon: Union[Unset, Identifikasjon]
        if isinstance(_identifikasjon, Unset):
            identifikasjon = UNSET
        else:
            identifikasjon = Identifikasjon.from_dict(_identifikasjon)

        _oppdateringsdato = d.pop("oppdateringsdato", UNSET)
        oppdateringsdato: Union[Unset, datetime.datetime]
        if isinstance(_oppdateringsdato, Unset):
            oppdateringsdato = UNSET
        else:
            oppdateringsdato = isoparse(_oppdateringsdato)

        beskrivelse = d.pop("beskrivelse", UNSET)

        _område = d.pop("område", UNSET)
        område: Union[Unset, Polygon]
        if isinstance(_område, Unset):
            område = UNSET
        else:
            område = Polygon.from_dict(_område)

        geovitenskapelig_undersoekelse_delomraade = cls(
            identifikasjon=identifikasjon,
            oppdateringsdato=oppdateringsdato,
            beskrivelse=beskrivelse,
            område=område,
        )

        geovitenskapelig_undersoekelse_delomraade.additional_properties = d
        return geovitenskapelig_undersoekelse_delomraade

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
