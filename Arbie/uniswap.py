"""Utility functions for interacting with Uniswap."""
import json
import time

from Arbie.data.file_reader import read_resource


class Uniswap(object):
    """Utility functions for trading tokens from Uniswap."""

    def __init__(self, w3, address, network="kovan", private_key=None):  # noqa: WPS211
        self.w3 = w3
        self.address = address
        self.private_key = private_key
        self.exchange_abi = read_resource(
            "exchange_abi.json", "contracts.uniswap",
        )
        self.factory_abi = read_resource(
            "factory_abi.json", "contracts.uniswap",
        )
        networks = json.loads(read_resource("contract_addresses.json"))
        self.tokens = networks[network]

    def token_address(self, token):
        factory_address = self.tokens["factory"]
        token_address = self.tokens[token]["token"]
        factory_contract = self.w3.eth.contract(
            address=factory_address, abi=self.factory_abi,
        )
        return factory_contract.functions.getExchange(token_address).call()

    def buy_token(self, token, amount):  # noqa: WPS210
        exchange_address = self.tokens[token]["exchange"]

        exchange_contract = self.w3.eth.contract(
            address=exchange_address, abi=self.exchange_abi,
        )
        # Send 0.1 eth
        eth_sold = self.w3.toHex(5 * 10 ** 16)  # noqa: WPS432

        tx_params = self._get_tx_params(eth_sold, 150000)  # noqa: WPS432

        transaction = exchange_contract.functions.ethToTokenSwapInput(
            4,
            int(time.time() + 300),  # noqa: WPS432
        )

        res = self._build_and_send_tx(transaction, tx_params)
        return self.w3.toHex(res)

    def _build_and_send_tx(self, function, tx_params):
        """Build and send a transaction."""
        transaction = function.buildTransaction(tx_params)
        if self.private_key is None:
            return self.w3.eth.sendTransaction(transaction)

        signed_txn = self.w3.eth.account.signTransaction(
            transaction, private_key=self.private_key,
        )
        return self.w3.eth.sendRawTransaction(signed_txn.rawTransaction)

    def _get_tx_params(self, amount=0, gas=150000):
        """Get generic transaction parameters."""
        return {
            "from": self.address,
            "value": amount,
            "gas": gas,
            "nonce": self.w3.eth.getTransactionCount(self.address),
        }
