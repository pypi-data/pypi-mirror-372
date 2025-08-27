import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.ekstern_identifikasjon import EksternIdentifikasjon


T = TypeVar("T", bound="GeotekniskDokument")


@_attrs_define
class GeotekniskDokument:
    """dokument(er) tilhørende geotekniske undersøkelsesområder og borehull <engelsk>accompanying documents to geotechnical
    investigation areas and boreholes</engelsk>

        Attributes:
            dokument_id (Union[Unset, str]):
            dokument_nø_kkel (Union[Unset, str]):
            dokument_type (Union[Unset, str]):
            dokument_filnavn (Union[Unset, str]):
            dokument_url (Union[Unset, str]):
            innhold_type (Union[Unset, str]):
            beskrivelse (Union[Unset, str]):
            ekstern_identifikasjon (Union[Unset, EksternIdentifikasjon]): Identifikasjon av et objekt, ivaretatt av den
                ansvarlige leverandør inn til NADAG.
            dokument_navn (Union[Unset, str]):
            opprettet_dato (Union[Unset, datetime.datetime]):
            dokument_nr (Union[Unset, str]):
            dokument_dato (Union[Unset, datetime.datetime]):
    """

    dokument_id: Union[Unset, str] = UNSET
    dokument_nø_kkel: Union[Unset, str] = UNSET
    dokument_type: Union[Unset, str] = UNSET
    dokument_filnavn: Union[Unset, str] = UNSET
    dokument_url: Union[Unset, str] = UNSET
    innhold_type: Union[Unset, str] = UNSET
    beskrivelse: Union[Unset, str] = UNSET
    ekstern_identifikasjon: Union[Unset, "EksternIdentifikasjon"] = UNSET
    dokument_navn: Union[Unset, str] = UNSET
    opprettet_dato: Union[Unset, datetime.datetime] = UNSET
    dokument_nr: Union[Unset, str] = UNSET
    dokument_dato: Union[Unset, datetime.datetime] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        dokument_id = self.dokument_id

        dokument_nø_kkel = self.dokument_nø_kkel

        dokument_type = self.dokument_type

        dokument_filnavn = self.dokument_filnavn

        dokument_url = self.dokument_url

        innhold_type = self.innhold_type

        beskrivelse = self.beskrivelse

        ekstern_identifikasjon: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.ekstern_identifikasjon, Unset):
            ekstern_identifikasjon = self.ekstern_identifikasjon.to_dict()

        dokument_navn = self.dokument_navn

        opprettet_dato: Union[Unset, str] = UNSET
        if not isinstance(self.opprettet_dato, Unset):
            opprettet_dato = self.opprettet_dato.isoformat()

        dokument_nr = self.dokument_nr

        dokument_dato: Union[Unset, str] = UNSET
        if not isinstance(self.dokument_dato, Unset):
            dokument_dato = self.dokument_dato.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if dokument_id is not UNSET:
            field_dict["dokumentID"] = dokument_id
        if dokument_nø_kkel is not UNSET:
            field_dict["dokumentNøkkel"] = dokument_nø_kkel
        if dokument_type is not UNSET:
            field_dict["dokumentType"] = dokument_type
        if dokument_filnavn is not UNSET:
            field_dict["dokumentFilnavn"] = dokument_filnavn
        if dokument_url is not UNSET:
            field_dict["dokumentURL"] = dokument_url
        if innhold_type is not UNSET:
            field_dict["innholdType"] = innhold_type
        if beskrivelse is not UNSET:
            field_dict["beskrivelse"] = beskrivelse
        if ekstern_identifikasjon is not UNSET:
            field_dict["eksternIdentifikasjon"] = ekstern_identifikasjon
        if dokument_navn is not UNSET:
            field_dict["dokumentNavn"] = dokument_navn
        if opprettet_dato is not UNSET:
            field_dict["opprettetDato"] = opprettet_dato
        if dokument_nr is not UNSET:
            field_dict["dokumentNr"] = dokument_nr
        if dokument_dato is not UNSET:
            field_dict["dokumentDato"] = dokument_dato

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.ekstern_identifikasjon import EksternIdentifikasjon

        d = dict(src_dict)
        dokument_id = d.pop("dokumentID", UNSET)

        dokument_nø_kkel = d.pop("dokumentNøkkel", UNSET)

        dokument_type = d.pop("dokumentType", UNSET)

        dokument_filnavn = d.pop("dokumentFilnavn", UNSET)

        dokument_url = d.pop("dokumentURL", UNSET)

        innhold_type = d.pop("innholdType", UNSET)

        beskrivelse = d.pop("beskrivelse", UNSET)

        _ekstern_identifikasjon = d.pop("eksternIdentifikasjon", UNSET)
        ekstern_identifikasjon: Union[Unset, EksternIdentifikasjon]
        if isinstance(_ekstern_identifikasjon, Unset):
            ekstern_identifikasjon = UNSET
        else:
            ekstern_identifikasjon = EksternIdentifikasjon.from_dict(_ekstern_identifikasjon)

        dokument_navn = d.pop("dokumentNavn", UNSET)

        _opprettet_dato = d.pop("opprettetDato", UNSET)
        opprettet_dato: Union[Unset, datetime.datetime]
        if isinstance(_opprettet_dato, Unset):
            opprettet_dato = UNSET
        else:
            opprettet_dato = isoparse(_opprettet_dato)

        dokument_nr = d.pop("dokumentNr", UNSET)

        _dokument_dato = d.pop("dokumentDato", UNSET)
        dokument_dato: Union[Unset, datetime.datetime]
        if isinstance(_dokument_dato, Unset):
            dokument_dato = UNSET
        else:
            dokument_dato = isoparse(_dokument_dato)

        geoteknisk_dokument = cls(
            dokument_id=dokument_id,
            dokument_nø_kkel=dokument_nø_kkel,
            dokument_type=dokument_type,
            dokument_filnavn=dokument_filnavn,
            dokument_url=dokument_url,
            innhold_type=innhold_type,
            beskrivelse=beskrivelse,
            ekstern_identifikasjon=ekstern_identifikasjon,
            dokument_navn=dokument_navn,
            opprettet_dato=opprettet_dato,
            dokument_nr=dokument_nr,
            dokument_dato=dokument_dato,
        )

        geoteknisk_dokument.additional_properties = d
        return geoteknisk_dokument

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
