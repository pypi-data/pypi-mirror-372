from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="StatiskSonderingData")


@_attrs_define
class StatiskSonderingData:
    """innsamlede data for utførelse og registrering ved gjennomføring av statisk sondering <engelsk>collected data for
    performance and recordings in static sounding</engelsk>

        Attributes:
            anvendtlast (Union[Unset, float]):
            boret_lengde (Union[Unset, float]):
            halve_omdreininger (Union[Unset, float]):
            med_slag (Union[Unset, bool]):
            nedpressing_tid (Union[Unset, int]):
            nedsynkning_hastighet (Union[Unset, float]):
            observasjon_kode (Union[Unset, str]):
            observasjon_merknad (Union[Unset, str]):
            rotasjon_hastighet (Union[Unset, float]):
            har_rotasjon (Union[Unset, bool]):
            side_friksjon (Union[Unset, float]):
            slag_frekvens (Union[Unset, float]):
    """

    anvendtlast: Union[Unset, float] = UNSET
    boret_lengde: Union[Unset, float] = UNSET
    halve_omdreininger: Union[Unset, float] = UNSET
    med_slag: Union[Unset, bool] = UNSET
    nedpressing_tid: Union[Unset, int] = UNSET
    nedsynkning_hastighet: Union[Unset, float] = UNSET
    observasjon_kode: Union[Unset, str] = UNSET
    observasjon_merknad: Union[Unset, str] = UNSET
    rotasjon_hastighet: Union[Unset, float] = UNSET
    har_rotasjon: Union[Unset, bool] = UNSET
    side_friksjon: Union[Unset, float] = UNSET
    slag_frekvens: Union[Unset, float] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        anvendtlast = self.anvendtlast

        boret_lengde = self.boret_lengde

        halve_omdreininger = self.halve_omdreininger

        med_slag = self.med_slag

        nedpressing_tid = self.nedpressing_tid

        nedsynkning_hastighet = self.nedsynkning_hastighet

        observasjon_kode = self.observasjon_kode

        observasjon_merknad = self.observasjon_merknad

        rotasjon_hastighet = self.rotasjon_hastighet

        har_rotasjon = self.har_rotasjon

        side_friksjon = self.side_friksjon

        slag_frekvens = self.slag_frekvens

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if anvendtlast is not UNSET:
            field_dict["anvendtlast"] = anvendtlast
        if boret_lengde is not UNSET:
            field_dict["boretLengde"] = boret_lengde
        if halve_omdreininger is not UNSET:
            field_dict["halveOmdreininger"] = halve_omdreininger
        if med_slag is not UNSET:
            field_dict["medSlag"] = med_slag
        if nedpressing_tid is not UNSET:
            field_dict["nedpressingTid"] = nedpressing_tid
        if nedsynkning_hastighet is not UNSET:
            field_dict["nedsynkningHastighet"] = nedsynkning_hastighet
        if observasjon_kode is not UNSET:
            field_dict["observasjonKode"] = observasjon_kode
        if observasjon_merknad is not UNSET:
            field_dict["observasjonMerknad"] = observasjon_merknad
        if rotasjon_hastighet is not UNSET:
            field_dict["rotasjonHastighet"] = rotasjon_hastighet
        if har_rotasjon is not UNSET:
            field_dict["harRotasjon"] = har_rotasjon
        if side_friksjon is not UNSET:
            field_dict["sideFriksjon"] = side_friksjon
        if slag_frekvens is not UNSET:
            field_dict["slagFrekvens"] = slag_frekvens

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        anvendtlast = d.pop("anvendtlast", UNSET)

        boret_lengde = d.pop("boretLengde", UNSET)

        halve_omdreininger = d.pop("halveOmdreininger", UNSET)

        med_slag = d.pop("medSlag", UNSET)

        nedpressing_tid = d.pop("nedpressingTid", UNSET)

        nedsynkning_hastighet = d.pop("nedsynkningHastighet", UNSET)

        observasjon_kode = d.pop("observasjonKode", UNSET)

        observasjon_merknad = d.pop("observasjonMerknad", UNSET)

        rotasjon_hastighet = d.pop("rotasjonHastighet", UNSET)

        har_rotasjon = d.pop("harRotasjon", UNSET)

        side_friksjon = d.pop("sideFriksjon", UNSET)

        slag_frekvens = d.pop("slagFrekvens", UNSET)

        statisk_sondering_data = cls(
            anvendtlast=anvendtlast,
            boret_lengde=boret_lengde,
            halve_omdreininger=halve_omdreininger,
            med_slag=med_slag,
            nedpressing_tid=nedpressing_tid,
            nedsynkning_hastighet=nedsynkning_hastighet,
            observasjon_kode=observasjon_kode,
            observasjon_merknad=observasjon_merknad,
            rotasjon_hastighet=rotasjon_hastighet,
            har_rotasjon=har_rotasjon,
            side_friksjon=side_friksjon,
            slag_frekvens=slag_frekvens,
        )

        statisk_sondering_data.additional_properties = d
        return statisk_sondering_data

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
