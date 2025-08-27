from __future__ import annotations

from typing import Any, Final, Unpack, overload
import sqlalchemy as sa
from sqlvault.base import SQLVaultBase, SQLVaultKeywordArguments, check


# Placeholder for empty default
DEFAULT_EMPTY: Final = object()


# ==========================================================================================
class SQLVault(SQLVaultBase):
    """Multi-table SQL key-value vault

    :param connection_string:
        SQLAlchemy connection string.
    :type connection_string: str

    :param tables:
        Collection of table names without schema or quotation; missing tables will be created.
        If the table name starts with an underscore `_`, it will be handled as _secure_ table without storing the key itself.
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

    def __contains__(self, position: tuple[str, Any]) -> bool:
        try:
            self._getvalue(*position)
        except KeyError:
            return False
        else:
            return True

    def __getitem__(self, position: tuple[str, Any]) -> Any:
        return self._getvalue(*position)

    def __setitem__(self, position: tuple[str, Any], value: Any) -> None:
        self._setvalue(*position, value)

    def __delitem__(self, position: tuple[str, Any]) -> None:  # noqa: WPS603
        self._delvalue(*position)

    @overload
    def get(self, tablename: str, key: Any) -> Any: ...
    @overload
    def get(self, tablename: str, key: Any, default: Any) -> Any: ...
    def get(self, tablename: str, key: Any, default: Any = DEFAULT_EMPTY) -> Any:
        """Get value from the vault"""
        try:
            value = self._getvalue(tablename, key)
        except KeyError:
            if default is DEFAULT_EMPTY:
                raise
            return default
        else:
            return value

    @overload
    def pop(self, tablename: str, key: Any) -> Any: ...
    @overload
    def pop(self, tablename: str, key: Any, default: Any) -> Any: ...
    def pop(self, tablename: str, key: Any, default: Any = DEFAULT_EMPTY) -> Any:
        """Pop value from the vault"""
        try:
            value = self._getvalue(tablename, key)
        except KeyError:
            if default is DEFAULT_EMPTY:
                raise
            return default
        else:
            self.__delitem__((tablename, key))
            return value

    @check
    def interface[KeyType, ValueType](
        self,
        tablename: str,
        keytype: type[KeyType] = object,
        valuetype: type[ValueType] = object,
    ) -> SQLSingleVault[KeyType, ValueType]:
        """Get single-table vault interface"""
        return SQLSingleVault.bind(tablename, self)


# ==========================================================================================
class SQLSingleVault[KeyType, ValueType](SQLVaultBase):
    """Simplified interface for sinle-table SQL key-value vault

    :param connection_string:
        SQLAlchemy connection string.
    :type connection_string: str

    :param table:
        Table name without schema or quotation; will be created if missing.
        If the table name starts with an underscore `_`, it will be handled as _secure_ table without storing the key itself.
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

    __slots__ = ('_tablename',)

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
        self._tablename = table

    def __contains__(self, key: KeyType) -> bool:
        try:
            self._getvalue(self._tablename, key)
        except KeyError:
            return False
        else:
            return True

    def __getitem__(self, key: KeyType) -> ValueType:
        return self._getvalue(self._tablename, key)

    def __setitem__(self, key: KeyType, value: ValueType) -> None:
        self._setvalue(self._tablename, key, value)

    def __delitem__(self, key: KeyType) -> None:  # noqa: WPS603
        self._delvalue(self._tablename, key)

    def __len__(self) -> int:
        """Get count of stored values"""
        table = self._metadata.tables[self._tablename]
        with self._engine.connect() as conn:
            row = conn.execute(
                sa.select(sa.func.count().label('length')).select_from(table)
            ).first()
        if row is None:
            raise ValueError('Cannot receive length from database')
        return row.length

    @overload
    def get(self, key: KeyType) -> ValueType: ...
    @overload
    def get(self, key: KeyType, default: ValueType) -> ValueType: ...
    def get(self, key: KeyType, default: ValueType = DEFAULT_EMPTY) -> ValueType:  # pyright: ignore[reportInconsistentOverload]
        """Get value from the vault"""
        try:
            value = self._getvalue(self._tablename, key)
        except KeyError:
            if default is DEFAULT_EMPTY:
                raise
            return default
        else:
            return value

    @overload
    def pop(self, key: KeyType) -> ValueType: ...
    @overload
    def pop(self, key: KeyType, default: ValueType) -> ValueType: ...
    def pop(self, key: KeyType, default: ValueType = DEFAULT_EMPTY) -> ValueType:  # pyright: ignore[reportInconsistentOverload]
        """Pop value from the vault"""
        try:
            value = self._getvalue(self._tablename, key)
        except KeyError:
            if default is DEFAULT_EMPTY:
                raise
            return default
        else:
            self._delvalue(self._tablename, key)
            return value

    @classmethod
    def bind(cls, tablename: str, parent: SQLVault) -> SQLSingleVault:
        """Bind as single-table interface"""
        interface = cls.__new__(cls)
        for slot in parent.__slots__:
            setattr(interface, slot, getattr(parent, slot))
        schema = parent._metadata.schema
        if schema and not tablename.startswith(f'{schema}.'):
            tablename = f'{schema}.{tablename}'
        interface._tablename = tablename
        return interface
