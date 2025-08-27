import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Literal, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.akvifer_type import AkviferType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.grunnvann_data import GrunnvannData
    from ..models.identifikasjon import Identifikasjon
    from ..models.overvaakning_data import OvervaakningData


T = TypeVar("T", bound="GrunnvannMaaling")


@_attrs_define
class GrunnvannMaaling:
    """måling av grunnvannstand i felt<engelsk>measurement of the ground water table in the field</engelsk>

    Attributes:
        json_type (Union[Literal['GrunnvannMaaling'], Unset]):
        identifikasjon (Union[Unset, Identifikasjon]): Unik identifikasjon av et objekt, ivaretatt av den ansvarlige
            produsent/forvalter, som kan benyttes av eksterne applikasjoner som referanse til objektet.

            NOTE1 Denne eksterne objektidentifikasjonen må ikke forveksles med en tematisk objektidentifikasjon, slik som
            f.eks bygningsnummer.

            NOTE 2 Denne unike identifikatoren vil ikke endres i løpet av objektets levetid.
        fra_borlengde (Union[Unset, float]):
        til_borlengde (Union[Unset, float]):
        insitu_test_start_tidspunkt (Union[Unset, datetime.datetime]):
        insitu_test_slutt_tidspunkt (Union[Unset, datetime.datetime]):
        er_langtidsobservasjon (Union[Unset, bool]):
        filter_dyp (Union[Unset, float]):
        filter_lengde (Union[Unset, float]):
        filter_type (Union[Unset, str]):
        grunnvann_akvifer (Union[Unset, AkviferType]): oversikt over mulige akvifertyper for
            grunnvannsmålinger<engelsk>overview of possible aquifer types for ground water measurements</engelsk>
        r_ø_r_bunn (Union[Unset, float]):
        r_ø_r_topp (Union[Unset, float]):
        r_ø_r_type (Union[Unset, str]):
        grunnvann_observasjon (Union[Unset, list['GrunnvannData']]):
        overv_å_kning_obervasjon (Union[Unset, list['OvervaakningData']]):
    """

    json_type: Union[Literal["GrunnvannMaaling"], Unset] = UNSET
    identifikasjon: Union[Unset, "Identifikasjon"] = UNSET
    fra_borlengde: Union[Unset, float] = UNSET
    til_borlengde: Union[Unset, float] = UNSET
    insitu_test_start_tidspunkt: Union[Unset, datetime.datetime] = UNSET
    insitu_test_slutt_tidspunkt: Union[Unset, datetime.datetime] = UNSET
    er_langtidsobservasjon: Union[Unset, bool] = UNSET
    filter_dyp: Union[Unset, float] = UNSET
    filter_lengde: Union[Unset, float] = UNSET
    filter_type: Union[Unset, str] = UNSET
    grunnvann_akvifer: Union[Unset, AkviferType] = UNSET
    r_ø_r_bunn: Union[Unset, float] = UNSET
    r_ø_r_topp: Union[Unset, float] = UNSET
    r_ø_r_type: Union[Unset, str] = UNSET
    grunnvann_observasjon: Union[Unset, list["GrunnvannData"]] = UNSET
    overv_å_kning_obervasjon: Union[Unset, list["OvervaakningData"]] = UNSET
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

        er_langtidsobservasjon = self.er_langtidsobservasjon

        filter_dyp = self.filter_dyp

        filter_lengde = self.filter_lengde

        filter_type = self.filter_type

        grunnvann_akvifer: Union[Unset, str] = UNSET
        if not isinstance(self.grunnvann_akvifer, Unset):
            grunnvann_akvifer = self.grunnvann_akvifer.value

        r_ø_r_bunn = self.r_ø_r_bunn

        r_ø_r_topp = self.r_ø_r_topp

        r_ø_r_type = self.r_ø_r_type

        grunnvann_observasjon: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.grunnvann_observasjon, Unset):
            grunnvann_observasjon = []
            for grunnvann_observasjon_item_data in self.grunnvann_observasjon:
                grunnvann_observasjon_item = grunnvann_observasjon_item_data.to_dict()
                grunnvann_observasjon.append(grunnvann_observasjon_item)

        overv_å_kning_obervasjon: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.overv_å_kning_obervasjon, Unset):
            overv_å_kning_obervasjon = []
            for overv_å_kning_obervasjon_item_data in self.overv_å_kning_obervasjon:
                overv_å_kning_obervasjon_item = overv_å_kning_obervasjon_item_data.to_dict()
                overv_å_kning_obervasjon.append(overv_å_kning_obervasjon_item)

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
        if er_langtidsobservasjon is not UNSET:
            field_dict["erLangtidsobservasjon"] = er_langtidsobservasjon
        if filter_dyp is not UNSET:
            field_dict["filterDyp"] = filter_dyp
        if filter_lengde is not UNSET:
            field_dict["filterLengde"] = filter_lengde
        if filter_type is not UNSET:
            field_dict["filterType"] = filter_type
        if grunnvann_akvifer is not UNSET:
            field_dict["grunnvannAkvifer"] = grunnvann_akvifer
        if r_ø_r_bunn is not UNSET:
            field_dict["rørBunn"] = r_ø_r_bunn
        if r_ø_r_topp is not UNSET:
            field_dict["rørTopp"] = r_ø_r_topp
        if r_ø_r_type is not UNSET:
            field_dict["rørType"] = r_ø_r_type
        if grunnvann_observasjon is not UNSET:
            field_dict["grunnvannObservasjon"] = grunnvann_observasjon
        if overv_å_kning_obervasjon is not UNSET:
            field_dict["overvåkningObervasjon"] = overv_å_kning_obervasjon

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.grunnvann_data import GrunnvannData
        from ..models.identifikasjon import Identifikasjon
        from ..models.overvaakning_data import OvervaakningData

        d = dict(src_dict)
        json_type = cast(Union[Literal["GrunnvannMaaling"], Unset], d.pop("jsonType", UNSET))
        if json_type != "GrunnvannMaaling" and not isinstance(json_type, Unset):
            raise ValueError(f"jsonType must match const 'GrunnvannMaaling', got '{json_type}'")

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

        er_langtidsobservasjon = d.pop("erLangtidsobservasjon", UNSET)

        filter_dyp = d.pop("filterDyp", UNSET)

        filter_lengde = d.pop("filterLengde", UNSET)

        filter_type = d.pop("filterType", UNSET)

        _grunnvann_akvifer = d.pop("grunnvannAkvifer", UNSET)
        grunnvann_akvifer: Union[Unset, AkviferType]
        if isinstance(_grunnvann_akvifer, Unset):
            grunnvann_akvifer = UNSET
        else:
            grunnvann_akvifer = AkviferType(_grunnvann_akvifer)

        r_ø_r_bunn = d.pop("rørBunn", UNSET)

        r_ø_r_topp = d.pop("rørTopp", UNSET)

        r_ø_r_type = d.pop("rørType", UNSET)

        grunnvann_observasjon = []
        _grunnvann_observasjon = d.pop("grunnvannObservasjon", UNSET)
        for grunnvann_observasjon_item_data in _grunnvann_observasjon or []:
            grunnvann_observasjon_item = GrunnvannData.from_dict(grunnvann_observasjon_item_data)

            grunnvann_observasjon.append(grunnvann_observasjon_item)

        overv_å_kning_obervasjon = []
        _overv_å_kning_obervasjon = d.pop("overvåkningObervasjon", UNSET)
        for overv_å_kning_obervasjon_item_data in _overv_å_kning_obervasjon or []:
            overv_å_kning_obervasjon_item = OvervaakningData.from_dict(overv_å_kning_obervasjon_item_data)

            overv_å_kning_obervasjon.append(overv_å_kning_obervasjon_item)

        grunnvann_maaling = cls(
            json_type=json_type,
            identifikasjon=identifikasjon,
            fra_borlengde=fra_borlengde,
            til_borlengde=til_borlengde,
            insitu_test_start_tidspunkt=insitu_test_start_tidspunkt,
            insitu_test_slutt_tidspunkt=insitu_test_slutt_tidspunkt,
            er_langtidsobservasjon=er_langtidsobservasjon,
            filter_dyp=filter_dyp,
            filter_lengde=filter_lengde,
            filter_type=filter_type,
            grunnvann_akvifer=grunnvann_akvifer,
            r_ø_r_bunn=r_ø_r_bunn,
            r_ø_r_topp=r_ø_r_topp,
            r_ø_r_type=r_ø_r_type,
            grunnvann_observasjon=grunnvann_observasjon,
            overv_å_kning_obervasjon=overv_å_kning_obervasjon,
        )

        grunnvann_maaling.additional_properties = d
        return grunnvann_maaling

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
