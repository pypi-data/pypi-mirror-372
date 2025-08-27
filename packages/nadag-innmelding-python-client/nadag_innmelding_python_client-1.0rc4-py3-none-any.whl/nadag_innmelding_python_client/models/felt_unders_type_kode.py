from enum import Enum


class FeltUndersTypeKode(str, Enum):
    FELTUNDERSMETODE = "FELTUNDERSMETODE"
    TOLKET = "TOLKET"
    TOLKETBERGHØYDE = "TOLKETBERGHØYDE"

    def __str__(self) -> str:
        return str(self.value)
