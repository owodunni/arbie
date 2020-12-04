"""Test arbie smart contracts."""

import pytest

from Arbie.Actions.arbitrage import ArbitrageFinder
from Arbie.Contracts import Arbie, GenericToken
from Arbie.Variables import BigNumber


class TestArbie(object):
    @pytest.mark.asyncio
    def test_out_given_in(self, arbie: Arbie, trade):
        trade.amount_in = 1
        amount_out = arbie.check_out_given_in(trade)
        assert amount_out > 1

        profit = ArbitrageFinder(trade).calculate_profit(1)
        assert pytest.approx(1, 1e-5) == amount_out - profit

    @pytest.mark.asyncio
    async def test_swap(self, trade, arbie, weth: GenericToken, deploy_address):
        trade.amount_in = 1
        balance_before = await weth.balance_of(deploy_address)

        assert balance_before > 1

        weth.approve(arbie.get_address(), BigNumber(2))

        assert arbie.swap(trade)

        assert await weth.balance_of(deploy_address) > balance_before
