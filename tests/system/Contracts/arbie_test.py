"""Test arbie smart contracts."""

import pytest

from Arbie.Actions.arbitrage import ArbitrageFinder
from Arbie.async_helpers import async_map
from Arbie.Contracts import Arbie, ContractFactory
from Arbie.Variables import BigNumber, Trade


async def create_pool(pool):
    return await pool.create_pool()


async def create_token(token):
    return await token.create_token()


large = 10e8


class TestArbie(object):
    @pytest.fixture
    def arbie(self, w3, deploy_address, uniswap_router):
        return ContractFactory(w3, Arbie).deploy_contract(
            deploy_address, uniswap_router.get_address()
        )

    @pytest.fixture
    async def pairs(self, factory, weth, dai, wbtc):
        p0 = await factory.setup_pair(
            [weth, dai],
            [
                BigNumber(large / 300.0),
                BigNumber(large),
            ],
        )

        p1 = await factory.setup_pair(
            [wbtc, dai],
            [
                BigNumber(large / 10000.0),
                BigNumber(large),
            ],
        )

        p2 = await factory.setup_pair(
            [wbtc, weth],
            [
                BigNumber(large / 10000.0),
                BigNumber(large / 285.0),
            ],
        )
        return await async_map(create_pool, [p0, p1, p2])

    @pytest.fixture
    async def path(self, weth, dai, wbtc):
        raw_path = [weth, dai, wbtc, weth]
        return await async_map(create_token, raw_path)

    @pytest.fixture
    def trade(self, pairs, path):
        return Trade(pairs, path)

    @pytest.mark.asyncio
    def test_out_given_in(self, arbie: Arbie, trade):
        amount_in = BigNumber(1)
        amount_out = arbie.check_out_given_in(amount_in, trade)
        assert amount_out > amount_in.to_number()

        profit = ArbitrageFinder(trade).calculate_profit(1)
        assert pytest.approx(1, 1e-5) == amount_out - profit
