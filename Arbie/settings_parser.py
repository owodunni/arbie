"""settings parser can be used for parsing input yaml."""


class SettingsParser(object):
    """
    It is configured with a yaml file.
    The yaml file can have the following properties.
    
    version: "1.0"
    store:
        redis: host_name:port

    variables:
        w3:
            type: Web3
            address: url:port
        weth:
            type: Token
            address: "0xABC"
        uniswap_factory:
            type: UniswapFactory
            address: "0xABC"
        balancer_factory:
            type: BalancerFactory
            address: "0xABC"

    actiontree:
        event:
            time: once, continous, 6000
            block: block_divider
            store: key
        actions:
            PathFinder:
                input:
                    weth: my_weth_token
                output:
                    trades: all_trades

    """

    def __init__(self, config):
        self.config = config
