"""Whitelist contains actions for finding good tokens."""

from Arbie.Actions import Action
from Arbie.Services import Coingecko


class Whitelist(Action):
    """SetUp Trader account for trading.

    [Settings]
    input:
    output:
        whitelist: whitelist
    """

    async def on_next(self, data):
        data.whitelist(await Coingecko().coins())
