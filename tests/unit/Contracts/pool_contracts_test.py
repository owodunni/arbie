"""Unittests of PoolContracts."""

from unittest.mock import MagicMock

import pytest

from Arbie.Contracts.pool_contract import PoolContract

pytestmark = pytest.mark.asyncio


async def should_raise(promise):
    with pytest.raises(NotImplementedError):
        await promise


class TestPoolContract(object):
    async def test_should_throw(self):
        pc = PoolContract(MagicMock(), None, MagicMock())

        await should_raise(pc.create_tokens())

        await should_raise(pc.get_balances())

        await should_raise(pc.get_weights())

        await should_raise(pc.get_fee())

        with pytest.raises(NotImplementedError):
            pc.get_type()
