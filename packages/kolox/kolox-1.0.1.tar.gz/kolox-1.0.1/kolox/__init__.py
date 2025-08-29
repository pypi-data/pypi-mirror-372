"""
kolox is provided by the kolo package.
There is no need to install it separately, this is just a dummy package to prevent confusion.

Please install and use kolo instead: https://pypi.org/project/kolo/
"""

__version__ = "1.0.1"

import warnings

warnings.warn(
    "kolox is provided by the kolo package. "
    "There is no need to install it separately. "
    "Please use 'kolo' directly: https://pypi.org/project/kolo/",
    UserWarning,
    stacklevel=2
)