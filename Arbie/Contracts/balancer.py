"""Utility functions for interacting with balancer."""

import logging
from typing import List

from Arbie import DeployContractError, IERC20TokenError
from Arbie.Contracts.circuit_breaker import CircuitBreaker
from Arbie.Contracts.contract import Contract, ContractFactory
from Arbie.Contracts.pool_contract import PoolContract
from Arbie.Contracts.tokens import GenericToken
from Arbie.Variables import BigNumber

logger = logging.getLogger()


class BalancerPool(PoolContract):
    name = "pool"
    protocol = "balancer"
    abi = "bpool"

    def get_number_of_tokens(self):
        return self.contract.functions.getNumTokens().call()

    def get_tokens(self) -> List[GenericToken]:
        token_addresses = self.contract.functions.getCurrentTokens().call()
        cf = ContractFactory(self.w3, GenericToken)
        return list(
            map(
                (
                    lambda a: cf.load_contract(
                        owner_address=self.owner_address, address=a
                    )
                ),
                token_addresses,
            )
        )

    def get_balances(self) -> List[BigNumber]:
        tokens = self.get_tokens()
        balances = []
        for token in tokens:
            b = self.contract.functions.getBalance(token.get_address()).call()
            try:
                balances.append(BigNumber.from_value(b, token.decimals()))
            except Exception:
                raise IERC20TokenError("Bad token in balancer pool")
        return balances

    def get_weights(self) -> List[float]:
        weights = list(
            map(
                (
                    lambda t: self.contract.functions.getNormalizedWeight(
                        t.get_address()
                    ).call()
                ),
                self.get_tokens(),
            )
        )
        sum_of_weights = sum(weights)
        return list(map((lambda x: x / sum_of_weights), weights))

    def get_fee(self) -> float:
        return BigNumber.from_value(
            self.contract.functions.getSwapFee().call()
        ).to_number()

    def bind(self, address: str, balance: BigNumber, denorm_weight: int) -> bool:
        if denorm_weight < 1:
            raise ValueError("Weight should be larger than 1")
        eth_safe_weight = BigNumber(denorm_weight)
        transaction = self.contract.functions.bind(
            address, balance.value, eth_safe_weight.value
        )
        return self._transact_status(transaction)

    def finalize(self) -> bool:
        return self._transact_status(self.contract.functions.finalize())


class BalancerFactory(Contract):
    name = "pool_factory"
    protocol = "balancer"
    abi = "pool_factory"

    def setup_pool(
        self,
        tokens: List[GenericToken],
        weights: List[float],
        amounts: List[BigNumber],
        approve_owner=True,
    ) -> BalancerPool:
        pool = self.new_pool()

        for token, weight, amount in zip(tokens, weights, amounts):
            if approve_owner:
                token.approve_owner()
            token.approve(pool.get_address(), amount)
            pool.bind(token.get_address(), amount, weight)

        pool.finalize()
        return pool

    def new_pool(self) -> BalancerPool:
        transaction = self.contract.functions.newBPool()
        status, address = self._transact_status_and_contract(transaction)

        if not status:
            raise DeployContractError("Failed to deploy BalancerPool.")

        return ContractFactory(self.w3, BalancerPool).load_contract(
            self.owner_address, address=address
        )

    def all_pools(self, start=0, steps=100) -> List[BalancerPool]:
        last_block = self.w3.eth.blockNumber
        events = []
        for from_block in range(start, last_block, steps):
            to_block = from_block + steps - 1
            if to_block > last_block:
                to_block = last_block
            logger.info(
                f"Searching for Pools in block range [{from_block}:{to_block}], total pools found: {len(events)}"
            )
            events.extend(self._get_pool_events(from_block, to_block))
        return self._create_pools(events)

    def _create_pools(self, new_pool_event):
        pools = []
        factory = ContractFactory(self.w3, BalancerPool)

        for event in new_pool_event:
            pool = factory.load_contract(self.owner_address, address=event.args.pool)
            pools.append(pool)
        return pools

    def _get_pool_events(self, from_block, to_block):
        func = self.contract.events.LOG_NEW_POOL.createFilter(
            fromBlock=int(from_block), toBlock=int(to_block)
        ).get_all_entries
        breaker = CircuitBreaker(3, 10, func)
        return breaker.safe_call()
