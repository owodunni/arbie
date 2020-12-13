"""Utility functions for createting large numbers."""


class BigNumber(object):
    """BigNumber is used for creating etheruem friendly numbers."""

    def __init__(self, value, exp=18):
        self.value = int(round(value * 10 ** exp))
        self.exp = exp

    def __eq__(self, other):
        if isinstance(other, BigNumber):
            return self.value == other.value and self.exp == other.exp
        return self.value == other

    def __gt__(self, other):
        if isinstance(other, BigNumber):
            return self.value > other.value
        return self.value > other

    def __truediv__(self, other):
        return self.to_number() / other.to_number()

    @classmethod
    def from_value(cls, value, exp=18):
        bg = cls(0, exp)
        bg.value = int(value)
        return bg

    def to_number(self) -> float:
        return self.value / (10 ** self.exp)
