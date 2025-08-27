import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.identifikasjon import Identifikasjon
    from ..models.point import Point
    from ..models.posisjonskvalitet_nadag import PosisjonskvalitetNADAG


T = TypeVar("T", bound="GeovitenskapeligObservasjon")


@_attrs_define
class GeovitenskapeligObservasjon:
    """andre typer observasjoner som ikke er samlet inn via fysiske borehull

    <engelsk>
    observations collected by other features, i.e. not borehole.
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
            posisjon (Union[Unset, Point]):
            observasjon_start (Union[Unset, datetime.datetime]):
            observasjon_slutt (Union[Unset, datetime.datetime]):
            observatør (Union[Unset, str]):
            opphav (Union[Unset, str]):
    """

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

        observasjon_start: Union[Unset, str] = UNSET
        if not isinstance(self.observasjon_start, Unset):
            observasjon_start = self.observasjon_start.isoformat()

        observasjon_slutt: Union[Unset, str] = UNSET
        if not isinstance(self.observasjon_slutt, Unset):
            observasjon_slutt = self.observasjon_slutt.isoformat()

        observatør = self.observatør

        opphav = self.opphav

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
        if observasjon_start is not UNSET:
            field_dict["observasjonStart"] = observasjon_start
        if observasjon_slutt is not UNSET:
            field_dict["observasjonSlutt"] = observasjon_slutt
        if observatør is not UNSET:
            field_dict["observatør"] = observatør
        if opphav is not UNSET:
            field_dict["opphav"] = opphav

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
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

        geovitenskapelig_observasjon = cls(
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
        )

        geovitenskapelig_observasjon.additional_properties = d
        return geovitenskapelig_observasjon

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
