import pathlib
from datetime import datetime
from decimal import Decimal
from typing import Any, Final

import pytest

from sqlvault import SQLVault


@pytest.fixture(scope='session')
def vault() -> SQLVault:
    """Instantiate local SQLVault"""
    localdb = pathlib.Path('./tests/test.db')
    if localdb.exists():
        localdb.unlink()
    return SQLVault(f'sqlite:///{localdb.as_posix()}', tables=['T1', 'T2'])


# Test key/value pairs
VALUES: Final = (
    (b'1010', b'binary-value'),
    ('1010', 'string-value'),
    (1010, 1234567890),
    (Decimal('1010'), Decimal('123.4567890')),
    (b'12.34', b'one-more-binary-value'),
    ('12.34', 'one-more-string-value'),
    (12.34, 1234.56789),
    (datetime(1993, 3, 4), datetime(2019, 3, 12)),
)


def test_get_default(vault: SQLVault):
    """Get missing key"""
    with pytest.raises(KeyError):
        vault['T1', 'missing-key']
    missing, default = object(), object()
    assert vault.get('T1', missing, default) == default


@pytest.mark.parametrize(('key', 'value'), VALUES)
def test_set_value(vault: SQLVault, key: Any, value: Any):
    """Set value"""
    vault['T2', key] = value


def test_length(vault: SQLVault):
    """Check length"""
    assert len(vault.interface('T1')) == 0
    assert len(vault.interface('T2')) == len(VALUES)


@pytest.mark.parametrize(('key', 'value'), VALUES)
def test_get_value(vault: SQLVault, key: Any, value: Any):
    """Get value"""
    assert value == vault.get('T2', key, value)


@pytest.mark.parametrize(
    ('key', 'result'),
    (
        (VALUES[0][0], True),
        (object(), False),
    ),
)
def test_has_value(vault: SQLVault, key: Any, result: bool):
    """Set value"""
    assert (('T2', key) in vault) == result


@pytest.mark.parametrize(('key', 'result'), VALUES)
def test_pop_value(vault: SQLVault, key: Any, result: Any):
    """Pop missing key"""
    rvalue = vault.pop('T2', key)
    assert rvalue == result
    with pytest.raises(KeyError):
        vault.pop('T2', key)


def test_del_value(vault: SQLVault):
    """Pop missing key"""
    key, value = object(), object()
    vault['T1', key] = value
    del vault['T1', key]  # noqa: WPS420
    assert ('T1', key) not in vault
