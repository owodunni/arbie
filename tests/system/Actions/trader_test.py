"""System tests for PoolUpdater."""

import pytest

from Arbie.Actions import ActionTree, SetUpTrader, Store, Trader
from Arbie.Actions.arbitrage import ArbitrageFinder
from Arbie.Contracts import GenericToken, UniswapV2Router, Weth
from Arbie.Variables import BigNumber


def send_eth(web3, from_address, to_address, value):
    tx_hash = web3.eth.sendTransaction(
        {"to": to_address, "from": from_address, "value": BigNumber(value).value}
    )
    return web3.eth.waitForTransactionReceipt(tx_hash, 180)


min_profit = "min_profit"
dry_run = "dry_run"


@pytest.fixture
def conf_dict():
    return {"input": {min_profit: min_profit}, "output": {}}


@pytest.fixture
def trade_conf(conf_dict):
    conf_dict["input"][dry_run] = False
    return conf_dict


@pytest.fixture
def trader_account(w3, weth: GenericToken, router, dummy_account):
    router.set_account(dummy_account)
    weth.transfer(dummy_account.address, BigNumber(2))
    weth.set_account(dummy_account)
    weth.approve(router.get_address(), BigNumber(2))
    return dummy_account


@pytest.fixture
def trade_store(w3_with_gas_strategy, router, bad_trade, trade, weth, trader_account):
    store = Store()
    store.add("router", router)
    store.add("filtered_trades", [bad_trade, trade])
    store.add("weth", weth)
    store.add("web3", w3_with_gas_strategy)
    store.add("account", trader_account)
    return store


class TestTrader(object):
    @pytest.mark.asyncio
    async def test_on_next(
        self, trade_store, trade, router: UniswapV2Router, trade_conf
    ):
        trade = ArbitrageFinder(trade).find_arbitrage_and_update_trade()
        _, gas_cost = router.swap(trade, dry_run=True)

        # min profit is set to -1 because we want to execute a bad trade
        # and see that it is reverted without costing us gas
        trade_store.add(min_profit, -1)
        tree = ActionTree(trade_store)
        tree.add_action(Trader(trade_conf))
        await tree.run()
        assert trade_store.get("profit") == pytest.approx(
            trade.profit - gas_cost, rel=1e-4
        )

    @pytest.mark.asyncio
    async def test_no_profit(self, trade_store, trade_conf):
        trade_store.add(min_profit, 4)
        tree = ActionTree(trade_store)
        tree.add_action(Trader(trade_conf))
        await tree.run()
        assert trade_store.get("profit") == 0

    @pytest.mark.asyncio
    async def test_dry_run(self, trade_store, trade, router, conf_dict):
        trade = ArbitrageFinder(trade).find_arbitrage_and_update_trade()

        trade_store.add(min_profit, -1)
        tree = ActionTree(trade_store)
        tree.add_action(Trader(conf_dict))
        await tree.run()
        assert trade_store.get("profit") == 0


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
    async def test_setup_trader(self, trade_store, real_weth: Weth):
        tree = ActionTree(trade_store)
        tree.add_action(SetUpTrader())
        await tree.run()
        assert trade_store.get("balance_weth") == 10
        real_weth.withdraw(10)
