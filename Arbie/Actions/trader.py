"""Trader contains actions for executing trades."""

import logging

from Arbie.Actions import Action
from Arbie.Contracts import GenericToken
from Arbie.Variables import BigNumber, PoolType

logger = logging.getLogger()


def _is_trade_uni(trade):
    for pool in trade.pools:
        if pool.pool_type is not PoolType.uniswap:
            return False
    return True


async def get_balance(weth: GenericToken, web3, trader_address):
    balance_pre = await weth.balance_of(trader_address)
    account_balance = BigNumber.from_value(web3.eth.getBalance(trader_address))
    return balance_pre.to_number() + account_balance.to_number()


def _perform_trade(trade, arbie, address, min_profit):
    if not _is_trade_uni(trade):
        return False

    amount_out = arbie.check_out_given_in(trade)
    if amount_out - trade.amount_in > min_profit:
        logger.info(f"Executing trade with return: {amount_out}, trade: {trade}")
        return arbie.swap(trade, address)
    return False


def perform_trade(data, trader_address):
    arbie = data.arbie()
    min_profit = data.min_profit()
    for trade in data.trades():
        if _perform_trade(trade, arbie, trader_address, min_profit):
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
        trader_address: trader_address
    output:
        profit: profit
    """

    async def on_next(self, data):
        trader_address = data.trader_address()
        balance_pre = await get_balance(data.weth(), data.web3(), trader_address)

        if not perform_trade(data, trader_address):
            raise Exception("No trade performed")

        balance_post = await get_balance(data.weth(), data.web3(), trader_address)

        data.profit(balance_post - balance_pre)
        logger.info("Finished trading")
