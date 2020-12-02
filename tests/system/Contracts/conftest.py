"""Fixtures for smart contracts."""

import pytest

from Arbie.Contracts import ContractFactory, UniswapV2Router


@pytest.fixture
def uniswap_router(w3, deploy_address, weth, factory):
    return ContractFactory(w3, UniswapV2Router).deploy_contract(
        deploy_address, factory.get_address(), weth.get_address()
    )
