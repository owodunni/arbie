"""System tests for PoolUpdater."""

import pytest

from Arbie.Actions import ActionTree, PoolUpdater, Store
from Arbie.Contracts import BalancerFactory, UniswapFactory


async def get_pools(pool_contracts):
    pools = []
    for contact in pool_contracts:
        try:
            pool = await contact.create_pool()
        except ValueError:
            continue
        pools.append(pool)
    return pools


@pytest.fixture
async def balancer_pools(pool_factory: BalancerFactory):
    pool_contracts = await pool_factory.all_pools()
    return await get_pools(pool_contracts)


@pytest.fixture
async def uniswap_pools(pair_factory: UniswapFactory):
    pool_contracts = await pair_factory.all_pairs()
    return await get_pools(pool_contracts)


@pytest.fixture
async def pools(balancer_pools, uniswap_pools):
    return balancer_pools + uniswap_pools


class TestPoolUpdater(object):
    @pytest.mark.asyncio
    async def test_on_next(self, w3, pools):
        store = Store()
        store.add("web3", w3)
        store.add("all_pools", pools)
        tree = ActionTree(store)
        tree.add_action(PoolUpdater())
        await tree.run()
        assert store.get("all_pools") == pools
