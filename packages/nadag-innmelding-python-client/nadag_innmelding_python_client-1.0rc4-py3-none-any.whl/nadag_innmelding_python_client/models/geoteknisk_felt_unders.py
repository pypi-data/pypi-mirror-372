import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.felt_unders_type_kode import FeltUndersTypeKode
from ..models.geoteknisk_felt_unders_metode_kode import GeotekniskFeltUndersMetodeKode
from ..models.tolkning_metode_kode import TolkningMetodeKode
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.ekstern_identifikasjon import EksternIdentifikasjon
    from ..models.geoteknisk_dokument import GeotekniskDokument
    from ..models.identifikasjon import Identifikasjon
    from ..models.point import Point


T = TypeVar("T", bound="GeotekniskFeltUnders")


@_attrs_define
class GeotekniskFeltUnders:
    """Geoteknisk feltundersøkelse

    Attributes:
        identifikasjon (Union[Unset, Identifikasjon]): Unik identifikasjon av et objekt, ivaretatt av den ansvarlige
            produsent/forvalter, som kan benyttes av eksterne applikasjoner som referanse til objektet.

            NOTE1 Denne eksterne objektidentifikasjonen må ikke forveksles med en tematisk objektidentifikasjon, slik som
            f.eks bygningsnummer.

            NOTE 2 Denne unike identifikatoren vil ikke endres i løpet av objektets levetid.
        posisjon (Union[Unset, Point]):
        geoteknisk_felt_unders_metode (Union[Unset, GeotekniskFeltUndersMetodeKode]): Koder for metoder benyttet ved
            geotekniske feltundersøkelser
        eksternidentifikasjon (Union[Unset, EksternIdentifikasjon]): Identifikasjon av et objekt, ivaretatt av den
            ansvarlige leverandør inn til NADAG.
        opprettet_dato (Union[Unset, datetime.datetime]):
        feltunders_type (Union[Unset, FeltUndersTypeKode]): Kodeliste for feltundersøkelsestype
        tolkning_metode (Union[Unset, TolkningMetodeKode]): Metoder benyttet for tolkning av geotekniske
            feltundersøkelser
        h_ø_yde_fjell (Union[Unset, float]):
        høyde (Union[Unset, float]):
        h_ø_yde_referanse (Union[Unset, str]):
        feltunders_nr (Union[Unset, str]):
        har_dokument (Union[Unset, list['GeotekniskDokument']]):
    """

    identifikasjon: Union[Unset, "Identifikasjon"] = UNSET
    posisjon: Union[Unset, "Point"] = UNSET
    geoteknisk_felt_unders_metode: Union[Unset, GeotekniskFeltUndersMetodeKode] = UNSET
    eksternidentifikasjon: Union[Unset, "EksternIdentifikasjon"] = UNSET
    opprettet_dato: Union[Unset, datetime.datetime] = UNSET
    feltunders_type: Union[Unset, FeltUndersTypeKode] = UNSET
    tolkning_metode: Union[Unset, TolkningMetodeKode] = UNSET
    h_ø_yde_fjell: Union[Unset, float] = UNSET
    høyde: Union[Unset, float] = UNSET
    h_ø_yde_referanse: Union[Unset, str] = UNSET
    feltunders_nr: Union[Unset, str] = UNSET
    har_dokument: Union[Unset, list["GeotekniskDokument"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        identifikasjon: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.identifikasjon, Unset):
            identifikasjon = self.identifikasjon.to_dict()

        posisjon: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.posisjon, Unset):
            posisjon = self.posisjon.to_dict()

        geoteknisk_felt_unders_metode: Union[Unset, str] = UNSET
        if not isinstance(self.geoteknisk_felt_unders_metode, Unset):
            geoteknisk_felt_unders_metode = self.geoteknisk_felt_unders_metode.value

        eksternidentifikasjon: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.eksternidentifikasjon, Unset):
            eksternidentifikasjon = self.eksternidentifikasjon.to_dict()

        opprettet_dato: Union[Unset, str] = UNSET
        if not isinstance(self.opprettet_dato, Unset):
            opprettet_dato = self.opprettet_dato.isoformat()

        feltunders_type: Union[Unset, str] = UNSET
        if not isinstance(self.feltunders_type, Unset):
            feltunders_type = self.feltunders_type.value

        tolkning_metode: Union[Unset, str] = UNSET
        if not isinstance(self.tolkning_metode, Unset):
            tolkning_metode = self.tolkning_metode.value

        h_ø_yde_fjell = self.h_ø_yde_fjell

        høyde = self.høyde

        h_ø_yde_referanse = self.h_ø_yde_referanse

        feltunders_nr = self.feltunders_nr

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
        if posisjon is not UNSET:
            field_dict["posisjon"] = posisjon
        if geoteknisk_felt_unders_metode is not UNSET:
            field_dict["geotekniskFeltUndersMetode"] = geoteknisk_felt_unders_metode
        if eksternidentifikasjon is not UNSET:
            field_dict["eksternidentifikasjon"] = eksternidentifikasjon
        if opprettet_dato is not UNSET:
            field_dict["opprettetDato"] = opprettet_dato
        if feltunders_type is not UNSET:
            field_dict["feltundersType"] = feltunders_type
        if tolkning_metode is not UNSET:
            field_dict["tolkningMetode"] = tolkning_metode
        if h_ø_yde_fjell is not UNSET:
            field_dict["høydeFjell"] = h_ø_yde_fjell
        if høyde is not UNSET:
            field_dict["høyde"] = høyde
        if h_ø_yde_referanse is not UNSET:
            field_dict["høydeReferanse"] = h_ø_yde_referanse
        if feltunders_nr is not UNSET:
            field_dict["feltundersNr"] = feltunders_nr
        if har_dokument is not UNSET:
            field_dict["harDokument"] = har_dokument

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.ekstern_identifikasjon import EksternIdentifikasjon
        from ..models.geoteknisk_dokument import GeotekniskDokument
        from ..models.identifikasjon import Identifikasjon
        from ..models.point import Point

        d = dict(src_dict)
        _identifikasjon = d.pop("identifikasjon", UNSET)
        identifikasjon: Union[Unset, Identifikasjon]
        if isinstance(_identifikasjon, Unset):
            identifikasjon = UNSET
        else:
            identifikasjon = Identifikasjon.from_dict(_identifikasjon)

        _posisjon = d.pop("posisjon", UNSET)
        posisjon: Union[Unset, Point]
        if isinstance(_posisjon, Unset):
            posisjon = UNSET
        else:
            posisjon = Point.from_dict(_posisjon)

        _geoteknisk_felt_unders_metode = d.pop("geotekniskFeltUndersMetode", UNSET)
        geoteknisk_felt_unders_metode: Union[Unset, GeotekniskFeltUndersMetodeKode]
        if isinstance(_geoteknisk_felt_unders_metode, Unset):
            geoteknisk_felt_unders_metode = UNSET
        else:
            geoteknisk_felt_unders_metode = GeotekniskFeltUndersMetodeKode(_geoteknisk_felt_unders_metode)

        _eksternidentifikasjon = d.pop("eksternidentifikasjon", UNSET)
        eksternidentifikasjon: Union[Unset, EksternIdentifikasjon]
        if isinstance(_eksternidentifikasjon, Unset):
            eksternidentifikasjon = UNSET
        else:
            eksternidentifikasjon = EksternIdentifikasjon.from_dict(_eksternidentifikasjon)

        _opprettet_dato = d.pop("opprettetDato", UNSET)
        opprettet_dato: Union[Unset, datetime.datetime]
        if isinstance(_opprettet_dato, Unset):
            opprettet_dato = UNSET
        else:
            opprettet_dato = isoparse(_opprettet_dato)

        _feltunders_type = d.pop("feltundersType", UNSET)
        feltunders_type: Union[Unset, FeltUndersTypeKode]
        if isinstance(_feltunders_type, Unset):
            feltunders_type = UNSET
        else:
            feltunders_type = FeltUndersTypeKode(_feltunders_type)

        _tolkning_metode = d.pop("tolkningMetode", UNSET)
        tolkning_metode: Union[Unset, TolkningMetodeKode]
        if isinstance(_tolkning_metode, Unset):
            tolkning_metode = UNSET
        else:
            tolkning_metode = TolkningMetodeKode(_tolkning_metode)

        h_ø_yde_fjell = d.pop("høydeFjell", UNSET)

        høyde = d.pop("høyde", UNSET)

        h_ø_yde_referanse = d.pop("høydeReferanse", UNSET)

        feltunders_nr = d.pop("feltundersNr", UNSET)

        har_dokument = []
        _har_dokument = d.pop("harDokument", UNSET)
        for har_dokument_item_data in _har_dokument or []:
            har_dokument_item = GeotekniskDokument.from_dict(har_dokument_item_data)

            har_dokument.append(har_dokument_item)

        geoteknisk_felt_unders = cls(
            identifikasjon=identifikasjon,
            posisjon=posisjon,
            geoteknisk_felt_unders_metode=geoteknisk_felt_unders_metode,
            eksternidentifikasjon=eksternidentifikasjon,
            opprettet_dato=opprettet_dato,
            feltunders_type=feltunders_type,
            tolkning_metode=tolkning_metode,
            h_ø_yde_fjell=h_ø_yde_fjell,
            høyde=høyde,
            h_ø_yde_referanse=h_ø_yde_referanse,
            feltunders_nr=feltunders_nr,
            har_dokument=har_dokument,
        )

        geoteknisk_felt_unders.additional_properties = d
        return geoteknisk_felt_unders

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
