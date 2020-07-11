from .data.fileReader import read_resource
import json
import time


class Uniswap:

    def __init__(self, w3, address, network='kovan', private_key=None):
        self.w3 = w3
        self.address = address
        self.private_key = private_key
        self.exchange_abi = read_resource(
            'exchange_abi.json', 'contracts.uniswap')
        self.factory_abi = read_resource(
            'factory_abi.json', 'contracts.uniswap')
        networks = json.loads(read_resource('contract_addresses.json'))
        self.tokens = networks[network]

    def token_address(self, token):
        factory_address = self.tokens['factory']
        token_address = self.tokens[token]['token']
        factory_contract = self.w3.eth.contract(
            address=factory_address, abi=self.factory_abi)
        return factory_contract.functions.getExchange(token_address).call()

    def buy_token(self, token, amount):
        exchange_address = self.tokens[token]['exchange']

        exchange_contract = self.w3.eth.contract(
            address=exchange_address, abi=self.exchange_abi)

        eth_sold = self.w3.toHex(5 * 10 ** 16)  # 0.1 ETH

        tx_params = self._get_tx_params(eth_sold, 150000)

        transaction = exchange_contract.functions.ethToTokenSwapInput(
            4,
            int(time.time() + 300))

        res = self._build_and_send_tx(transaction, tx_params)
        return self.w3.toHex(res)

    def _build_and_send_tx(self, function, tx_params):
        """Build and send a transaction."""
        transaction = function.buildTransaction(tx_params)
        if self.private_key is None:
            return self.w3.eth.sendTransaction(transaction)
        else:
            signed_txn = self.w3.eth.account.signTransaction(
                transaction, private_key=self.private_key)
            return self.w3.eth.sendRawTransaction(signed_txn.rawTransaction)

    def _get_tx_params(self, value=0, gas=150000):
        """Get generic transaction parameters."""
        return {
            "from": self.address,
            "value": value,
            "gas": gas,
            "nonce": self.w3.eth.getTransactionCount(self.address),
        }

    def mint_dai(self, amount):
        address = self.tokens['dai_test']
        abi = read_resource(
            'dai_test_abi.json', 'contracts.tokensets')
        contract = self.w3.eth.contract(
            address=address, abi=abi)
        return self.mint(contract, amount)

    def mint_usdc(self, amount):
        address = self.tokens['tusd_test']
        abi = read_resource(
            'tusd_test_abi.json', 'contracts.tokensets')
        contract = self.w3.eth.contract(
            address=address, abi=abi)
        return self.mint(contract, amount)

    def mint(self, contract, amount):
        transaction = contract.functions.greedIsGood(
            self.address, amount)
        tx_params = self._get_tx_params()
        res = self._build_and_send_tx(transaction, tx_params)
        return self.w3.toHex(res)
