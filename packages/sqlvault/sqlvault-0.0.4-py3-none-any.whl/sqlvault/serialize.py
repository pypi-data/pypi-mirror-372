import enum
import pickle
from typing import Any, Callable, Concatenate, Final, Protocol, final


@final
class Serialization(enum.IntEnum):
    """Data serialization type"""

    OBJECT = -1
    """Object is serialized with user-defined serializer"""
    BINARY = 0
    """Object is not (already) serialized"""
    UNICODE = enum.auto()
    """Object is serialized as UTF-8 string"""


@final
class Serializer[OriginalType: Any](Protocol):
    """Serializer object protocol"""

    dumps: Final[Callable[Concatenate[OriginalType, ...], bytes]]  # noqa: WPS234
    loads: Final[Callable[Concatenate[bytes, ...], OriginalType]]  # noqa: WPS234


# Default serializer
DEFAULT_SERIALIZER: Final[Serializer] = pickle
