"""arbitrage can be used to find to arbitrage opertunity between two Pools."""

from typing import List, NewType

from sympy import nsolve, symbols

from Arbie import Balance, Token
from Arbie.Variables.pool import Pool

Pools = List[Pool]
x = symbols('x')


class Trade(object):

    def __init__(self, pool: Pool, token_in: Token, token_out: Token):
        self.pool = pool
        self.token_in = token_in
        self.token_out = token_out


TradeOpportunity = NewType('TradeOpportunity', List[Trade])


def find_arbitrage(trades: TradeOpportunity) -> Balance:
    if len(trades) < 2:
        raise ValueError('Can only found arbitrage opportunity between two or more pools')

    if not token_in_pools(trades):
        raise ValueError('Tokens does not exist in pools')
    
    profit = calculate_optimal_arbitrage(trades)
    return Balance(trades[0].token_in, profit)


def token_in_pools(trades: TradeOpportunity) -> bool:
    for trade in trades:
        pool = trade.pool
        if trade.token_in not in pool.tokens or trade.token_out not in pool.tokens:
            return False
    return True


def arbitrage_expr(trades: TradeOpportunity):
    first_trade = trades[0]
    expr = first_trade.pool.out_given_in_expr(
        first_trade.token_in,
        first_trade.token_out)

    for trade in trades[1:]:
        inner_expr = trade.pool.out_given_in_expr(trade.token_in, trade.token_out)
        expr = inner_expr.subs(x, expr) - x

    return expr


def arbitrage_diff_expr(trade: TradeOpportunity):
    return arbitrage_expr(trade).diff(x)


def calculate_optimal_arbitrage(trade: TradeOpportunity) -> float:
    sol = nsolve(arbitrage_diff_expr(trade), 0)
    if sol <= 0:
        raise  AssertionError('No arbitrage opportunity found.')
    return sol


class Arbitrage(Action):
    """Find optimal arbitrage opertunity for a list sorted trades.

    Remove all trades that are not profitable.

    [Settings]
    input:
        trades: all_trades
    output:
        out_trades: filtered_trades
        out_balance: trade_balance
    """

    def on_next(self, data):
        out_trades = []
        out_balance = []
        for trade in data.trades()
            try:
                out_balance.append(find_arbitrage(trade))
                out_trades.append(trade)

        
                
            
