"""B10 TCache - Lock-free PyTorch compilation cache for Baseten."""

from .core import load_compile_cache, save_compile_cache, clear_local_cache
from .utils import CacheError, CacheValidationError
from .space_monitor import CacheOperationInterrupted
from .info import get_cache_info, list_available_caches
from .constants import SaveStatus, LoadStatus

# Version
__version__ = "0.4.0"

__all__ = [
    "CacheError",
    "CacheValidationError",
    "CacheOperationInterrupted",
    "SaveStatus",
    "LoadStatus",
    "load_compile_cache",
    "save_compile_cache",
    "clear_local_cache",
    "get_cache_info",
    "list_available_caches",
]
