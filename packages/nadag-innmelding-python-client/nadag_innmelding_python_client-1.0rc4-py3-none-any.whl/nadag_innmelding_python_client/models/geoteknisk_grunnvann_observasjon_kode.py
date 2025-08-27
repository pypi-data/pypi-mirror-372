from enum import Enum


class GeotekniskGrunnvannObservasjonKode(str, Enum):
    ERSTATTET = "ERSTATTET"
    FERDIG = "FERDIG"
    FROSSET = "FROSSET"
    FUNKSJONSJEKKFEILET = "FUNKSJONSJEKKFEILET"
    FUNKSJONSJEKKOK = "FUNKSJONSJEKKOK"
    IKKESPESIFISERT = "IKKESPESIFISERT"
    SPYLET = "SPYLET"
    STIKK = "STIKK"
    TØRR = "TØRR"
    VANNSTRØM = "VANNSTRØM"

    def __str__(self) -> str:
        return str(self.value)
