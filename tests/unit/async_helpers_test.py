"""Unittest of async_helpers.py."""
import asyncio
from unittest.mock import MagicMock

import pytest

from Arbie.async_helpers import CircuitBreaker, async_map


async def pass_through(some_value):
    await asyncio.sleep(0)
    return some_value


@pytest.mark.asyncio
async def test_async_map():
    res = await async_map(pass_through, range(3))
    assert res == [0, 1, 2]


@pytest.mark.asyncio
async def test_async_map_chunk():
    res = await async_map(pass_through, range(3), 2)
    assert res == [0, 1, 2]


class TestCircuitBreaker(object):
    def test_safe_call(self):
        mock = MagicMock(side_effect=[Exception(), 1337])  # noqa: WPS432
        breaker = CircuitBreaker(2, 0, mock)
        value = breaker.safe_call()
        assert value == 1337  # noqa: WPS432
        assert mock.call_count == 2

    def test_safe_call_raises_after_retrie_count(self):
        mock = MagicMock(side_effect=ValueError())  # noqa: WPS432
        breaker = CircuitBreaker(1, 0, mock)
        with pytest.raises(ValueError):
            breaker.safe_call()
