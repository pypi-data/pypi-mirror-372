import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Literal, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.gass_data import GassData
    from ..models.identifikasjon import Identifikasjon


T = TypeVar("T", bound="GassMaaling")


@_attrs_define
class GassMaaling:
    """måling av  gass<engelsk>measurement of gas</engelsk>

    Attributes:
        json_type (Union[Literal['GassMaaling'], Unset]):
        identifikasjon (Union[Unset, Identifikasjon]): Unik identifikasjon av et objekt, ivaretatt av den ansvarlige
            produsent/forvalter, som kan benyttes av eksterne applikasjoner som referanse til objektet.

            NOTE1 Denne eksterne objektidentifikasjonen må ikke forveksles med en tematisk objektidentifikasjon, slik som
            f.eks bygningsnummer.

            NOTE 2 Denne unike identifikatoren vil ikke endres i løpet av objektets levetid.
        fra_borlengde (Union[Unset, float]):
        til_borlengde (Union[Unset, float]):
        insitu_test_start_tidspunkt (Union[Unset, datetime.datetime]):
        insitu_test_slutt_tidspunkt (Union[Unset, datetime.datetime]):
        plassering (Union[Unset, str]):
        bygg_nummer (Union[Unset, str]):
        gass_observasjon (Union[Unset, list['GassData']]):
    """

    json_type: Union[Literal["GassMaaling"], Unset] = UNSET
    identifikasjon: Union[Unset, "Identifikasjon"] = UNSET
    fra_borlengde: Union[Unset, float] = UNSET
    til_borlengde: Union[Unset, float] = UNSET
    insitu_test_start_tidspunkt: Union[Unset, datetime.datetime] = UNSET
    insitu_test_slutt_tidspunkt: Union[Unset, datetime.datetime] = UNSET
    plassering: Union[Unset, str] = UNSET
    bygg_nummer: Union[Unset, str] = UNSET
    gass_observasjon: Union[Unset, list["GassData"]] = UNSET
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

        plassering = self.plassering

        bygg_nummer = self.bygg_nummer

        gass_observasjon: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.gass_observasjon, Unset):
            gass_observasjon = []
            for gass_observasjon_item_data in self.gass_observasjon:
                gass_observasjon_item = gass_observasjon_item_data.to_dict()
                gass_observasjon.append(gass_observasjon_item)

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
        if plassering is not UNSET:
            field_dict["plassering"] = plassering
        if bygg_nummer is not UNSET:
            field_dict["byggNummer"] = bygg_nummer
        if gass_observasjon is not UNSET:
            field_dict["gassObservasjon"] = gass_observasjon

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.gass_data import GassData
        from ..models.identifikasjon import Identifikasjon

        d = dict(src_dict)
        json_type = cast(Union[Literal["GassMaaling"], Unset], d.pop("jsonType", UNSET))
        if json_type != "GassMaaling" and not isinstance(json_type, Unset):
            raise ValueError(f"jsonType must match const 'GassMaaling', got '{json_type}'")

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

        plassering = d.pop("plassering", UNSET)

        bygg_nummer = d.pop("byggNummer", UNSET)

        gass_observasjon = []
        _gass_observasjon = d.pop("gassObservasjon", UNSET)
        for gass_observasjon_item_data in _gass_observasjon or []:
            gass_observasjon_item = GassData.from_dict(gass_observasjon_item_data)

            gass_observasjon.append(gass_observasjon_item)

        gass_maaling = cls(
            json_type=json_type,
            identifikasjon=identifikasjon,
            fra_borlengde=fra_borlengde,
            til_borlengde=til_borlengde,
            insitu_test_start_tidspunkt=insitu_test_start_tidspunkt,
            insitu_test_slutt_tidspunkt=insitu_test_slutt_tidspunkt,
            plassering=plassering,
            bygg_nummer=bygg_nummer,
            gass_observasjon=gass_observasjon,
        )

        gass_maaling.additional_properties = d
        return gass_maaling

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
