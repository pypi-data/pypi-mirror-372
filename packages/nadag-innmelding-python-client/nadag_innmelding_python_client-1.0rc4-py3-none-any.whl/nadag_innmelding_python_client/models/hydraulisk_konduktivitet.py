from enum import Enum


class HydrauliskKonduktivitet(str, Enum):
    DÅRLIG_VANNGIVER = "DÅRLIG_VANNGIVER"
    GANSKE_DÅRLIG_VANNGIVER = "GANSKE_DÅRLIG_VANNGIVER"
    GOD_VANNGIVER = "GOD_VANNGIVER"
    MEGET_DÅRLIG_VANNGIVER = "MEGET_DÅRLIG_VANNGIVER"
    MEGET_GOD_VANNGIVER = "MEGET_GOD_VANNGIVER"

    def __str__(self) -> str:
        return str(self.value)
