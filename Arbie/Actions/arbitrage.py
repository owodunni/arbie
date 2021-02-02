"""arbitrage can be used to find to arbitrage opertunity between two Pools."""

import logging
from functools import partial
from multiprocessing import Pool
from operator import is_not
from typing import Tuple

from sympy import nsolve, symbols

from Arbie.Actions import Action
from Arbie.Variables import Trade

logger = logging.getLogger()
x = symbols("x")


class ArbitrageFinder(object):
    def __init__(self, trade: Trade, precision=10e3):
        self.trade = trade
        self.precision = precision

    def find_arbitrage_and_update_trade(self) -> Tuple[float, float]:
        if len(self.trade) < 3:
            raise ValueError(
                "Can only find arbitrage opportunity between at leat 3 tokens"
            )

        if not self.token_in_pools():
            raise ValueError("Tokens does not exist in pools")

        self.trade.amount_in = self.calculate_optimal_arbitrage()
        self.trade.profit = self.calculate_profit(self.trade.amount_in)

        return self.trade

    def token_in_pools(self) -> bool:
        for pool, token_in, token_out in self.trade:
            if token_in not in pool.tokens or token_out not in pool.tokens:
                return False
        return True

    def trade_expr(self):
        return self.expr_builder(lambda inner, expr: inner.subs(x, expr))

    def arbitrage_expr(self):
        return self.trade_expr() - x

    def expr_builder(self, subs_expr):  # noqa: WPS210
        i = 0
        expr = None
        for pool, token_in, token_out in self.trade:
            inner_expr = pool.out_given_in_expr(token_in, token_out, self.precision)
            if i > 0:
                expr = subs_expr(inner_expr, expr)
            else:
                expr = inner_expr
                i = i + 1
        return expr

    def arbitrage_diff_expr(self):
        return self.arbitrage_expr().diff(x)

    def calculate_optimal_arbitrage(self) -> float:
        sol = nsolve(self.arbitrage_diff_expr(), 0)
        if sol <= 0:
            raise AssertionError("No arbitrage opportunity found.")
        return sol / self.precision

    def calculate_profit(self, value) -> float:
        return self.arbitrage_expr().subs(x, value * self.precision) / self.precision

    def _initial_expr(self):
        pool, trade_in, trade_out = self.trade[0]
        return pool.out_given_in_expr(trade_in, trade_out)


def _check_oportunity(trade):
    try:
        return ArbitrageFinder(trade).find_arbitrage_and_update_trade()
    except (AssertionError, ValueError, TypeError):
        return None


class Arbitrage(Action):
    """Find optimal arbitrage opportunity for a list sorted trades.

    Remove all trades that are not profitable.

    [Settings]
    input:
        trades: all_trades
        process_trades: 20000
        top_trades: 10
        processes: 10
    output:
        out_trades: filtered_trades
    """

    async def on_next(self, data):
        raw_trades = data.trades()[: data.process_trades()]

        with Pool(data.processes()) as p:  # noqa: WPS432
            trades = p.map(_check_oportunity, raw_trades)

        trades = list(filter(partial(is_not, None), trades))
        sorted_trade = sorted(
            trades, key=lambda trade: trade.profit / trade.amount_in, reverse=True
        )
        logger.info(f"Top trade has {sorted_trade[0].profit}")
        data.out_trades(sorted_trade[: data.top_trades()])
