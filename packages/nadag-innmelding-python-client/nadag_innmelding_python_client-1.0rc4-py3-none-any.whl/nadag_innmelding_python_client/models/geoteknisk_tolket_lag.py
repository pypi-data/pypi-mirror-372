import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.hoved_lag_klassifisering import HovedLagKlassifisering
from ..models.klassifiserings_metode import KlassifiseringsMetode
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.ekstern_identifikasjon import EksternIdentifikasjon
    from ..models.point import Point


T = TypeVar("T", bound="GeotekniskTolketLag")


@_attrs_define
class GeotekniskTolketLag:
    """Lag med geoteknisk tolkning

    Attributes:
        tolket_lag_id (Union[Unset, str]):
        klassifisering_metode (Union[Unset, KlassifiseringsMetode]): oversikt over klassifiseringsmetoder for
            bestemmelse av grunnforhold<engelsk>overview of classification methods for determination of ground
            conditions</engelsk>
        hoved_lag_klassifiserings_kode (Union[Unset, HovedLagKlassifisering]): oversikt over lagdeling og jordart for
            klassifisering og identifisering av grunnforhold<engelsk>overview of stratification and soil type for
            classification and identification of ground conditions</engelsk>
        lag_beskrivelse (Union[Unset, str]):
        tolket_av (Union[Unset, str]):
        tolket_tidspunkt (Union[Unset, datetime.datetime]):
        tolkning_merknad (Union[Unset, str]):
        navn (Union[Unset, str]):
        p_å_terreng_overflate (Union[Unset, bool]):
        vurdering (Union[Unset, float]):
        under_terreng_overflate (Union[Unset, bool]):
        ekstern_identifikasjon (Union[Unset, EksternIdentifikasjon]): Identifikasjon av et objekt, ivaretatt av den
            ansvarlige leverandør inn til NADAG.
        posisjon (Union[Unset, Point]):
        høyde (Union[Unset, float]):
        h_ø_yde_referanse (Union[Unset, str]):
    """

    tolket_lag_id: Union[Unset, str] = UNSET
    klassifisering_metode: Union[Unset, KlassifiseringsMetode] = UNSET
    hoved_lag_klassifiserings_kode: Union[Unset, HovedLagKlassifisering] = UNSET
    lag_beskrivelse: Union[Unset, str] = UNSET
    tolket_av: Union[Unset, str] = UNSET
    tolket_tidspunkt: Union[Unset, datetime.datetime] = UNSET
    tolkning_merknad: Union[Unset, str] = UNSET
    navn: Union[Unset, str] = UNSET
    p_å_terreng_overflate: Union[Unset, bool] = UNSET
    vurdering: Union[Unset, float] = UNSET
    under_terreng_overflate: Union[Unset, bool] = UNSET
    ekstern_identifikasjon: Union[Unset, "EksternIdentifikasjon"] = UNSET
    posisjon: Union[Unset, "Point"] = UNSET
    høyde: Union[Unset, float] = UNSET
    h_ø_yde_referanse: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        tolket_lag_id = self.tolket_lag_id

        klassifisering_metode: Union[Unset, str] = UNSET
        if not isinstance(self.klassifisering_metode, Unset):
            klassifisering_metode = self.klassifisering_metode.value

        hoved_lag_klassifiserings_kode: Union[Unset, str] = UNSET
        if not isinstance(self.hoved_lag_klassifiserings_kode, Unset):
            hoved_lag_klassifiserings_kode = self.hoved_lag_klassifiserings_kode.value

        lag_beskrivelse = self.lag_beskrivelse

        tolket_av = self.tolket_av

        tolket_tidspunkt: Union[Unset, str] = UNSET
        if not isinstance(self.tolket_tidspunkt, Unset):
            tolket_tidspunkt = self.tolket_tidspunkt.isoformat()

        tolkning_merknad = self.tolkning_merknad

        navn = self.navn

        p_å_terreng_overflate = self.p_å_terreng_overflate

        vurdering = self.vurdering

        under_terreng_overflate = self.under_terreng_overflate

        ekstern_identifikasjon: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.ekstern_identifikasjon, Unset):
            ekstern_identifikasjon = self.ekstern_identifikasjon.to_dict()

        posisjon: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.posisjon, Unset):
            posisjon = self.posisjon.to_dict()

        høyde = self.høyde

        h_ø_yde_referanse = self.h_ø_yde_referanse

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if tolket_lag_id is not UNSET:
            field_dict["tolketLagID"] = tolket_lag_id
        if klassifisering_metode is not UNSET:
            field_dict["klassifiseringMetode"] = klassifisering_metode
        if hoved_lag_klassifiserings_kode is not UNSET:
            field_dict["hovedLagKlassifiseringsKode"] = hoved_lag_klassifiserings_kode
        if lag_beskrivelse is not UNSET:
            field_dict["lagBeskrivelse"] = lag_beskrivelse
        if tolket_av is not UNSET:
            field_dict["tolketAv"] = tolket_av
        if tolket_tidspunkt is not UNSET:
            field_dict["tolketTidspunkt"] = tolket_tidspunkt
        if tolkning_merknad is not UNSET:
            field_dict["tolkningMerknad"] = tolkning_merknad
        if navn is not UNSET:
            field_dict["navn"] = navn
        if p_å_terreng_overflate is not UNSET:
            field_dict["påTerrengOverflate"] = p_å_terreng_overflate
        if vurdering is not UNSET:
            field_dict["vurdering"] = vurdering
        if under_terreng_overflate is not UNSET:
            field_dict["underTerrengOverflate"] = under_terreng_overflate
        if ekstern_identifikasjon is not UNSET:
            field_dict["eksternIdentifikasjon"] = ekstern_identifikasjon
        if posisjon is not UNSET:
            field_dict["posisjon"] = posisjon
        if høyde is not UNSET:
            field_dict["høyde"] = høyde
        if h_ø_yde_referanse is not UNSET:
            field_dict["høydeReferanse"] = h_ø_yde_referanse

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.ekstern_identifikasjon import EksternIdentifikasjon
        from ..models.point import Point

        d = dict(src_dict)
        tolket_lag_id = d.pop("tolketLagID", UNSET)

        _klassifisering_metode = d.pop("klassifiseringMetode", UNSET)
        klassifisering_metode: Union[Unset, KlassifiseringsMetode]
        if isinstance(_klassifisering_metode, Unset):
            klassifisering_metode = UNSET
        else:
            klassifisering_metode = KlassifiseringsMetode(_klassifisering_metode)

        _hoved_lag_klassifiserings_kode = d.pop("hovedLagKlassifiseringsKode", UNSET)
        hoved_lag_klassifiserings_kode: Union[Unset, HovedLagKlassifisering]
        if isinstance(_hoved_lag_klassifiserings_kode, Unset):
            hoved_lag_klassifiserings_kode = UNSET
        else:
            hoved_lag_klassifiserings_kode = HovedLagKlassifisering(_hoved_lag_klassifiserings_kode)

        lag_beskrivelse = d.pop("lagBeskrivelse", UNSET)

        tolket_av = d.pop("tolketAv", UNSET)

        _tolket_tidspunkt = d.pop("tolketTidspunkt", UNSET)
        tolket_tidspunkt: Union[Unset, datetime.datetime]
        if isinstance(_tolket_tidspunkt, Unset):
            tolket_tidspunkt = UNSET
        else:
            tolket_tidspunkt = isoparse(_tolket_tidspunkt)

        tolkning_merknad = d.pop("tolkningMerknad", UNSET)

        navn = d.pop("navn", UNSET)

        p_å_terreng_overflate = d.pop("påTerrengOverflate", UNSET)

        vurdering = d.pop("vurdering", UNSET)

        under_terreng_overflate = d.pop("underTerrengOverflate", UNSET)

        _ekstern_identifikasjon = d.pop("eksternIdentifikasjon", UNSET)
        ekstern_identifikasjon: Union[Unset, EksternIdentifikasjon]
        if isinstance(_ekstern_identifikasjon, Unset):
            ekstern_identifikasjon = UNSET
        else:
            ekstern_identifikasjon = EksternIdentifikasjon.from_dict(_ekstern_identifikasjon)

        _posisjon = d.pop("posisjon", UNSET)
        posisjon: Union[Unset, Point]
        if isinstance(_posisjon, Unset):
            posisjon = UNSET
        else:
            posisjon = Point.from_dict(_posisjon)

        høyde = d.pop("høyde", UNSET)

        h_ø_yde_referanse = d.pop("høydeReferanse", UNSET)

        geoteknisk_tolket_lag = cls(
            tolket_lag_id=tolket_lag_id,
            klassifisering_metode=klassifisering_metode,
            hoved_lag_klassifiserings_kode=hoved_lag_klassifiserings_kode,
            lag_beskrivelse=lag_beskrivelse,
            tolket_av=tolket_av,
            tolket_tidspunkt=tolket_tidspunkt,
            tolkning_merknad=tolkning_merknad,
            navn=navn,
            p_å_terreng_overflate=p_å_terreng_overflate,
            vurdering=vurdering,
            under_terreng_overflate=under_terreng_overflate,
            ekstern_identifikasjon=ekstern_identifikasjon,
            posisjon=posisjon,
            høyde=høyde,
            h_ø_yde_referanse=h_ø_yde_referanse,
        )

        geoteknisk_tolket_lag.additional_properties = d
        return geoteknisk_tolket_lag

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
