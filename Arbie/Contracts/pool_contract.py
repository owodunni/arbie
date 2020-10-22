"""Base abstract class for pool contracts."""

from typing import List

from Arbie.Contracts.contract import Contract
from Arbie.Contracts.tokens import GenericToken
from Arbie.Variables import BigNumber, Pool, Token


class PoolContract(Contract):
    def get_tokens(self) -> List[GenericToken]:
        raise NotImplementedError()

    def get_balances(self) -> List[BigNumber]:
        raise NotImplementedError()

    def get_weights(self) -> List[float]:
        raise NotImplementedError()

    def get_fee(self) -> float:
        raise NotImplementedError()

    def create_tokens(self) -> List[Token]:
        return list(map((lambda t: t.create_token()), self.get_tokens()))

    def create_pool(self) -> Pool:
        tokens = self.create_tokens()
        balances = list(map((lambda bg: bg.to_number()), self.get_balances()))
        return Pool(tokens, balances, self.get_weights(), self.get_fee())
