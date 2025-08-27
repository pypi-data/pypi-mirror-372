from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="TrykksonderingData")


@_attrs_define
class TrykksonderingData:
    """data fra utførelse av trykksondering (med poretrykksmåling) CPT(U)<engelsk>data fra performance of cone penetration
    test (with pore pressure measurements) CPT(U)</engelsk>

        Attributes:
            anvendt_last (Union[Unset, float]):
            boret_dybde (Union[Unset, float]):
            boret_lengde (Union[Unset, float]):
            friksjon (Union[Unset, float]):
            helning (Union[Unset, float]):
            initielt_poretrykk (Union[Unset, float]):
            resistivitet (Union[Unset, float]):
            korrigert_friksjon (Union[Unset, float]):
            korrigert_nedpressnings_kraft (Union[Unset, float]):
            nedpressing_hastighet (Union[Unset, float]):
            nedpressings_kraft (Union[Unset, float]):
            nedpressings_tid (Union[Unset, int]):
            observasjon_kode (Union[Unset, str]):
            observasjon_merknad (Union[Unset, str]):
            poretrykk (Union[Unset, float]):
            skj_æ_rb_ø_lge_hastighet (Union[Unset, float]):
            temperatur (Union[Unset, float]):
            nedpressing_trykk (Union[Unset, float]):
    """

    anvendt_last: Union[Unset, float] = UNSET
    boret_dybde: Union[Unset, float] = UNSET
    boret_lengde: Union[Unset, float] = UNSET
    friksjon: Union[Unset, float] = UNSET
    helning: Union[Unset, float] = UNSET
    initielt_poretrykk: Union[Unset, float] = UNSET
    resistivitet: Union[Unset, float] = UNSET
    korrigert_friksjon: Union[Unset, float] = UNSET
    korrigert_nedpressnings_kraft: Union[Unset, float] = UNSET
    nedpressing_hastighet: Union[Unset, float] = UNSET
    nedpressings_kraft: Union[Unset, float] = UNSET
    nedpressings_tid: Union[Unset, int] = UNSET
    observasjon_kode: Union[Unset, str] = UNSET
    observasjon_merknad: Union[Unset, str] = UNSET
    poretrykk: Union[Unset, float] = UNSET
    skj_æ_rb_ø_lge_hastighet: Union[Unset, float] = UNSET
    temperatur: Union[Unset, float] = UNSET
    nedpressing_trykk: Union[Unset, float] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        anvendt_last = self.anvendt_last

        boret_dybde = self.boret_dybde

        boret_lengde = self.boret_lengde

        friksjon = self.friksjon

        helning = self.helning

        initielt_poretrykk = self.initielt_poretrykk

        resistivitet = self.resistivitet

        korrigert_friksjon = self.korrigert_friksjon

        korrigert_nedpressnings_kraft = self.korrigert_nedpressnings_kraft

        nedpressing_hastighet = self.nedpressing_hastighet

        nedpressings_kraft = self.nedpressings_kraft

        nedpressings_tid = self.nedpressings_tid

        observasjon_kode = self.observasjon_kode

        observasjon_merknad = self.observasjon_merknad

        poretrykk = self.poretrykk

        skj_æ_rb_ø_lge_hastighet = self.skj_æ_rb_ø_lge_hastighet

        temperatur = self.temperatur

        nedpressing_trykk = self.nedpressing_trykk

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if anvendt_last is not UNSET:
            field_dict["anvendtLast"] = anvendt_last
        if boret_dybde is not UNSET:
            field_dict["boretDybde"] = boret_dybde
        if boret_lengde is not UNSET:
            field_dict["boretLengde"] = boret_lengde
        if friksjon is not UNSET:
            field_dict["friksjon"] = friksjon
        if helning is not UNSET:
            field_dict["helning"] = helning
        if initielt_poretrykk is not UNSET:
            field_dict["initieltPoretrykk"] = initielt_poretrykk
        if resistivitet is not UNSET:
            field_dict["resistivitet"] = resistivitet
        if korrigert_friksjon is not UNSET:
            field_dict["korrigertFriksjon"] = korrigert_friksjon
        if korrigert_nedpressnings_kraft is not UNSET:
            field_dict["korrigertNedpressningsKraft"] = korrigert_nedpressnings_kraft
        if nedpressing_hastighet is not UNSET:
            field_dict["nedpressingHastighet"] = nedpressing_hastighet
        if nedpressings_kraft is not UNSET:
            field_dict["nedpressingsKraft"] = nedpressings_kraft
        if nedpressings_tid is not UNSET:
            field_dict["nedpressingsTid"] = nedpressings_tid
        if observasjon_kode is not UNSET:
            field_dict["observasjonKode"] = observasjon_kode
        if observasjon_merknad is not UNSET:
            field_dict["observasjonMerknad"] = observasjon_merknad
        if poretrykk is not UNSET:
            field_dict["poretrykk"] = poretrykk
        if skj_æ_rb_ø_lge_hastighet is not UNSET:
            field_dict["skjærbølgeHastighet"] = skj_æ_rb_ø_lge_hastighet
        if temperatur is not UNSET:
            field_dict["temperatur"] = temperatur
        if nedpressing_trykk is not UNSET:
            field_dict["nedpressingTrykk"] = nedpressing_trykk

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        anvendt_last = d.pop("anvendtLast", UNSET)

        boret_dybde = d.pop("boretDybde", UNSET)

        boret_lengde = d.pop("boretLengde", UNSET)

        friksjon = d.pop("friksjon", UNSET)

        helning = d.pop("helning", UNSET)

        initielt_poretrykk = d.pop("initieltPoretrykk", UNSET)

        resistivitet = d.pop("resistivitet", UNSET)

        korrigert_friksjon = d.pop("korrigertFriksjon", UNSET)

        korrigert_nedpressnings_kraft = d.pop("korrigertNedpressningsKraft", UNSET)

        nedpressing_hastighet = d.pop("nedpressingHastighet", UNSET)

        nedpressings_kraft = d.pop("nedpressingsKraft", UNSET)

        nedpressings_tid = d.pop("nedpressingsTid", UNSET)

        observasjon_kode = d.pop("observasjonKode", UNSET)

        observasjon_merknad = d.pop("observasjonMerknad", UNSET)

        poretrykk = d.pop("poretrykk", UNSET)

        skj_æ_rb_ø_lge_hastighet = d.pop("skjærbølgeHastighet", UNSET)

        temperatur = d.pop("temperatur", UNSET)

        nedpressing_trykk = d.pop("nedpressingTrykk", UNSET)

        trykksondering_data = cls(
            anvendt_last=anvendt_last,
            boret_dybde=boret_dybde,
            boret_lengde=boret_lengde,
            friksjon=friksjon,
            helning=helning,
            initielt_poretrykk=initielt_poretrykk,
            resistivitet=resistivitet,
            korrigert_friksjon=korrigert_friksjon,
            korrigert_nedpressnings_kraft=korrigert_nedpressnings_kraft,
            nedpressing_hastighet=nedpressing_hastighet,
            nedpressings_kraft=nedpressings_kraft,
            nedpressings_tid=nedpressings_tid,
            observasjon_kode=observasjon_kode,
            observasjon_merknad=observasjon_merknad,
            poretrykk=poretrykk,
            skj_æ_rb_ø_lge_hastighet=skj_æ_rb_ø_lge_hastighet,
            temperatur=temperatur,
            nedpressing_trykk=nedpressing_trykk,
        )

        trykksondering_data.additional_properties = d
        return trykksondering_data

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
