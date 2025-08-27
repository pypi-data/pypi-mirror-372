from enum import Enum


class LagPosisjon(str, Enum):
    HØYRE = "HØYRE"
    IKKEANGITT = "IKKEANGITT"
    MIDTEN = "MIDTEN"
    VENSTRE = "VENSTRE"

    def __str__(self) -> str:
        return str(self.value)
