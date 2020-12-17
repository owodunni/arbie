"""Pool finder is responsible for finding all pools."""
import logging
from math import isclose
from typing import List, Tuple

from prometheus_async.aio import time

from Arbie import IERC20TokenError, PoolValueError
from Arbie.Actions.action import Action
from Arbie.async_helpers import async_map
from Arbie.Contracts import UniswapFactory, UniswapPair
from Arbie.Contracts.pool_contract import PoolContract
from Arbie.prometheus import get_prometheus
from Arbie.settings_parser import create_web3_provider
from Arbie.Variables import Pools, Token, Tokens

logger = logging.getLogger()

CREATE_TOKEN_TIME = get_prometheus().summary(
    "pool_finder_create_and_check_token", "Time for creating and checking a token"
)


def check_and_get_price(balances) -> Tuple[bool, float]:
    for balance in balances:
        if isclose(balance.value, 0, abs_tol=1e-3):  # noqa: WPS432
            return True, 0
    return False, balances[0] / balances[1]


class TokenFinder(object):
    def __init__(self, weth, web3, test_provider):
        self.weth = weth
        self.web3 = web3
        self.test_provider = test_provider
        self.original_provider = web3.provider

    async def create_token_if_weth_pair(self, pair: UniswapPair, price):
        tokens = await pair.get_tokens()
        t0 = tokens[0]
        t1 = tokens[1]
        if self.weth.address == t0.get_address():
            return await t1.create_token(price)
        if self.weth.address == t1.get_address():
            return await t0.create_token(1 / price)

    @time(CREATE_TOKEN_TIME)
    async def create_and_check_token(self, pair):
        balances = None
        try:
            balances = await pair.get_balances()
        except IERC20TokenError:
            return None

        is_zero, price = check_and_get_price(balances)
        if is_zero:
            return None

        token = await self.create_token_if_weth_pair(pair, price)
        if not token:
            return None

        if self._check_if_malicious(token, pair):
            return None

        logger.info(f"Finished creating token from {pair.get_address()}")
        return token

    async def create_tokens(self, uniswap_pairs: List[UniswapPair]) -> List[Token]:
        tokens = await async_map(self.create_and_check_token, uniswap_pairs)
        tokens.append(self.weth)
        token_set = set(tokens)
        token_set.discard(None)
        return list(token_set)

    async def _check_if_malicious(self, token, pair):
        """Check if a token is malicious.

        Certain tokens can be paused, that means that any trade
        through those tokens will fail. Not removing theses tokens
        early will give us bad data down the line.

        Certain tokens might steal funds. That means that any trade with them
        can not be accurate if we do not know exactly how they steal funds.
        Therefore we remove those as well.

        There might be other ways for tokens to be maliciouse, time will tell.
        """
        self.web3.provider = self.test_provider
        try:  # noqa: WPS328
            pass  # noqa: WPS420
        except IERC20TokenError:
            logger.warning("Found malicious token: {token}")
            return False
        self.web3.provider = self.original_provider
        return True


async def create_and_filter_pools(
    pool_contracts: List[PoolContract], tokens: List[Tokens]
) -> Pools:
    pools = []
    for contract in pool_contracts:
        logger.info(
            f"Filtering contract {pool_contracts.index(contract)} of {len(pool_contracts)}"
        )
        try:
            pool = await contract.create_pool()
        except IERC20TokenError as e:
            logger.warning(f"Failed to create pool, bad token. {e}")
            continue
        except PoolValueError as e:
            logger.warning(f"Failed to create pool, bad pool. {e}")
            continue
        for token in pool.tokens:
            try:
                index = tokens.index(token)
            # Token not found in pool
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
        web3: web3
        weth: weth
        uniswap_factory: uniswap_factory
        fork_address: fork_address
    output:
        pools: all_pools
        tokens: all_tokens
    """

    async def on_next(self, data):
        weth = await data.weth().create_token(1)

        tf = TokenFinder(weth, data.web3(), create_web3_provider(data.fork_address))
        tokens, pools = await self._get_pairs_and_tokens(
            data.uniswap_factory(), weth, tf
        )

        await self._get_pools_and_tokens(pools, tokens)

        data.pools(pools)
        data.tokens(tokens)

    async def _get_pools_and_tokens(self, pair_contracts, tokens):
        pools = (await create_and_filter_pools(pair_contracts, tokens),)
        return tokens, pools

    async def _get_pairs_and_tokens(self, factory: UniswapFactory, token_finder):
        pairs = await factory.all_pairs()
        logging.getLogger().info("Found all uniswap pairs, filtering tokens.")
        tokens, weth_pairs = await token_finder.create_tokens(pairs)
        return tokens, pairs
