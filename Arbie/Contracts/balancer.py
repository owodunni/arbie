"""Utility functions for interacting with balancer."""

from typing import List

from Arbie import DeployContractError
from Arbie.Contracts.contract import Contract, ContractFactory
from Arbie.Contracts.pool_contract import PoolContract
from Arbie.Contracts.tokens import GenericToken
from Arbie.Variables import Address, BigNumber


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
                        owner_address=self.owner_address, address=Address(a)
                    )
                ),
                token_addresses,
            )
        )

    def get_balances(self) -> List[BigNumber]:
        tokens = self.get_tokens()
        balances = []
        for token in tokens:
            b = self.contract.functions.getBalance(token.get_address().value).call()
            balances.append(BigNumber.from_value(b, token.decimals()))
        return balances

    def get_weights(self) -> List[float]:
        weights = list(
            map(
                (
                    lambda t: self.contract.functions.getNormalizedWeight(
                        t.get_address().value
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

    def bind(self, address: Address, balance: BigNumber, denorm_weight: int) -> bool:
        if denorm_weight < 1:
            raise ValueError("Weight should be larger than 1")
        eth_safe_weight = BigNumber(denorm_weight)
        transaction = self.contract.functions.bind(
            address.value, balance.value, eth_safe_weight.value
        )
        return self._transact_status(transaction)

    def finalize(self) -> bool:
        return self._transact_status(self.contract.functions.finalize())


class BalancerFactory(Contract):
    name = "pool_factory"
    protocol = "balancer"
    abi = "pool_factory"

    def setup_pool(
        self, tokens: List[GenericToken], weights: List[float], amounts: List[BigNumber]
    ) -> BalancerPool:
        pool = self.new_pool()

        for token, weight, amount in zip(tokens, weights, amounts):
            token.approve_owner()
            token.approve(pool.get_address(), amount)
            pool.bind(token.get_address(), amount, weight)

        pool.finalize()
        return pool

    def new_pool(self) -> bool:
        transaction = self.contract.functions.newBPool()
        status, address = self._transact_status_and_contract(transaction)

        if not status:
            raise DeployContractError("Failed to deploy BalancerPool.")

        return ContractFactory(self.w3, BalancerPool).load_contract(
            self.owner_address, address=address
        )

    def all_pools(self) -> List[BalancerPool]:
        event_filter = self.contract.events.LOG_NEW_POOL.createFilter(fromBlock=0)
        return self._create_pools(event_filter.get_all_entries())

    def _create_pools(self, new_pool_event):
        pools = []
        factory = ContractFactory(self.w3, BalancerPool)

        for event in new_pool_event:
            pool = factory.load_contract(
                self.owner_address, address=Address(event.args.pool)
            )
            pools.append(pool)
        return pools
