from enum import Enum


class GjennomboretMedium(str, Enum):
    BERG = "BERG"
    IS = "IS"
    LUFT = "LUFT"
    LØSMASSE = "LØSMASSE"
    USPESIFISERT = "USPESIFISERT"
    VANN = "VANN"

    def __str__(self) -> str:
        return str(self.value)
