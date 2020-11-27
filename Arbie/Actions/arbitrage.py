"""arbitrage can be used to find to arbitrage opertunity between two Pools."""

import logging
from typing import Tuple

from sympy import nsolve, symbols

from Arbie.Actions import Action
from Arbie.Variables import ArbitrageOpportunity

logger = logging.getLogger()
x = symbols("x")


class ArbitrageFinder(object):
    def __init__(self, trades: ArbitrageOpportunity):
        self.trades = trades

    def find_arbitrage(self) -> Tuple[float, float]:
        if len(self.trades) < 2:
            raise ValueError(
                "Can only found arbitrage opportunity between two or more pools"
            )

        if not self.token_in_pools():
            raise ValueError("Tokens does not exist in pools")

        trade_input = self.calculate_optimal_arbitrage()
        profit = self.calculate_profit(trade_input)

        return trade_input, profit

    def token_in_pools(self) -> bool:
        for trade in self.trades:
            pool = trade.pool
            if trade.token_in not in pool.tokens or trade.token_out not in pool.tokens:
                return False
        return True

    def trade_expr(self):
        first_trade = self.trades[0]
        expr = first_trade.pool.out_given_in_expr(
            first_trade.token_in, first_trade.token_out
        )

        for trade in self.trades[1:]:
            inner_expr = trade.pool.out_given_in_expr(trade.token_in, trade.token_out)
            expr = inner_expr.subs(x, expr)

        return expr

    def arbitrage_expr(self):
        first_trade = self.trades[0]
        expr = first_trade.pool.out_given_in_expr(
            first_trade.token_in, first_trade.token_out
        )

        for trade in self.trades[1:]:
            inner_expr = trade.pool.out_given_in_expr(trade.token_in, trade.token_out)
            expr = inner_expr.subs(x, expr) - x

        return expr

    def arbitrage_diff_expr(self):
        return self.arbitrage_expr().diff(x)

    def calculate_optimal_arbitrage(self) -> float:
        sol = nsolve(self.arbitrage_diff_expr(), 0)
        if sol <= 0:
            raise AssertionError("No arbitrage opportunity found.")
        return sol

    def calculate_profit(self, value) -> float:
        expr = self.trade_expr()
        return expr.subs(x, value) - value


def _update_oportunity(raw_trades, nmb_trades):
    trades = []
    for index, arb in enumerate(raw_trades):
        amount_in = None
        profit = None
        try:
            amount_in, profit = ArbitrageFinder(arb).find_arbitrage()
        except (AssertionError, ValueError, TypeError):
            continue

        arb.amount_in = amount_in
        arb.profit = profit
        trades.append(arb)
        logger.info(
            f"Found oportunity {index}:{len(raw_trades)}"
            + " with profit {arb.profit} for {arb.amount_in} eth"
        )
        if index > nmb_trades:
            break

    return trades


class Arbitrage(Action):
    """Find optimal arbitrage opportunity for a list sorted trades.

    Remove all trades that are not profitable.

    [Settings]
    input:
        trades: all_trades
        nmb_trades: 100
    output:
        out_trades: filtered_trades
    """

    async def on_next(self, data):
        trades = _update_oportunity(data.trades(), data.nmb_trades())

        sorted_trade = sorted(
            trades, key=lambda trade: trade.profit / trade.amount_in, reverse=True
        )
        logger.info(
            f"Top trade has {sorted_trade[0].profit} was {sorted_trade[0].trades}"
        )
        data.out_trades(sorted_trade)
