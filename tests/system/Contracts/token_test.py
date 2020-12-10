"""Test uniswap contracts."""
import pytest

from Arbie.Contracts import ContractFactory
from Arbie.Contracts.tokens import GenericToken, Weth
from Arbie.Variables import BigNumber

bg10 = BigNumber(10)


@pytest.fixture
def token_factory(w3) -> ContractFactory:
    return ContractFactory(w3, GenericToken)


@pytest.fixture
def dai(deploy_address, token_factory) -> GenericToken:
    return token_factory.deploy_contract(deploy_address, "Dai", "DAI", bg10.value)


@pytest.mark.asyncio
async def test_decimals(dai: GenericToken):
    assert await dai.decimals() == 18


class TestToken(object):
    def test_equals(self, dai, token_factory):
        dai2 = token_factory.load_contract(
            owner_address=dai.owner_address, address=dai.get_address()
        )
        assert dai == dai2

    def test_approve(self, dai: GenericToken, deploy_address):
        assert dai.approve(deploy_address, bg10)

    @pytest.mark.asyncio
    async def test_transfer(self, dai: GenericToken, deploy_address, dummy_address):
        dai.approve(deploy_address, bg10)
        dai.transfer(dummy_address, bg10)
        bg = await dai.balance_of(dummy_address)
        assert bg.to_number() == 10

    @pytest.mark.asyncio
    async def test_name(self, dai: GenericToken):
        name = await dai.get_name()
        assert name == "Dai"


class TestWeth(object):
    @pytest.mark.asyncio
    async def test_deposit_withdraw(self, real_weth: Weth, dummy_address):
        real_weth.set_owner_address(dummy_address)
        real_weth.deposit(2)
        assert await real_weth.balance_of(dummy_address) == BigNumber(2)

        real_weth.withdraw(2)
        assert await real_weth.balance_of(dummy_address) == BigNumber(0)
