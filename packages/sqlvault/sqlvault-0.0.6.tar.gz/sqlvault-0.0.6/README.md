# Simple SQL-based key/value store

## Install
```sh
pip install sqlvault
```

## How to use

```python

from sqlvault import SQLVault

vault = SQLVault('sqlite:///local.db', tables=['keysA', 'keysB'])

keys_a_vault = vault.interface('keysA')
keys_b_vault = vault.interface('keysB')

keys_a_vault['k1'] = 'av1'
keys_b_vault['k1'] = 'bv1'

keys_a_vault['k1']
>>> 'av1'

keys_b_vault['k1']
>>> 'bv1'
```

## Limitations

As you can see, the interface is very similar to a dictionary, but there is no way to
- get all the stored keys (since the keys themselves are not stored - only their hashes)
- get all stored key/value pairs (in view of the previous point)
