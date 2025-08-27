import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Literal, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.dilatometer_test_data import DilatometerTestData
    from ..models.identifikasjon import Identifikasjon


T = TypeVar("T", bound="DilatometerTest")


@_attrs_define
class DilatometerTest:
    """en enkel innretning, formet som et flatt blad designet for å trykkes ned i bakken. Merknad: ble utviklet for å
    bestemme modulus for en jordart.
    <engelsk>a simple device, shaped in the form of a flat blade designed to be pushed into the ground Note: It was
    developed to evaluate the soil modulus.</engelsk>

        Attributes:
            json_type (Union[Literal['DilatometerTest'], Unset]):
            identifikasjon (Union[Unset, Identifikasjon]): Unik identifikasjon av et objekt, ivaretatt av den ansvarlige
                produsent/forvalter, som kan benyttes av eksterne applikasjoner som referanse til objektet.

                NOTE1 Denne eksterne objektidentifikasjonen må ikke forveksles med en tematisk objektidentifikasjon, slik som
                f.eks bygningsnummer.

                NOTE 2 Denne unike identifikatoren vil ikke endres i løpet av objektets levetid.
            fra_borlengde (Union[Unset, float]):
            til_borlengde (Union[Unset, float]):
            insitu_test_start_tidspunkt (Union[Unset, datetime.datetime]):
            insitu_test_slutt_tidspunkt (Union[Unset, datetime.datetime]):
            material_indeks (Union[Unset, float]):
            horisontal_spenning_indeks (Union[Unset, float]):
            dilatometer_modulus (Union[Unset, float]):
            dilatometer_observasjon (Union[Unset, list['DilatometerTestData']]):
    """

    json_type: Union[Literal["DilatometerTest"], Unset] = UNSET
    identifikasjon: Union[Unset, "Identifikasjon"] = UNSET
    fra_borlengde: Union[Unset, float] = UNSET
    til_borlengde: Union[Unset, float] = UNSET
    insitu_test_start_tidspunkt: Union[Unset, datetime.datetime] = UNSET
    insitu_test_slutt_tidspunkt: Union[Unset, datetime.datetime] = UNSET
    material_indeks: Union[Unset, float] = UNSET
    horisontal_spenning_indeks: Union[Unset, float] = UNSET
    dilatometer_modulus: Union[Unset, float] = UNSET
    dilatometer_observasjon: Union[Unset, list["DilatometerTestData"]] = UNSET
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

        material_indeks = self.material_indeks

        horisontal_spenning_indeks = self.horisontal_spenning_indeks

        dilatometer_modulus = self.dilatometer_modulus

        dilatometer_observasjon: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.dilatometer_observasjon, Unset):
            dilatometer_observasjon = []
            for dilatometer_observasjon_item_data in self.dilatometer_observasjon:
                dilatometer_observasjon_item = dilatometer_observasjon_item_data.to_dict()
                dilatometer_observasjon.append(dilatometer_observasjon_item)

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
        if material_indeks is not UNSET:
            field_dict["materialIndeks"] = material_indeks
        if horisontal_spenning_indeks is not UNSET:
            field_dict["horisontalSpenningIndeks"] = horisontal_spenning_indeks
        if dilatometer_modulus is not UNSET:
            field_dict["dilatometerModulus"] = dilatometer_modulus
        if dilatometer_observasjon is not UNSET:
            field_dict["dilatometerObservasjon"] = dilatometer_observasjon

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.dilatometer_test_data import DilatometerTestData
        from ..models.identifikasjon import Identifikasjon

        d = dict(src_dict)
        json_type = cast(Union[Literal["DilatometerTest"], Unset], d.pop("jsonType", UNSET))
        if json_type != "DilatometerTest" and not isinstance(json_type, Unset):
            raise ValueError(f"jsonType must match const 'DilatometerTest', got '{json_type}'")

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

        material_indeks = d.pop("materialIndeks", UNSET)

        horisontal_spenning_indeks = d.pop("horisontalSpenningIndeks", UNSET)

        dilatometer_modulus = d.pop("dilatometerModulus", UNSET)

        dilatometer_observasjon = []
        _dilatometer_observasjon = d.pop("dilatometerObservasjon", UNSET)
        for dilatometer_observasjon_item_data in _dilatometer_observasjon or []:
            dilatometer_observasjon_item = DilatometerTestData.from_dict(dilatometer_observasjon_item_data)

            dilatometer_observasjon.append(dilatometer_observasjon_item)

        dilatometer_test = cls(
            json_type=json_type,
            identifikasjon=identifikasjon,
            fra_borlengde=fra_borlengde,
            til_borlengde=til_borlengde,
            insitu_test_start_tidspunkt=insitu_test_start_tidspunkt,
            insitu_test_slutt_tidspunkt=insitu_test_slutt_tidspunkt,
            material_indeks=material_indeks,
            horisontal_spenning_indeks=horisontal_spenning_indeks,
            dilatometer_modulus=dilatometer_modulus,
            dilatometer_observasjon=dilatometer_observasjon,
        )

        dilatometer_test.additional_properties = d
        return dilatometer_test

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
