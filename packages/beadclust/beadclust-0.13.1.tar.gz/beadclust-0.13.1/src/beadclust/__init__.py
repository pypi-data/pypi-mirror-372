import logging
from importlib import metadata
from . import cli
from . import cluster
from . import db
from . import filter
from . import filter_params
from . import io
from . import plot


try:
    from importlib import metadata
    __version__ = metadata.version("beadclust")
    del metadata
except Exception:
    __version__ = "unknown"


logging.getLogger(__name__).addHandler(logging.NullHandler())
