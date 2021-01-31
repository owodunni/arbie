"""Trader contains actions for executing trades."""

import logging

from web3.exceptions import ContractLogicError

from Arbie import TransactionError
from Arbie.Actions import Action
from Arbie.Variables import BigNumber

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
        router: router
        min_eth: 1
        min_weth: 2
        max_weth: 10
        account: account
    output:
        balance_eth: balance_eth
        balance_weth: balance_weth
    """

    async def on_next(self, data):
        balance_checker = BalanceChecker(data.web3(), data.weth())
        trader_account = data.account()
        amount_eth, amount_weth = await balance_checker.check_and_convert(
            trader_account.address,
            data.min_eth(),
            data.min_weth(),
            data.max_weth(),
        )
        router = data.router()
        if not router.approve(data.weth()):
            raise Exception("Failed to authorize arbie to spend tokens.")

        logger.info(
            f"Finished setting up trader, eth: {amount_eth}, weth: {amount_weth}"
        )

        data.balance_eth(amount_eth)
        data.balance_weth(amount_weth)


def _perform_trade(trade, router, min_profit):
    amount_out = router.check_out_given_in(trade)
    try:
        _, gas_cost = router.swap(trade, dry_run=True)
    except ContractLogicError as e:
        logger.warning(e)
        return False

    profit = amount_out - trade.amount_in - gas_cost

    logger.info(
        f"Checking trade with profit {profit}, amount_in: {trade.amount_in}, amount out: {amount_out}, gas cost: {gas_cost}"
    )
    if profit > min_profit:
        logger.info(f"Executing trade {trade}")
        return router.swap(trade)
    return False


def perform_trade(data, amount_weth):
    router = data.router()
    min_profit = data.min_profit()
    for trade in data.trades():
        # Make sure that we don't try to trade with more weth then we have
        trade.amount_in = min(trade.amount_in, amount_weth)
        if _perform_trade(trade, router, min_profit):
            return True
    return False


class Trader(Action):
    """Find optimal arbitrage opportunity for a list sorted trades.

    Remove all trades that are not profitable.

    [Settings]
    input:
        web3: web3
        router: router
        trades: filtered_trades
        min_profit: 0.3
        weth: weth
        account: account
    output:
        profit: profit
    """

    async def on_next(self, data):  # noqa: WPS210
        trader_account = data.account()
        balance_checker = BalanceChecker(data.web3(), data.weth())
        amount_eth, amount_weth = await balance_checker.check(trader_account.address)
        balance_pre = amount_weth + amount_eth
        logger.info(f"amount_eth: {amount_eth}, amount_weth: {amount_weth}")

        if not perform_trade(data, amount_weth):
            logger.warning("No trade opportunity found.")

        balance_post = await balance_checker.check_total(trader_account.address)

        data.profit(balance_post - balance_pre)
        logger.info("Finished trading")


class LogTrader(Action):
    """Log arbitrage opportunity for a list sorted trades.

    Remove all trades that are not profitable.

    [Settings]
    input:
        web3: web3
        router: router
        trades: filtered_trades
        min_profit: 0.3
        weth: weth
    output:
        profit_per_trade: profit_per_trade
        profit: profit
    """

    async def on_next(self, data):  # noqa: WPS210
        value = self._log_trades(data)
        profit = sum(value)
        profit_per_trade = profit / len(value)

        logger.info(f"Total profit: {profit}, profit per trade: {profit_per_trade}")

        data.profit_per_trade(profit_per_trade)
        data.profit(profit)

        logger.info("Finished trading")

    def _log_trades(self, data):
        router = data.router()
        min_profit = data.min_profit()
        profits = []
        for trade in data.trades():
            profit = self._log_trade(trade, router, min_profit)
            if profit:
                profits.append(profit)
        return profits

    def _log_trade(self, trade, router, min_profit):
        amount_out = router.check_out_given_in(trade)
        try:
            status, gas_cost = router.swap(trade, dry_run=True)
        except ContractLogicError:
            return None
        profit = amount_out - trade.amount_in - gas_cost
        if profit > min_profit:
            logger.info(
                f"Executing trade with profit {profit}, amount_in: {trade.amount_in}, amount out: {amount_out}"
            )
            return profit
