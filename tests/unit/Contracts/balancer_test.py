"""Test balancer contracts."""
from Arbie.Contracts import ContractFactory
from Arbie.Contracts.balancer import PoolFactory

from .web3_helper_test import *  # noqa: F403, WPS300, WPS347, F401

@pytest.fixture
def pool_factory(deploy_address, w3) -> PoolFactory:
    return ContractFactory(w3, PoolFactory).deploy_contract(deploy_address)

def test_create_new_pool(pool_factory):
    pool_factory.new_bpool()
