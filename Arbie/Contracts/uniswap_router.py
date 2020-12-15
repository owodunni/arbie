"""Utility functions for interacting with Arbie.sol."""

import logging

from Arbie.Contracts.contract import Contract
from Arbie.Contracts.tokens import GenericToken
from Arbie.Variables import BigNumber, Trade

logger = logging.getLogger()


class UniswapV2Router(Contract):
    name = "UniswapV2Router02"
    protocol = "uniswap"

    def approve(self, weth: GenericToken):
        if weth.allowance(self.get_address()) < BigNumber(10e6):  # noqa: WPS432
            return weth.approve(self.get_address(), BigNumber(10e8))  # noqa: WPS432
        return True

    def check_out_given_in(self, trade: Trade):
        path_address = list(map(lambda t: t.address, trade.path))
        amount_out = self.contract.functions.getAmountsOut(
            BigNumber(trade.amount_in).value, path_address
        ).call()
        return BigNumber.from_value(amount_out[-1]).to_number()

    def swap(self, trade):
        gas = self._estimate_gas_swap(trade)
        transaction = self._swap_transaction(trade)
        return self._transact_status(transaction, gas=gas)

    def _swap_transaction(self, trade):
        path = list(map(lambda t: t.address, trade.path))
        return self.contract.functions.swapExactTokensForTokens(
            BigNumber(trade.amount_in).value,
            BigNumber(trade.amount_in).value,
            path,
            self._get_account(),
            # Require trades to be executed in 120 seconds
            self.w3.eth.getBlock("latest").timestamp + 120,  # noqa: WPS432
        )

    def _estimate_gas_swap(self, trade):
        transaction = self._swap_transaction(trade)
        # Lets use a bit more gas then required, since
        # some tokens like $VLO actually suck gas
        # out of the transaction
        return int(self._estimate_gas(transaction) * 1.05) + 1  # noqa: WPS432
