from enum import Enum


class VannProeveKilde(str, Enum):
    GRUNNVANN = "GRUNNVANN"
    OVERFLATEVANN = "OVERFLATEVANN"
    POREVANN = "POREVANN"
    SIGEVANN = "SIGEVANN"

    def __str__(self) -> str:
        return str(self.value)
