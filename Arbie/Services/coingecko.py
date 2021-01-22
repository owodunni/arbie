"""Module for gettings tokens from Coingecko."""

import logging
from urllib.parse import urljoin

import requests

from Arbie.async_helpers import CircuitBreaker, async_map, run_async

logger = logging.getLogger()

COINGECKO_URL = "https://api.coingecko.com"

COINS_URL = urljoin(COINGECKO_URL, "api/v3/coins/list")


class Coingecko(object):
    def __init__(self, batch_size=5, timeout=0.6, retries=3, retrie_timeout=10):
        self.batch_size = batch_size
        self.timeout = timeout
        self.breaker = CircuitBreaker(retries, retrie_timeout, requests.get)

    async def coins(self):
        ids = await self.ids()
        if ids:
            return await self.coins_from_ids(ids)
        return []

    async def coins_from_ids(self, ids):
        response = await self._coin_urls(ids)
        addresses = set(map(self._parse_eth_coin, response))
        addresses.remove(None)
        return list(addresses)

    async def ids(self):
        rs = await self._get(COINS_URL)
        if rs.ok:
            return list(map(lambda i: i["id"], rs.json()))

    async def _coin_urls(self, ids):
        urls = list(map(self._coin_url, ids))
        return await async_map(self._get, urls, self.batch_size, self.timeout)

    async def _coin_ticker(self, coin_id):
        url = self._coin_url(coin_id)
        rs = await self._get(url)
        return self._parse_eth_coin(rs)

    def _coin_url(self, coin_id):
        return urljoin(COINGECKO_URL, f"api/v3/coins/{coin_id}/tickers")

    def _parse_eth_coin(self, response):
        if not response.ok:
            return None
        tickers = self._tickers(response)
        if (
            tickers is None
            or tickers["target"] != "ETH"
            or not self._ok(tickers["is_anomaly"])
        ):
            return None
        address = tickers["base"].lower()
        eth_address_length = 42  # noqa: WPS432
        if len(address) == eth_address_length:
            return address

    def _tickers(self, response):
        tickers = response.json()["tickers"]
        if tickers:
            return tickers[0]

    def _ok(self, is_anomaly):
        return not is_anomaly

    async def _get(self, url):
        logger.info(f"Requesting endpoing {url}")
        return await run_async(self.breaker.safe_call, url)
