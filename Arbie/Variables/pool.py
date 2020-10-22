"""Test class for setting up AMMs."""
from typing import List, NewType, Tuple

from sympy import symbols

from Arbie.Variables.address import Address
from Arbie.Variables.token import Balance, Balances, Token, Tokens

x = symbols("x")


def get_value(values: Balances, token: Token) -> Balance:
    for v in values:
        if v.token == token:
            return v.value


class Pool(object):
    """Pool can create a arbitrary AMM that can be used for testing.

    The math can be found here https://balancer.finance/whitepaper/
    """

    def __init__(
        self,
        tokens: Tokens,
        balances: List[float],
        weights: List[float],
        fee: float = 0,
        **kwargs,
    ):  # noqa: WPS221

        self.tokens = tokens
        self.balances = Balance.create(tokens, balances)
        self.weights = Balance.create(tokens, weights)
        self.fee = fee

        if sum(weights) != 1:
            raise ValueError("Weights are not normalized")

        if self.fee > 1 or self.fee < 0:
            raise ValueError(f"Fee: {self.fee}, should be between 0 and 1")

        if "address" in kwargs:
            self.address = kwargs.get("address")
        else:
            self.address = Address()

    def __str__(self):
        return f"""
Pool(
  Tokens: {self.tokens},
  Balances: {self.balances},
  Weights: {self.weights},
  Fee: {self.fee}
  Address: {self.address.value})"""

    def __repr__(self):
        return self.__str__()

    def __hash__(self):
        return hash(self.address)

    def get_weights(self, token_in: Token, token_out: Token) -> Tuple[float, float]:
        return (get_value(self.weights, token_in), get_value(self.weights, token_out))

    def get_balances(self, token_in: Token, token_out: Token) -> Tuple[float, float]:
        return (get_value(self.balances, token_in), get_value(self.balances, token_out))

    def spot_price(self, token_in: Token, token_out: Token) -> float:
        """Ratio between token_in and token_out.

        A ratio > 1 means that token_in is less valuable then token_out
        A ratio < 1 means that token_in is more valuable then token_out

        token_in / ratio = token_out

        If the ratio is 400 then it takes 400 token_in for 1 token_out
        """
        bi, bo = self.get_balances(token_in, token_out)
        wi, wo = self.get_weights(token_in, token_out)
        return (bi / wi) / (bo / wo)

    def in_given_out_expr(self, token_in: Token, token_out: Token):
        bi, bo = self.get_balances(token_in, token_out)
        wi, wo = self.get_weights(token_in, token_out)

        return bi * ((bo / (bo - x * (1 - self.fee))) ** (wo / wi) - 1)  # noqa: WPS221'

    def out_given_in_expr(self, token_in: Token, token_out: Token) -> float:
        bi, bo = self.get_balances(token_in, token_out)
        wi, wo = self.get_weights(token_in, token_out)

        return bo * (1 - (bi / (bi + x * (1 - self.fee))) ** (wi / wo))  # noqa: WPS221

    def in_given_out(self, token_in: Token, token_out: Token, amount: float) -> float:
        expr = self.in_given_out_expr(token_in, token_out)
        return expr.subs(x, amount)

    def out_given_in(self, token_in: Token, token_out: Token, amount: float) -> float:
        expr = self.out_given_in_expr(token_in, token_out)
        return expr.subs(x, amount)


Pools = NewType("Pools", List[Pool])
