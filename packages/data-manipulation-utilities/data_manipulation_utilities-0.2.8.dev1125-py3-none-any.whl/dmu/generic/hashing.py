'''
Module with functions needed to provide hashes
'''

import os
import json
import hashlib
from typing import Any

import pandas as pnd
from dmu.logging.log_store import LogStore

log=LogStore.add_logger('dmu:generic.hashing')
# ------------------------------------
def _object_to_string(obj : Any) -> str:
    def default_encoder(x):
        raise TypeError(f"Unserializable type: {type(x)}")

    return json.dumps(obj, sort_keys=True, default=default_encoder)
# ------------------------------------
def _dataframe_to_hash(df : pnd.DataFrame) -> str:
    sr_hash = pnd.util.hash_pandas_object(df, index=True)
    values  = sr_hash.values
    hsh     = hashlib.sha256(values)
    hsh     = hsh.hexdigest()

    return hsh
# ------------------------------------
def hash_object(obj : Any) -> str:
    '''
    Function taking a python object and returning
    a string representing the hash
    '''

    if isinstance(obj, pnd.DataFrame):
        value = _dataframe_to_hash(df=obj)
        value = value[:10]

        return value

    string     = _object_to_string(obj=obj)
    string_bin = string.encode('utf-8')
    hsh        = hashlib.sha256(string_bin)
    value      = hsh.hexdigest()
    value      = value[:10]

    return value
# ------------------------------------
def hash_file(path : str) -> str:
    '''
    Parameters
    ----------------
    path: Path to file whose content has to be hashed

    Returns
    ----------------
    A string representing the hash
    '''
    if not os.path.isfile(path):
        raise FileNotFoundError(f'Cannot find: {path}')

    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)

    value = h.hexdigest()

    return value[:10]
# ------------------------------------
