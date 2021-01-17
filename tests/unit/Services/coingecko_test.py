"""unit test for Coingecko."""

from unittest.mock import MagicMock

import pytest
from pytest_mock.plugin import MockerFixture

from Arbie.Services import Coingecko

pytestmark = pytest.mark.asyncio

coins = [
    {"id": "1ai", "symbol": "1ai", "name": "1AI"},
    {"id": "velo-token", "symbol": "VLO", "name": "VELO Token"},
    {"id": "1inch", "symbol": "1inch", "name": "1inch"},
]

coin_1a1 = {
    "name": "1AI",
    "tickers": [
        {
            "base": "1AI",
            "target": "BTC",
            "market": {
                "name": "Vindax",
                "identifier": "vindax",
                "has_trading_incentive": False,
            },
            "last": 1e-8,
            "volume": 51070,
            "converted_last": {"btc": 1e-8, "eth": 2.919e-7, "usd": 0.00036442},
            "converted_volume": {"btc": 0.0005107, "eth": 0.01490667, "usd": 18.61},
            "trust_score": None,
            "bid_ask_spread_percentage": 50,
            "timestamp": "2021-01-17T02:39:22+00:00",
            "last_traded_at": "2021-01-17T02:39:22+00:00",
            "last_fetch_at": "2021-01-18T02:17:05+00:00",
            "is_anomaly": False,
            "is_stale": True,
            "trade_url": "https://vindax.com/exchange-base.html?symbol=1AI_BTC",
            "token_info_url": None,
            "coin_id": "1ai",
            "target_coin_id": "bitcoin",
        }
    ],
}

coin_vlo = {
    "name": "VELO Token",
    "tickers": [
        {
            "base": "0X98AD9B32DD10F8D8486927D846D4DF8BAF39ABE2",
            "target": "ETH",
            "market": {
                "name": "Uniswap (v2)",
                "identifier": "uniswap",
                "has_trading_incentive": False,
            },
            "last": 0.00000243692314918803,
            "volume": 932296.695673962,
            "converted_last": {"btc": 9.41e-8, "eth": 0.00000244, "usd": 0.00333838},
            "converted_volume": {"btc": 0.08776486, "eth": 2.274565, "usd": 3112.36},
            "trust_score": "green",
            "bid_ask_spread_percentage": 0.614416,
            "timestamp": "2021-01-20T05:32:35+00:00",
            "last_traded_at": "2021-01-20T05:32:35+00:00",
            "last_fetch_at": "2021-01-20T06:01:50+00:00",
            "is_anomaly": False,
            "is_stale": False,
            "trade_url": "https://app.uniswap.org/#/swap?outputCurrency=0x98ad9b32dd10f8d8486927d846d4df8baf39abe2",
            "token_info_url": "https://info.uniswap.org/token/0x98ad9b32dd10f8d8486927d846d4df8baf39abe2",
            "coin_id": "velo-token",
            "target_coin_id": "ethereum",
        }
    ],
}

coin_1inch = {
    "name": "1inch",
    "tickers": [
        {
            "base": "0X111111111117DC0AA78B770FA6A738034120C302",
            "target": "ETH",
            "market": {
                "name": "1inch Liquidity Protocol",
                "identifier": "one_inch_liquidity_protocol",
                "has_trading_incentive": False,
            },
            "last": 0.0013669431402898,
            "volume": 4600000.73782359,
            "converted_last": {"btc": 0.0000527, "eth": 0.00136693, "usd": 1.87},
            "converted_volume": {"btc": 242.4, "eth": 6288, "usd": 8592901},
            "trust_score": "green",
            "bid_ask_spread_percentage": 0.602722,
            "timestamp": "2021-01-20T06:04:08+00:00",
            "last_traded_at": "2021-01-20T06:04:08+00:00",
            "last_fetch_at": "2021-01-20T06:04:08+00:00",
            "is_anomaly": True,  # Modified from original inorder to test anomaly detection
            "is_stale": False,
            "token_info_url": None,
            "coin_id": "1inch",
            "target_coin_id": "ethereum",
        },
    ],
}


def bad_request(endpoint):
    mock = MagicMock()
    mock.ok = True
    return mock


def load_data(endpoint):
    mock = MagicMock()
    mock.ok = True
    json = None
    if "coins/list" in endpoint:
        json = coins
    elif "velo" in endpoint:
        json = coin_vlo
    elif "1inch" in endpoint:
        json = coin_1inch
    elif "1ai" in endpoint:
        json = coin_1a1
    mock.json.return_value = json
    return mock


@pytest.fixture
def request_mock(mocker: MockerFixture):
    mock = mocker.patch("Arbie.Services.coingecko.requests")
    mock.get.side_effect = load_data
    return mock


class TestCoingecko(object):
    async def test_coins(self, request_mock: MagicMock):
        addresses = await Coingecko().coins()
        assert len(addresses) == 1
        assert addresses[0] == "0x98ad9b32dd10f8d8486927d846d4df8baf39abe2"

    async def test_bad_request(self, request_mock: MagicMock):
        request_mock.get.side_effect = bad_request
        addresses = await Coingecko().coins()
        assert not addresses
