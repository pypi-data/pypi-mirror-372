from __future__ import annotations

from collections import OrderedDict
from threading import RLock
from typing import Any, Callable, Concatenate, Final, Protocol, Self

from sqlvault.serialize import DEFAULT_SERIALIZER, Serializer

# Default cache size for memoized methods
DEFAULT_CACHE_SIZE: Final = 32


class Picklable(Protocol):
    """Picklable object"""

    def __reduce__(self) -> str | tuple[Any, ...]: ...  # noqa: WPS603


class Memoized[Instance, **ArgSpec, ReturnType](Protocol):
    """Memoized property"""

    def __call__(self, *args: ArgSpec.args, **kwargs: ArgSpec.kwargs) -> ReturnType: ...
    def clear_cache(self, *args: Picklable): ...


class memoize[Instance, **ArgSpec, ReturnType]:
    """Least-recently-used cache decorator

    Must be the top-level decorator for using `clear_cache()` !

    Caching is performed using the first `nargs` arguments.

    If `maxsize` is less or equal to zero, the LRU feature is disabled and the cache
    can grow without bound.

    Arguments to the cached function may be not hashable, but must be picklable.
    """

    __slots__ = (
        'nargs',
        'maxsize',
        '_serializer',
        '_instance',
        '_cache',
        '_lock',
        '__wrapped__',
    )

    def __init__(
        self,
        *,
        nargs: int,
        maxsize: int = 0,
        serializer: Serializer = DEFAULT_SERIALIZER,
    ):
        self.nargs: Final = nargs
        self.maxsize = maxsize
        self._serializer = serializer
        self._instance = None
        self._cache = OrderedDict[bytes, Any]()
        self._lock = RLock()

    def __call__(self, *args: ArgSpec.args, **kwargs: ArgSpec.kwargs) -> ReturnType:
        """Cache wrapper"""
        key = self._serializer.dumps(args[: self.nargs])
        if key in self._cache:
            # move up the key if cache is size-limited
            if self.maxsize > 0:
                with self._lock:
                    self._cache.move_to_end(key)
            return self._cache[key]  # noqa: WPS529
        # calc value
        value = self.__wrapped__(self._instance, *args, **kwargs)  # type: ignore[reportCallIssue]  # noqa: WPS110
        with self._lock:
            self._cache[key] = value
            # pop last item
            if len(self._cache) > self.maxsize:
                self._cache.popitem(last=False)
        return value  # type: ignore[reportReturnType]

    def __get__(
        self,
        instance: Instance,
        owner: type[Instance] | None = None,
    ) -> Self:
        """Set instance and return cache wrapper"""
        if self._instance is None:
            self._instance = instance
        return self

    def register[_Instance, **_ArgSpec, _ReturnType](
        self, method: Callable[Concatenate[_Instance, _ArgSpec], _ReturnType]
    ) -> memoize[_Instance, _ArgSpec, _ReturnType]:
        """Set method for memoizing"""
        self.__wrapped__ = method
        return self  # type: ignore[reportReturnType]

    def clear_cache(
        self, *args: Picklable
    ):  # NOTE how to forward N first argtypes here?
        """Remove cache for args or the whole cache if no args provided"""
        assert not args or len(args) == self.nargs, (
            'args count must be equal to nargs or zero'
        )
        if len(args) == 0:
            with self._lock:
                self._cache.clear()
        elif len(args) == self.nargs:
            key = self._serializer.dumps(args[: self.nargs + 1])
            with self._lock:
                self._cache.pop(key, None)
        else:
            raise ValueError(
                'The number of arguments provided does not match the parameter nargs'
            )
