"""Main init."""

from Arbie.exception import (  # noqa: F401
    DeployContractError,
    IERC20TokenError,
    PoolValueError,
    StateError,
    TransactionError,
)
from Arbie.settings_parser import SettingsParser  # noqa: F401

__version__ = "0.8.2"  # noqa: WPS410
__version_info__ = tuple(
    int(i) for i in __version__.split(".") if i.isdigit()
)  # noqa: WPS221
