from enum import Enum


class DeformasjonObservasjonKode(str, Enum):
    HINDRING = "HINDRING"
    IKKESPESIFISERT = "IKKESPESIFISERT"
    SKADET = "SKADET"
    USIKKERT = "USIKKERT"

    def __str__(self) -> str:
        return str(self.value)
