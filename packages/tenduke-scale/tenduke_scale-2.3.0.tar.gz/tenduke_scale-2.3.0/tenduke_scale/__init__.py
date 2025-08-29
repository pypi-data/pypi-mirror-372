"""10Duke Scale SDK for Python.

Provides 10Duke Scale API client.
"""

import importlib.metadata as importlib_metadata

from .describe_license_options import DescribeLicenseOptions
from .paging import PagingOptions

__version__ = importlib_metadata.version(__name__)


__all__ = [
    "DescribeLicenseOptions",
    "PagingOptions",
]
