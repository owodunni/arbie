"""Trades contain variables for trading."""

from typing import List

from Arbie.Variables.pool import Pool
from Arbie.Variables.token import Balance, Token


class Trade(object):
    def __init__(self, pool: Pool, token_in: Token, token_out: Token):
        self.pool = pool
        self.token_in = token_in
        self.token_out = token_out


class ArbitrageOpportunity(object):
    def __init__(self, trades: List[Trade], ratio=None):
        self.trades = trades
        self.amount_in = None
        self.profit = None
        self.ratio = ratio

    def __iter__(self):
        return iter(self.trades)

    def __len__(self):
        return len(self.trades)

    def __getitem__(self, i):
        return self.trades[i]

    def set_balance(self, balance: Balance):
        self.balance = balance
