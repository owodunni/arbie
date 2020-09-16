"""Test balancer contracts."""
import pytest

from Arbie.Contracts import ContractFactory
from Arbie.Contracts.balancer import PoolFactory

from .web3_helper_test import *  # noqa: F403, WPS300, WPS347, F401


@pytest.fixture
def pool_factory(deploy_address, w3) -> PoolFactory:
    return ContractFactory(w3, PoolFactory).deploy_contract(deploy_address)


def test_create_new_pool(pool_factory):  # noqa: WPS442
    pool_factory.new_bpool()
    assert len(pool_factory.all_pools()) == 1


def test_get_number_of_tokens(pool_factory):  # noqa: WPS442
    pool_factory.new_bpool()
    pools = pool_factory.all_pools()
    assert pools[0].get_number_of_tokens() == 0
