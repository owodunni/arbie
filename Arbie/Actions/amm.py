"""Test class for setting up AMMs."""
from typing import List, NewType, Tuple

from sympy import symbols

x = symbols('x')


class Token(object):
    """Token can be used to identify a ERC20 token."""

    def __init__(self, name: str, address=None):
        self.name = name
        self.address = address

    def __eq__(self, other):
        return self.address == other.address and self.name == other.name


class Variable(object):
    """Variable bound to Token in pool."""

    def __init__(self, token: Token, value: float):
        self.token = token
        self.value = value

    @classmethod
    def create(cls, tokens: List[Token], values: List[float]) -> List[object]:
        if len(tokens) != len(values):
            raise ValueError('All inputs must be of same length.')

        variables = []
        for token, value in zip(tokens, values):
            variables.append(cls(token, value))
        return variables


Variables = NewType('Variables', List[Variable])


def get_value(values: Variables, token: Token) -> Variable:
    for v in values:
        if v.token == token:
            return v.value


class Amm(object):
    """Amm can create a arbitrary AMM that can be used for testing.

    The math can be found here https://balancer.finance/whitepaper/
    """

    def __init__(self, tokens: List[Token], balances: List[float], weights: List[float], fee: float = 0):  # noqa: WPS221

        self.tokens = tokens
        self.balances = Variable.create(tokens, balances)
        self.weights = Variable.create(tokens, weights)
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

    def in_given_out_expr(self, token_in: Token, token_out: Token):
        bi, bo = self.get_balances(token_in, token_out)
        wi, wo = self.get_weights(token_in, token_out)

        return bi * ((bo / (bo - x * (1 - self.fee)))**(wo / wi) - 1)  # noqa: WPS221'

    def out_given_in_expr(self, token_in: Token, token_out: Token) -> float:
        bi, bo = self.get_balances(token_in, token_out)
        wi, wo = self.get_weights(token_in, token_out)

        return bo * (1 - (bi / (bi + x * (1 - self.fee)))**(wi / wo))  # noqa: WPS221

    def in_given_out(self, token_in: Token, token_out: Token, amount: float) -> float:
        expr = self.in_given_out_expr(token_in, token_out)
        return expr.subs(x, amount)

    def out_given_in(self, token_in: Token, token_out: Token, amount: float) -> float:
        expr = self.out_given_in_expr(token_in, token_out)
        return expr.subs(x, amount)
