"""Trader contains actions for executing trades."""

import logging

from Arbie import TransactionError
from Arbie.Actions import Action
from Arbie.Variables import BigNumber, PoolType

logger = logging.getLogger()


class BalanceChecker(object):
    def __init__(self, web3, weth):
        self.web3 = web3
        self.weth = weth

    async def check(self, address):
        amount_weth = await self.weth.balance_of(address)
        amount_eth = BigNumber.from_value(self.web3.eth.getBalance(address))
        return amount_eth.to_number(), amount_weth.to_number()

    async def check_total(self, address):
        return sum(await self.check(address))

    async def check_and_convert(self, trader_address, min_eth, min_weth, max_weth):
        amount_eth, amount_weth = await self.check(trader_address)

        # Already have sufficient amount setup
        if amount_eth > min_eth and amount_weth > min_weth:
            return amount_eth, amount_weth

        # We don't have sufficient supply
        if amount_eth + amount_weth < min_eth + min_weth:
            raise ValueError(
                f"Not enough liquidity eth: {amount_eth}, min_eth: {min_eth}, weth {amount_weth}, min_weth: {min_weth}"
            )

        # ETH is good but not weth
        if amount_eth > min_eth + min_weth:
            self._to_weth(amount_eth, min_eth, max_weth)
        else:
            self._to_eth(amount_eth, amount_weth, min_eth, min_weth)

        return await self.check(trader_address)

    def _to_weth(self, amount_eth, min_eth, max_weth):
        max_deposit = amount_eth - min_eth
        max_deposit = min(max_deposit, max_weth)
        status = self.weth.deposit(max_deposit)
        if not status:
            raise TransactionError("Failed to deposit eth for weth")

    def _to_eth(self, amount_eth, amount_weth, min_eth, min_weth):
        max_withdraw = amount_weth - min_weth
        max_withdraw = min(max_withdraw, min_eth - amount_eth)
        status = self.weth.withdraw(max_withdraw)
        if not status:
            raise TransactionError("Failed to withdraw weth for eth")


class SetUpTrader(Action):
    """SetUp Trader account for trading.

    [Settings]
    input:
        web3: web3
        weth: weth
        min_eth: 1
        min_weth: 2
        max_weth: 10
        trader_account: trader_account
    output:
        balance_eth: balance_eth
        balance_weth: balance_weth
    """

    async def on_next(self, data):
        balance_checker = BalanceChecker(data.web3(), data.weth())
        trader_account = data.trader_account()
        amount_eth, amount_weth = await balance_checker.check_and_convert(
            trader_account.address,
            data.min_eth(),
            data.min_weth(),
            data.max_weth(),
        )
        data.balance_eth(amount_eth)
        data.balance_weth(amount_weth)


def _is_trade_uni(trade):
    for pool in trade.pools:
        if pool.pool_type is not PoolType.uniswap:
            return False
    return True


def _perform_trade(trade, arbie, min_profit):
    if not _is_trade_uni(trade):
        return False

    amount_out = arbie.check_out_given_in(trade)
    gas_cost = arbie.estimate_swap_const(trade)
    if amount_out - trade.amount_in - gas_cost > min_profit:
        logger.info(f"Executing trade with return: {amount_out}, trade: {trade}")
        return arbie.swap(trade)
    return False


def perform_trade(data):
    arbie = data.arbie()
    min_profit = data.min_profit()
    for trade in data.trades():
        if _perform_trade(trade, arbie, min_profit):
            return True
    return False


class Trader(Action):
    """Find optimal arbitrage opportunity for a list sorted trades.

    Remove all trades that are not profitable.

    [Settings]
    input:
        web3: web3
        arbie: arbie
        trades: filtered_trades
        min_profit: 0.3
        weth: weth
        trader_account: trader_account
    output:
        profit: profit
    """

    async def on_next(self, data):
        trader_account = data.trader_account()
        balance_checker = BalanceChecker(data.web3(), data.weth())
        balance_pre = await balance_checker.check_total(trader_account.address)

        if not perform_trade(data):
            raise Exception("No trade performed")

        balance_post = await balance_checker.check_total(trader_account.address)

        data.profit(balance_post - balance_pre)
        logger.info("Finished trading")
