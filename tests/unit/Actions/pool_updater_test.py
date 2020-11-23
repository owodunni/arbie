"""Unittest for pool updater."""

from unittest.mock import MagicMock

import pytest

from Arbie.Actions import ActionTree, PoolUpdater, Store


class TestPoolUpdater(object):
    @pytest.mark.asyncio
    async def test_on_next(self, pools):
        store = Store()
        store.add("web3", MagicMock())
        store.add("all_pools", pools)
        tree = ActionTree(store)
        tree.add_action(PoolUpdater())
        with pytest.raises(ValueError):
            await tree.run()
