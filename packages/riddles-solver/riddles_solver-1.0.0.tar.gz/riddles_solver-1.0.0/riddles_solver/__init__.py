"""
Library for solving riddles using repixify.com
"""

from .client import Client
from .async_client import AsyncClient
from .key_extractor import get_key

__version__ = "1.0.0"
__all__ = ["Client", "AsyncClient", "get_key"]
