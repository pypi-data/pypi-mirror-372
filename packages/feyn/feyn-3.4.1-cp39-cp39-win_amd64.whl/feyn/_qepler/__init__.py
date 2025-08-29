from pandas import DataFrame
import pandas.util
from functools import wraps
from numpy import ndarray

def pandas_lru_cache(func):
    def _compute_hash_of_dataframe(data: DataFrame):
        hashes = pandas.util.hash_pandas_object(data)
        return hash(tuple(hashes)),

    def _compute_hash(arg):
        if isinstance(arg, DataFrame):
            return _compute_hash_of_dataframe(arg)
        if isinstance(arg, list):
            return tuple(arg)
        if isinstance(arg, ndarray):
            return tuple(arg)

        return arg,

    def _make_key(args, kwargs):
        key_set = ()
        for a in args:
            key_set += _compute_hash(a)

        for k in kwargs.items():
            key_set += _compute_hash(k)

        return hash(key_set)

    func._pandas_cache = {}

    @wraps(func)
    def wrapper(*args, **kwargs):
        key = _make_key(args, kwargs)
        if key in func._pandas_cache:
            return func._pandas_cache[key]

        result = func(*args, **kwargs)
        func._pandas_cache = {
            key: result
        }
        return result
    return wrapper
