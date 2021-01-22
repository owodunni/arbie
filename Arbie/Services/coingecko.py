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
        self.breaker = CircuitBreaker(retries, retrie_timeout, self._get_json)

    async def coins(self):
        ids = await self.ids()
        if ids:
            return await self.coins_from_ids(ids)

    async def coins_from_ids(self, ids):
        urls = list(map(self._coin_url, ids))
        addresses = await async_map(
            self._parse_eth_coin, urls, self.batch_size, self.timeout
        )
        addresses = set(addresses)
        addresses.remove(None)
        return list(addresses)

    async def ids(self):
        rs_json = await self._get(COINS_URL)
        return list(map(lambda i: i["id"], rs_json))

    async def _coin_ticker(self, coin_id):
        url = self._coin_url(coin_id)
        return await self._parse_eth_coin(url)

    def _coin_url(self, coin_id):
        return urljoin(COINGECKO_URL, f"api/v3/coins/{coin_id}/tickers")

    async def _parse_eth_coin(self, url):
        body = await self._get(url)

        for ticker in self._tickers(body):
            if (
                ticker is None
                or ticker["target"] != "ETH"
                or not self._ok(ticker["is_anomaly"])
            ):
                continue

            address = ticker["base"].lower()
            logger.info(f"Found token: {address}")

            eth_address_length = 42  # noqa: WPS432
            if len(address) == eth_address_length:
                return address

    def _tickers(self, body):
        tickers = body["tickers"]
        if tickers:
            return tickers
        return []

    def _ok(self, is_anomaly):
        return not is_anomaly

    def _get_json(self, url):
        response = requests.get(url)
        if not response.ok:
            raise ConnectionError(f"Failed to connect to {url}, response: {response}")
        return response.json()

    async def _get(self, url):
        logger.info(f"Requesting endpoing {url}")
        return await run_async(self.breaker.safe_call, url)
