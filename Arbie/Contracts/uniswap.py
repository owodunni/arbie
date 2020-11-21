"""Utility functions for interacting with Uniswap."""
import logging
from typing import List, Tuple

from Arbie import DeployContractError, IERC20TokenError
from Arbie.async_helpers import async_map
from Arbie.Contracts.contract import Contract, ContractFactory
from Arbie.Contracts.pool_contract import PoolContract
from Arbie.Contracts.tokens import GenericToken
from Arbie.Variables import BigNumber

logger = logging.getLogger()


async def create_reserve(result: Tuple[float, GenericToken]):
    (value, token) = result
    try:
        exp = await token.decimals()
    except Exception:
        raise IERC20TokenError("Token doesn't contain decimals.")
    return BigNumber.from_value(value, exp)


class UniswapPair(PoolContract):
    name = "pair"
    protocol = "uniswap"
    abi = "pair"

    fee = 0.003
    weight = 0.5

    def mint(self, address: str) -> bool:
        transaction = self.contract.functions.mint(address)
        return self._transact_status(transaction)

    def get_token0(self) -> GenericToken:
        return self._get_token(self.contract.functions.token0())

    def get_token1(self) -> GenericToken:
        return self._get_token(self.contract.functions.token1())

    def get_tokens(self) -> List[GenericToken]:
        return [self.get_token0(), self.get_token1()]

    async def get_balances(self) -> List[BigNumber]:
        tokens = self.get_tokens()
        reserves = await self._get_reserves()
        return await async_map(create_reserve, zip(reserves, tokens))

    def get_fee(self) -> float:
        return self.fee

    def get_weights(self) -> List[float]:
        return [self.weight, self.weight]

    def _get_token(self, function) -> GenericToken:
        cf = ContractFactory(self.w3, GenericToken)
        token_address = function.call()
        return cf.load_contract(self.owner_address, address=token_address)

    async def _get_reserves(self):
        return await self._call_async(self.contract.functions.getReserves())


class UniswapFactory(Contract):
    name = "factory_v2"
    protocol = "uniswap"
    abi = "factory_v2"

    print_divider = 20  # noqa: WPS432

    def __init__(self, w3, owner_address: str, contract):
        self.cf = ContractFactory(w3, UniswapPair)
        super(UniswapFactory, self).__init__(w3, owner_address, contract)

    async def all_pairs_length(self) -> int:
        return await self._call_async(self.contract.functions.allPairsLength())

    async def get_pair_address(self, index) -> str:
        return await self._call_async(self.contract.functions.allPairs(index))

    async def all_pairs(self, sleep=0) -> List[UniswapPair]:
        number_of_pairs = await self.all_pairs_length()
        return await async_map(self._create_pair_index, range(number_of_pairs))

    async def create_pair(
        self, token_a: GenericToken, token_b: GenericToken
    ) -> UniswapPair:
        transaction = self.contract.functions.createPair(
            token_a.get_address(), token_b.get_address()
        )

        if not self._transact_status(transaction):
            raise DeployContractError("Failed to deploy UniswapPair")
        pair_nmb = await self.all_pairs_length()
        return await self._create_pair_index(pair_nmb - 1)

    async def setup_pair(
        self, tokens: List[GenericToken], amounts: List[BigNumber]
    ) -> UniswapPair:
        pair = await self.create_pair(tokens[0], tokens[1])

        for token, amount in zip(tokens, amounts):
            token.transfer(pair.get_address(), amount)
        try:
            pair.mint(self.owner_address)
        except Exception:
            raise ValueError(f"Failed to mint tokens {tokens[0]},{tokens[1]}")
        return pair

    async def _create_pair_index(self, index) -> UniswapPair:
        address = await self.get_pair_address(index)
        if index % UniswapFactory.print_divider == 0:
            logger.info(f"Creating pair number {index}")
        return self.cf.load_contract(self.owner_address, address=address)
