"""Whitelist contains actions for finding good tokens."""

import logging

from Arbie.Actions import Action
from Arbie.Services import Coingecko

logger = logging.getLogger()


class Whitelist(Action):
    """SetUp Trader account for trading.

       Coingecko is used for finding whitelisted tokens it has a limit
       of 10 requests/second. However in reality it is much lower.
       The base settings allow for 1 requests every 0.6 seconds
       is equal to 4 req/sec. In total we need to do ~6000 request
       which will take ~25 min.
    [Settings]
    input:
        requests: 4
        delay: 1
        retries: 3
        retrie_delay: 30
    output:
        whitelist: whitelist
    """

    async def on_next(self, data):
        gecko = Coingecko(
            data.requests(), data.delay(), data.retries(), data.retrie_delay()
        )
        coins = await gecko.coins()
        if not coins:
            raise ConnectionError("No Coins from Coingecko")
        data.whitelist(coins)
        logger.info(f"Whitelist: {coins}")
