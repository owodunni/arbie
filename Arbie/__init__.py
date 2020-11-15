"""Main init."""

from Arbie.exception import (  # noqa: F401
    DeployContractError,
    IERC20TokenError,
    PoolValueError,
)

from Arbie.settings_parser import SettingsParser

__version__ = "0.3.2"  # noqa: WPS410
__version_info__ = tuple(
    int(i) for i in __version__.split(".") if i.isdigit()
)  # noqa: WPS221
