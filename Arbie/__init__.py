from .uniswap import Uniswap
from .uniswap import read_resource

__all__ = ['Uniswap', 'read_resource']

__version__ = "0.1.0"
__version_info__ = tuple(
    int(i) for i in __version__.split(".") if i.isdigit()
)
