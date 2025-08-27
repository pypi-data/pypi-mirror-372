import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Literal, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.hydrauliske_data import HydrauliskeData
    from ..models.identifikasjon import Identifikasjon


T = TypeVar("T", bound="HydrauliskTest")


@_attrs_define
class HydrauliskTest:
    """måling av vannstrømning, vannhastighetsbestemmelse og hydraulisk splitting i felt <engelsk>measurement of hydraulic
    tests (i.e. water flow, pulse tests and hydraulic fracturing tests) in the field</engelsk>

        Attributes:
            json_type (Union[Literal['HydrauliskTest'], Unset]):
            identifikasjon (Union[Unset, Identifikasjon]): Unik identifikasjon av et objekt, ivaretatt av den ansvarlige
                produsent/forvalter, som kan benyttes av eksterne applikasjoner som referanse til objektet.

                NOTE1 Denne eksterne objektidentifikasjonen må ikke forveksles med en tematisk objektidentifikasjon, slik som
                f.eks bygningsnummer.

                NOTE 2 Denne unike identifikatoren vil ikke endres i løpet av objektets levetid.
            fra_borlengde (Union[Unset, float]):
            til_borlengde (Union[Unset, float]):
            insitu_test_start_tidspunkt (Union[Unset, datetime.datetime]):
            insitu_test_slutt_tidspunkt (Union[Unset, datetime.datetime]):
            r_ø_r_bunn (Union[Unset, float]):
            r_ø_r_topp (Union[Unset, float]):
            r_ø_r_type (Union[Unset, str]):
            hydraulisk_observasjon (Union[Unset, list['HydrauliskeData']]):
    """

    json_type: Union[Literal["HydrauliskTest"], Unset] = UNSET
    identifikasjon: Union[Unset, "Identifikasjon"] = UNSET
    fra_borlengde: Union[Unset, float] = UNSET
    til_borlengde: Union[Unset, float] = UNSET
    insitu_test_start_tidspunkt: Union[Unset, datetime.datetime] = UNSET
    insitu_test_slutt_tidspunkt: Union[Unset, datetime.datetime] = UNSET
    r_ø_r_bunn: Union[Unset, float] = UNSET
    r_ø_r_topp: Union[Unset, float] = UNSET
    r_ø_r_type: Union[Unset, str] = UNSET
    hydraulisk_observasjon: Union[Unset, list["HydrauliskeData"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        json_type = self.json_type

        identifikasjon: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.identifikasjon, Unset):
            identifikasjon = self.identifikasjon.to_dict()

        fra_borlengde = self.fra_borlengde

        til_borlengde = self.til_borlengde

        insitu_test_start_tidspunkt: Union[Unset, str] = UNSET
        if not isinstance(self.insitu_test_start_tidspunkt, Unset):
            insitu_test_start_tidspunkt = self.insitu_test_start_tidspunkt.isoformat()

        insitu_test_slutt_tidspunkt: Union[Unset, str] = UNSET
        if not isinstance(self.insitu_test_slutt_tidspunkt, Unset):
            insitu_test_slutt_tidspunkt = self.insitu_test_slutt_tidspunkt.isoformat()

        r_ø_r_bunn = self.r_ø_r_bunn

        r_ø_r_topp = self.r_ø_r_topp

        r_ø_r_type = self.r_ø_r_type

        hydraulisk_observasjon: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.hydraulisk_observasjon, Unset):
            hydraulisk_observasjon = []
            for hydraulisk_observasjon_item_data in self.hydraulisk_observasjon:
                hydraulisk_observasjon_item = hydraulisk_observasjon_item_data.to_dict()
                hydraulisk_observasjon.append(hydraulisk_observasjon_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if json_type is not UNSET:
            field_dict["jsonType"] = json_type
        if identifikasjon is not UNSET:
            field_dict["identifikasjon"] = identifikasjon
        if fra_borlengde is not UNSET:
            field_dict["fraBorlengde"] = fra_borlengde
        if til_borlengde is not UNSET:
            field_dict["tilBorlengde"] = til_borlengde
        if insitu_test_start_tidspunkt is not UNSET:
            field_dict["insituTestStartTidspunkt"] = insitu_test_start_tidspunkt
        if insitu_test_slutt_tidspunkt is not UNSET:
            field_dict["insituTestSluttTidspunkt"] = insitu_test_slutt_tidspunkt
        if r_ø_r_bunn is not UNSET:
            field_dict["rørBunn"] = r_ø_r_bunn
        if r_ø_r_topp is not UNSET:
            field_dict["rørTopp"] = r_ø_r_topp
        if r_ø_r_type is not UNSET:
            field_dict["rørType"] = r_ø_r_type
        if hydraulisk_observasjon is not UNSET:
            field_dict["hydrauliskObservasjon"] = hydraulisk_observasjon

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.hydrauliske_data import HydrauliskeData
        from ..models.identifikasjon import Identifikasjon

        d = dict(src_dict)
        json_type = cast(Union[Literal["HydrauliskTest"], Unset], d.pop("jsonType", UNSET))
        if json_type != "HydrauliskTest" and not isinstance(json_type, Unset):
            raise ValueError(f"jsonType must match const 'HydrauliskTest', got '{json_type}'")

        _identifikasjon = d.pop("identifikasjon", UNSET)
        identifikasjon: Union[Unset, Identifikasjon]
        if isinstance(_identifikasjon, Unset):
            identifikasjon = UNSET
        else:
            identifikasjon = Identifikasjon.from_dict(_identifikasjon)

        fra_borlengde = d.pop("fraBorlengde", UNSET)

        til_borlengde = d.pop("tilBorlengde", UNSET)

        _insitu_test_start_tidspunkt = d.pop("insituTestStartTidspunkt", UNSET)
        insitu_test_start_tidspunkt: Union[Unset, datetime.datetime]
        if isinstance(_insitu_test_start_tidspunkt, Unset):
            insitu_test_start_tidspunkt = UNSET
        else:
            insitu_test_start_tidspunkt = isoparse(_insitu_test_start_tidspunkt)

        _insitu_test_slutt_tidspunkt = d.pop("insituTestSluttTidspunkt", UNSET)
        insitu_test_slutt_tidspunkt: Union[Unset, datetime.datetime]
        if isinstance(_insitu_test_slutt_tidspunkt, Unset):
            insitu_test_slutt_tidspunkt = UNSET
        else:
            insitu_test_slutt_tidspunkt = isoparse(_insitu_test_slutt_tidspunkt)

        r_ø_r_bunn = d.pop("rørBunn", UNSET)

        r_ø_r_topp = d.pop("rørTopp", UNSET)

        r_ø_r_type = d.pop("rørType", UNSET)

        hydraulisk_observasjon = []
        _hydraulisk_observasjon = d.pop("hydrauliskObservasjon", UNSET)
        for hydraulisk_observasjon_item_data in _hydraulisk_observasjon or []:
            hydraulisk_observasjon_item = HydrauliskeData.from_dict(hydraulisk_observasjon_item_data)

            hydraulisk_observasjon.append(hydraulisk_observasjon_item)

        hydraulisk_test = cls(
            json_type=json_type,
            identifikasjon=identifikasjon,
            fra_borlengde=fra_borlengde,
            til_borlengde=til_borlengde,
            insitu_test_start_tidspunkt=insitu_test_start_tidspunkt,
            insitu_test_slutt_tidspunkt=insitu_test_slutt_tidspunkt,
            r_ø_r_bunn=r_ø_r_bunn,
            r_ø_r_topp=r_ø_r_topp,
            r_ø_r_type=r_ø_r_type,
            hydraulisk_observasjon=hydraulisk_observasjon,
        )

        hydraulisk_test.additional_properties = d
        return hydraulisk_test

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
