from importlib.metadata import metadata

try:
    _metadata = metadata("algorave")
    __version__ = _metadata["Version"]
    __author__ = _metadata["Author"]
    __maintainer__ = _metadata["Maintainer"]
except Exception:  # noqa: BLE001
    __version__ = "unknown"
    __author__ = "Ben Elfner"
    __maintainer__ = "Ben Elfner"

from contextlib import suppress

from .augmentations import *
from .core.composition import *
from .core.serialization import *
from .core.transforms_interface import *

with suppress(ImportError):
    from .pytorch import *

