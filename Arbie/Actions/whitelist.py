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
        # 2 requests every 0.6 seconds is equal to 3,33 req/sec
        # In total we need to do ~6000 request which will take 30 min
        data.whitelist(await Coingecko(2, 0.6).coins())  # noqa: WPS432
