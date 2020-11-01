"""Utility functions for interacting with Uniswap."""

from typing import List

from Arbie import DeployContractError
from Arbie.Contracts.contract import Contract, ContractFactory
from Arbie.Contracts.pool_contract import PoolContract
from Arbie.Contracts.tokens import GenericToken
from Arbie.Variables import Address, BigNumber


class UniswapPair(PoolContract):
    name = "pair"
    protocol = "uniswap"
    abi = "pair"

    fee = 0.003
    weight = 0.5

    def mint(self, address: Address) -> bool:
        transaction = self.contract.functions.mint(address.value)
        return self._transact_status(transaction)

    def get_token0(self) -> GenericToken:
        return self._get_token(self.contract.functions.token0())

    def get_token1(self) -> GenericToken:
        return self._get_token(self.contract.functions.token1())

    def get_tokens(self) -> List[GenericToken]:
        return [self.get_token0(), self.get_token1()]

    def get_balances(self) -> List[BigNumber]:
        reserves = self.contract.functions.getReserves().call()

        bg_reservers = []
        for reserve, token in zip(reserves, self.get_tokens()):
            exp = token.decimals()
            bg_reservers.append(BigNumber.from_value(reserve, exp))

        return bg_reservers

    def get_fee(self) -> float:
        return self.fee

    def get_weights(self) -> List[float]:
        return [self.weight, self.weight]

    def _get_token(self, function) -> GenericToken:
        cf = ContractFactory(self.w3, GenericToken)
        token_address = function.call()
        return cf.load_contract(self.owner_address, address=Address(token_address))


class UniswapFactory(Contract):
    name = "factory_v2"
    protocol = "uniswap"
    abi = "factory_v2"

    def all_pairs_length(self) -> int:
        return self.contract.functions.allPairsLength().call()

    def get_pair_address(self, index) -> Address:
        return Address(self.contract.functions.allPairs(index).call())

    def all_pairs(self, sleep=0) -> List[UniswapPair]:
        pairs = []
        for i in range(0, self.all_pairs_length()):
            pairs.append(self._create_pair_index(i))
        return pairs

    def create_pair(self, token_a: GenericToken, token_b: GenericToken) -> UniswapPair:
        transaction = self.contract.functions.createPair(
            token_a.get_address().value, token_b.get_address().value
        )

        if not self._transact_status(transaction):
            raise DeployContractError("Failed to deploy UniswapPair")

        return self._create_pair_index(self.all_pairs_length() - 1)

    def setup_pair(
        self, tokens: List[GenericToken], amounts: List[BigNumber]
    ) -> UniswapPair:
        pair = self.create_pair(tokens[0], tokens[1])

        for token, amount in zip(tokens, amounts):
            token.transfer(pair.get_address(), amount)

        pair.mint(self.owner_address)
        return pair

    def _create_pair_index(self, index) -> UniswapPair:
        cf = ContractFactory(self.w3, UniswapPair)
        return cf.load_contract(
            self.owner_address, address=self.get_pair_address(index)
        )
