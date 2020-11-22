"""Unittest for pool updater."""

import pytest

from Arbie.Actions import ActionTree, PoolUpdater, Store


class TestPoolUpdater(object):
    @pytest.mark.asyncio
    async def test_on_next(self, web3_mock, pools, tokens):
        store = Store()
        store.add("web3", web3_mock)
        store.add("all_pools", pools)
        store.add("all_tokens", tokens)
        tree = ActionTree(store)
        tree.add_action(PoolUpdater())
        with pytest.raises(NotImplementedError):
            await tree.run()
