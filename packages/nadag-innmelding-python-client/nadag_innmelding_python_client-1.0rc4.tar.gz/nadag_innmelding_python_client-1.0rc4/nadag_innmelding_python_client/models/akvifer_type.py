from enum import Enum


class AkviferType(str, Enum):
    ARTESISK = "ARTESISK"
    IKKE_ANGITT = "IKKE_ANGITT"
    LUKKET = "LUKKET"
    UTETT = "UTETT"
    ÅPEN = "ÅPEN"

    def __str__(self) -> str:
        return str(self.value)
