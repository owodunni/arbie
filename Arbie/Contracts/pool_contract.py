"""Base abstract class for pool contracts."""

from typing import List

from Arbie import PoolValueError
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
        if len(tokens) < 2:
            raise PoolValueError(
                f"Pool: {self.get_address}, has insufficient tokens: {len(tokens)}"
            )
        balances = list(map((lambda bg: bg.to_number()), self.get_balances()))
        weights = self.get_weights()
        if sum(weights) != 1:
            raise PoolValueError(
                f"Pool: {self.get_address}, weights {sum(weights)} != 1"
            )
        return Pool(
            tokens,
            balances,
            weights,
            self.get_fee(),
            address=self.get_address(),
        )
