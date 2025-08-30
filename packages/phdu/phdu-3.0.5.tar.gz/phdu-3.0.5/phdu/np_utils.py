import numpy as np
from numpy.lib.stride_tricks import as_strided

def rolling_view(x, window):
    """
    Returns rolling view (no extra memory needed) over first axis of x.

    Output shape: ``(x.shape[0]-window+1, window, *x.shape[1:])``
    """
    stride = x.strides[0]
    shape = [x.shape[0] - window + 1, window]
    strides = [stride, stride]
    if x.ndim > 1:
        shape += [*x.shape[1:]]
        strides += [*x.strides[1:]]
    return as_strided(x, shape=shape, strides=strides)

def idxs_condition(x, condition):
    """
    Returns idx where condition is first met. Ignore rest until fails and mets the condition again.

    Attributes:
        x:          np.ndarray
        condition:  f: x -> bool array
    """
    verify_condition = condition(x)
    changes = np.where(np.abs(np.diff((verify_condition).astype(int))) == 1)[0]
    if changes.size > 0:
        changes += 1
        if verify_condition[changes[0]]:
            return changes[::2]
        else:
            return changes[1::2]
    else:
        return changes

def numpy_fill(arr):
    '''Fills nan with previous not-NaN values'''
    mask = np.isnan(arr)
    if mask.all():
        return np.nan
    else:
        idx = np.where(~mask, np.arange(mask.shape[0]), 0)
        np.maximum.accumulate(idx,axis=0, out=idx)
        out = arr[np.arange(idx.shape[0])[idx]]
        if mask[0] and idx[0] == 0:
            out[:(idx == 0).sum()] = arr[idx[idx > 0][0]]
        return out

def longest_sequence(x):
    """
    Returns the longest sequence of True or False in a boolean array.
    """
    changes = np.diff(x)
    changes_idx = np.hstack((0, np.where(changes != 0)[0] + 1))
    lengths = np.diff(changes_idx)
    idx_max_length = lengths.argmax()
    start, end = changes_idx[idx_max_length], changes_idx[idx_max_length+1]
    x_pruned = x[start:end]
    assert x_pruned.shape[0] == lengths.max()
    assert np.all(x_pruned) or not np.any(x_pruned)
    # create a mask
    mask = np.zeros(x.shape[0], dtype=bool)
    mask[start:end] = True
    return mask

def _percentile_boot_paired(X, Y, func, alpha=0.05, R=int(1e4), seed=0, names=None):
    """"
    Bootstrap a statistic that takes X, Y as input.
    NOTE: If the stat can be written in numpy, a modified numba version is recommended.
    """
    np.random.seed(seed)
    N = X.size
    data_paired = np.vstack((X, Y)).T
    idxs_resampling = np.random.randint(low=0, high=N, size=R*N)
    data_resampled = data_paired[idxs_resampling].reshape(R, N, 2)

    stat = func(X, Y)
    if hasattr(stat, "__len__"):
        boot_sample = np.empty((R, len(stat)))
    else:
        boot_sample = np.empty((R))
    for i, r in enumerate(tqdm(data_resampled)):
        boot_sample[i] = func(*r.T)
    alpha_ptg = alpha*100
    results = pd.Series(dict(stat=names,
                             sample_stat=stat,
                             lower_bound=np.percentile(boot_sample, alpha_ptg, axis=0),
                             upper_bound=np.percentile(boot_sample, 100-alpha_ptg, axis=0),
                             CI=np.percentile(boot_sample, [alpha_ptg/2, 100 - alpha_ptg/2], axis=0),
                            ))
    return results
