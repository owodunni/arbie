"""Unittest trader."""

import asyncio
from unittest.mock import MagicMock

import pytest

from Arbie import TransactionError
from Arbie.Actions.trader import BalanceChecker
from Arbie.Variables import BigNumber


def amount_to_future(amount):
    future = asyncio.Future()
    future.set_result(BigNumber(amount))
    return future


def setup_eth(amounts):
    mock = MagicMock()
    mock.eth = mock
    mock.getBalance.side_effect = list(
        map(lambda a: BigNumber(a).value, amounts)
    )  # noqa: WPS221
    return mock


def setup_weth(amounts):
    mock = MagicMock()
    mock.balance_of.side_effect = list(map(amount_to_future, amounts))
    return mock


def setup_mocks(eth_amounts, weth_amounts):
    return setup_eth(eth_amounts), setup_weth(weth_amounts)


some_address = "any address"


class TestBalanceChecker(object):
    @pytest.mark.asyncio
    async def test_check(self):
        checker = BalanceChecker(*setup_mocks([1], [2]))
        eth, weth = await checker.check(some_address)
        assert eth == 1
        assert weth == 2

    @pytest.mark.asyncio
    async def test_low_eth(self):
        checker = BalanceChecker(*setup_mocks([1], [0]))
        with pytest.raises(ValueError):
            await checker.check_and_convert(some_address, 1, 2, 10)

    @pytest.mark.asyncio
    async def test_high_eth_and_weth(self):
        checker = BalanceChecker(*setup_mocks([12], [11]))
        eth, weth = await checker.check_and_convert(some_address, 1, 2, 10)
        assert eth == 12
        assert weth == 11

    @pytest.mark.asyncio
    async def test_high_eth(self):
        eth_mock, weth_mock = setup_mocks([12, 2], [0, 10])
        checker = BalanceChecker(eth_mock, weth_mock)

        eth, weth = await checker.check_and_convert(some_address, 1, 2, 10)
        assert eth == 2
        assert weth == 10

        weth_mock.deposit.assert_called_once_with(10)

    @pytest.mark.asyncio
    async def test_high_weth(self):
        eth_mock, weth_mock = setup_mocks([0.5, 1], [10, 9.5])
        checker = BalanceChecker(eth_mock, weth_mock)

        eth, weth = await checker.check_and_convert(some_address, 1, 2, 10)
        assert eth == 1
        assert weth == 9.5

        weth_mock.withdraw.assert_called_once_with(0.5)

    @pytest.mark.asyncio
    async def test_high_eth_transaction_error(self):
        eth_mock, weth_mock = setup_mocks([12], [0])
        weth_mock.deposit.return_value = False

        checker = BalanceChecker(eth_mock, weth_mock)
        with pytest.raises(TransactionError):
            await checker.check_and_convert(some_address, 1, 2, 10)

    @pytest.mark.asyncio
    async def test_high_weth_transaction_error(self):
        eth_mock, weth_mock = setup_mocks([0.5], [10])
        weth_mock.withdraw.return_value = False

        checker = BalanceChecker(eth_mock, weth_mock)
        with pytest.raises(TransactionError):
            await checker.check_and_convert(some_address, 1, 2, 10)
