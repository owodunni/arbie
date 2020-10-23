"""Help module for web3 tests."""
from typing import List

import pytest

from Arbie.Variables import Pool, Token

small = 10000
medium = 1000000
large = 100000000


@pytest.fixture
def eth() -> Token:
    return Token("eth", 1)


@pytest.fixture
def dai() -> Token:
    return Token("dai", 300)


@pytest.fixture
def btc() -> Token:
    return Token("btc", 3.0 / 100)


@pytest.fixture
def yam() -> Token:
    return Token("yam", 3000)


@pytest.fixture
def pools(dai, eth, btc, yam) -> List[Pool]:
    return [
        Pool(
            [eth, dai, yam],
            [small / 303.0, small / 0.9, small / 0.1],
            [1 / 3.0, 1 / 3.0, 1 / 3.0],
            0.004,
        ),
        Pool([eth, btc], [large / 305.0, large / 10000], [5 / 6, 1 / 6], 0.01),
        Pool(
            [eth, dai, btc],
            [medium / 301.0, medium / 1.1, medium / 10020],
            [1 / 2.0, 1 / 4.0, 1 / 4.0],
            0.004,
        ),
        Pool([dai, yam], [small / 1.1, small / 0.1], [1 / 2.0, 1 / 2.0], 0.001),
    ]
