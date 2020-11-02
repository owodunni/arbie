"""Unique exceptions for Arbie."""


class DeployContractError(Exception):
    """Raised when a contract can not be deployed."""


class IERC20TokenError(Exception):
    """Raised when a IErc20 token is not Erc20 compliant."""


class PoolValueError(Exception):
    """Raised when a Pool is not initialized properly.

    This can hapen when a pool dosn't have atleast 2 tokens.
    Or when the token weights dosn't add to one.
    """
