from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.geoteknisk_proeveseriedel_data import GeotekniskProeveseriedelData


T = TypeVar("T", bound="GeotekniskProeveseriedel")


@_attrs_define
class GeotekniskProeveseriedel:
    """delprøve av en  prøveserie<engelsk> Soli test part </engelsk>

    Attributes:
        pr_ø_ve_metode (Union[Unset, str]):
        pr_ø_veseriedel_navn (Union[Unset, str]):
        fra_lengde (Union[Unset, float]):
        til_lengde (Union[Unset, float]):
        pr_ø_veseriedel_id (Union[Unset, str]):
        har_data (Union[Unset, list['GeotekniskProeveseriedelData']]):
    """

    pr_ø_ve_metode: Union[Unset, str] = UNSET
    pr_ø_veseriedel_navn: Union[Unset, str] = UNSET
    fra_lengde: Union[Unset, float] = UNSET
    til_lengde: Union[Unset, float] = UNSET
    pr_ø_veseriedel_id: Union[Unset, str] = UNSET
    har_data: Union[Unset, list["GeotekniskProeveseriedelData"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        pr_ø_ve_metode = self.pr_ø_ve_metode

        pr_ø_veseriedel_navn = self.pr_ø_veseriedel_navn

        fra_lengde = self.fra_lengde

        til_lengde = self.til_lengde

        pr_ø_veseriedel_id = self.pr_ø_veseriedel_id

        har_data: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.har_data, Unset):
            har_data = []
            for har_data_item_data in self.har_data:
                har_data_item = har_data_item_data.to_dict()
                har_data.append(har_data_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if pr_ø_ve_metode is not UNSET:
            field_dict["prøveMetode"] = pr_ø_ve_metode
        if pr_ø_veseriedel_navn is not UNSET:
            field_dict["prøveseriedelNavn"] = pr_ø_veseriedel_navn
        if fra_lengde is not UNSET:
            field_dict["fraLengde"] = fra_lengde
        if til_lengde is not UNSET:
            field_dict["tilLengde"] = til_lengde
        if pr_ø_veseriedel_id is not UNSET:
            field_dict["prøveseriedelId"] = pr_ø_veseriedel_id
        if har_data is not UNSET:
            field_dict["harData"] = har_data

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.geoteknisk_proeveseriedel_data import GeotekniskProeveseriedelData

        d = dict(src_dict)
        pr_ø_ve_metode = d.pop("prøveMetode", UNSET)

        pr_ø_veseriedel_navn = d.pop("prøveseriedelNavn", UNSET)

        fra_lengde = d.pop("fraLengde", UNSET)

        til_lengde = d.pop("tilLengde", UNSET)

        pr_ø_veseriedel_id = d.pop("prøveseriedelId", UNSET)

        har_data = []
        _har_data = d.pop("harData", UNSET)
        for har_data_item_data in _har_data or []:
            har_data_item = GeotekniskProeveseriedelData.from_dict(har_data_item_data)

            har_data.append(har_data_item)

        geoteknisk_proeveseriedel = cls(
            pr_ø_ve_metode=pr_ø_ve_metode,
            pr_ø_veseriedel_navn=pr_ø_veseriedel_navn,
            fra_lengde=fra_lengde,
            til_lengde=til_lengde,
            pr_ø_veseriedel_id=pr_ø_veseriedel_id,
            har_data=har_data,
        )

        geoteknisk_proeveseriedel.additional_properties = d
        return geoteknisk_proeveseriedel

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
