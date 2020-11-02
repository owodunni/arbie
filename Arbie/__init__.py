"""Main init."""

from Arbie.exception import DeployContractError, IERC20TokenError  # noqa: F401

__version__ = "0.3.0"  # noqa: WPS410
__version_info__ = tuple(
    int(i) for i in __version__.split(".") if i.isdigit()
)  # noqa: WPS221
