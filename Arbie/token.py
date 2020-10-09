"""Basic token representation."""
from typing import List, NewType


class Token(object):
    """Token is a light weight representation of a ERC20 token."""

    def __init__(self, name: str, address=None):
        self.name = name
        self.address = address

    def __str__(self):
        return f'Token(Name: {self.name}, Address: {self.address})'

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.__hash__() == other.__hash__()

    def __hash__(self):
        if self.address is not None:
            return hash(self.address)
        return hash(self.name)


class Balance(object):
    """Balance of token."""

    def __init__(self, token: Token, value: float):
        self.token = token
        self.value = value

    def __str__(self):
        return f'Balance(Token: {self.token}, Value: {self.value})'

    def __repr__(self):
        return self.__str__()

    @classmethod
    def create(cls, tokens: List[Token], values: List[float]) -> List[object]:
        if len(tokens) != len(values):
            raise ValueError('All inputs must be of same length.')

        balances = []
        for token, value in zip(tokens, values):
            balances.append(cls(token, value))
        return balances


Balances = NewType('Balances', List[Balance])
Tokens = NewType('Tokens', List[Token])
