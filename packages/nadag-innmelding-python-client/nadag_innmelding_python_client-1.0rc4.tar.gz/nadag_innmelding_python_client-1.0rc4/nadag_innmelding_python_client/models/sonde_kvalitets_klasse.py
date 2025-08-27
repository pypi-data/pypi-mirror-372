from enum import Enum


class SondeKvalitetsKlasse(str, Enum):
    KLASSE_1 = "KLASSE_1"
    KLASSE_2 = "KLASSE_2"
    KLASSE_3 = "KLASSE_3"
    KLASSE_4 = "KLASSE_4"

    def __str__(self) -> str:
        return str(self.value)
