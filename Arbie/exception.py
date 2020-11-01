"""Unique exceptions for Arbie."""


class DeployContractError(Exception):
    """Raised when a contract can not be deployed."""


class IERC20TokenError(Exception):
    """Raised when a IErc20 token is not Erc20 compliant."""
