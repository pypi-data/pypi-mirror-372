import enum
import pickle
from typing import Any, Callable, Concatenate, Final, Protocol, final


@final
class Serialization(enum.IntEnum):
    """Data serialization type"""

    BINARY = 1
    """Object does not require serialization"""
    UNICODE = 2
    """Object is serialized as UTF-8 string"""
    OBJECT = 255
    """Object is serialized with user-defined serializer"""


@final
class Serializer[OriginalType: Any](Protocol):
    """Serializer object protocol"""

    dumps: Final[Callable[Concatenate[OriginalType, ...], bytes]]  # noqa: WPS234
    loads: Final[Callable[Concatenate[bytes, ...], OriginalType]]  # noqa: WPS234


# Default serializer
DEFAULT_SERIALIZER: Final[Serializer] = pickle
