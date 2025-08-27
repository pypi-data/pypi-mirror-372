import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.geoteknisk_tolket_lag import GeotekniskTolketLag
    from ..models.identifikasjon import Identifikasjon
    from ..models.point import Point


T = TypeVar("T", bound="GeotekniskTolketPunkt")


@_attrs_define
class GeotekniskTolketPunkt:
    """Punkt med geoteknisk tolkning

    Attributes:
        identifikasjon (Union[Unset, Identifikasjon]): Unik identifikasjon av et objekt, ivaretatt av den ansvarlige
            produsent/forvalter, som kan benyttes av eksterne applikasjoner som referanse til objektet.

            NOTE1 Denne eksterne objektidentifikasjonen må ikke forveksles med en tematisk objektidentifikasjon, slik som
            f.eks bygningsnummer.

            NOTE 2 Denne unike identifikatoren vil ikke endres i løpet av objektets levetid.
        tolket_av (Union[Unset, str]):
        tolket_tidspunkt (Union[Unset, datetime.datetime]):
        navn (Union[Unset, str]):
        posisjon (Union[Unset, Point]):
        har_tolket_lag (Union[Unset, list['GeotekniskTolketLag']]):
    """

    identifikasjon: Union[Unset, "Identifikasjon"] = UNSET
    tolket_av: Union[Unset, str] = UNSET
    tolket_tidspunkt: Union[Unset, datetime.datetime] = UNSET
    navn: Union[Unset, str] = UNSET
    posisjon: Union[Unset, "Point"] = UNSET
    har_tolket_lag: Union[Unset, list["GeotekniskTolketLag"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        identifikasjon: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.identifikasjon, Unset):
            identifikasjon = self.identifikasjon.to_dict()

        tolket_av = self.tolket_av

        tolket_tidspunkt: Union[Unset, str] = UNSET
        if not isinstance(self.tolket_tidspunkt, Unset):
            tolket_tidspunkt = self.tolket_tidspunkt.isoformat()

        navn = self.navn

        posisjon: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.posisjon, Unset):
            posisjon = self.posisjon.to_dict()

        har_tolket_lag: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.har_tolket_lag, Unset):
            har_tolket_lag = []
            for har_tolket_lag_item_data in self.har_tolket_lag:
                har_tolket_lag_item = har_tolket_lag_item_data.to_dict()
                har_tolket_lag.append(har_tolket_lag_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if identifikasjon is not UNSET:
            field_dict["identifikasjon"] = identifikasjon
        if tolket_av is not UNSET:
            field_dict["tolketAv"] = tolket_av
        if tolket_tidspunkt is not UNSET:
            field_dict["tolketTidspunkt"] = tolket_tidspunkt
        if navn is not UNSET:
            field_dict["navn"] = navn
        if posisjon is not UNSET:
            field_dict["posisjon"] = posisjon
        if har_tolket_lag is not UNSET:
            field_dict["harTolketLag"] = har_tolket_lag

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.geoteknisk_tolket_lag import GeotekniskTolketLag
        from ..models.identifikasjon import Identifikasjon
        from ..models.point import Point

        d = dict(src_dict)
        _identifikasjon = d.pop("identifikasjon", UNSET)
        identifikasjon: Union[Unset, Identifikasjon]
        if isinstance(_identifikasjon, Unset):
            identifikasjon = UNSET
        else:
            identifikasjon = Identifikasjon.from_dict(_identifikasjon)

        tolket_av = d.pop("tolketAv", UNSET)

        _tolket_tidspunkt = d.pop("tolketTidspunkt", UNSET)
        tolket_tidspunkt: Union[Unset, datetime.datetime]
        if isinstance(_tolket_tidspunkt, Unset):
            tolket_tidspunkt = UNSET
        else:
            tolket_tidspunkt = isoparse(_tolket_tidspunkt)

        navn = d.pop("navn", UNSET)

        _posisjon = d.pop("posisjon", UNSET)
        posisjon: Union[Unset, Point]
        if isinstance(_posisjon, Unset):
            posisjon = UNSET
        else:
            posisjon = Point.from_dict(_posisjon)

        har_tolket_lag = []
        _har_tolket_lag = d.pop("harTolketLag", UNSET)
        for har_tolket_lag_item_data in _har_tolket_lag or []:
            har_tolket_lag_item = GeotekniskTolketLag.from_dict(har_tolket_lag_item_data)

            har_tolket_lag.append(har_tolket_lag_item)

        geoteknisk_tolket_punkt = cls(
            identifikasjon=identifikasjon,
            tolket_av=tolket_av,
            tolket_tidspunkt=tolket_tidspunkt,
            navn=navn,
            posisjon=posisjon,
            har_tolket_lag=har_tolket_lag,
        )

        geoteknisk_tolket_punkt.additional_properties = d
        return geoteknisk_tolket_punkt

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
