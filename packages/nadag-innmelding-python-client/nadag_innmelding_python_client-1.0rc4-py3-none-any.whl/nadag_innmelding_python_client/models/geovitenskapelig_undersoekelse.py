import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.identifikasjon import Identifikasjon
    from ..models.multi_polygon import MultiPolygon
    from ..models.polygon import Polygon


T = TypeVar("T", bound="GeovitenskapeligUndersoekelse")


@_attrs_define
class GeovitenskapeligUndersoekelse:
    """geovitenskaplig undersøkelse som utføres innen for et gitt område og tidsperiode og som ofte er knyttet til et
    prosjekt

    <engelsk>
    soil geoscientific investigation of a given area and time period and usually with a connection to a specific project
    </engelsk>

        Attributes:
            identifikasjon (Union[Unset, Identifikasjon]): Unik identifikasjon av et objekt, ivaretatt av den ansvarlige
                produsent/forvalter, som kan benyttes av eksterne applikasjoner som referanse til objektet.

                NOTE1 Denne eksterne objektidentifikasjonen må ikke forveksles med en tematisk objektidentifikasjon, slik som
                f.eks bygningsnummer.

                NOTE 2 Denne unike identifikatoren vil ikke endres i løpet av objektets levetid.
            oppdateringsdato (Union[Unset, datetime.datetime]):
            beskrivelse (Union[Unset, str]):
            område (Union[Unset, Polygon]):
            oppdragsgiver (Union[Unset, str]):
            oppdragstaker (Union[Unset, str]):
            prosjekt_navn (Union[Unset, str]):
            unders_ø_kelse_periode_fra (Union[Unset, datetime.datetime]):
            sammensattområde (Union[Unset, MultiPolygon]):
            unders_ø_kelse_periode_til (Union[Unset, datetime.datetime]):
    """

    identifikasjon: Union[Unset, "Identifikasjon"] = UNSET
    oppdateringsdato: Union[Unset, datetime.datetime] = UNSET
    beskrivelse: Union[Unset, str] = UNSET
    område: Union[Unset, "Polygon"] = UNSET
    oppdragsgiver: Union[Unset, str] = UNSET
    oppdragstaker: Union[Unset, str] = UNSET
    prosjekt_navn: Union[Unset, str] = UNSET
    unders_ø_kelse_periode_fra: Union[Unset, datetime.datetime] = UNSET
    sammensattområde: Union[Unset, "MultiPolygon"] = UNSET
    unders_ø_kelse_periode_til: Union[Unset, datetime.datetime] = UNSET
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

        oppdragsgiver = self.oppdragsgiver

        oppdragstaker = self.oppdragstaker

        prosjekt_navn = self.prosjekt_navn

        unders_ø_kelse_periode_fra: Union[Unset, str] = UNSET
        if not isinstance(self.unders_ø_kelse_periode_fra, Unset):
            unders_ø_kelse_periode_fra = self.unders_ø_kelse_periode_fra.isoformat()

        sammensattområde: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.sammensattområde, Unset):
            sammensattområde = self.sammensattområde.to_dict()

        unders_ø_kelse_periode_til: Union[Unset, str] = UNSET
        if not isinstance(self.unders_ø_kelse_periode_til, Unset):
            unders_ø_kelse_periode_til = self.unders_ø_kelse_periode_til.isoformat()

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
        if oppdragsgiver is not UNSET:
            field_dict["oppdragsgiver"] = oppdragsgiver
        if oppdragstaker is not UNSET:
            field_dict["oppdragstaker"] = oppdragstaker
        if prosjekt_navn is not UNSET:
            field_dict["prosjektNavn"] = prosjekt_navn
        if unders_ø_kelse_periode_fra is not UNSET:
            field_dict["undersøkelsePeriodeFra"] = unders_ø_kelse_periode_fra
        if sammensattområde is not UNSET:
            field_dict["sammensattområde"] = sammensattområde
        if unders_ø_kelse_periode_til is not UNSET:
            field_dict["undersøkelsePeriodeTil"] = unders_ø_kelse_periode_til

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.identifikasjon import Identifikasjon
        from ..models.multi_polygon import MultiPolygon
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

        oppdragsgiver = d.pop("oppdragsgiver", UNSET)

        oppdragstaker = d.pop("oppdragstaker", UNSET)

        prosjekt_navn = d.pop("prosjektNavn", UNSET)

        _unders_ø_kelse_periode_fra = d.pop("undersøkelsePeriodeFra", UNSET)
        unders_ø_kelse_periode_fra: Union[Unset, datetime.datetime]
        if isinstance(_unders_ø_kelse_periode_fra, Unset):
            unders_ø_kelse_periode_fra = UNSET
        else:
            unders_ø_kelse_periode_fra = isoparse(_unders_ø_kelse_periode_fra)

        _sammensattområde = d.pop("sammensattområde", UNSET)
        sammensattområde: Union[Unset, MultiPolygon]
        if isinstance(_sammensattområde, Unset):
            sammensattområde = UNSET
        else:
            sammensattområde = MultiPolygon.from_dict(_sammensattområde)

        _unders_ø_kelse_periode_til = d.pop("undersøkelsePeriodeTil", UNSET)
        unders_ø_kelse_periode_til: Union[Unset, datetime.datetime]
        if isinstance(_unders_ø_kelse_periode_til, Unset):
            unders_ø_kelse_periode_til = UNSET
        else:
            unders_ø_kelse_periode_til = isoparse(_unders_ø_kelse_periode_til)

        geovitenskapelig_undersoekelse = cls(
            identifikasjon=identifikasjon,
            oppdateringsdato=oppdateringsdato,
            beskrivelse=beskrivelse,
            område=område,
            oppdragsgiver=oppdragsgiver,
            oppdragstaker=oppdragstaker,
            prosjekt_navn=prosjekt_navn,
            unders_ø_kelse_periode_fra=unders_ø_kelse_periode_fra,
            sammensattområde=sammensattområde,
            unders_ø_kelse_periode_til=unders_ø_kelse_periode_til,
        )

        geovitenskapelig_undersoekelse.additional_properties = d
        return geovitenskapelig_undersoekelse

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
