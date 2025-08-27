import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Literal, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.identifikasjon import Identifikasjon
    from ..models.platebelastning_data import PlatebelastningData


T = TypeVar("T", bound="Platebelastning")


@_attrs_define
class Platebelastning:
    """undersøkelse for måling av in situ deformasjons- og konsolideringsegenskaper i
    friksjonsjordarter<engelsk>investigation for measurement of in situ deformation- and consolidation properties in
    friction soils</engelsk>

        Attributes:
            json_type (Union[Literal['Platebelastning'], Unset]):
            identifikasjon (Union[Unset, Identifikasjon]): Unik identifikasjon av et objekt, ivaretatt av den ansvarlige
                produsent/forvalter, som kan benyttes av eksterne applikasjoner som referanse til objektet.

                NOTE1 Denne eksterne objektidentifikasjonen må ikke forveksles med en tematisk objektidentifikasjon, slik som
                f.eks bygningsnummer.

                NOTE 2 Denne unike identifikatoren vil ikke endres i løpet av objektets levetid.
            fra_borlengde (Union[Unset, float]):
            til_borlengde (Union[Unset, float]):
            insitu_test_start_tidspunkt (Union[Unset, datetime.datetime]):
            insitu_test_slutt_tidspunkt (Union[Unset, datetime.datetime]):
            lasttrinn_antall (Union[Unset, int]):
            areal_plate (Union[Unset, float]):
            platebelastning_observasjon (Union[Unset, list['PlatebelastningData']]):
    """

    json_type: Union[Literal["Platebelastning"], Unset] = UNSET
    identifikasjon: Union[Unset, "Identifikasjon"] = UNSET
    fra_borlengde: Union[Unset, float] = UNSET
    til_borlengde: Union[Unset, float] = UNSET
    insitu_test_start_tidspunkt: Union[Unset, datetime.datetime] = UNSET
    insitu_test_slutt_tidspunkt: Union[Unset, datetime.datetime] = UNSET
    lasttrinn_antall: Union[Unset, int] = UNSET
    areal_plate: Union[Unset, float] = UNSET
    platebelastning_observasjon: Union[Unset, list["PlatebelastningData"]] = UNSET
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

        lasttrinn_antall = self.lasttrinn_antall

        areal_plate = self.areal_plate

        platebelastning_observasjon: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.platebelastning_observasjon, Unset):
            platebelastning_observasjon = []
            for platebelastning_observasjon_item_data in self.platebelastning_observasjon:
                platebelastning_observasjon_item = platebelastning_observasjon_item_data.to_dict()
                platebelastning_observasjon.append(platebelastning_observasjon_item)

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
        if lasttrinn_antall is not UNSET:
            field_dict["lasttrinnAntall"] = lasttrinn_antall
        if areal_plate is not UNSET:
            field_dict["arealPlate"] = areal_plate
        if platebelastning_observasjon is not UNSET:
            field_dict["platebelastningObservasjon"] = platebelastning_observasjon

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.identifikasjon import Identifikasjon
        from ..models.platebelastning_data import PlatebelastningData

        d = dict(src_dict)
        json_type = cast(Union[Literal["Platebelastning"], Unset], d.pop("jsonType", UNSET))
        if json_type != "Platebelastning" and not isinstance(json_type, Unset):
            raise ValueError(f"jsonType must match const 'Platebelastning', got '{json_type}'")

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

        lasttrinn_antall = d.pop("lasttrinnAntall", UNSET)

        areal_plate = d.pop("arealPlate", UNSET)

        platebelastning_observasjon = []
        _platebelastning_observasjon = d.pop("platebelastningObservasjon", UNSET)
        for platebelastning_observasjon_item_data in _platebelastning_observasjon or []:
            platebelastning_observasjon_item = PlatebelastningData.from_dict(platebelastning_observasjon_item_data)

            platebelastning_observasjon.append(platebelastning_observasjon_item)

        platebelastning = cls(
            json_type=json_type,
            identifikasjon=identifikasjon,
            fra_borlengde=fra_borlengde,
            til_borlengde=til_borlengde,
            insitu_test_start_tidspunkt=insitu_test_start_tidspunkt,
            insitu_test_slutt_tidspunkt=insitu_test_slutt_tidspunkt,
            lasttrinn_antall=lasttrinn_antall,
            areal_plate=areal_plate,
            platebelastning_observasjon=platebelastning_observasjon,
        )

        platebelastning.additional_properties = d
        return platebelastning

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
