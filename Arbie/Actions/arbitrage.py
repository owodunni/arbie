"""arbitrage can be used to find to arbitrage opertunity between two Pools."""

import logging
from typing import Tuple

from sympy import nsolve, symbols

from Arbie.Actions import Action
from Arbie.Variables import Trade

logger = logging.getLogger()
x = symbols("x")


class ArbitrageFinder(object):
    def __init__(self, trade: Trade):
        self.trade = trade

    def find_arbitrage(self) -> Tuple[float, float]:
        if len(self.trade) < 3:
            raise ValueError(
                "Can only find arbitrage opportunity between at leat 3 tokens"
            )

        if not self.token_in_pools():
            raise ValueError("Tokens does not exist in pools")

        trade_input = self.calculate_optimal_arbitrage()
        profit = self.calculate_profit(trade_input)

        return trade_input, profit

    def token_in_pools(self) -> bool:
        for pool, token_in, token_out in self.trade:
            if token_in not in pool.tokens or token_out not in pool.tokens:
                return False
        return True

    def trade_expr(self):
        return self.expr_builder(lambda inner, expr: inner.subs(x, expr))

    def arbitrage_expr(self):
        return self.expr_builder(lambda inner, expr: inner.subs(x, expr) - x)

    def expr_builder(self, subs_expr):  # noqa: WPS210
        i = 0
        expr = None
        for pool, token_in, token_out in self.trade:
            inner_expr = pool.out_given_in_expr(token_in, token_out)
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
        return sol

    def calculate_profit(self, value) -> float:
        expr = self.trade_expr()
        return expr.subs(x, value) - value

    def _initial_expr(self):
        pool, trade_in, trade_out = self.trade[0]
        return pool.out_given_in_expr(trade_in, trade_out)


def _update_oportunity(raw_trades, nmb_trades):
    trades = []
    for index, arb in enumerate(raw_trades):
        amount_in = None
        profit = None
        try:
            amount_in, profit = ArbitrageFinder(arb).find_arbitrage()
        except (AssertionError, ValueError, TypeError) as e:
            logger.warning(f"No arbitrage found {e}")
            continue

        arb.amount_in = amount_in
        arb.profit = profit
        trades.append(arb)
        logger.info(
            f"Found opportunity {index}:{len(raw_trades)}"
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
        logger.info(f"Top trade has {sorted_trade[0].profit}")
        data.out_trades(sorted_trade)
