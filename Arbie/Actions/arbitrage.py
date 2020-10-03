"""arbitrage can be used to find to arbitrage opertunity between two Amms."""

from typing import List

from sympy import nsolve, symbols

from Arbie.Actions.amm import Amm, Token, Variable

Pools = List[Amm]
x = symbols('x')


class TradeOpertunity(object):
    """A trade opertunity contains a list of pools and the tokens to trade with those pools."""

    def __init__(self, pools: Pools, token_in: Token, token_out: Token):
        self.pools = pools
        self.token_in = token_in
        self.token_out = token_out


def find_arbitrage(trade: TradeOpertunity) -> Variable:
    if len(trade.pools) != 2:
        raise ValueError('Can only found arbitrage opertunity between two pools')

    if not token_in_pools(trade):
        raise ValueError('Tokens does not exist in pools')

    if not opertunity(trade):
        raise ValueError(
            'No arbitrage opertunity found in pools, perform the trade in reverse order')

    profit = calculate_optimal_arbitrage(trade)
    return Variable(trade.token_in, profit)


def token_in_pools(trade: TradeOpertunity) -> bool:
    for pool in trade.pools:
        if trade.token_in not in pool.tokens or trade.token_out not in pool.tokens:
            return False
    return True


def opertunity(trade: TradeOpertunity) -> bool:
    prices = []
    for pool in trade.pools:
        prices.append(pool.spot_price(trade.token_in, trade.token_out))

    # If there is an opertunity then the price of the first pool
    # should be smaller then the price of the second pool
    return prices[0] < prices[1]


def arbitrage_expr(trade: TradeOpertunity):
    expr = trade.pools[0].out_given_in_expr(trade.token_in, trade.token_out)
    expr2 = trade.pools[1].out_given_in_expr(trade.token_out, trade.token_in)

    return expr2.subs(x, expr) - x


def arbitrage_diff_expr(trade: TradeOpertunity):
    return arbitrage_expr(trade).diff(x)


def calculate_optimal_arbitrage(trade: TradeOpertunity) -> float:
    sol = nsolve(arbitrage_diff_expr(trade), 0)
    if sol <= 0:
        raise ValueError('No arbitrage opertunity found.')
    return sol
