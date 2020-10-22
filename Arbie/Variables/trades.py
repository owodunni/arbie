"""Trades contain variables for trading."""

from typing import List

from Arbie.Variables.token import Balance, Token
from Arbie.Variables.pool import Pool

class Trade(object):

    def __init__(self, pool: Pool, token_in: Token, token_out: Token):
        self.pool = pool
        self.token_in = token_in
        self.token_out = token_out


class ArbitrageOpportunity(object):

    def __init__(self, trades: List[Trade], balance: Balance=None, ratio=None):
        self.trades = trades
        self.balance = balance
        self.ratio = ratio
