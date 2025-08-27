import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.gjennomboret_medium import GjennomboretMedium
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.borlengde_til_berg import BorlengdeTilBerg
    from ..models.identifikasjon import Identifikasjon
    from ..models.point import Point
    from ..models.posisjonskvalitet_nadag import PosisjonskvalitetNADAG


T = TypeVar("T", bound="GeovitenskapligBorehull")


@_attrs_define
class GeovitenskapligBorehull:
    """område representert ved et punkt hvor det skal foretas en eller flere borehullundersøkelser - også kalt logisk
    borehull i motsetning til borhullundersøkelse som representerer hvert fysiske borehull

    Merknad: Det logiske borehullet har en posisjon som representerer de fysiske borhullundersøkelsene foretatt i
    området

    <engelsk>
    borehole consists of one or more physical borehole investigations. The borehole has a position, representing a
    collection of borehole investigations. The position of the borehole is often given the same position as one of the
    asscoated borehole investigations. The associated borehole investigations should be in a reasonable short distance
    (e.g. 0,5 m) from the position of the borehole.
    </engelsk>

        Attributes:
            datafangstdato (Union[Unset, datetime.datetime]):
            digitaliseringsmålestokk (Union[Unset, int]):
            identifikasjon (Union[Unset, Identifikasjon]): Unik identifikasjon av et objekt, ivaretatt av den ansvarlige
                produsent/forvalter, som kan benyttes av eksterne applikasjoner som referanse til objektet.

                NOTE1 Denne eksterne objektidentifikasjonen må ikke forveksles med en tematisk objektidentifikasjon, slik som
                f.eks bygningsnummer.

                NOTE 2 Denne unike identifikatoren vil ikke endres i løpet av objektets levetid.
            kvalitet (Union[Unset, PosisjonskvalitetNADAG]): Posisjonskvalitet slik den brukes i NADAG (Nasjonal Database
                for Grunnundersøkelser).
                (En realisering av den generelle Posisjonskvalitet)
            oppdateringsdato (Union[Unset, datetime.datetime]):
            antall_borehull_unders_ø_kelser (Union[Unset, int]):
            beskrivelse (Union[Unset, str]):
            boret_lengde_til_berg (Union[Unset, BorlengdeTilBerg]): dybde til fjell som ikke er målt men basert på tolkning

                <engelsk>
                depth to bedrock based on interpretation
                </engelsk>
            gjennomboret_medium (Union[Unset, list[GjennomboretMedium]]):
            posisjon (Union[Unset, Point]):
    """

    datafangstdato: Union[Unset, datetime.datetime] = UNSET
    digitaliseringsmålestokk: Union[Unset, int] = UNSET
    identifikasjon: Union[Unset, "Identifikasjon"] = UNSET
    kvalitet: Union[Unset, "PosisjonskvalitetNADAG"] = UNSET
    oppdateringsdato: Union[Unset, datetime.datetime] = UNSET
    antall_borehull_unders_ø_kelser: Union[Unset, int] = UNSET
    beskrivelse: Union[Unset, str] = UNSET
    boret_lengde_til_berg: Union[Unset, "BorlengdeTilBerg"] = UNSET
    gjennomboret_medium: Union[Unset, list[GjennomboretMedium]] = UNSET
    posisjon: Union[Unset, "Point"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        datafangstdato: Union[Unset, str] = UNSET
        if not isinstance(self.datafangstdato, Unset):
            datafangstdato = self.datafangstdato.isoformat()

        digitaliseringsmålestokk = self.digitaliseringsmålestokk

        identifikasjon: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.identifikasjon, Unset):
            identifikasjon = self.identifikasjon.to_dict()

        kvalitet: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.kvalitet, Unset):
            kvalitet = self.kvalitet.to_dict()

        oppdateringsdato: Union[Unset, str] = UNSET
        if not isinstance(self.oppdateringsdato, Unset):
            oppdateringsdato = self.oppdateringsdato.isoformat()

        antall_borehull_unders_ø_kelser = self.antall_borehull_unders_ø_kelser

        beskrivelse = self.beskrivelse

        boret_lengde_til_berg: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.boret_lengde_til_berg, Unset):
            boret_lengde_til_berg = self.boret_lengde_til_berg.to_dict()

        gjennomboret_medium: Union[Unset, list[str]] = UNSET
        if not isinstance(self.gjennomboret_medium, Unset):
            gjennomboret_medium = []
            for gjennomboret_medium_item_data in self.gjennomboret_medium:
                gjennomboret_medium_item = gjennomboret_medium_item_data.value
                gjennomboret_medium.append(gjennomboret_medium_item)

        posisjon: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.posisjon, Unset):
            posisjon = self.posisjon.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if datafangstdato is not UNSET:
            field_dict["datafangstdato"] = datafangstdato
        if digitaliseringsmålestokk is not UNSET:
            field_dict["digitaliseringsmålestokk"] = digitaliseringsmålestokk
        if identifikasjon is not UNSET:
            field_dict["identifikasjon"] = identifikasjon
        if kvalitet is not UNSET:
            field_dict["kvalitet"] = kvalitet
        if oppdateringsdato is not UNSET:
            field_dict["oppdateringsdato"] = oppdateringsdato
        if antall_borehull_unders_ø_kelser is not UNSET:
            field_dict["antallBorehullUndersøkelser"] = antall_borehull_unders_ø_kelser
        if beskrivelse is not UNSET:
            field_dict["beskrivelse"] = beskrivelse
        if boret_lengde_til_berg is not UNSET:
            field_dict["boretLengdeTilBerg"] = boret_lengde_til_berg
        if gjennomboret_medium is not UNSET:
            field_dict["gjennomboretMedium"] = gjennomboret_medium
        if posisjon is not UNSET:
            field_dict["posisjon"] = posisjon

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.borlengde_til_berg import BorlengdeTilBerg
        from ..models.identifikasjon import Identifikasjon
        from ..models.point import Point
        from ..models.posisjonskvalitet_nadag import PosisjonskvalitetNADAG

        d = dict(src_dict)
        _datafangstdato = d.pop("datafangstdato", UNSET)
        datafangstdato: Union[Unset, datetime.datetime]
        if isinstance(_datafangstdato, Unset):
            datafangstdato = UNSET
        else:
            datafangstdato = isoparse(_datafangstdato)

        digitaliseringsmålestokk = d.pop("digitaliseringsmålestokk", UNSET)

        _identifikasjon = d.pop("identifikasjon", UNSET)
        identifikasjon: Union[Unset, Identifikasjon]
        if isinstance(_identifikasjon, Unset):
            identifikasjon = UNSET
        else:
            identifikasjon = Identifikasjon.from_dict(_identifikasjon)

        _kvalitet = d.pop("kvalitet", UNSET)
        kvalitet: Union[Unset, PosisjonskvalitetNADAG]
        if isinstance(_kvalitet, Unset):
            kvalitet = UNSET
        else:
            kvalitet = PosisjonskvalitetNADAG.from_dict(_kvalitet)

        _oppdateringsdato = d.pop("oppdateringsdato", UNSET)
        oppdateringsdato: Union[Unset, datetime.datetime]
        if isinstance(_oppdateringsdato, Unset):
            oppdateringsdato = UNSET
        else:
            oppdateringsdato = isoparse(_oppdateringsdato)

        antall_borehull_unders_ø_kelser = d.pop("antallBorehullUndersøkelser", UNSET)

        beskrivelse = d.pop("beskrivelse", UNSET)

        _boret_lengde_til_berg = d.pop("boretLengdeTilBerg", UNSET)
        boret_lengde_til_berg: Union[Unset, BorlengdeTilBerg]
        if isinstance(_boret_lengde_til_berg, Unset):
            boret_lengde_til_berg = UNSET
        else:
            boret_lengde_til_berg = BorlengdeTilBerg.from_dict(_boret_lengde_til_berg)

        gjennomboret_medium = []
        _gjennomboret_medium = d.pop("gjennomboretMedium", UNSET)
        for gjennomboret_medium_item_data in _gjennomboret_medium or []:
            gjennomboret_medium_item = GjennomboretMedium(gjennomboret_medium_item_data)

            gjennomboret_medium.append(gjennomboret_medium_item)

        _posisjon = d.pop("posisjon", UNSET)
        posisjon: Union[Unset, Point]
        if isinstance(_posisjon, Unset):
            posisjon = UNSET
        else:
            posisjon = Point.from_dict(_posisjon)

        geovitenskaplig_borehull = cls(
            datafangstdato=datafangstdato,
            digitaliseringsmålestokk=digitaliseringsmålestokk,
            identifikasjon=identifikasjon,
            kvalitet=kvalitet,
            oppdateringsdato=oppdateringsdato,
            antall_borehull_unders_ø_kelser=antall_borehull_unders_ø_kelser,
            beskrivelse=beskrivelse,
            boret_lengde_til_berg=boret_lengde_til_berg,
            gjennomboret_medium=gjennomboret_medium,
            posisjon=posisjon,
        )

        geovitenskaplig_borehull.additional_properties = d
        return geovitenskaplig_borehull

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
