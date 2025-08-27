from enum import Enum


class KvalitetBorlengdeTilBerg(str, Enum):
    ANTATT = "ANTATT"
    PÅVIST = "PÅVIST"

    def __str__(self) -> str:
        return str(self.value)
