"""System tests for PoolUpdater."""

import pytest

from Arbie.Actions import ActionTree, Store, Trader
from Arbie.Contracts import GenericToken
from Arbie.Variables import BigNumber


class TestTrader(object):
    @pytest.fixture
    def trader_address(self, w3, weth: GenericToken, arbie, dummy_address):
        weth.transfer(dummy_address, BigNumber(2))
        weth.approve(arbie.get_address(), BigNumber(2), dummy_address)
        return dummy_address

    @pytest.fixture
    def trade_store(self, w3, arbie, trade, weth, trader_address):
        store = Store()
        store.add("arbie", arbie)
        store.add("filtered_trades", [trade])
        store.add("weth", weth)
        store.add("web3", w3)
        store.add("trader_address", trader_address)
        return store

    @pytest.mark.asyncio
    async def test_on_next(self, trade_store, trade):
        trade.amount_in = 1
        trade_store.add("min_profit", 0)
        tree = ActionTree(trade_store)
        tree.add_action(Trader({"input": {"min_profit": "min_profit"}, "output": {}}))
        await tree.run()
        assert trade_store.get("profit") > 0.036  # noqa: WPS432

    @pytest.mark.asyncio
    async def test_no_profit(self, trade_store, trade):
        trade.amount_in = 1
        tree = ActionTree(trade_store)
        tree.add_action(Trader())
        with pytest.raises(Exception):
            await tree.run()
