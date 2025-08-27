import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="EksternIdentifikasjon")


@_attrs_define
class EksternIdentifikasjon:
    """Identifikasjon av et objekt, ivaretatt av den ansvarlige leverandør inn til NADAG.

    Attributes:
        ekstern_id (Union[Unset, str]):
        ekstern_navnerom (Union[Unset, str]):
        ekstern_versjon_id (Union[Unset, str]):
        ekstern_levering_dato (Union[Unset, datetime.datetime]):
    """

    ekstern_id: Union[Unset, str] = UNSET
    ekstern_navnerom: Union[Unset, str] = UNSET
    ekstern_versjon_id: Union[Unset, str] = UNSET
    ekstern_levering_dato: Union[Unset, datetime.datetime] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        ekstern_id = self.ekstern_id

        ekstern_navnerom = self.ekstern_navnerom

        ekstern_versjon_id = self.ekstern_versjon_id

        ekstern_levering_dato: Union[Unset, str] = UNSET
        if not isinstance(self.ekstern_levering_dato, Unset):
            ekstern_levering_dato = self.ekstern_levering_dato.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if ekstern_id is not UNSET:
            field_dict["eksternId"] = ekstern_id
        if ekstern_navnerom is not UNSET:
            field_dict["eksternNavnerom"] = ekstern_navnerom
        if ekstern_versjon_id is not UNSET:
            field_dict["eksternVersjonId"] = ekstern_versjon_id
        if ekstern_levering_dato is not UNSET:
            field_dict["eksternLeveringDato"] = ekstern_levering_dato

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        ekstern_id = d.pop("eksternId", UNSET)

        ekstern_navnerom = d.pop("eksternNavnerom", UNSET)

        ekstern_versjon_id = d.pop("eksternVersjonId", UNSET)

        _ekstern_levering_dato = d.pop("eksternLeveringDato", UNSET)
        ekstern_levering_dato: Union[Unset, datetime.datetime]
        if isinstance(_ekstern_levering_dato, Unset):
            ekstern_levering_dato = UNSET
        else:
            ekstern_levering_dato = isoparse(_ekstern_levering_dato)

        ekstern_identifikasjon = cls(
            ekstern_id=ekstern_id,
            ekstern_navnerom=ekstern_navnerom,
            ekstern_versjon_id=ekstern_versjon_id,
            ekstern_levering_dato=ekstern_levering_dato,
        )

        ekstern_identifikasjon.additional_properties = d
        return ekstern_identifikasjon

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
