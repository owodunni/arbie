"""System tests for PoolUpdater."""

import pytest

from Arbie.Actions import ActionTree, LogTrader, SetUpTrader, Store, Trader
from Arbie.Contracts import GenericToken, Weth
from Arbie.Variables import BigNumber


def send_eth(web3, from_address, to_address, value):
    tx_hash = web3.eth.sendTransaction(
        {"to": to_address, "from": from_address, "value": BigNumber(value).value}
    )
    return web3.eth.waitForTransactionReceipt(tx_hash, 180)  # noqa: WPS432


@pytest.fixture
def trader_account(w3, weth: GenericToken, router, dummy_account):
    router.set_account(dummy_account)
    weth.transfer(dummy_account.address, BigNumber(2))
    weth.set_account(dummy_account)
    weth.approve(router.get_address(), BigNumber(2))
    return dummy_account


min_profit = "min_profit"

conf_dict = {"input": {min_profit: min_profit}, "output": {}}


@pytest.fixture
def trade_store(w3, router, trade, weth, trader_account):
    store = Store()
    store.add("router", router)
    store.add("filtered_trades", [trade])
    store.add("weth", weth)
    store.add("web3", w3)
    store.add("account", trader_account)
    return store


class TestTrader(object):
    @pytest.mark.asyncio
    async def test_on_next(self, trade_store, trade):
        trade.amount_in = 1
        trade_store.add(min_profit, 0)
        tree = ActionTree(trade_store)
        tree.add_action(Trader(conf_dict))
        await tree.run()
        assert trade_store.get("profit") > 0.036  # noqa: WPS432

    @pytest.mark.asyncio
    async def test_no_profit(self, trade_store, trade):
        trade.amount_in = 1
        tree = ActionTree(trade_store)
        tree.add_action(Trader())
        with pytest.raises(Exception):
            await tree.run()


class TestLogTrader(object):
    @pytest.mark.asyncio
    async def test_on_next(self, trade_store, trade):
        trade.amount_in = 1
        trade_store.add(min_profit, 0)
        tree = ActionTree(trade_store)
        tree.add_action(LogTrader(conf_dict))
        await tree.run()
        assert trade_store.get("profit") > 0.036  # noqa: WPS432


class TestSetUpTrader(object):
    @pytest.fixture
    def trade_store(self, w3, router, real_weth, dummy_account):
        real_weth.set_account(dummy_account)
        store = Store()
        store.add("weth", real_weth)
        store.add("web3", w3)
        store.add("account", dummy_account)
        store.add("router", router)
        return store

    @pytest.mark.asyncio
    async def test_setup_trader(self, trade_store, dummy_account, real_weth: Weth):
        tree = ActionTree(trade_store)
        tree.add_action(SetUpTrader())
        await tree.run()
        assert trade_store.get("balance_weth") == 10
        real_weth.withdraw(10)
