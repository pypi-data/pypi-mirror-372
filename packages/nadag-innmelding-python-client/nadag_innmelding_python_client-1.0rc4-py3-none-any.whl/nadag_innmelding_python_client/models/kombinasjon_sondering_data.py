from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="KombinasjonSonderingData")


@_attrs_define
class KombinasjonSonderingData:
    """innsamlede data for utførelse og registrering ved gjennomføring av totalsondering<engelsk>collected data for
    performance of and recordings made during total sounding</engelsk>

        Attributes:
            anvendt_last (Union[Unset, float]):
            boret_lengde (Union[Unset, float]):
            dreie_moment (Union[Unset, float]):
            nedpressing_hastighet (Union[Unset, float]):
            nedpressing_kraft (Union[Unset, float]):
            nedpressing_tid (Union[Unset, int]):
            observasjon_kode (Union[Unset, str]):
            observasjon_merknad (Union[Unset, str]):
            rotasjon_hastighet (Union[Unset, float]):
            slag_frekvens (Union[Unset, float]):
            spyle_mengde (Union[Unset, float]):
            spyle_trykk (Union[Unset, float]):
    """

    anvendt_last: Union[Unset, float] = UNSET
    boret_lengde: Union[Unset, float] = UNSET
    dreie_moment: Union[Unset, float] = UNSET
    nedpressing_hastighet: Union[Unset, float] = UNSET
    nedpressing_kraft: Union[Unset, float] = UNSET
    nedpressing_tid: Union[Unset, int] = UNSET
    observasjon_kode: Union[Unset, str] = UNSET
    observasjon_merknad: Union[Unset, str] = UNSET
    rotasjon_hastighet: Union[Unset, float] = UNSET
    slag_frekvens: Union[Unset, float] = UNSET
    spyle_mengde: Union[Unset, float] = UNSET
    spyle_trykk: Union[Unset, float] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        anvendt_last = self.anvendt_last

        boret_lengde = self.boret_lengde

        dreie_moment = self.dreie_moment

        nedpressing_hastighet = self.nedpressing_hastighet

        nedpressing_kraft = self.nedpressing_kraft

        nedpressing_tid = self.nedpressing_tid

        observasjon_kode = self.observasjon_kode

        observasjon_merknad = self.observasjon_merknad

        rotasjon_hastighet = self.rotasjon_hastighet

        slag_frekvens = self.slag_frekvens

        spyle_mengde = self.spyle_mengde

        spyle_trykk = self.spyle_trykk

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if anvendt_last is not UNSET:
            field_dict["anvendtLast"] = anvendt_last
        if boret_lengde is not UNSET:
            field_dict["boretLengde"] = boret_lengde
        if dreie_moment is not UNSET:
            field_dict["dreieMoment"] = dreie_moment
        if nedpressing_hastighet is not UNSET:
            field_dict["nedpressingHastighet"] = nedpressing_hastighet
        if nedpressing_kraft is not UNSET:
            field_dict["nedpressingKraft"] = nedpressing_kraft
        if nedpressing_tid is not UNSET:
            field_dict["nedpressingTid"] = nedpressing_tid
        if observasjon_kode is not UNSET:
            field_dict["observasjonKode"] = observasjon_kode
        if observasjon_merknad is not UNSET:
            field_dict["observasjonMerknad"] = observasjon_merknad
        if rotasjon_hastighet is not UNSET:
            field_dict["rotasjonHastighet"] = rotasjon_hastighet
        if slag_frekvens is not UNSET:
            field_dict["slagFrekvens"] = slag_frekvens
        if spyle_mengde is not UNSET:
            field_dict["spyleMengde"] = spyle_mengde
        if spyle_trykk is not UNSET:
            field_dict["spyleTrykk"] = spyle_trykk

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        anvendt_last = d.pop("anvendtLast", UNSET)

        boret_lengde = d.pop("boretLengde", UNSET)

        dreie_moment = d.pop("dreieMoment", UNSET)

        nedpressing_hastighet = d.pop("nedpressingHastighet", UNSET)

        nedpressing_kraft = d.pop("nedpressingKraft", UNSET)

        nedpressing_tid = d.pop("nedpressingTid", UNSET)

        observasjon_kode = d.pop("observasjonKode", UNSET)

        observasjon_merknad = d.pop("observasjonMerknad", UNSET)

        rotasjon_hastighet = d.pop("rotasjonHastighet", UNSET)

        slag_frekvens = d.pop("slagFrekvens", UNSET)

        spyle_mengde = d.pop("spyleMengde", UNSET)

        spyle_trykk = d.pop("spyleTrykk", UNSET)

        kombinasjon_sondering_data = cls(
            anvendt_last=anvendt_last,
            boret_lengde=boret_lengde,
            dreie_moment=dreie_moment,
            nedpressing_hastighet=nedpressing_hastighet,
            nedpressing_kraft=nedpressing_kraft,
            nedpressing_tid=nedpressing_tid,
            observasjon_kode=observasjon_kode,
            observasjon_merknad=observasjon_merknad,
            rotasjon_hastighet=rotasjon_hastighet,
            slag_frekvens=slag_frekvens,
            spyle_mengde=spyle_mengde,
            spyle_trykk=spyle_trykk,
        )

        kombinasjon_sondering_data.additional_properties = d
        return kombinasjon_sondering_data

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
