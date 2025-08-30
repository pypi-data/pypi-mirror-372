"""
Helper functions.
"""
import numpy as np
import pandas as pd

class DefaultValueDict(dict):
    def __missing__(self, key):
        return key

def sequence_or_stream(x, maxlen=None):
    """
    if maxlen is None => returns a stream
    else              => returns sequence of elements of x repeated up to the desired len.

    Attrs:
        - x (iterable)
        - maxlen (int|None)
    """
    x = list(x)
    x_len = len(x)
    if maxlen is None: # stream
        def stream():
            n = 0
            while True:
                yield x[n]
                n = (n + 1) % x_len
        return stream()
    else:
        mod = maxlen % x_len
        return x * (maxlen // x_len) + ([] if mod == 0 else x[:mod])

def merge_dict_list(*dicts, concat_arr_axis=None, concat_df_axis=None, extend_list=True):
    """
    Merge dictionaries with list values.

    Attributes:
        - concat_arr_axis [int|None]: if not None, concatenate arrays in the list values along the specified axis.
        - concat_df_axis [int|None]: if not None, concatenate dataframes in the list values along the specified axis.
        - extend_list [bool]: if True, extend lists.
    """
    keys = set(dicts[0].keys())
    assert all(keys == set(d.keys()) for d in dicts), "All dictionaries must have the same keys"

    def join_lists(ls):
        L = []
        for l in ls:
            L += l
        return L
    merged_dict = {k: join_lists([d[k] for d in dicts]) for k in keys}

    if concat_arr_axis is not None:
        for k, v in merged_dict.items():
            if isinstance(v[0], np.ndarray):
                merged_dict[k] = np.concatenate(v, axis=concat_arr_axis)
    if concat_df_axis is not None:
        for k, v in merged_dict.items():
            if isinstance(v[0], pd.DataFrame):
                merged_dict[k] = pd.concat(v, axis=concat_df_axis)
    if extend_list:
        for k, v in merged_dict.items():
            if isinstance(v[0], list):
                merged_dict[k] = join_lists(v)
    return merged_dict
