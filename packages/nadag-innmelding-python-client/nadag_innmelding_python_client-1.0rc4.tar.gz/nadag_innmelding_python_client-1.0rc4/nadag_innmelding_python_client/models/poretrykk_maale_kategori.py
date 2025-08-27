from enum import Enum


class PoretrykkMaaleKategori(str, Enum):
    ELEKTRISK = "ELEKTRISK"
    HYDRAULISK = "HYDRAULISK"

    def __str__(self) -> str:
        return str(self.value)
