import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.geoteknisk_metode_kode import GeotekniskMetodeKode
from ..models.geoteknisk_stoppkode import GeotekniskStoppkode
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.blokk_proeve import BlokkProeve
    from ..models.borlengde_til_berg import BorlengdeTilBerg
    from ..models.dilatometer_test import DilatometerTest
    from ..models.dynamisk_sondering import DynamiskSondering
    from ..models.ekstern_identifikasjon import EksternIdentifikasjon
    from ..models.gass_maaling import GassMaaling
    from ..models.gass_proeve import GassProeve
    from ..models.geoteknisk_dokument import GeotekniskDokument
    from ..models.geoteknisk_proeveserie import GeotekniskProeveserie
    from ..models.grave_proeve import GraveProeve
    from ..models.grunnvann_maaling import GrunnvannMaaling
    from ..models.hydraulisk_test import HydrauliskTest
    from ..models.identifikasjon import Identifikasjon
    from ..models.kanne_proeve import KanneProeve
    from ..models.kjerne_boring import KjerneBoring
    from ..models.kjerne_proeve import KjerneProeve
    from ..models.kombinasjon_sondering import KombinasjonSondering
    from ..models.miljoe_undersoekelse import MiljoeUndersoekelse
    from ..models.naver_proeve import NaverProeve
    from ..models.platebelastning import Platebelastning
    from ..models.point import Point
    from ..models.poretrykk_maaling import PoretrykkMaaling
    from ..models.posisjonskvalitet_nadag import PosisjonskvalitetNADAG
    from ..models.ram_proeve import RamProeve
    from ..models.sediment_proeve import SedimentProeve
    from ..models.skovl_proeve import SkovlProeve
    from ..models.statisk_sondering import StatiskSondering
    from ..models.stempel_proeve import StempelProeve
    from ..models.trykksondering import Trykksondering
    from ..models.vann_proeve import VannProeve
    from ..models.vingeboring import Vingeboring


T = TypeVar("T", bound="GeotekniskBorehullUnders")


@_attrs_define
class GeotekniskBorehullUnders:
    """geografisk punkt hvor det er utført feltforsøk, prøvetaking, måling av poretrykk osv. med tilhørende observasjoner
    <engelsk>geographical location where field tests, sampling, pore pressure measurements etc. with corresponding
    observations have been carried out</engelsk>

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
            posisjon (Union[Unset, Point]):
            bore_beskrivelse (Union[Unset, str]):
            borehull_forl_ø_p (Union[Unset, list['Point']]):
            boret_azimuth (Union[Unset, float]):
            boret_helningsgrad (Union[Unset, float]):
            boret_lengde (Union[Unset, float]):
            boret_lengde_til_berg (Union[Unset, BorlengdeTilBerg]): dybde til fjell som ikke er målt men basert på tolkning

                <engelsk>
                depth to bedrock based on interpretation
                </engelsk>
            dybde_fra_gitt_posisjon (Union[Unset, float]):
            dybde_fra_vannoverflaten (Union[Unset, float]):
            lenke_til_tileggsinfo (Union[Unset, str]):
            opphav (Union[Unset, str]):
            unders_ø_kelse_slutt (Union[Unset, datetime.datetime]):
            unders_ø_kelse_start (Union[Unset, datetime.datetime]):
            v_æ_rforhold_ved_boring (Union[Unset, str]):
            høyde (Union[Unset, float]):
            h_ø_yde_referanse (Union[Unset, str]):
            unders_ø_kelse_nr (Union[Unset, str]):
            ekstern_identifikasjon (Union[Unset, EksternIdentifikasjon]): Identifikasjon av et objekt, ivaretatt av den
                ansvarlige leverandør inn til NADAG.
            opprettet_dato (Union[Unset, datetime.datetime]):
            geoteknisk_metode (Union[Unset, GeotekniskMetodeKode]): Kode for metoder benyttet ved geotekniske
                borehullundersøkelser
            dybde_grunnvannstand (Union[Unset, float]):
            forboret_diameter (Union[Unset, float]):
            forboret_lengde (Union[Unset, float]):
            forboring_metode (Union[Unset, str]):
            stopp_kode (Union[Unset, GeotekniskStoppkode]): oversikt over koder for stopp av boring ved utførelse av en
                grunnundersøkelse <engelsk>overview of codes for termination of boring in a ground investigation</engelsk>
            forboret_start_lengde (Union[Unset, float]):
            metode (Union[Unset, list[Union['BlokkProeve', 'DilatometerTest', 'DynamiskSondering', 'GassMaaling',
                'GassProeve', 'GeotekniskProeveserie', 'GraveProeve', 'GrunnvannMaaling', 'HydrauliskTest', 'KanneProeve',
                'KjerneBoring', 'KjerneProeve', 'KombinasjonSondering', 'MiljoeUndersoekelse', 'NaverProeve', 'Platebelastning',
                'PoretrykkMaaling', 'RamProeve', 'SedimentProeve', 'SkovlProeve', 'StatiskSondering', 'StempelProeve',
                'Trykksondering', 'VannProeve', 'Vingeboring']]]):
            har_dokument (Union[Unset, list['GeotekniskDokument']]):
    """

    datafangstdato: Union[Unset, datetime.datetime] = UNSET
    digitaliseringsmålestokk: Union[Unset, int] = UNSET
    identifikasjon: Union[Unset, "Identifikasjon"] = UNSET
    kvalitet: Union[Unset, "PosisjonskvalitetNADAG"] = UNSET
    oppdateringsdato: Union[Unset, datetime.datetime] = UNSET
    posisjon: Union[Unset, "Point"] = UNSET
    bore_beskrivelse: Union[Unset, str] = UNSET
    borehull_forl_ø_p: Union[Unset, list["Point"]] = UNSET
    boret_azimuth: Union[Unset, float] = UNSET
    boret_helningsgrad: Union[Unset, float] = UNSET
    boret_lengde: Union[Unset, float] = UNSET
    boret_lengde_til_berg: Union[Unset, "BorlengdeTilBerg"] = UNSET
    dybde_fra_gitt_posisjon: Union[Unset, float] = UNSET
    dybde_fra_vannoverflaten: Union[Unset, float] = UNSET
    lenke_til_tileggsinfo: Union[Unset, str] = UNSET
    opphav: Union[Unset, str] = UNSET
    unders_ø_kelse_slutt: Union[Unset, datetime.datetime] = UNSET
    unders_ø_kelse_start: Union[Unset, datetime.datetime] = UNSET
    v_æ_rforhold_ved_boring: Union[Unset, str] = UNSET
    høyde: Union[Unset, float] = UNSET
    h_ø_yde_referanse: Union[Unset, str] = UNSET
    unders_ø_kelse_nr: Union[Unset, str] = UNSET
    ekstern_identifikasjon: Union[Unset, "EksternIdentifikasjon"] = UNSET
    opprettet_dato: Union[Unset, datetime.datetime] = UNSET
    geoteknisk_metode: Union[Unset, GeotekniskMetodeKode] = UNSET
    dybde_grunnvannstand: Union[Unset, float] = UNSET
    forboret_diameter: Union[Unset, float] = UNSET
    forboret_lengde: Union[Unset, float] = UNSET
    forboring_metode: Union[Unset, str] = UNSET
    stopp_kode: Union[Unset, GeotekniskStoppkode] = UNSET
    forboret_start_lengde: Union[Unset, float] = UNSET
    metode: Union[
        Unset,
        list[
            Union[
                "BlokkProeve",
                "DilatometerTest",
                "DynamiskSondering",
                "GassMaaling",
                "GassProeve",
                "GeotekniskProeveserie",
                "GraveProeve",
                "GrunnvannMaaling",
                "HydrauliskTest",
                "KanneProeve",
                "KjerneBoring",
                "KjerneProeve",
                "KombinasjonSondering",
                "MiljoeUndersoekelse",
                "NaverProeve",
                "Platebelastning",
                "PoretrykkMaaling",
                "RamProeve",
                "SedimentProeve",
                "SkovlProeve",
                "StatiskSondering",
                "StempelProeve",
                "Trykksondering",
                "VannProeve",
                "Vingeboring",
            ]
        ],
    ] = UNSET
    har_dokument: Union[Unset, list["GeotekniskDokument"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.blokk_proeve import BlokkProeve
        from ..models.dilatometer_test import DilatometerTest
        from ..models.dynamisk_sondering import DynamiskSondering
        from ..models.gass_maaling import GassMaaling
        from ..models.gass_proeve import GassProeve
        from ..models.geoteknisk_proeveserie import GeotekniskProeveserie
        from ..models.grave_proeve import GraveProeve
        from ..models.grunnvann_maaling import GrunnvannMaaling
        from ..models.hydraulisk_test import HydrauliskTest
        from ..models.kanne_proeve import KanneProeve
        from ..models.kjerne_boring import KjerneBoring
        from ..models.kjerne_proeve import KjerneProeve
        from ..models.kombinasjon_sondering import KombinasjonSondering
        from ..models.miljoe_undersoekelse import MiljoeUndersoekelse
        from ..models.naver_proeve import NaverProeve
        from ..models.platebelastning import Platebelastning
        from ..models.poretrykk_maaling import PoretrykkMaaling
        from ..models.ram_proeve import RamProeve
        from ..models.sediment_proeve import SedimentProeve
        from ..models.skovl_proeve import SkovlProeve
        from ..models.statisk_sondering import StatiskSondering
        from ..models.stempel_proeve import StempelProeve
        from ..models.trykksondering import Trykksondering
        from ..models.vann_proeve import VannProeve

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

        posisjon: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.posisjon, Unset):
            posisjon = self.posisjon.to_dict()

        bore_beskrivelse = self.bore_beskrivelse

        borehull_forl_ø_p: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.borehull_forl_ø_p, Unset):
            borehull_forl_ø_p = []
            for componentsschemas_line_string_item_data in self.borehull_forl_ø_p:
                componentsschemas_line_string_item = componentsschemas_line_string_item_data.to_dict()
                borehull_forl_ø_p.append(componentsschemas_line_string_item)

        boret_azimuth = self.boret_azimuth

        boret_helningsgrad = self.boret_helningsgrad

        boret_lengde = self.boret_lengde

        boret_lengde_til_berg: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.boret_lengde_til_berg, Unset):
            boret_lengde_til_berg = self.boret_lengde_til_berg.to_dict()

        dybde_fra_gitt_posisjon = self.dybde_fra_gitt_posisjon

        dybde_fra_vannoverflaten = self.dybde_fra_vannoverflaten

        lenke_til_tileggsinfo = self.lenke_til_tileggsinfo

        opphav = self.opphav

        unders_ø_kelse_slutt: Union[Unset, str] = UNSET
        if not isinstance(self.unders_ø_kelse_slutt, Unset):
            unders_ø_kelse_slutt = self.unders_ø_kelse_slutt.isoformat()

        unders_ø_kelse_start: Union[Unset, str] = UNSET
        if not isinstance(self.unders_ø_kelse_start, Unset):
            unders_ø_kelse_start = self.unders_ø_kelse_start.isoformat()

        v_æ_rforhold_ved_boring = self.v_æ_rforhold_ved_boring

        høyde = self.høyde

        h_ø_yde_referanse = self.h_ø_yde_referanse

        unders_ø_kelse_nr = self.unders_ø_kelse_nr

        ekstern_identifikasjon: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.ekstern_identifikasjon, Unset):
            ekstern_identifikasjon = self.ekstern_identifikasjon.to_dict()

        opprettet_dato: Union[Unset, str] = UNSET
        if not isinstance(self.opprettet_dato, Unset):
            opprettet_dato = self.opprettet_dato.isoformat()

        geoteknisk_metode: Union[Unset, str] = UNSET
        if not isinstance(self.geoteknisk_metode, Unset):
            geoteknisk_metode = self.geoteknisk_metode.value

        dybde_grunnvannstand = self.dybde_grunnvannstand

        forboret_diameter = self.forboret_diameter

        forboret_lengde = self.forboret_lengde

        forboring_metode = self.forboring_metode

        stopp_kode: Union[Unset, str] = UNSET
        if not isinstance(self.stopp_kode, Unset):
            stopp_kode = self.stopp_kode.value

        forboret_start_lengde = self.forboret_start_lengde

        metode: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.metode, Unset):
            metode = []
            for metode_item_data in self.metode:
                metode_item: dict[str, Any]
                if isinstance(metode_item_data, BlokkProeve):
                    metode_item = metode_item_data.to_dict()
                elif isinstance(metode_item_data, DilatometerTest):
                    metode_item = metode_item_data.to_dict()
                elif isinstance(metode_item_data, DynamiskSondering):
                    metode_item = metode_item_data.to_dict()
                elif isinstance(metode_item_data, GassMaaling):
                    metode_item = metode_item_data.to_dict()
                elif isinstance(metode_item_data, GassProeve):
                    metode_item = metode_item_data.to_dict()
                elif isinstance(metode_item_data, GeotekniskProeveserie):
                    metode_item = metode_item_data.to_dict()
                elif isinstance(metode_item_data, GraveProeve):
                    metode_item = metode_item_data.to_dict()
                elif isinstance(metode_item_data, GrunnvannMaaling):
                    metode_item = metode_item_data.to_dict()
                elif isinstance(metode_item_data, HydrauliskTest):
                    metode_item = metode_item_data.to_dict()
                elif isinstance(metode_item_data, KanneProeve):
                    metode_item = metode_item_data.to_dict()
                elif isinstance(metode_item_data, KjerneBoring):
                    metode_item = metode_item_data.to_dict()
                elif isinstance(metode_item_data, KjerneProeve):
                    metode_item = metode_item_data.to_dict()
                elif isinstance(metode_item_data, KombinasjonSondering):
                    metode_item = metode_item_data.to_dict()
                elif isinstance(metode_item_data, MiljoeUndersoekelse):
                    metode_item = metode_item_data.to_dict()
                elif isinstance(metode_item_data, NaverProeve):
                    metode_item = metode_item_data.to_dict()
                elif isinstance(metode_item_data, Platebelastning):
                    metode_item = metode_item_data.to_dict()
                elif isinstance(metode_item_data, PoretrykkMaaling):
                    metode_item = metode_item_data.to_dict()
                elif isinstance(metode_item_data, RamProeve):
                    metode_item = metode_item_data.to_dict()
                elif isinstance(metode_item_data, SedimentProeve):
                    metode_item = metode_item_data.to_dict()
                elif isinstance(metode_item_data, SkovlProeve):
                    metode_item = metode_item_data.to_dict()
                elif isinstance(metode_item_data, StatiskSondering):
                    metode_item = metode_item_data.to_dict()
                elif isinstance(metode_item_data, StempelProeve):
                    metode_item = metode_item_data.to_dict()
                elif isinstance(metode_item_data, Trykksondering):
                    metode_item = metode_item_data.to_dict()
                elif isinstance(metode_item_data, VannProeve):
                    metode_item = metode_item_data.to_dict()
                else:
                    metode_item = metode_item_data.to_dict()

                metode.append(metode_item)

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
        if posisjon is not UNSET:
            field_dict["posisjon"] = posisjon
        if bore_beskrivelse is not UNSET:
            field_dict["boreBeskrivelse"] = bore_beskrivelse
        if borehull_forl_ø_p is not UNSET:
            field_dict["borehullForløp"] = borehull_forl_ø_p
        if boret_azimuth is not UNSET:
            field_dict["boretAzimuth"] = boret_azimuth
        if boret_helningsgrad is not UNSET:
            field_dict["boretHelningsgrad"] = boret_helningsgrad
        if boret_lengde is not UNSET:
            field_dict["boretLengde"] = boret_lengde
        if boret_lengde_til_berg is not UNSET:
            field_dict["boretLengdeTilBerg"] = boret_lengde_til_berg
        if dybde_fra_gitt_posisjon is not UNSET:
            field_dict["dybdeFraGittPosisjon"] = dybde_fra_gitt_posisjon
        if dybde_fra_vannoverflaten is not UNSET:
            field_dict["dybdeFraVannoverflaten"] = dybde_fra_vannoverflaten
        if lenke_til_tileggsinfo is not UNSET:
            field_dict["lenkeTilTileggsinfo"] = lenke_til_tileggsinfo
        if opphav is not UNSET:
            field_dict["opphav"] = opphav
        if unders_ø_kelse_slutt is not UNSET:
            field_dict["undersøkelseSlutt"] = unders_ø_kelse_slutt
        if unders_ø_kelse_start is not UNSET:
            field_dict["undersøkelseStart"] = unders_ø_kelse_start
        if v_æ_rforhold_ved_boring is not UNSET:
            field_dict["værforholdVedBoring"] = v_æ_rforhold_ved_boring
        if høyde is not UNSET:
            field_dict["høyde"] = høyde
        if h_ø_yde_referanse is not UNSET:
            field_dict["høydeReferanse"] = h_ø_yde_referanse
        if unders_ø_kelse_nr is not UNSET:
            field_dict["undersøkelseNr"] = unders_ø_kelse_nr
        if ekstern_identifikasjon is not UNSET:
            field_dict["eksternIdentifikasjon"] = ekstern_identifikasjon
        if opprettet_dato is not UNSET:
            field_dict["opprettetDato"] = opprettet_dato
        if geoteknisk_metode is not UNSET:
            field_dict["geotekniskMetode"] = geoteknisk_metode
        if dybde_grunnvannstand is not UNSET:
            field_dict["dybdeGrunnvannstand"] = dybde_grunnvannstand
        if forboret_diameter is not UNSET:
            field_dict["forboretDiameter"] = forboret_diameter
        if forboret_lengde is not UNSET:
            field_dict["forboretLengde"] = forboret_lengde
        if forboring_metode is not UNSET:
            field_dict["forboringMetode"] = forboring_metode
        if stopp_kode is not UNSET:
            field_dict["stoppKode"] = stopp_kode
        if forboret_start_lengde is not UNSET:
            field_dict["forboretStartLengde"] = forboret_start_lengde
        if metode is not UNSET:
            field_dict["metode"] = metode
        if har_dokument is not UNSET:
            field_dict["harDokument"] = har_dokument

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.blokk_proeve import BlokkProeve
        from ..models.borlengde_til_berg import BorlengdeTilBerg
        from ..models.dilatometer_test import DilatometerTest
        from ..models.dynamisk_sondering import DynamiskSondering
        from ..models.ekstern_identifikasjon import EksternIdentifikasjon
        from ..models.gass_maaling import GassMaaling
        from ..models.gass_proeve import GassProeve
        from ..models.geoteknisk_dokument import GeotekniskDokument
        from ..models.geoteknisk_proeveserie import GeotekniskProeveserie
        from ..models.grave_proeve import GraveProeve
        from ..models.grunnvann_maaling import GrunnvannMaaling
        from ..models.hydraulisk_test import HydrauliskTest
        from ..models.identifikasjon import Identifikasjon
        from ..models.kanne_proeve import KanneProeve
        from ..models.kjerne_boring import KjerneBoring
        from ..models.kjerne_proeve import KjerneProeve
        from ..models.kombinasjon_sondering import KombinasjonSondering
        from ..models.miljoe_undersoekelse import MiljoeUndersoekelse
        from ..models.naver_proeve import NaverProeve
        from ..models.platebelastning import Platebelastning
        from ..models.point import Point
        from ..models.poretrykk_maaling import PoretrykkMaaling
        from ..models.posisjonskvalitet_nadag import PosisjonskvalitetNADAG
        from ..models.ram_proeve import RamProeve
        from ..models.sediment_proeve import SedimentProeve
        from ..models.skovl_proeve import SkovlProeve
        from ..models.statisk_sondering import StatiskSondering
        from ..models.stempel_proeve import StempelProeve
        from ..models.trykksondering import Trykksondering
        from ..models.vann_proeve import VannProeve
        from ..models.vingeboring import Vingeboring

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

        _posisjon = d.pop("posisjon", UNSET)
        posisjon: Union[Unset, Point]
        if isinstance(_posisjon, Unset):
            posisjon = UNSET
        else:
            posisjon = Point.from_dict(_posisjon)

        bore_beskrivelse = d.pop("boreBeskrivelse", UNSET)

        borehull_forl_ø_p = []
        _borehull_forl_ø_p = d.pop("borehullForløp", UNSET)
        for componentsschemas_line_string_item_data in _borehull_forl_ø_p or []:
            componentsschemas_line_string_item = Point.from_dict(componentsschemas_line_string_item_data)

            borehull_forl_ø_p.append(componentsschemas_line_string_item)

        boret_azimuth = d.pop("boretAzimuth", UNSET)

        boret_helningsgrad = d.pop("boretHelningsgrad", UNSET)

        boret_lengde = d.pop("boretLengde", UNSET)

        _boret_lengde_til_berg = d.pop("boretLengdeTilBerg", UNSET)
        boret_lengde_til_berg: Union[Unset, BorlengdeTilBerg]
        if isinstance(_boret_lengde_til_berg, Unset):
            boret_lengde_til_berg = UNSET
        else:
            boret_lengde_til_berg = BorlengdeTilBerg.from_dict(_boret_lengde_til_berg)

        dybde_fra_gitt_posisjon = d.pop("dybdeFraGittPosisjon", UNSET)

        dybde_fra_vannoverflaten = d.pop("dybdeFraVannoverflaten", UNSET)

        lenke_til_tileggsinfo = d.pop("lenkeTilTileggsinfo", UNSET)

        opphav = d.pop("opphav", UNSET)

        _unders_ø_kelse_slutt = d.pop("undersøkelseSlutt", UNSET)
        unders_ø_kelse_slutt: Union[Unset, datetime.datetime]
        if isinstance(_unders_ø_kelse_slutt, Unset):
            unders_ø_kelse_slutt = UNSET
        else:
            unders_ø_kelse_slutt = isoparse(_unders_ø_kelse_slutt)

        _unders_ø_kelse_start = d.pop("undersøkelseStart", UNSET)
        unders_ø_kelse_start: Union[Unset, datetime.datetime]
        if isinstance(_unders_ø_kelse_start, Unset):
            unders_ø_kelse_start = UNSET
        else:
            unders_ø_kelse_start = isoparse(_unders_ø_kelse_start)

        v_æ_rforhold_ved_boring = d.pop("værforholdVedBoring", UNSET)

        høyde = d.pop("høyde", UNSET)

        h_ø_yde_referanse = d.pop("høydeReferanse", UNSET)

        unders_ø_kelse_nr = d.pop("undersøkelseNr", UNSET)

        _ekstern_identifikasjon = d.pop("eksternIdentifikasjon", UNSET)
        ekstern_identifikasjon: Union[Unset, EksternIdentifikasjon]
        if isinstance(_ekstern_identifikasjon, Unset):
            ekstern_identifikasjon = UNSET
        else:
            ekstern_identifikasjon = EksternIdentifikasjon.from_dict(_ekstern_identifikasjon)

        _opprettet_dato = d.pop("opprettetDato", UNSET)
        opprettet_dato: Union[Unset, datetime.datetime]
        if isinstance(_opprettet_dato, Unset):
            opprettet_dato = UNSET
        else:
            opprettet_dato = isoparse(_opprettet_dato)

        _geoteknisk_metode = d.pop("geotekniskMetode", UNSET)
        geoteknisk_metode: Union[Unset, GeotekniskMetodeKode]
        if isinstance(_geoteknisk_metode, Unset):
            geoteknisk_metode = UNSET
        else:
            geoteknisk_metode = GeotekniskMetodeKode(_geoteknisk_metode)

        dybde_grunnvannstand = d.pop("dybdeGrunnvannstand", UNSET)

        forboret_diameter = d.pop("forboretDiameter", UNSET)

        forboret_lengde = d.pop("forboretLengde", UNSET)

        forboring_metode = d.pop("forboringMetode", UNSET)

        _stopp_kode = d.pop("stoppKode", UNSET)
        stopp_kode: Union[Unset, GeotekniskStoppkode]
        if isinstance(_stopp_kode, Unset):
            stopp_kode = UNSET
        else:
            stopp_kode = GeotekniskStoppkode(_stopp_kode)

        forboret_start_lengde = d.pop("forboretStartLengde", UNSET)

        metode = []
        _metode = d.pop("metode", UNSET)
        for metode_item_data in _metode or []:

            def _parse_metode_item(
                data: object,
            ) -> Union[
                "BlokkProeve",
                "DilatometerTest",
                "DynamiskSondering",
                "GassMaaling",
                "GassProeve",
                "GeotekniskProeveserie",
                "GraveProeve",
                "GrunnvannMaaling",
                "HydrauliskTest",
                "KanneProeve",
                "KjerneBoring",
                "KjerneProeve",
                "KombinasjonSondering",
                "MiljoeUndersoekelse",
                "NaverProeve",
                "Platebelastning",
                "PoretrykkMaaling",
                "RamProeve",
                "SedimentProeve",
                "SkovlProeve",
                "StatiskSondering",
                "StempelProeve",
                "Trykksondering",
                "VannProeve",
                "Vingeboring",
            ]:
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    componentsschemas_geotekniskmetode_type_0 = BlokkProeve.from_dict(data)

                    return componentsschemas_geotekniskmetode_type_0
                except:  # noqa: E722
                    pass
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    componentsschemas_geotekniskmetode_type_1 = DilatometerTest.from_dict(data)

                    return componentsschemas_geotekniskmetode_type_1
                except:  # noqa: E722
                    pass
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    componentsschemas_geotekniskmetode_type_2 = DynamiskSondering.from_dict(data)

                    return componentsschemas_geotekniskmetode_type_2
                except:  # noqa: E722
                    pass
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    componentsschemas_geotekniskmetode_type_3 = GassMaaling.from_dict(data)

                    return componentsschemas_geotekniskmetode_type_3
                except:  # noqa: E722
                    pass
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    componentsschemas_geotekniskmetode_type_4 = GassProeve.from_dict(data)

                    return componentsschemas_geotekniskmetode_type_4
                except:  # noqa: E722
                    pass
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    componentsschemas_geotekniskmetode_type_5 = GeotekniskProeveserie.from_dict(data)

                    return componentsschemas_geotekniskmetode_type_5
                except:  # noqa: E722
                    pass
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    componentsschemas_geotekniskmetode_type_6 = GraveProeve.from_dict(data)

                    return componentsschemas_geotekniskmetode_type_6
                except:  # noqa: E722
                    pass
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    componentsschemas_geotekniskmetode_type_7 = GrunnvannMaaling.from_dict(data)

                    return componentsschemas_geotekniskmetode_type_7
                except:  # noqa: E722
                    pass
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    componentsschemas_geotekniskmetode_type_8 = HydrauliskTest.from_dict(data)

                    return componentsschemas_geotekniskmetode_type_8
                except:  # noqa: E722
                    pass
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    componentsschemas_geotekniskmetode_type_9 = KanneProeve.from_dict(data)

                    return componentsschemas_geotekniskmetode_type_9
                except:  # noqa: E722
                    pass
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    componentsschemas_geotekniskmetode_type_10 = KjerneBoring.from_dict(data)

                    return componentsschemas_geotekniskmetode_type_10
                except:  # noqa: E722
                    pass
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    componentsschemas_geotekniskmetode_type_11 = KjerneProeve.from_dict(data)

                    return componentsschemas_geotekniskmetode_type_11
                except:  # noqa: E722
                    pass
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    componentsschemas_geotekniskmetode_type_12 = KombinasjonSondering.from_dict(data)

                    return componentsschemas_geotekniskmetode_type_12
                except:  # noqa: E722
                    pass
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    componentsschemas_geotekniskmetode_type_13 = MiljoeUndersoekelse.from_dict(data)

                    return componentsschemas_geotekniskmetode_type_13
                except:  # noqa: E722
                    pass
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    componentsschemas_geotekniskmetode_type_14 = NaverProeve.from_dict(data)

                    return componentsschemas_geotekniskmetode_type_14
                except:  # noqa: E722
                    pass
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    componentsschemas_geotekniskmetode_type_15 = Platebelastning.from_dict(data)

                    return componentsschemas_geotekniskmetode_type_15
                except:  # noqa: E722
                    pass
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    componentsschemas_geotekniskmetode_type_16 = PoretrykkMaaling.from_dict(data)

                    return componentsschemas_geotekniskmetode_type_16
                except:  # noqa: E722
                    pass
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    componentsschemas_geotekniskmetode_type_17 = RamProeve.from_dict(data)

                    return componentsschemas_geotekniskmetode_type_17
                except:  # noqa: E722
                    pass
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    componentsschemas_geotekniskmetode_type_18 = SedimentProeve.from_dict(data)

                    return componentsschemas_geotekniskmetode_type_18
                except:  # noqa: E722
                    pass
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    componentsschemas_geotekniskmetode_type_19 = SkovlProeve.from_dict(data)

                    return componentsschemas_geotekniskmetode_type_19
                except:  # noqa: E722
                    pass
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    componentsschemas_geotekniskmetode_type_20 = StatiskSondering.from_dict(data)

                    return componentsschemas_geotekniskmetode_type_20
                except:  # noqa: E722
                    pass
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    componentsschemas_geotekniskmetode_type_21 = StempelProeve.from_dict(data)

                    return componentsschemas_geotekniskmetode_type_21
                except:  # noqa: E722
                    pass
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    componentsschemas_geotekniskmetode_type_22 = Trykksondering.from_dict(data)

                    return componentsschemas_geotekniskmetode_type_22
                except:  # noqa: E722
                    pass
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    componentsschemas_geotekniskmetode_type_23 = VannProeve.from_dict(data)

                    return componentsschemas_geotekniskmetode_type_23
                except:  # noqa: E722
                    pass
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_geotekniskmetode_type_24 = Vingeboring.from_dict(data)

                return componentsschemas_geotekniskmetode_type_24

            metode_item = _parse_metode_item(metode_item_data)

            metode.append(metode_item)

        har_dokument = []
        _har_dokument = d.pop("harDokument", UNSET)
        for har_dokument_item_data in _har_dokument or []:
            har_dokument_item = GeotekniskDokument.from_dict(har_dokument_item_data)

            har_dokument.append(har_dokument_item)

        geoteknisk_borehull_unders = cls(
            datafangstdato=datafangstdato,
            digitaliseringsmålestokk=digitaliseringsmålestokk,
            identifikasjon=identifikasjon,
            kvalitet=kvalitet,
            oppdateringsdato=oppdateringsdato,
            posisjon=posisjon,
            bore_beskrivelse=bore_beskrivelse,
            borehull_forl_ø_p=borehull_forl_ø_p,
            boret_azimuth=boret_azimuth,
            boret_helningsgrad=boret_helningsgrad,
            boret_lengde=boret_lengde,
            boret_lengde_til_berg=boret_lengde_til_berg,
            dybde_fra_gitt_posisjon=dybde_fra_gitt_posisjon,
            dybde_fra_vannoverflaten=dybde_fra_vannoverflaten,
            lenke_til_tileggsinfo=lenke_til_tileggsinfo,
            opphav=opphav,
            unders_ø_kelse_slutt=unders_ø_kelse_slutt,
            unders_ø_kelse_start=unders_ø_kelse_start,
            v_æ_rforhold_ved_boring=v_æ_rforhold_ved_boring,
            høyde=høyde,
            h_ø_yde_referanse=h_ø_yde_referanse,
            unders_ø_kelse_nr=unders_ø_kelse_nr,
            ekstern_identifikasjon=ekstern_identifikasjon,
            opprettet_dato=opprettet_dato,
            geoteknisk_metode=geoteknisk_metode,
            dybde_grunnvannstand=dybde_grunnvannstand,
            forboret_diameter=forboret_diameter,
            forboret_lengde=forboret_lengde,
            forboring_metode=forboring_metode,
            stopp_kode=stopp_kode,
            forboret_start_lengde=forboret_start_lengde,
            metode=metode,
            har_dokument=har_dokument,
        )

        geoteknisk_borehull_unders.additional_properties = d
        return geoteknisk_borehull_unders

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
