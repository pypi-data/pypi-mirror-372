from enum import Enum


class KvikkleirePaavisningKode(str, Enum):
    ANTATT = "ANTATT"
    ANTATTIKKEKVIKK = "ANTATTIKKEKVIKK"
    IKKEVURDERT = "IKKEVURDERT"
    SIKKER = "SIKKER"
    USIKKER = "USIKKER"

    def __str__(self) -> str:
        return str(self.value)
