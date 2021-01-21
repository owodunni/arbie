"""Integration test for Coingecko API."""

import pytest

from Arbie.Services import Coingecko

pytestmark = pytest.mark.asyncio


class TestCoingecko(object):
    async def test_btc_coin(self):
        response = await Coingecko()._coin_ticker("01coin")  # noqa: WPS437
        assert response is None

    async def test_eth_coin(self):
        address = await Coingecko()._coin_ticker("velo-token")  # noqa: WPS437
        assert address == "0x98ad9B32dD10f8D8486927D846D4Df8BAf39Abe2".lower()

    async def test_get_ids(self):
        ids = await Coingecko().ids()  # noqa: WPS437
        assert len(ids) > 6000  # noqa: WPS432
