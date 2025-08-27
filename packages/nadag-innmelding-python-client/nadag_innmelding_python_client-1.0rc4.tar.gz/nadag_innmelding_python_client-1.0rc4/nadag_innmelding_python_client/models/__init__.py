"""Contains all the data models used in inputs/outputs"""

from .akvifer_type import AkviferType
from .attachment_info_dto import AttachmentInfoDto
from .attachment_infos_dto import AttachmentInfosDto
from .blokk_proeve import BlokkProeve
from .borlengde_til_berg import BorlengdeTilBerg
from .deformasjon_maale_data import DeformasjonMaaleData
from .deformasjon_maaling import DeformasjonMaaling
from .deformasjon_observasjon_kode import DeformasjonObservasjonKode
from .deformasjon_overvaakning_data import DeformasjonOvervaakningData
from .dilatometer_test import DilatometerTest
from .dilatometer_test_data import DilatometerTestData
from .dissipasjon_data import DissipasjonData
from .dynamisk_sondering import DynamiskSondering
from .dynamisk_sondering_data import DynamiskSonderingData
from .ekstern_identifikasjon import EksternIdentifikasjon
from .epsg_code import EpsgCode
from .felt_unders_type_kode import FeltUndersTypeKode
from .gass_data import GassData
from .gass_maaling import GassMaaling
from .gass_proeve import GassProeve
from .geometry import Geometry
from .geometry_collection import GeometryCollection
from .geoteknisk_bore_observasjonskode import GeotekniskBoreObservasjonskode
from .geoteknisk_borehull import GeotekniskBorehull
from .geoteknisk_borehull_unders import GeotekniskBorehullUnders
from .geoteknisk_dokument import GeotekniskDokument
from .geoteknisk_felt_unders import GeotekniskFeltUnders
from .geoteknisk_felt_unders_metode_kode import GeotekniskFeltUndersMetodeKode
from .geoteknisk_grunnvann_observasjon_kode import GeotekniskGrunnvannObservasjonKode
from .geoteknisk_insitu_test import GeotekniskInsituTest
from .geoteknisk_metode_kode import GeotekniskMetodeKode
from .geoteknisk_observasjon_nadag import GeotekniskObservasjonNADAG
from .geoteknisk_proeveserie import GeotekniskProeveserie
from .geoteknisk_proeveseriedel import GeotekniskProeveseriedel
from .geoteknisk_proeveseriedel_data import GeotekniskProeveseriedelData
from .geoteknisk_proevetaking import GeotekniskProevetaking
from .geoteknisk_sondering import GeotekniskSondering
from .geoteknisk_stoppkode import GeotekniskStoppkode
from .geoteknisk_tolket_lag import GeotekniskTolketLag
from .geoteknisk_tolket_punkt import GeotekniskTolketPunkt
from .geoteknisk_unders import GeotekniskUnders
from .geoteknisk_undersoekelse_grense import GeotekniskUndersoekelseGrense
from .geovitenskapelig_observasjon import GeovitenskapeligObservasjon
from .geovitenskapelig_undersoekelse import GeovitenskapeligUndersoekelse
from .geovitenskapelig_undersoekelse_delomraade import GeovitenskapeligUndersoekelseDelomraade
from .geovitenskapelig_undersoekelse_delomraade_grense import GeovitenskapeligUndersoekelseDelomraadeGrense
from .geovitenskapelig_undersoekelse_grense import GeovitenskapeligUndersoekelseGrense
from .geovitenskaplig_borehull import GeovitenskapligBorehull
from .geovitenskaplig_borehull_undersoekelse import GeovitenskapligBorehullUndersoekelse
from .gjennomboret_medium import GjennomboretMedium
from .grave_proeve import GraveProeve
from .grunnvann_data import GrunnvannData
from .grunnvann_maaling import GrunnvannMaaling
from .hoved_lag_klassifisering import HovedLagKlassifisering
from .hydraulisk_konduktivitet import HydrauliskKonduktivitet
from .hydraulisk_test import HydrauliskTest
from .hydrauliske_data import HydrauliskeData
from .identifikasjon import Identifikasjon
from .kanne_proeve import KanneProeve
from .kjerne_boring import KjerneBoring
from .kjerne_boring_data import KjerneBoringData
from .kjerne_proeve import KjerneProeve
from .klassifiserings_metode import KlassifiseringsMetode
from .kombinasjon_sondering import KombinasjonSondering
from .kombinasjon_sondering_data import KombinasjonSonderingData
from .kopidata import Kopidata
from .kvalitet_borlengde_til_berg import KvalitetBorlengdeTilBerg
from .kvikkleire_paavisning_kode import KvikkleirePaavisningKode
from .lag_posisjon import LagPosisjon
from .maalemetode import Maalemetode
from .maalemetode_hoeyde import MaalemetodeHoeyde
from .miljoe_undersoekelse import MiljoeUndersoekelse
from .multi_polygon import MultiPolygon
from .naver_proeve import NaverProeve
from .nedpressings_kapasitet import NedpressingsKapasitet
from .overvaakning_data import OvervaakningData
from .platebelastning import Platebelastning
from .platebelastning_data import PlatebelastningData
from .point import Point
from .polygon import Polygon
from .poretrykk_data import PoretrykkData
from .poretrykk_data_insitu import PoretrykkDataInsitu
from .poretrykk_maale_kategori import PoretrykkMaaleKategori
from .poretrykk_maaling import PoretrykkMaaling
from .posisjonskvalitet import Posisjonskvalitet
from .posisjonskvalitet_nadag import PosisjonskvalitetNADAG
from .proevetaking_type import ProevetakingType
from .ram_proeve import RamProeve
from .representasjon_kvalitet import RepresentasjonKvalitet
from .sediment_proeve import SedimentProeve
from .skovl_proeve import SkovlProeve
from .sonde_kvalitets_klasse import SondeKvalitetsKlasse
from .statisk_sondering import StatiskSondering
from .statisk_sondering_data import StatiskSonderingData
from .stempel_proeve import StempelProeve
from .supertype_geotekn_obj_omr import SupertypeGeoteknObjOmr
from .supertype_geotekn_obj_pkt import SupertypeGeoteknObjPkt
from .synbarhet import Synbarhet
from .tolkning_metode_kode import TolkningMetodeKode
from .trykksondering import Trykksondering
from .trykksondering_data import TrykksonderingData
from .validated_geoteknisk_unders import ValidatedGeotekniskUnders
from .validated_geoteknisk_unders_diagnostics import ValidatedGeotekniskUndersDiagnostics
from .vann_proeve import VannProeve
from .vann_proeve_kilde import VannProeveKilde
from .vingeboring import Vingeboring
from .vingeboring_data import VingeboringData

__all__ = (
    "AkviferType",
    "AttachmentInfoDto",
    "AttachmentInfosDto",
    "BlokkProeve",
    "BorlengdeTilBerg",
    "DeformasjonMaaleData",
    "DeformasjonMaaling",
    "DeformasjonObservasjonKode",
    "DeformasjonOvervaakningData",
    "DilatometerTest",
    "DilatometerTestData",
    "DissipasjonData",
    "DynamiskSondering",
    "DynamiskSonderingData",
    "EksternIdentifikasjon",
    "EpsgCode",
    "FeltUndersTypeKode",
    "GassData",
    "GassMaaling",
    "GassProeve",
    "Geometry",
    "GeometryCollection",
    "GeotekniskBorehull",
    "GeotekniskBorehullUnders",
    "GeotekniskBoreObservasjonskode",
    "GeotekniskDokument",
    "GeotekniskFeltUnders",
    "GeotekniskFeltUndersMetodeKode",
    "GeotekniskGrunnvannObservasjonKode",
    "GeotekniskInsituTest",
    "GeotekniskMetodeKode",
    "GeotekniskObservasjonNADAG",
    "GeotekniskProeveserie",
    "GeotekniskProeveseriedel",
    "GeotekniskProeveseriedelData",
    "GeotekniskProevetaking",
    "GeotekniskSondering",
    "GeotekniskStoppkode",
    "GeotekniskTolketLag",
    "GeotekniskTolketPunkt",
    "GeotekniskUnders",
    "GeotekniskUndersoekelseGrense",
    "GeovitenskapeligObservasjon",
    "GeovitenskapeligUndersoekelse",
    "GeovitenskapeligUndersoekelseDelomraade",
    "GeovitenskapeligUndersoekelseDelomraadeGrense",
    "GeovitenskapeligUndersoekelseGrense",
    "GeovitenskapligBorehull",
    "GeovitenskapligBorehullUndersoekelse",
    "GjennomboretMedium",
    "GraveProeve",
    "GrunnvannData",
    "GrunnvannMaaling",
    "HovedLagKlassifisering",
    "HydrauliskeData",
    "HydrauliskKonduktivitet",
    "HydrauliskTest",
    "Identifikasjon",
    "KanneProeve",
    "KjerneBoring",
    "KjerneBoringData",
    "KjerneProeve",
    "KlassifiseringsMetode",
    "KombinasjonSondering",
    "KombinasjonSonderingData",
    "Kopidata",
    "KvalitetBorlengdeTilBerg",
    "KvikkleirePaavisningKode",
    "LagPosisjon",
    "Maalemetode",
    "MaalemetodeHoeyde",
    "MiljoeUndersoekelse",
    "MultiPolygon",
    "NaverProeve",
    "NedpressingsKapasitet",
    "OvervaakningData",
    "Platebelastning",
    "PlatebelastningData",
    "Point",
    "Polygon",
    "PoretrykkData",
    "PoretrykkDataInsitu",
    "PoretrykkMaaleKategori",
    "PoretrykkMaaling",
    "Posisjonskvalitet",
    "PosisjonskvalitetNADAG",
    "ProevetakingType",
    "RamProeve",
    "RepresentasjonKvalitet",
    "SedimentProeve",
    "SkovlProeve",
    "SondeKvalitetsKlasse",
    "StatiskSondering",
    "StatiskSonderingData",
    "StempelProeve",
    "SupertypeGeoteknObjOmr",
    "SupertypeGeoteknObjPkt",
    "Synbarhet",
    "TolkningMetodeKode",
    "Trykksondering",
    "TrykksonderingData",
    "ValidatedGeotekniskUnders",
    "ValidatedGeotekniskUndersDiagnostics",
    "VannProeve",
    "VannProeveKilde",
    "Vingeboring",
    "VingeboringData",
)
