"""Main init."""

from Arbie.exception import DeployContractError  # noqa: F401

__version__ = "0.2.0"  # noqa: WPS410
__version_info__ = tuple(
    int(i) for i in __version__.split(".") if i.isdigit()
)  # noqa: WPS221
