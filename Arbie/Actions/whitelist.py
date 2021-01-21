"""Whitelist contains actions for finding good tokens."""

from Arbie.Actions import Action
from Arbie.Services import Coingecko


class Whitelist(Action):
    """SetUp Trader account for trading.

       Coingecko is used for finding whitelisted tokens it has a limit
       of 10 requests/second. However in reality it is much lower.
       The base settings allow for 1 requests every 0.6 seconds
       is equal to 1.67 req/sec. In total we need to do ~6000 request
       which will take ~60 min.
    [Settings]
    input:
        requests: 1
        delay: 0.6
    output:
        whitelist: whitelist
    """

    async def on_next(self, data):
        data.whitelist(await Coingecko(1, 0.6).coins())  # noqa: WPS432
