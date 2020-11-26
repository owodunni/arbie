"""Unittest of async_helpers.py."""
import asyncio

import pytest

from Arbie.async_helpers import async_map


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
