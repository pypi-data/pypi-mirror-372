from enum import Enum


class NedpressingsKapasitet(str, Enum):
    VALUE_0 = "_10_KN"
    VALUE_1 = "_100_KN"
    VALUE_2 = "_50_KN"

    def __str__(self) -> str:
        return str(self.value)
