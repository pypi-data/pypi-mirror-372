import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.representasjon_kvalitet import RepresentasjonKvalitet
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.ekstern_identifikasjon import EksternIdentifikasjon
    from ..models.geoteknisk_borehull import GeotekniskBorehull
    from ..models.geoteknisk_dokument import GeotekniskDokument
    from ..models.geoteknisk_felt_unders import GeotekniskFeltUnders
    from ..models.geoteknisk_tolket_punkt import GeotekniskTolketPunkt
    from ..models.identifikasjon import Identifikasjon
    from ..models.multi_polygon import MultiPolygon
    from ..models.polygon import Polygon


T = TypeVar("T", bound="GeotekniskUnders")


@_attrs_define
class GeotekniskUnders:
    """geografisk område hvor det finnes eller er planlagt geotekniske borehull tilhørende et gitt prosjekt
    <engelsk>geographical area where there are or are planned geotechnical boreholes for a given project</engelsk>

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
            ekstern_identifikasjon (Union[Unset, EksternIdentifikasjon]): Identifikasjon av et objekt, ivaretatt av den
                ansvarlige leverandør inn til NADAG.
            representasjon_kvalitet (Union[Unset, RepresentasjonKvalitet]): Angir hva avgrensningen/polygonen for en
                geoteknisk undersøkelse fysisk representerer.
            opprettet_dato (Union[Unset, datetime.datetime]):
            prosjekt_nr (Union[Unset, str]):
            opphav (Union[Unset, str]):
            unders_ø_kelse_å_r_antatt (Union[Unset, int]):
            felt_unders (Union[Unset, list['GeotekniskFeltUnders']]):
            unders_pkt (Union[Unset, list['GeotekniskBorehull']]):
            har_tolkning (Union[Unset, list['GeotekniskTolketPunkt']]):
            har_dokument (Union[Unset, list['GeotekniskDokument']]):
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
    ekstern_identifikasjon: Union[Unset, "EksternIdentifikasjon"] = UNSET
    representasjon_kvalitet: Union[Unset, RepresentasjonKvalitet] = UNSET
    opprettet_dato: Union[Unset, datetime.datetime] = UNSET
    prosjekt_nr: Union[Unset, str] = UNSET
    opphav: Union[Unset, str] = UNSET
    unders_ø_kelse_å_r_antatt: Union[Unset, int] = UNSET
    felt_unders: Union[Unset, list["GeotekniskFeltUnders"]] = UNSET
    unders_pkt: Union[Unset, list["GeotekniskBorehull"]] = UNSET
    har_tolkning: Union[Unset, list["GeotekniskTolketPunkt"]] = UNSET
    har_dokument: Union[Unset, list["GeotekniskDokument"]] = UNSET
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

        ekstern_identifikasjon: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.ekstern_identifikasjon, Unset):
            ekstern_identifikasjon = self.ekstern_identifikasjon.to_dict()

        representasjon_kvalitet: Union[Unset, str] = UNSET
        if not isinstance(self.representasjon_kvalitet, Unset):
            representasjon_kvalitet = self.representasjon_kvalitet.value

        opprettet_dato: Union[Unset, str] = UNSET
        if not isinstance(self.opprettet_dato, Unset):
            opprettet_dato = self.opprettet_dato.isoformat()

        prosjekt_nr = self.prosjekt_nr

        opphav = self.opphav

        unders_ø_kelse_å_r_antatt = self.unders_ø_kelse_å_r_antatt

        felt_unders: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.felt_unders, Unset):
            felt_unders = []
            for felt_unders_item_data in self.felt_unders:
                felt_unders_item = felt_unders_item_data.to_dict()
                felt_unders.append(felt_unders_item)

        unders_pkt: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.unders_pkt, Unset):
            unders_pkt = []
            for unders_pkt_item_data in self.unders_pkt:
                unders_pkt_item = unders_pkt_item_data.to_dict()
                unders_pkt.append(unders_pkt_item)

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
        if ekstern_identifikasjon is not UNSET:
            field_dict["eksternIdentifikasjon"] = ekstern_identifikasjon
        if representasjon_kvalitet is not UNSET:
            field_dict["representasjonKvalitet"] = representasjon_kvalitet
        if opprettet_dato is not UNSET:
            field_dict["opprettetDato"] = opprettet_dato
        if prosjekt_nr is not UNSET:
            field_dict["prosjektNr"] = prosjekt_nr
        if opphav is not UNSET:
            field_dict["opphav"] = opphav
        if unders_ø_kelse_å_r_antatt is not UNSET:
            field_dict["undersøkelseÅrAntatt"] = unders_ø_kelse_å_r_antatt
        if felt_unders is not UNSET:
            field_dict["feltUnders"] = felt_unders
        if unders_pkt is not UNSET:
            field_dict["undersPkt"] = unders_pkt
        if har_tolkning is not UNSET:
            field_dict["harTolkning"] = har_tolkning
        if har_dokument is not UNSET:
            field_dict["harDokument"] = har_dokument

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.ekstern_identifikasjon import EksternIdentifikasjon
        from ..models.geoteknisk_borehull import GeotekniskBorehull
        from ..models.geoteknisk_dokument import GeotekniskDokument
        from ..models.geoteknisk_felt_unders import GeotekniskFeltUnders
        from ..models.geoteknisk_tolket_punkt import GeotekniskTolketPunkt
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

        _ekstern_identifikasjon = d.pop("eksternIdentifikasjon", UNSET)
        ekstern_identifikasjon: Union[Unset, EksternIdentifikasjon]
        if isinstance(_ekstern_identifikasjon, Unset):
            ekstern_identifikasjon = UNSET
        else:
            ekstern_identifikasjon = EksternIdentifikasjon.from_dict(_ekstern_identifikasjon)

        _representasjon_kvalitet = d.pop("representasjonKvalitet", UNSET)
        representasjon_kvalitet: Union[Unset, RepresentasjonKvalitet]
        if isinstance(_representasjon_kvalitet, Unset):
            representasjon_kvalitet = UNSET
        else:
            representasjon_kvalitet = RepresentasjonKvalitet(_representasjon_kvalitet)

        _opprettet_dato = d.pop("opprettetDato", UNSET)
        opprettet_dato: Union[Unset, datetime.datetime]
        if isinstance(_opprettet_dato, Unset):
            opprettet_dato = UNSET
        else:
            opprettet_dato = isoparse(_opprettet_dato)

        prosjekt_nr = d.pop("prosjektNr", UNSET)

        opphav = d.pop("opphav", UNSET)

        unders_ø_kelse_å_r_antatt = d.pop("undersøkelseÅrAntatt", UNSET)

        felt_unders = []
        _felt_unders = d.pop("feltUnders", UNSET)
        for felt_unders_item_data in _felt_unders or []:
            felt_unders_item = GeotekniskFeltUnders.from_dict(felt_unders_item_data)

            felt_unders.append(felt_unders_item)

        unders_pkt = []
        _unders_pkt = d.pop("undersPkt", UNSET)
        for unders_pkt_item_data in _unders_pkt or []:
            unders_pkt_item = GeotekniskBorehull.from_dict(unders_pkt_item_data)

            unders_pkt.append(unders_pkt_item)

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

        geoteknisk_unders = cls(
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
            ekstern_identifikasjon=ekstern_identifikasjon,
            representasjon_kvalitet=representasjon_kvalitet,
            opprettet_dato=opprettet_dato,
            prosjekt_nr=prosjekt_nr,
            opphav=opphav,
            unders_ø_kelse_å_r_antatt=unders_ø_kelse_å_r_antatt,
            felt_unders=felt_unders,
            unders_pkt=unders_pkt,
            har_tolkning=har_tolkning,
            har_dokument=har_dokument,
        )

        geoteknisk_unders.additional_properties = d
        return geoteknisk_unders

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
