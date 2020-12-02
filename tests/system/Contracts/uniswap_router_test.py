"""Test UniswapV2Router smart contracts."""

from Arbie.Contracts import ContractFactory, UniswapV2Router


class TestUniswapV2Router(object):
    def test_create_router(self, w3, deploy_address, weth, pair_factory):
        ContractFactory(w3, UniswapV2Router).deploy_contract(
            deploy_address, pair_factory.get_address(), weth.get_address()
        )
