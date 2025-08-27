import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Literal, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.poretrykk_maale_kategori import PoretrykkMaaleKategori
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.identifikasjon import Identifikasjon
    from ..models.poretrykk_data import PoretrykkData


T = TypeVar("T", bound="PoretrykkMaaling")


@_attrs_define
class PoretrykkMaaling:
    """måling av poretrykkforhold i grunnen foretatt i løpet av en tidsperiode og / eller i flere dybder. poretrykk er
    trykket i porevannet angitt som kraft pr. flateenhet, og med atmosføretrykket som referanse<engelsk>measurement of
    pore pressure in the groundwater during a time period and / or in several depths. the pore pressure is the pressure
    in the pore water given as force per area unit, with the atmospheric pressure as reference</engelsk>

        Attributes:
            json_type (Union[Literal['PoretrykkMaaling'], Unset]):
            identifikasjon (Union[Unset, Identifikasjon]): Unik identifikasjon av et objekt, ivaretatt av den ansvarlige
                produsent/forvalter, som kan benyttes av eksterne applikasjoner som referanse til objektet.

                NOTE1 Denne eksterne objektidentifikasjonen må ikke forveksles med en tematisk objektidentifikasjon, slik som
                f.eks bygningsnummer.

                NOTE 2 Denne unike identifikatoren vil ikke endres i løpet av objektets levetid.
            fra_borlengde (Union[Unset, float]):
            til_borlengde (Union[Unset, float]):
            insitu_test_start_tidspunkt (Union[Unset, datetime.datetime]):
            insitu_test_slutt_tidspunkt (Union[Unset, datetime.datetime]):
            installasjon_tidspunkt (Union[Unset, datetime.datetime]):
            filter_lengde (Union[Unset, float]):
            kote_spiss (Union[Unset, float]):
            filter_type (Union[Unset, str]):
            r_ø_r_topp_filter (Union[Unset, float]):
            r_ø_r_topp_slange (Union[Unset, float]):
            r_ø_r_topp (Union[Unset, float]):
            r_ø_r_bunn (Union[Unset, float]):
            m_å_lerspiss_nummer (Union[Unset, str]):
            m_å_ler_kategori (Union[Unset, PoretrykkMaaleKategori]): oversikt over aktuelle typer
                poretrykksmålere<engelsk>overview of possible types of pore pressure measurement devices</engelsk>
            m_å_ler_type (Union[Unset, str]):
            poretrykk_observasjon (Union[Unset, list['PoretrykkData']]):
    """

    json_type: Union[Literal["PoretrykkMaaling"], Unset] = UNSET
    identifikasjon: Union[Unset, "Identifikasjon"] = UNSET
    fra_borlengde: Union[Unset, float] = UNSET
    til_borlengde: Union[Unset, float] = UNSET
    insitu_test_start_tidspunkt: Union[Unset, datetime.datetime] = UNSET
    insitu_test_slutt_tidspunkt: Union[Unset, datetime.datetime] = UNSET
    installasjon_tidspunkt: Union[Unset, datetime.datetime] = UNSET
    filter_lengde: Union[Unset, float] = UNSET
    kote_spiss: Union[Unset, float] = UNSET
    filter_type: Union[Unset, str] = UNSET
    r_ø_r_topp_filter: Union[Unset, float] = UNSET
    r_ø_r_topp_slange: Union[Unset, float] = UNSET
    r_ø_r_topp: Union[Unset, float] = UNSET
    r_ø_r_bunn: Union[Unset, float] = UNSET
    m_å_lerspiss_nummer: Union[Unset, str] = UNSET
    m_å_ler_kategori: Union[Unset, PoretrykkMaaleKategori] = UNSET
    m_å_ler_type: Union[Unset, str] = UNSET
    poretrykk_observasjon: Union[Unset, list["PoretrykkData"]] = UNSET
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

        installasjon_tidspunkt: Union[Unset, str] = UNSET
        if not isinstance(self.installasjon_tidspunkt, Unset):
            installasjon_tidspunkt = self.installasjon_tidspunkt.isoformat()

        filter_lengde = self.filter_lengde

        kote_spiss = self.kote_spiss

        filter_type = self.filter_type

        r_ø_r_topp_filter = self.r_ø_r_topp_filter

        r_ø_r_topp_slange = self.r_ø_r_topp_slange

        r_ø_r_topp = self.r_ø_r_topp

        r_ø_r_bunn = self.r_ø_r_bunn

        m_å_lerspiss_nummer = self.m_å_lerspiss_nummer

        m_å_ler_kategori: Union[Unset, str] = UNSET
        if not isinstance(self.m_å_ler_kategori, Unset):
            m_å_ler_kategori = self.m_å_ler_kategori.value

        m_å_ler_type = self.m_å_ler_type

        poretrykk_observasjon: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.poretrykk_observasjon, Unset):
            poretrykk_observasjon = []
            for poretrykk_observasjon_item_data in self.poretrykk_observasjon:
                poretrykk_observasjon_item = poretrykk_observasjon_item_data.to_dict()
                poretrykk_observasjon.append(poretrykk_observasjon_item)

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
        if installasjon_tidspunkt is not UNSET:
            field_dict["installasjonTidspunkt"] = installasjon_tidspunkt
        if filter_lengde is not UNSET:
            field_dict["filterLengde"] = filter_lengde
        if kote_spiss is not UNSET:
            field_dict["koteSpiss"] = kote_spiss
        if filter_type is not UNSET:
            field_dict["filterType"] = filter_type
        if r_ø_r_topp_filter is not UNSET:
            field_dict["rørToppFilter"] = r_ø_r_topp_filter
        if r_ø_r_topp_slange is not UNSET:
            field_dict["rørToppSlange"] = r_ø_r_topp_slange
        if r_ø_r_topp is not UNSET:
            field_dict["rørTopp"] = r_ø_r_topp
        if r_ø_r_bunn is not UNSET:
            field_dict["rørBunn"] = r_ø_r_bunn
        if m_å_lerspiss_nummer is not UNSET:
            field_dict["målerspissNummer"] = m_å_lerspiss_nummer
        if m_å_ler_kategori is not UNSET:
            field_dict["målerKategori"] = m_å_ler_kategori
        if m_å_ler_type is not UNSET:
            field_dict["målerType"] = m_å_ler_type
        if poretrykk_observasjon is not UNSET:
            field_dict["poretrykkObservasjon"] = poretrykk_observasjon

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.identifikasjon import Identifikasjon
        from ..models.poretrykk_data import PoretrykkData

        d = dict(src_dict)
        json_type = cast(Union[Literal["PoretrykkMaaling"], Unset], d.pop("jsonType", UNSET))
        if json_type != "PoretrykkMaaling" and not isinstance(json_type, Unset):
            raise ValueError(f"jsonType must match const 'PoretrykkMaaling', got '{json_type}'")

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

        _installasjon_tidspunkt = d.pop("installasjonTidspunkt", UNSET)
        installasjon_tidspunkt: Union[Unset, datetime.datetime]
        if isinstance(_installasjon_tidspunkt, Unset):
            installasjon_tidspunkt = UNSET
        else:
            installasjon_tidspunkt = isoparse(_installasjon_tidspunkt)

        filter_lengde = d.pop("filterLengde", UNSET)

        kote_spiss = d.pop("koteSpiss", UNSET)

        filter_type = d.pop("filterType", UNSET)

        r_ø_r_topp_filter = d.pop("rørToppFilter", UNSET)

        r_ø_r_topp_slange = d.pop("rørToppSlange", UNSET)

        r_ø_r_topp = d.pop("rørTopp", UNSET)

        r_ø_r_bunn = d.pop("rørBunn", UNSET)

        m_å_lerspiss_nummer = d.pop("målerspissNummer", UNSET)

        _m_å_ler_kategori = d.pop("målerKategori", UNSET)
        m_å_ler_kategori: Union[Unset, PoretrykkMaaleKategori]
        if isinstance(_m_å_ler_kategori, Unset):
            m_å_ler_kategori = UNSET
        else:
            m_å_ler_kategori = PoretrykkMaaleKategori(_m_å_ler_kategori)

        m_å_ler_type = d.pop("målerType", UNSET)

        poretrykk_observasjon = []
        _poretrykk_observasjon = d.pop("poretrykkObservasjon", UNSET)
        for poretrykk_observasjon_item_data in _poretrykk_observasjon or []:
            poretrykk_observasjon_item = PoretrykkData.from_dict(poretrykk_observasjon_item_data)

            poretrykk_observasjon.append(poretrykk_observasjon_item)

        poretrykk_maaling = cls(
            json_type=json_type,
            identifikasjon=identifikasjon,
            fra_borlengde=fra_borlengde,
            til_borlengde=til_borlengde,
            insitu_test_start_tidspunkt=insitu_test_start_tidspunkt,
            insitu_test_slutt_tidspunkt=insitu_test_slutt_tidspunkt,
            installasjon_tidspunkt=installasjon_tidspunkt,
            filter_lengde=filter_lengde,
            kote_spiss=kote_spiss,
            filter_type=filter_type,
            r_ø_r_topp_filter=r_ø_r_topp_filter,
            r_ø_r_topp_slange=r_ø_r_topp_slange,
            r_ø_r_topp=r_ø_r_topp,
            r_ø_r_bunn=r_ø_r_bunn,
            m_å_lerspiss_nummer=m_å_lerspiss_nummer,
            m_å_ler_kategori=m_å_ler_kategori,
            m_å_ler_type=m_å_ler_type,
            poretrykk_observasjon=poretrykk_observasjon,
        )

        poretrykk_maaling.additional_properties = d
        return poretrykk_maaling

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
