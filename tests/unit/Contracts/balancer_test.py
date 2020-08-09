"""Test balancer contracts."""
from Arbie.Contracts import ContractFactory
from Arbie.Contracts.balancer import PoolFactory

from .web3_helper_test import *  # noqa: F403, WPS300, WPS347, F401


def test_create_pool_factory(deploy_address, w3):
    ContractFactory(w3, PoolFactory).deploy_contract(deploy_address)
