"""Test class for setting up AMMs."""
from typing import List, NewType, Tuple


class Token(object):
    """Token can be used to identify a ERC20 token."""

    def __init__(self, name: str):
        self.name = name


class Variable(object):
    """Variable bound to Token in pool."""

    def __init__(self, token: Token, value: float):
        self.token = token
        self.value = value

    def __add__(self, other):
        if self._is_number(other):
            return self.value + other
        return self.value + other.value

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        return self.__add__(-other)

    def __rsub__(self, other):
        return self.__sub__(other)

    def __mul__(self, other):
        if self._is_number(other):
            return self.value * other
        return self.value * other.value

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        if self._is_number(other):
            return self.value / other
        return self.value / other.value

    def _is_number(self, number):
        return isinstance(number, (int, float))


Variables = NewType('Variables', List[Variable])


def get_value(values: Variables, token: Token) -> Variable:
    for v in values:
        if v.token == token:
            return v
    raise ValueError('Token \"{0}\" not found'.format(token.name))


class Amm(object):
    """Amm can create a arbitrary AMM that can be used for testing.

    The math can be found here https://balancer.finance/whitepaper/
    """

    def __init__(self, balances: Variables, weights: Variables, fee: float = 0):
        self.balances = balances
        self.weights = weights
        self.fee = fee

        if sum(weights) != 1:
            raise ValueError('Weights are not normalized')

    def get_weights(self, token_in: Token, token_out: Token) -> Tuple[Variables, Variables]:
        return (get_value(self.weights, token_in), get_value(self.weights, token_out))

    def get_balances(self, token_in: Token, token_out: Token) -> Tuple[Variables, Variables]:
        return (get_value(self.balances, token_in), get_value(self.balances, token_out))

    def spot_price(self, token_in: Token, token_out: Token) -> float:
        bi, bo = self.get_balances(token_in, token_out)
        wi, wo = self.get_weights(token_in, token_out)
        return (bi / wi) / (bo / wo)

    def in_given_out(self, token_in: Token, token_out: Token, amount: float) -> float:
        bi, bo = self.get_balances(token_in, token_out)
        wi, wo = self.get_weights(token_in, token_out)
        fee = self.fee
        return bi * ((bo / (bo - amount * (1 - fee)))**(wo / wi) - 1)  # noqa: WPS221

    def out_given_in(self, token_in: Token, token_out: Token, amount: float) -> float:
        bi, bo = self.get_balances(token_in, token_out)
        wi, wo = self.get_weights(token_in, token_out)
        fee = self.fee
        return bo * (1 - (bi / (bi + amount * (1 - fee)))**(wi / wo))  # noqa: WPS221
