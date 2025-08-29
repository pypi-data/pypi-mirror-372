import logging
from logging import NullHandler

logging.getLogger(__name__).addHandler(NullHandler())

try:
    from ._version import __version__
except ImportError:
    __version__ == "0.0.0"  # noqa: B015
