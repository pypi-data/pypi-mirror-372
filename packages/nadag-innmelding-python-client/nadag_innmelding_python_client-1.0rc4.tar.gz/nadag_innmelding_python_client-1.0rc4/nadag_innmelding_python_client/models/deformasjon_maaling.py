import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Literal, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.geoteknisk_stoppkode import GeotekniskStoppkode
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.borlengde_til_berg import BorlengdeTilBerg
    from ..models.deformasjon_maale_data import DeformasjonMaaleData
    from ..models.deformasjon_overvaakning_data import DeformasjonOvervaakningData
    from ..models.ekstern_identifikasjon import EksternIdentifikasjon
    from ..models.identifikasjon import Identifikasjon
    from ..models.point import Point
    from ..models.posisjonskvalitet_nadag import PosisjonskvalitetNADAG


T = TypeVar("T", bound="DeformasjonMaaling")


@_attrs_define
class DeformasjonMaaling:
    """undersøkelse for måling av setninger og deformasjoner i felt<engelsk>investigation for measurement of settlements
    and deformations in the field</engelsk>

        Attributes:
            json_type (Union[Literal['DeformasjonMaaling'], Unset]):
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
            observasjon_start (Union[Unset, datetime.datetime]):
            observasjon_slutt (Union[Unset, datetime.datetime]):
            observatør (Union[Unset, str]):
            opphav (Union[Unset, str]):
            bore_beskrivelse (Union[Unset, str]):
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
            v_æ_rforhold_ved_boring (Union[Unset, str]):
            høyde (Union[Unset, float]):
            h_ø_yde_referanse (Union[Unset, str]):
            unders_ø_kelse_nr (Union[Unset, str]):
            ekstern_identifikasjon (Union[Unset, EksternIdentifikasjon]): Identifikasjon av et objekt, ivaretatt av den
                ansvarlige leverandør inn til NADAG.
            opprettet_dato (Union[Unset, datetime.datetime]):
            dybde_grunnvannstand (Union[Unset, float]):
            forboret_diameter (Union[Unset, float]):
            forboret_lengde (Union[Unset, float]):
            forboring_metode (Union[Unset, str]):
            stopp_kode (Union[Unset, GeotekniskStoppkode]): oversikt over koder for stopp av boring ved utførelse av en
                grunnundersøkelse <engelsk>overview of codes for termination of boring in a ground investigation</engelsk>
            forboret_start_lengde (Union[Unset, float]):
            absoluttverdi (Union[Unset, bool]):
            installasjon_tidspunkt (Union[Unset, datetime.datetime]):
            installasjon_niv_å (Union[Unset, float]):
            målertype (Union[Unset, str]):
            målepunkt (Union[Unset, float]):
            har_overv_å_kning_observasjon (Union[Unset, list['DeformasjonOvervaakningData']]):
            har_setning_observasjon (Union[Unset, list['DeformasjonMaaleData']]):
    """

    json_type: Union[Literal["DeformasjonMaaling"], Unset] = UNSET
    datafangstdato: Union[Unset, datetime.datetime] = UNSET
    digitaliseringsmålestokk: Union[Unset, int] = UNSET
    identifikasjon: Union[Unset, "Identifikasjon"] = UNSET
    kvalitet: Union[Unset, "PosisjonskvalitetNADAG"] = UNSET
    oppdateringsdato: Union[Unset, datetime.datetime] = UNSET
    posisjon: Union[Unset, "Point"] = UNSET
    observasjon_start: Union[Unset, datetime.datetime] = UNSET
    observasjon_slutt: Union[Unset, datetime.datetime] = UNSET
    observatør: Union[Unset, str] = UNSET
    opphav: Union[Unset, str] = UNSET
    bore_beskrivelse: Union[Unset, str] = UNSET
    boret_azimuth: Union[Unset, float] = UNSET
    boret_helningsgrad: Union[Unset, float] = UNSET
    boret_lengde: Union[Unset, float] = UNSET
    boret_lengde_til_berg: Union[Unset, "BorlengdeTilBerg"] = UNSET
    dybde_fra_gitt_posisjon: Union[Unset, float] = UNSET
    dybde_fra_vannoverflaten: Union[Unset, float] = UNSET
    lenke_til_tileggsinfo: Union[Unset, str] = UNSET
    v_æ_rforhold_ved_boring: Union[Unset, str] = UNSET
    høyde: Union[Unset, float] = UNSET
    h_ø_yde_referanse: Union[Unset, str] = UNSET
    unders_ø_kelse_nr: Union[Unset, str] = UNSET
    ekstern_identifikasjon: Union[Unset, "EksternIdentifikasjon"] = UNSET
    opprettet_dato: Union[Unset, datetime.datetime] = UNSET
    dybde_grunnvannstand: Union[Unset, float] = UNSET
    forboret_diameter: Union[Unset, float] = UNSET
    forboret_lengde: Union[Unset, float] = UNSET
    forboring_metode: Union[Unset, str] = UNSET
    stopp_kode: Union[Unset, GeotekniskStoppkode] = UNSET
    forboret_start_lengde: Union[Unset, float] = UNSET
    absoluttverdi: Union[Unset, bool] = UNSET
    installasjon_tidspunkt: Union[Unset, datetime.datetime] = UNSET
    installasjon_niv_å: Union[Unset, float] = UNSET
    målertype: Union[Unset, str] = UNSET
    målepunkt: Union[Unset, float] = UNSET
    har_overv_å_kning_observasjon: Union[Unset, list["DeformasjonOvervaakningData"]] = UNSET
    har_setning_observasjon: Union[Unset, list["DeformasjonMaaleData"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        json_type = self.json_type

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

        observasjon_start: Union[Unset, str] = UNSET
        if not isinstance(self.observasjon_start, Unset):
            observasjon_start = self.observasjon_start.isoformat()

        observasjon_slutt: Union[Unset, str] = UNSET
        if not isinstance(self.observasjon_slutt, Unset):
            observasjon_slutt = self.observasjon_slutt.isoformat()

        observatør = self.observatør

        opphav = self.opphav

        bore_beskrivelse = self.bore_beskrivelse

        boret_azimuth = self.boret_azimuth

        boret_helningsgrad = self.boret_helningsgrad

        boret_lengde = self.boret_lengde

        boret_lengde_til_berg: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.boret_lengde_til_berg, Unset):
            boret_lengde_til_berg = self.boret_lengde_til_berg.to_dict()

        dybde_fra_gitt_posisjon = self.dybde_fra_gitt_posisjon

        dybde_fra_vannoverflaten = self.dybde_fra_vannoverflaten

        lenke_til_tileggsinfo = self.lenke_til_tileggsinfo

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

        dybde_grunnvannstand = self.dybde_grunnvannstand

        forboret_diameter = self.forboret_diameter

        forboret_lengde = self.forboret_lengde

        forboring_metode = self.forboring_metode

        stopp_kode: Union[Unset, str] = UNSET
        if not isinstance(self.stopp_kode, Unset):
            stopp_kode = self.stopp_kode.value

        forboret_start_lengde = self.forboret_start_lengde

        absoluttverdi = self.absoluttverdi

        installasjon_tidspunkt: Union[Unset, str] = UNSET
        if not isinstance(self.installasjon_tidspunkt, Unset):
            installasjon_tidspunkt = self.installasjon_tidspunkt.isoformat()

        installasjon_niv_å = self.installasjon_niv_å

        målertype = self.målertype

        målepunkt = self.målepunkt

        har_overv_å_kning_observasjon: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.har_overv_å_kning_observasjon, Unset):
            har_overv_å_kning_observasjon = []
            for har_overv_å_kning_observasjon_item_data in self.har_overv_å_kning_observasjon:
                har_overv_å_kning_observasjon_item = har_overv_å_kning_observasjon_item_data.to_dict()
                har_overv_å_kning_observasjon.append(har_overv_å_kning_observasjon_item)

        har_setning_observasjon: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.har_setning_observasjon, Unset):
            har_setning_observasjon = []
            for har_setning_observasjon_item_data in self.har_setning_observasjon:
                har_setning_observasjon_item = har_setning_observasjon_item_data.to_dict()
                har_setning_observasjon.append(har_setning_observasjon_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if json_type is not UNSET:
            field_dict["jsonType"] = json_type
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
        if observasjon_start is not UNSET:
            field_dict["observasjonStart"] = observasjon_start
        if observasjon_slutt is not UNSET:
            field_dict["observasjonSlutt"] = observasjon_slutt
        if observatør is not UNSET:
            field_dict["observatør"] = observatør
        if opphav is not UNSET:
            field_dict["opphav"] = opphav
        if bore_beskrivelse is not UNSET:
            field_dict["boreBeskrivelse"] = bore_beskrivelse
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
        if absoluttverdi is not UNSET:
            field_dict["absoluttverdi"] = absoluttverdi
        if installasjon_tidspunkt is not UNSET:
            field_dict["installasjonTidspunkt"] = installasjon_tidspunkt
        if installasjon_niv_å is not UNSET:
            field_dict["installasjonNivå"] = installasjon_niv_å
        if målertype is not UNSET:
            field_dict["målertype"] = målertype
        if målepunkt is not UNSET:
            field_dict["målepunkt"] = målepunkt
        if har_overv_å_kning_observasjon is not UNSET:
            field_dict["harOvervåkningObservasjon"] = har_overv_å_kning_observasjon
        if har_setning_observasjon is not UNSET:
            field_dict["harSetningObservasjon"] = har_setning_observasjon

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.borlengde_til_berg import BorlengdeTilBerg
        from ..models.deformasjon_maale_data import DeformasjonMaaleData
        from ..models.deformasjon_overvaakning_data import DeformasjonOvervaakningData
        from ..models.ekstern_identifikasjon import EksternIdentifikasjon
        from ..models.identifikasjon import Identifikasjon
        from ..models.point import Point
        from ..models.posisjonskvalitet_nadag import PosisjonskvalitetNADAG

        d = dict(src_dict)
        json_type = cast(Union[Literal["DeformasjonMaaling"], Unset], d.pop("jsonType", UNSET))
        if json_type != "DeformasjonMaaling" and not isinstance(json_type, Unset):
            raise ValueError(f"jsonType must match const 'DeformasjonMaaling', got '{json_type}'")

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

        _observasjon_start = d.pop("observasjonStart", UNSET)
        observasjon_start: Union[Unset, datetime.datetime]
        if isinstance(_observasjon_start, Unset):
            observasjon_start = UNSET
        else:
            observasjon_start = isoparse(_observasjon_start)

        _observasjon_slutt = d.pop("observasjonSlutt", UNSET)
        observasjon_slutt: Union[Unset, datetime.datetime]
        if isinstance(_observasjon_slutt, Unset):
            observasjon_slutt = UNSET
        else:
            observasjon_slutt = isoparse(_observasjon_slutt)

        observatør = d.pop("observatør", UNSET)

        opphav = d.pop("opphav", UNSET)

        bore_beskrivelse = d.pop("boreBeskrivelse", UNSET)

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

        absoluttverdi = d.pop("absoluttverdi", UNSET)

        _installasjon_tidspunkt = d.pop("installasjonTidspunkt", UNSET)
        installasjon_tidspunkt: Union[Unset, datetime.datetime]
        if isinstance(_installasjon_tidspunkt, Unset):
            installasjon_tidspunkt = UNSET
        else:
            installasjon_tidspunkt = isoparse(_installasjon_tidspunkt)

        installasjon_niv_å = d.pop("installasjonNivå", UNSET)

        målertype = d.pop("målertype", UNSET)

        målepunkt = d.pop("målepunkt", UNSET)

        har_overv_å_kning_observasjon = []
        _har_overv_å_kning_observasjon = d.pop("harOvervåkningObservasjon", UNSET)
        for har_overv_å_kning_observasjon_item_data in _har_overv_å_kning_observasjon or []:
            har_overv_å_kning_observasjon_item = DeformasjonOvervaakningData.from_dict(
                har_overv_å_kning_observasjon_item_data
            )

            har_overv_å_kning_observasjon.append(har_overv_å_kning_observasjon_item)

        har_setning_observasjon = []
        _har_setning_observasjon = d.pop("harSetningObservasjon", UNSET)
        for har_setning_observasjon_item_data in _har_setning_observasjon or []:
            har_setning_observasjon_item = DeformasjonMaaleData.from_dict(har_setning_observasjon_item_data)

            har_setning_observasjon.append(har_setning_observasjon_item)

        deformasjon_maaling = cls(
            json_type=json_type,
            datafangstdato=datafangstdato,
            digitaliseringsmålestokk=digitaliseringsmålestokk,
            identifikasjon=identifikasjon,
            kvalitet=kvalitet,
            oppdateringsdato=oppdateringsdato,
            posisjon=posisjon,
            observasjon_start=observasjon_start,
            observasjon_slutt=observasjon_slutt,
            observatør=observatør,
            opphav=opphav,
            bore_beskrivelse=bore_beskrivelse,
            boret_azimuth=boret_azimuth,
            boret_helningsgrad=boret_helningsgrad,
            boret_lengde=boret_lengde,
            boret_lengde_til_berg=boret_lengde_til_berg,
            dybde_fra_gitt_posisjon=dybde_fra_gitt_posisjon,
            dybde_fra_vannoverflaten=dybde_fra_vannoverflaten,
            lenke_til_tileggsinfo=lenke_til_tileggsinfo,
            v_æ_rforhold_ved_boring=v_æ_rforhold_ved_boring,
            høyde=høyde,
            h_ø_yde_referanse=h_ø_yde_referanse,
            unders_ø_kelse_nr=unders_ø_kelse_nr,
            ekstern_identifikasjon=ekstern_identifikasjon,
            opprettet_dato=opprettet_dato,
            dybde_grunnvannstand=dybde_grunnvannstand,
            forboret_diameter=forboret_diameter,
            forboret_lengde=forboret_lengde,
            forboring_metode=forboring_metode,
            stopp_kode=stopp_kode,
            forboret_start_lengde=forboret_start_lengde,
            absoluttverdi=absoluttverdi,
            installasjon_tidspunkt=installasjon_tidspunkt,
            installasjon_niv_å=installasjon_niv_å,
            målertype=målertype,
            målepunkt=målepunkt,
            har_overv_å_kning_observasjon=har_overv_å_kning_observasjon,
            har_setning_observasjon=har_setning_observasjon,
        )

        deformasjon_maaling.additional_properties = d
        return deformasjon_maaling

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
