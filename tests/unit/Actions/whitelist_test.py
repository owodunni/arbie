"""Test whitelist."""

import pytest
from pytest_mock.plugin import MockerFixture

from Arbie.Actions import ActionTree, Store, Whitelist
from Arbie.Services import Coingecko


class TestWhitelist(object):
    @pytest.mark.asyncio
    async def test_on_next(self, mocker: MockerFixture):
        mocker.patch.object(
            Coingecko,
            "coins",
            return_value=[
                "0xdac17f958d2ee523a2206206994597c13d831ec7",
                "0x514910771af9ca656af840dff83e8264ecf986ca",
            ],
        )
        store = Store()
        tree = ActionTree(store)
        tree.add_action(Whitelist())
        await tree.run()

        assert len(store.get("whitelist")) == 2
