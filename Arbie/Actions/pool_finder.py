"""Pool finder is responsible for finding all pools."""
from typing import List

from Arbie.Actions.action import Action
from Arbie.Contracts import UniswapPair
from Arbie.Contracts.pool_contract import PoolContract
from Arbie.Variables import Token, Tokens, Pools


def create_tokens_and_pairs(uniswap_pairs: List[UniswapPair], uoa: Token) -> List[Token]:
    token_set = set()
    token_set.add(uoa)
    for pair in uniswap_pairs:
        tokens = pair.get_tokens()
        balances = pair.get_balances()
        if uoa.address == tokens[0].get_address():
            token_set.add(
                tokens[1].create_token(balances[0]/balances[1]))
        elif uoa.address == tokens[1].get_address():
            token_set.add(
                tokens[0].create_token(balances[1] / balances[0]))

    return list(token_set)


def create_and_filter_pools(pool_contracts: List[PoolContract], tokens: List[Tokens]) -> Pools:
    pools = []
    for contract in pool_contracts:
        pool = contract.create_pool()
        for token in pool.tokens:
            try:
                index = tokens.index(token)
            except ValueError:
                continue
            if token in tokens:
                token.price = tokens[index].price
        pools.append(pool)
    return pools



class PoolFinder(Action):
    """PoolFinder is responsible for finding pools.

    [Settings]
    input:
        weth: weth
        uniswap_factory: uniswap_factory
        balancer_factory: balancer_factory
    output:
        pools: all_pools
        tokens: all_tokens
    """

    def on_next(self, data):
        uniswap_factory = data.uniswap_factory()
        balancer_factory = data.balancer_factory()
        weth = data.weth()

        uniswap_pairs = uniswap_factory.all_pairs()
        balancer_pools = balancer_factory.all_pools()
        tokens = create_tokens_and_pairs(uniswap_pairs, weth)

        pools = create_and_filter_pools(uniswap_pairs, tokens) + create_and_filter_pools(balancer_pools, tokens)

        data.pools(pools)
        data.tokens(tokens)
