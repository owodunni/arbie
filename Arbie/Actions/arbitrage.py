"""arbitrage can be used to find to arbitrage opertunity between two Pools."""

from typing import Tuple

from sympy import nsolve, symbols

from Arbie.Variables import ArbitrageOpportunity, Balance
from Arbie.Actions import Action

x = symbols('x')


def find_arbitrage(trades: ArbitrageOpportunity) -> Tuple[float, float]:
    if len(trades) < 2:
        raise ValueError('Can only found arbitrage opportunity between two or more pools')

    if not token_in_pools(trades):
        raise ValueError('Tokens does not exist in pools')

    trade_input = calculate_optimal_arbitrage(trades)
    profit = calculate_profit(trades, trade_input)

    return trade_input, profit


def token_in_pools(trades: ArbitrageOpportunity) -> bool:
    for trade in trades:
        pool = trade.pool
        if trade.token_in not in pool.tokens or trade.token_out not in pool.tokens:
            return False
    return True


def trade_expr(trades: ArbitrageOpportunity):
    first_trade = trades[0]
    expr = first_trade.pool.out_given_in_expr(
        first_trade.token_in,
        first_trade.token_out)

    for trade in trades[1:]:
        inner_expr = trade.pool.out_given_in_expr(trade.token_in, trade.token_out)
        expr = inner_expr.subs(x, expr)

    return expr


def arbitrage_expr(trades: ArbitrageOpportunity):
    first_trade = trades[0]
    expr = first_trade.pool.out_given_in_expr(
        first_trade.token_in,
        first_trade.token_out)

    for trade in trades[1:]:
        inner_expr = trade.pool.out_given_in_expr(trade.token_in, trade.token_out)
        expr = inner_expr.subs(x, expr) - x

    return expr


def arbitrage_diff_expr(trade: ArbitrageOpportunity):
    return arbitrage_expr(trade).diff(x)


def calculate_optimal_arbitrage(trade: ArbitrageOpportunity) -> float:
    sol = nsolve(arbitrage_diff_expr(trade), 0)
    if sol <= 0:
        raise AssertionError('No arbitrage opportunity found.')
    return sol


def calculate_profit(trade: ArbitrageOpportunity, value) -> float:
    expr = trade_expr(trade)
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
            try:
                amount_in, profit = find_arbitrage(arbitrage_opportunity)
                arbitrage_opportunity.amount_in = amount_in
                arbitrage_opportunity.profit = profit
                trades.append(arbitrage_opportunity)
            except AssertionError:
                pass

        sorted_trade = sorted(trades, key=lambda trade: trade.profit, reverse=True)
        data.out_trades(sorted_trade)
