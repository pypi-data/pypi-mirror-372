import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.gjennomboret_medium import GjennomboretMedium
from ..models.kvikkleire_paavisning_kode import KvikkleirePaavisningKode
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.borlengde_til_berg import BorlengdeTilBerg
    from ..models.deformasjon_maaling import DeformasjonMaaling
    from ..models.ekstern_identifikasjon import EksternIdentifikasjon
    from ..models.geoteknisk_borehull_unders import GeotekniskBorehullUnders
    from ..models.geoteknisk_dokument import GeotekniskDokument
    from ..models.geoteknisk_tolket_punkt import GeotekniskTolketPunkt
    from ..models.identifikasjon import Identifikasjon
    from ..models.point import Point
    from ..models.posisjonskvalitet_nadag import PosisjonskvalitetNADAG


T = TypeVar("T", bound="GeotekniskBorehull")


@_attrs_define
class GeotekniskBorehull:
    """geografisk område representert ved et punkt som er den logiske enhet for tolking av laginndeling og egenskaper til
    de forskjellige jordlag <engelsk>geographical area represented by a location which is the logical unit for
    interpretation of stratification and properties for the different strata </engelsk>

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
            bore_nr (Union[Unset, str]):
            høyde (Union[Unset, float]):
            h_ø_yde_referanse (Union[Unset, str]):
            opprettet_dato (Union[Unset, datetime.datetime]):
            ekstern_identifikasjon (Union[Unset, EksternIdentifikasjon]): Identifikasjon av et objekt, ivaretatt av den
                ansvarlige leverandør inn til NADAG.
            kvikkleire_på_visning (Union[Unset, KvikkleirePaavisningKode]): Koder for grad av sikkerhet for påvisning av
                kvikkleire eller sprøbruddmateriale
            opprinnelig_geoteknisk_unders_id (Union[Unset, str]):
            opphav (Union[Unset, str]):
            maks_boret_lengde (Union[Unset, float]):
            har_observasjon (Union[Unset, list['DeformasjonMaaling']]):
            har_unders_ø_kelse (Union[Unset, list['GeotekniskBorehullUnders']]):
            har_tolkning (Union[Unset, list['GeotekniskTolketPunkt']]):
            har_dokument (Union[Unset, list['GeotekniskDokument']]):
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
    bore_nr: Union[Unset, str] = UNSET
    høyde: Union[Unset, float] = UNSET
    h_ø_yde_referanse: Union[Unset, str] = UNSET
    opprettet_dato: Union[Unset, datetime.datetime] = UNSET
    ekstern_identifikasjon: Union[Unset, "EksternIdentifikasjon"] = UNSET
    kvikkleire_på_visning: Union[Unset, KvikkleirePaavisningKode] = UNSET
    opprinnelig_geoteknisk_unders_id: Union[Unset, str] = UNSET
    opphav: Union[Unset, str] = UNSET
    maks_boret_lengde: Union[Unset, float] = UNSET
    har_observasjon: Union[Unset, list["DeformasjonMaaling"]] = UNSET
    har_unders_ø_kelse: Union[Unset, list["GeotekniskBorehullUnders"]] = UNSET
    har_tolkning: Union[Unset, list["GeotekniskTolketPunkt"]] = UNSET
    har_dokument: Union[Unset, list["GeotekniskDokument"]] = UNSET
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

        bore_nr = self.bore_nr

        høyde = self.høyde

        h_ø_yde_referanse = self.h_ø_yde_referanse

        opprettet_dato: Union[Unset, str] = UNSET
        if not isinstance(self.opprettet_dato, Unset):
            opprettet_dato = self.opprettet_dato.isoformat()

        ekstern_identifikasjon: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.ekstern_identifikasjon, Unset):
            ekstern_identifikasjon = self.ekstern_identifikasjon.to_dict()

        kvikkleire_på_visning: Union[Unset, str] = UNSET
        if not isinstance(self.kvikkleire_på_visning, Unset):
            kvikkleire_på_visning = self.kvikkleire_på_visning.value

        opprinnelig_geoteknisk_unders_id = self.opprinnelig_geoteknisk_unders_id

        opphav = self.opphav

        maks_boret_lengde = self.maks_boret_lengde

        har_observasjon: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.har_observasjon, Unset):
            har_observasjon = []
            for har_observasjon_item_data in self.har_observasjon:
                har_observasjon_item = har_observasjon_item_data.to_dict()
                har_observasjon.append(har_observasjon_item)

        har_unders_ø_kelse: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.har_unders_ø_kelse, Unset):
            har_unders_ø_kelse = []
            for har_unders_ø_kelse_item_data in self.har_unders_ø_kelse:
                har_unders_ø_kelse_item = har_unders_ø_kelse_item_data.to_dict()
                har_unders_ø_kelse.append(har_unders_ø_kelse_item)

        har_tolkning: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.har_tolkning, Unset):
            har_tolkning = []
            for har_tolkning_item_data in self.har_tolkning:
                har_tolkning_item = har_tolkning_item_data.to_dict()
                har_tolkning.append(har_tolkning_item)

        har_dokument: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.har_dokument, Unset):
            har_dokument = []
            for har_dokument_item_data in self.har_dokument:
                har_dokument_item = har_dokument_item_data.to_dict()
                har_dokument.append(har_dokument_item)

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
        if bore_nr is not UNSET:
            field_dict["boreNr"] = bore_nr
        if høyde is not UNSET:
            field_dict["høyde"] = høyde
        if h_ø_yde_referanse is not UNSET:
            field_dict["høydeReferanse"] = h_ø_yde_referanse
        if opprettet_dato is not UNSET:
            field_dict["opprettetDato"] = opprettet_dato
        if ekstern_identifikasjon is not UNSET:
            field_dict["eksternIdentifikasjon"] = ekstern_identifikasjon
        if kvikkleire_på_visning is not UNSET:
            field_dict["kvikkleirePåvisning"] = kvikkleire_på_visning
        if opprinnelig_geoteknisk_unders_id is not UNSET:
            field_dict["opprinneligGeotekniskUndersID"] = opprinnelig_geoteknisk_unders_id
        if opphav is not UNSET:
            field_dict["opphav"] = opphav
        if maks_boret_lengde is not UNSET:
            field_dict["maksBoretLengde"] = maks_boret_lengde
        if har_observasjon is not UNSET:
            field_dict["harObservasjon"] = har_observasjon
        if har_unders_ø_kelse is not UNSET:
            field_dict["harUndersøkelse"] = har_unders_ø_kelse
        if har_tolkning is not UNSET:
            field_dict["harTolkning"] = har_tolkning
        if har_dokument is not UNSET:
            field_dict["harDokument"] = har_dokument

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.borlengde_til_berg import BorlengdeTilBerg
        from ..models.deformasjon_maaling import DeformasjonMaaling
        from ..models.ekstern_identifikasjon import EksternIdentifikasjon
        from ..models.geoteknisk_borehull_unders import GeotekniskBorehullUnders
        from ..models.geoteknisk_dokument import GeotekniskDokument
        from ..models.geoteknisk_tolket_punkt import GeotekniskTolketPunkt
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

        bore_nr = d.pop("boreNr", UNSET)

        høyde = d.pop("høyde", UNSET)

        h_ø_yde_referanse = d.pop("høydeReferanse", UNSET)

        _opprettet_dato = d.pop("opprettetDato", UNSET)
        opprettet_dato: Union[Unset, datetime.datetime]
        if isinstance(_opprettet_dato, Unset):
            opprettet_dato = UNSET
        else:
            opprettet_dato = isoparse(_opprettet_dato)

        _ekstern_identifikasjon = d.pop("eksternIdentifikasjon", UNSET)
        ekstern_identifikasjon: Union[Unset, EksternIdentifikasjon]
        if isinstance(_ekstern_identifikasjon, Unset):
            ekstern_identifikasjon = UNSET
        else:
            ekstern_identifikasjon = EksternIdentifikasjon.from_dict(_ekstern_identifikasjon)

        _kvikkleire_på_visning = d.pop("kvikkleirePåvisning", UNSET)
        kvikkleire_på_visning: Union[Unset, KvikkleirePaavisningKode]
        if isinstance(_kvikkleire_på_visning, Unset):
            kvikkleire_på_visning = UNSET
        else:
            kvikkleire_på_visning = KvikkleirePaavisningKode(_kvikkleire_på_visning)

        opprinnelig_geoteknisk_unders_id = d.pop("opprinneligGeotekniskUndersID", UNSET)

        opphav = d.pop("opphav", UNSET)

        maks_boret_lengde = d.pop("maksBoretLengde", UNSET)

        har_observasjon = []
        _har_observasjon = d.pop("harObservasjon", UNSET)
        for har_observasjon_item_data in _har_observasjon or []:
            har_observasjon_item = DeformasjonMaaling.from_dict(har_observasjon_item_data)

            har_observasjon.append(har_observasjon_item)

        har_unders_ø_kelse = []
        _har_unders_ø_kelse = d.pop("harUndersøkelse", UNSET)
        for har_unders_ø_kelse_item_data in _har_unders_ø_kelse or []:
            har_unders_ø_kelse_item = GeotekniskBorehullUnders.from_dict(har_unders_ø_kelse_item_data)

            har_unders_ø_kelse.append(har_unders_ø_kelse_item)

        har_tolkning = []
        _har_tolkning = d.pop("harTolkning", UNSET)
        for har_tolkning_item_data in _har_tolkning or []:
            har_tolkning_item = GeotekniskTolketPunkt.from_dict(har_tolkning_item_data)

            har_tolkning.append(har_tolkning_item)

        har_dokument = []
        _har_dokument = d.pop("harDokument", UNSET)
        for har_dokument_item_data in _har_dokument or []:
            har_dokument_item = GeotekniskDokument.from_dict(har_dokument_item_data)

            har_dokument.append(har_dokument_item)

        geoteknisk_borehull = cls(
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
            bore_nr=bore_nr,
            høyde=høyde,
            h_ø_yde_referanse=h_ø_yde_referanse,
            opprettet_dato=opprettet_dato,
            ekstern_identifikasjon=ekstern_identifikasjon,
            kvikkleire_på_visning=kvikkleire_på_visning,
            opprinnelig_geoteknisk_unders_id=opprinnelig_geoteknisk_unders_id,
            opphav=opphav,
            maks_boret_lengde=maks_boret_lengde,
            har_observasjon=har_observasjon,
            har_unders_ø_kelse=har_unders_ø_kelse,
            har_tolkning=har_tolkning,
            har_dokument=har_dokument,
        )

        geoteknisk_borehull.additional_properties = d
        return geoteknisk_borehull

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
