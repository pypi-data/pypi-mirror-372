from __future__ import annotations

import hashlib
from functools import wraps
from typing import (  # noqa: WPS235
    TYPE_CHECKING,
    Any,
    Callable,
    Final,
    NotRequired,
    Sequence,
    TypedDict,
    Unpack,
    final,
    overload,
)

import sqlalchemy as sa

from sqlvault.memoize import DEFAULT_CACHE_SIZE, memoize
from sqlvault.serialize import DEFAULT_SERIALIZER, Serialization, Serializer

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


# Minimal SQL-supported size of unique indexed field
# i.e. SQL Server support 900 bytes for clustered uniques and 1700 for non-clustered
UNIQUE_INDEX_LENGTH: Final = 900
# Default hash factory
DEFAULT_HASHFACTORY: Final = HashFactory(
    hashlib.sha256, DEFAULT_SERIALIZER, DEFAULT_CACHE_SIZE
)
# Placeholder for empty default
DEFAULT_EMPTY: Final = object()


# ==========================================================================================
@final
class SQLVaultKeywordArguments(TypedDict):
    """Keyword arguments specification"""

    serializer: NotRequired[Serializer]
    hashfactory: NotRequired[HashFactory]
    cache_size: NotRequired[int]
    unique_index_length: NotRequired[int]


class SQLVault:
    """Multi-table SQL key-value vault

    :param connection_string:
        SQLAlchemy connection string.
    :type connection_string: str

    :param tables:
        Collection of table names without schema or quotation; missing tables will be created.
    :type tables: Sequence[str]

    :param schema:
        SQL schema name (if supported and required), must exist in the database.
        Use database default if not provided.
    :type schema: str

    :param serializer:
        User-defined serializer for values.
    :type serializer: Serializer

    :param cache_size:
        Maximal vault cache size.
    :type cache_size:  int

    :param hashfunc:
        Hash function for HashFactory
    :type hashfunc: HashFunction

    :param hashfactory_cache_size:
        maximal HashFactory cache size
    :type hashfactory_cache_size: int

    :param unique_index_length:
        maximal size of key field
    :type unique_index_length: int
    """

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
                sa.Column('value', sa.LargeBinary(), nullable=False),
                sa.Column('dtype', sa.Integer, nullable=False),
            )
        self._metadata.create_all(self._engine)
        self._serializer: Serializer = kwargs.get('serializer', DEFAULT_SERIALIZER)
        self._hashfactory = kwargs.get('hashfactory', DEFAULT_HASHFACTORY)
        self._getvalue.maxsize = kwargs.get('cache_size', DEFAULT_CACHE_SIZE)

    @check
    def interface[KeyType, ValueType](
        self,
        tablename: str,
        keytype: type[KeyType] = object,
        valuetype: type[ValueType] = object,
    ) -> SQLSingleVault[KeyType, ValueType]:
        """Get single-table vault interface"""
        return SQLSingleVault.bind(tablename, self)

    def serialize(self, value: Any) -> tuple[bytes, Serialization]:
        """Serialize provided value"""
        match value:
            case bytes() | bytearray():
                return value, Serialization.BINARY
            case str():
                return value.encode(), Serialization.UNICODE
            case _:
                return self._serializer.dumps(value), Serialization.OBJECT

    def deserialize(self, value: bytes, dtype: int) -> Any:
        """Seserialize provided value"""
        match dtype:
            case Serialization.BINARY:
                return value
            case Serialization.UNICODE:
                return value.decode()
            case Serialization.OBJECT:
                return self._serializer.loads(value)

    @check
    def length(self, tablename: str) -> int:
        """Get count of stored values"""
        table = self._metadata.tables[tablename]
        with self._engine.connect() as conn:
            rowset = conn.execute(
                sa.select(sa.func.count().label('qty')).select_from(table)
            ).first()
        if rowset is None:
            raise ValueError('rowset is None')
        return rowset.qty

    @overload
    def getvalue(self, tablename: str, key: Any) -> Any: ...
    @overload
    def getvalue(self, tablename: str, key: Any, default: Any) -> Any: ...
    def getvalue(self, tablename: str, key: Any, default: Any = DEFAULT_EMPTY) -> Any:
        """Get value from the vault"""
        try:
            value = self._getvalue(tablename, key)
        except KeyError:
            if default is DEFAULT_EMPTY:
                raise
            return default
        else:
            return value

    @check
    def setvalue(self, tablename: str, key: Any, value: Any):  # noqa: WPS210
        """Set value in the vault"""
        keyhash = self._hashfactory(key)
        table = self._metadata.tables[tablename]
        rowvalue = dict(
            zip(
                (table.c.keyhash, table.c.value, table.c.dtype),
                (keyhash, *self.serialize(value)),
            )
        )
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
    def delvalue(self, tablename: str, key: Any):
        """Remove value from the vault"""
        keyhash = self._hashfactory(key)
        table = self._metadata.tables[tablename]
        with self._engine.begin() as conn:
            conn.execute(
                sa.delete(table).where(table.c.keyhash == keyhash),
            )
        self._getvalue.clear_cache(tablename, key)

    @overload
    def popvalue(self, tablename: str, key: Any) -> Any: ...
    @overload
    def popvalue(self, tablename: str, key: Any, default: Any) -> Any: ...
    def popvalue(self, tablename: str, key: Any, default: Any = DEFAULT_EMPTY) -> Any:
        """Pop value from the vault"""
        try:
            value = self._getvalue(tablename, key)
        except KeyError:
            if default is DEFAULT_EMPTY:
                raise
            return default
        else:
            self.delvalue(tablename, key)
            return value

    @check
    def hasvalue(self, tablename: str, key: Any) -> bool:
        """Check if key exists in the vault"""
        try:
            self._getvalue(tablename, key)
        except KeyError:
            return False
        else:
            return True

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
        return self.deserialize(row.value, row.dtype)


class SQLSingleVault[KeyType, ValueType](SQLVault):
    """Simplified interface for sinle-table SQL key-value vault"""

    __slots__ = ('tablename',)

    def __init__(
        self,
        connection_string: str,
        table: str,
        schema: str = '',
        **kwargs: Unpack[SQLVaultKeywordArguments],
    ):
        super().__init__(connection_string, [table], schema, **kwargs)
        if schema and not table.startswith(f'{schema}.'):
            table = f'{schema}.{table}'
        self.tablename = table

    def __len__(self) -> int:
        """Get count of stored values"""
        return self.length(self.tablename)

    @classmethod
    def bind(cls, tablename: str, parent: SQLVault) -> SQLSingleVault:
        """Bind as single-table interface"""
        interface = cls.__new__(cls)
        for slot in parent.__slots__:
            setattr(interface, slot, getattr(parent, slot))
        schema = parent._metadata.schema
        if schema and not tablename.startswith(f'{schema}.'):
            tablename = f'{schema}.{tablename}'
        interface.tablename = tablename
        return interface

    @overload
    def get(self, key: KeyType) -> ValueType: ...
    @overload
    def get(self, key: KeyType, default: ValueType) -> ValueType: ...
    def get(self, key: KeyType, default: ValueType = DEFAULT_EMPTY) -> ValueType:  # pyright: ignore[reportInconsistentOverload]
        """Get value from the vault"""
        return self.getvalue(self.tablename, key, default)

    def set(self, key: KeyType, value: ValueType):
        """Set value in the vault"""
        return self.setvalue(self.tablename, key, value)

    def delete(self, key: KeyType):
        """Remove value from the vault"""
        return self.delvalue(self.tablename, key)

    @overload
    def pop(self, key: KeyType) -> ValueType: ...
    @overload
    def pop(self, key: KeyType, default: ValueType) -> ValueType: ...
    def pop(self, key: KeyType, default: ValueType = DEFAULT_EMPTY) -> ValueType:  # pyright: ignore[reportInconsistentOverload]
        """Pop value from the vault"""
        return self.popvalue(self.tablename, key, default)

    def has(self, key: KeyType) -> bool:
        """Check if key exists in the vault"""
        return self.hasvalue(self.tablename, key)

    __contains__ = has
    __getitem__ = get
    __setitem__ = set
    __delitem__ = delete
