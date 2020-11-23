"""System tests for PoolUpdater."""

import asyncio
import pytest

from Arbie.Actions import ActionTree, PoolUpdater, Store
from Arbie.Contracts import GenericToken, BalancerFactory, ContractFactory, UniswapFactory
from Arbie.Variables import BigNumber
from Arbie.async_helpers import async_map

small = 10e4
medium = 10e6
large = 10e8


@pytest.fixture
async def pool_factory(
        dai: GenericToken,
        weth: GenericToken,
        yam: GenericToken,
        wbtc: GenericToken,
        w3,
        deploy_address,
) -> BalancerFactory:
    factory = ContractFactory(w3, BalancerFactory).deploy_contract(deploy_address)

    f1 = factory.setup_pool(
        [weth, dai, yam],
        [5, 5, 5],
        [
            BigNumber(small / 303.0),
            BigNumber(small / 0.9),
            BigNumber(small / 0.1),
        ],
    )

    f2 = factory.setup_pool(
        [weth, wbtc],
        [5, 1],
        [
            BigNumber(5 * large / 301.0),
            BigNumber(large / 10000),
        ],  # noqa: WPS221
    )
    await asyncio.gather(f1, f2)
    return factory


@pytest.fixture
async def pair_factory(  # noqa: WPS210
        dai: GenericToken,
        weth: GenericToken,
        yam: GenericToken,
        wbtc: GenericToken,
        bad,
        w3,
        deploy_address,
) -> UniswapFactory:
    factory = ContractFactory(w3, UniswapFactory).deploy_contract(
        deploy_address, deploy_address
    )
    await factory.setup_pair(
        [weth, dai],
        [BigNumber(large / 300), BigNumber(large)],
    )
    await factory.setup_pair(
        [weth, wbtc],
        [
            BigNumber(large / 300),
            BigNumber(large / 10000),
        ],
    )
    return factory


@pytest.fixture
async def balancer_pools(pool_factory: BalancerFactory):
    pool_contracts = await pool_factory.all_pools()
    return [await contract.create_pool() for contract in pool_contracts]

@pytest.fixture
async def uniswap_pools(pair_factory: UniswapFactory):
    pool_contracts = await pair_factory.all_pairs()
    return [await contract.create_pool() for contract in pool_contracts]

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
