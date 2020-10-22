"""arbitrage can be used to find to arbitrage opertunity between two Pools."""

from typing import Tuple

from sympy import nsolve, symbols

from Arbie.Actions import Action
from Arbie.Variables import ArbitrageOpportunity

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


class Arbitrage(Action):
    """Find optimal arbitrage opportunity for a list sorted trades.

    Remove all trades that are not profitable.

    [Settings]
    input:
        trades: all_trades
    output:
        out_trades: filtered_trades
    """

    def on_next(self, data):
        trades = []
        for arbitrage_opportunity in data.trades():
            amount_in = None
            profit = None
            try:
                amount_in, profit = ArbitrageFinder(
                    arbitrage_opportunity
                ).find_arbitrage()
            except AssertionError:
                continue

            arbitrage_opportunity.amount_in = amount_in
            arbitrage_opportunity.profit = profit
            trades.append(arbitrage_opportunity)

        sorted_trade = sorted(trades, key=lambda trade: trade.profit, reverse=True)
        data.out_trades(sorted_trade)
