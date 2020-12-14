"""Trades contain variables for trading."""

from Arbie.Variables.pool import Pools
from Arbie.Variables.token import Balance, Tokens


class Trade(object):
    def __init__(self, pools: Pools, path: Tokens, ratio=None, amount_in=None):
        self.pools = pools
        self.path = path
        self.amount_in = amount_in
        self.profit = None
        self.balance = None
        self.ratio = ratio

    def __len__(self):
        return len(self.path)

    def __str__(self):
        return f"""
Trade(
    pools:{self.pools},
    path:{self.path},
    amount_in:{self.amount_in},
    profit:{self.profit},
    balance:{self.balance},
    ratio:{self.ratio})"""  # noqa: WPS221

    def __iter__(self):
        return iter(self._generator())

    def __getitem__(self, i):
        return self.pools[i], self.path[i], self.path[i + 1]  # noqa: WPS221

    def set_balance(self, balance: Balance):
        self.balance = balance

    def _generator(self):
        yield from (self[i] for i, _ in enumerate(self.pools))
