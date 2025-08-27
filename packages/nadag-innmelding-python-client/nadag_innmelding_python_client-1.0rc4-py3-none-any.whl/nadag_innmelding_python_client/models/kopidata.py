import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="Kopidata")


@_attrs_define
class Kopidata:
    """angivelse av at objektet er hentet fra en kopi av originaldata

    Merknad:
    Kan benyttes dersom man gjør et uttak av en database som ikke inneholder originaldataene.

        Attributes:
            original_datavert (str):
            kopidato (datetime.datetime):
            omr_å_de_id (Union[Unset, int]):
    """

    original_datavert: str
    kopidato: datetime.datetime
    omr_å_de_id: Union[Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        original_datavert = self.original_datavert

        kopidato = self.kopidato.isoformat()

        omr_å_de_id = self.omr_å_de_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "originalDatavert": original_datavert,
                "kopidato": kopidato,
            }
        )
        if omr_å_de_id is not UNSET:
            field_dict["områdeId"] = omr_å_de_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        original_datavert = d.pop("originalDatavert")

        kopidato = isoparse(d.pop("kopidato"))

        omr_å_de_id = d.pop("områdeId", UNSET)

        kopidata = cls(
            original_datavert=original_datavert,
            kopidato=kopidato,
            omr_å_de_id=omr_å_de_id,
        )

        kopidata.additional_properties = d
        return kopidata

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
