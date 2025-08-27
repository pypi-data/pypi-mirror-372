import hashlib
from abc import abstractmethod
from functools import wraps
from typing import (  # noqa: WPS235
    TYPE_CHECKING,
    Any,
    Callable,
    Sequence,
    NotRequired,
    TypedDict,
    Unpack,
    Final,
    final,
)
import sqlalchemy as sa

from sqlvault.memoize import DEFAULT_CACHE_SIZE, memoize
from sqlvault.serialize import DEFAULT_SERIALIZER, Serializer, Serialization

if TYPE_CHECKING:
    from _hashlib import HASH


# ==========================================================================================
@final
class HashFactory[**ArgSpec]:
    """Key hashing factory"""

    __slots__ = ('_hashfunc', '_serializer')

    def __init__(
        self,
        hashfunc: Callable[ArgSpec, 'HASH'],
        serializer: Serializer = DEFAULT_SERIALIZER,
        cache_size: int = DEFAULT_CACHE_SIZE,
    ):
        self._hashfunc = hashfunc
        self._serializer = serializer
        self._serialize.maxsize = cache_size
        self.__call__.maxsize = cache_size

    @memoize(nargs=1).register
    def __call__(self, *args: ArgSpec.args, **kwargs: ArgSpec.kwargs) -> bytes:
        """Calculate hash of the first argument

        If argument is of a non-buffer type, it will be serialized first.
        """
        arguments = list(args)
        try:
            memoryview(arguments[0])  # pyright: ignore[reportArgumentType]
        except TypeError:
            arguments[0] = self._serialize(arguments[0])
        return self._hashfunc(*arguments, **kwargs).digest()  # pyright: ignore[reportCallIssue]

    @memoize(nargs=1).register
    def _serialize(self, key: Any) -> bytes:
        """Serialize non-buffer objects"""
        return self._serializer.dumps(key)


# ==========================================================================================
# Minimal SQL-supported size of unique indexed field
# i.e. SQL Server support 900 bytes for clustered uniques and 1700 for non-clustered
UNIQUE_INDEX_LENGTH: Final = 900
# Default hash factory
DEFAULT_HASHFACTORY: Final = HashFactory(
    hashlib.sha256, DEFAULT_SERIALIZER, DEFAULT_CACHE_SIZE
)
# Secure prefix fot table names
SECURE_PREFIX: Final = '_'


# ==========================================================================================
def check(method):
    """Check if table is present in SQL metadata"""

    @wraps(method)
    def decorator(self, tablename: str, *args, **kwargs):
        schema = self._metadata.schema
        if schema and not tablename.startswith(f'{schema}.'):
            tablename = f'{schema}.{tablename}'
        if tablename not in self._metadata.tables:
            raise KeyError('No such table found: %s', tablename)
        return method(self, tablename, *args, **kwargs)

    return decorator


# ==========================================================================================
@final
class SQLVaultKeywordArguments(TypedDict):
    """Keyword arguments specification"""

    serializer: NotRequired[Serializer]
    hashfactory: NotRequired[HashFactory]
    cache_size: NotRequired[int]
    unique_index_length: NotRequired[int]


class SQLVaultBase:
    """Multi-table SQL key-value base class"""

    __slots__ = ('_engine', '_metadata', '_hashfactory', '_serializer')

    def __init__(
        self,
        connection_string: str,
        tables: Sequence[str],
        schema: str = '',
        **kwargs: Unpack[SQLVaultKeywordArguments],
    ):
        self._engine = sa.create_engine(connection_string)
        self._metadata = sa.MetaData(schema or None)
        for table in tables:
            sa.Table(
                table,
                self._metadata,
                sa.Column(
                    'keyhash',
                    sa.LargeBinary(
                        kwargs.get('unique_index_length', UNIQUE_INDEX_LENGTH)
                    ),
                    primary_key=True,
                    unique=True,
                    nullable=False,
                ),
                # declare variable columns
                *()
                if table.startswith(SECURE_PREFIX)
                else (sa.Column('key', sa.LargeBinary(), nullable=False),),
                # declare permanent columns
                sa.Column('value', sa.LargeBinary(), nullable=False),
            )

        self._metadata.create_all(self._engine)
        self._serializer: Serializer = kwargs.get('serializer', DEFAULT_SERIALIZER)
        self._hashfactory = kwargs.get('hashfactory', DEFAULT_HASHFACTORY)
        self._getvalue.maxsize = kwargs.get('cache_size', DEFAULT_CACHE_SIZE)

    @abstractmethod
    def __contains__(self, key: Any) -> Any:
        raise NotImplementedError()

    @abstractmethod
    def __getitem__(self, key: Any) -> Any:
        raise NotImplementedError()

    @abstractmethod
    def __setitem__(self, key: Any, value: Any) -> None:
        raise NotImplementedError()

    @abstractmethod
    def __delitem__(self, key: Any):  # noqa: WPS603
        raise NotImplementedError()

    def serialize(self, value: Any) -> bytes:
        """Serialize provided value"""
        # object dtype is stored in the first byte
        match value:
            case bytes() | bytearray():
                encoded = bytes((Serialization.BINARY, *value))
            case str():
                encoded = bytes((Serialization.UNICODE, *value.encode()))
            case _:
                encoded = bytes((Serialization.OBJECT, *self._serializer.dumps(value)))
        return encoded

    def deserialize(self, value: bytes) -> Any:
        """Deserialize provided value"""
        # object dtype is stored in the first byte
        match value[0]:
            case Serialization.BINARY:
                return value[1:]
            case Serialization.UNICODE:
                return value[1:].decode()
            case Serialization.OBJECT:
                return self._serializer.loads(value[1:])

    def dispose(self):
        """Clear cache and close SQL connections"""
        self._getvalue.clear_cache()
        self._engine.dispose()

    @memoize(nargs=2).register
    @check
    def _getvalue(self, tablename: str, key: Any) -> Any:
        """Get value from the vault"""
        table = self._metadata.tables[tablename]
        with self._engine.connect() as conn:
            row = conn.execute(
                sa.select(table).where(table.c.keyhash == self._hashfactory(key)),
            ).first()
        if row is None:
            raise KeyError(key)
        return self.deserialize(row.value)

    @check
    def _setvalue(self, tablename: str, key: Any, value: Any):  # noqa: WPS210
        """Set value in the vault"""
        keyhash = self._hashfactory(key)
        table = self._metadata.tables[tablename]
        rowvalue = {
            table.c.keyhash: keyhash,
            table.c.value: self.serialize(value),
        }
        if not table.name.startswith(SECURE_PREFIX):
            rowvalue[table.c.key] = self.serialize(key)
        with self._engine.begin() as conn:
            # check if value exists
            row = conn.execute(
                sa.select(table).where(table.c.keyhash == keyhash),
            ).first()
            # insert/update
            if row is None:
                querypart = sa.insert(table)
            else:
                querypart = sa.update(table).where(table.c.keyhash == keyhash)
            conn.execute(querypart.values(rowvalue))
        self._getvalue.clear_cache(tablename, key)

    @check
    def _delvalue(self, tablename: str, key: Any):
        """Remove value from the vault"""
        keyhash = self._hashfactory(key)
        table = self._metadata.tables[tablename]
        with self._engine.begin() as conn:
            conn.execute(
                sa.delete(table).where(table.c.keyhash == keyhash),
            )
        self._getvalue.clear_cache(tablename, key)
