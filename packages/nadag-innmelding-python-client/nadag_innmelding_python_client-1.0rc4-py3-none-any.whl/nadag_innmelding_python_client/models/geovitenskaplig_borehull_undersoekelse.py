import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.borlengde_til_berg import BorlengdeTilBerg
    from ..models.identifikasjon import Identifikasjon
    from ..models.point import Point
    from ..models.posisjonskvalitet_nadag import PosisjonskvalitetNADAG


T = TypeVar("T", bound="GeovitenskapligBorehullUndersoekelse")


@_attrs_define
class GeovitenskapligBorehullUndersoekelse:
    """et enkelt fysisk undersøkelsespunkt som inneholder beskrivelsen av borehullforløpet

    Merknad: Flere undersøkelser kan tilhøre det samme borehullet, men det er undersøkelsen som representerer de enkelte
    sonderinger / boringer.

    <engelsk>a pysical borehole which contain a description of the borehole geometry Note: Several investigations can
    belong to the same borehole, and it is the investigation which contain the geometry along the borehole. </engelsk>

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

        geovitenskaplig_borehull_undersoekelse = cls(
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
        )

        geovitenskaplig_borehull_undersoekelse.additional_properties = d
        return geovitenskaplig_borehull_undersoekelse

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
