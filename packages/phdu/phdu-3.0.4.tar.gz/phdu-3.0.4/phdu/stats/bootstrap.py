"""
Numba version of bias-corrected and accelerated (BCa) bootstrap.
                 studentized.
                 studentized (variance-stabilized).
                 percentile.
"""
import numpy as np
import pandas as pd
from numba import njit, boolean
from numba.core.registry import CPUDispatcher
from itertools import product
from collections import defaultdict
from collections.abc import Iterable
import warnings
try:
    from scipy.special import ndtri, ndtr
except:
    warnings.warn('scipy not available. Numba BCa bootstrap will not work.', RuntimeWarning)
try:
    from statsmodels.nonparametric.smoothers_lowess import lowess
    from scipy.interpolate import interp1d # for interpolation of new data points
except:
    warnings.warn('scipy or statsmodels not available. Studentized bootstrap will not work.', RuntimeWarning)
try:
    shell = get_ipython().__class__.__name__
    if shell == 'ZMQInteractiveShell': # script being run in Jupyter notebook
        from tqdm.notebook import tqdm
    elif shell == 'TerminalInteractiveShell': #script being run in iPython terminal
        from tqdm import tqdm
except NameError:
    from tqdm import tqdm # Probably runing on standard python terminal.

from ..np_utils import numpy_fill
from ._integration import simpson3oct_vec
from . import conf_interval

@njit
def resample_paired_nb(X, Y, func, output_len=1, R=int(1e5), seed=0):
    np.random.seed(seed)
    r = R - 1
    N = X.size
    data_paired = np.vstack((X, Y)).T
    idxs_resampling = np.random.randint(low=0, high=N, size=r*N)
    data_resampled = data_paired[idxs_resampling].reshape(r, N, 2)
    stat = func(X, Y)

    boot_sample = np.empty((R, output_len))
    boot_sample[0] = stat # first element is the sample statistic.
    for i, r in enumerate(data_resampled):
        x, y = r.T
        boot_sample[i+1] = func(x, y)
    return boot_sample

@njit
def resample_nb_X(X, R=int(1e5), seed=0, smooth=False, N=0):
    """X: array of shape (N, n_vars)."""
    np.random.seed(seed)
    n, num_vars = X.shape
    if N == 0:
        N = n
    idxs_resampling = np.random.randint(low=0, high=n, size=R*N)
    data_resampled = X[idxs_resampling].reshape(R, N, num_vars)
    if smooth:
        def x_in_percentile(x):
            low, high  = np.percentile(x, [5, 95])
            z = x[(x>low) & (x<high)]
            return z
        def std_percentile(x):
            z = x_in_percentile(x)
            return z.std() / np.sqrt(z.size)
        h = np.array([std_percentile(x) for x in X.T])
        n_trimmed = x_in_percentile(X.T[0]).size
        for k, h_k in enumerate(h):
            data_resampled[:,:,k] += h_k * np.random.standard_t(n_trimmed, R*N)
    return data_resampled

@njit
def resample_nb_X_multidim(X, R=int(1e5), seed=0, N=0):
    """X: array of shape (N, *dims)."""
    np.random.seed(seed)
    n = X.shape[0]
    if N == 0:
        N = n
    idxs_resampling = np.random.randint(low=0, high=n, size=R*N)
    data_resampled = X[idxs_resampling].reshape(R, N, *X.shape[1:])
    return data_resampled

@njit
def resample_nb(X, func, output_len=1, R=int(1e5), seed=0, smooth=False, N=0):
    """X: array of shape (N, n_vars)."""
    if X.ndim > 2:
        assert not smooth, "Smooth not supported for multidimensional data."
        data_resampled = resample_nb_X_multidim(X, R=R-1, seed=seed, N=N)
    else:
        data_resampled = resample_nb_X(X, R=R-1, seed=seed, smooth=smooth, N=N)

    boot_sample = np.empty((R, output_len))
    boot_sample[0] = func(X) # first element is the sample statistic.
    for i, r in enumerate(data_resampled):
        boot_sample[i+1] = func(r)
    return boot_sample

@njit
def resample_twosamples_nb(X1, X2, func, output_len=1, R=int(1e5), seed=0, smooth=False, N=0):
    """Xi: array of shape (N, n_vars)."""
    data_resampled_1 = resample_nb_X(X1, R=R-1, seed=seed, smooth=smooth, N=N)
    data_resampled_2 = resample_nb_X(X2, R=R-1, seed=seed+1, smooth=smooth, N=N)

    boot_sample = np.empty((R, output_len))
    boot_sample[0] = func(X1, X2) # first element is the sample statistic.
    for i, (r1, r2) in enumerate(zip(data_resampled_1, data_resampled_2)):
        boot_sample[i+1] = func(r1, r2)
    return boot_sample

def resample_twosamples(X1, X2, func, output_len=1, R=int(1e5), seed=0, smooth=False, N=0):
    """Xi: array of shape (N, n_vars)."""
    data_resampled_1 = resample_nb_X(X1, R=R-1, seed=seed, smooth=smooth, N=N)
    data_resampled_2 = resample_nb_X(X2, R=R-1, seed=seed, smooth=smooth, N=N)

    boot_sample = np.empty((R, output_len))
    boot_sample[0] = func(X1, X2) # first element is the sample statistic.
    for i, (r1, r2) in enumerate(zip(data_resampled_1, data_resampled_2), start=1):
        boot_sample[i] = func(r1, r2)
    return boot_sample

@njit
def _nb_mean(x):
    """
    njit version of numpy mean.
    """
    return np.mean(x)

@njit
def resample_block_nb(X, Y, func, output_len=1, R=int(1e4), R_B=int(1e3), seed=0, aggregator=_nb_mean):
    """
    This function follows the following procedure:
    1. Resamples paired blocks of data (X_k, Y_k) R times. k denotes the block label.
    2. For each subset  X_k and Y_k, resample their contents R_B times.
    3. Calculate the aggregated values of X_k and Y_k. Let's call them X_k^* and Y_k^*.
    4. Compute the statistic of interest (func) using X_k^* and Y_k^*. Notice that now paired statistics can be used.

    X, Y:         ragged arrays or tuples. Each element is an array containing the data for a block. Ensure there are no NaNs.
    func:         numba function f: X,Y  ->  Z,   Z: 1D array of size output_len.
    aggregator:   numba function for aggregating data from a block.
    """
    np.random.seed(seed)
    R_T = R * R_B
    boot_sample = np.empty((R_T, output_len))

    num_blocks = len(X)
    assert num_blocks == len(Y), "X and Y must have the same # blocks"

    idxs_resampling_blocks = np.random.randint(low=0, high=num_blocks, size=R*num_blocks).reshape(R, num_blocks)

    for i, idx_blocks in enumerate(idxs_resampling_blocks):
        Xi = [X[k] for k in idx_blocks]
        Yi = [Y[k] for k in idx_blocks]
        n_Xi = [len(x) for x in Xi]
        n_Yi = [len(y) for y in Yi]
        idxs_resampling_Xi = [np.random.randint(low=0, high=n, size=R_B*n).reshape(R_B, n) for n in n_Xi]
        idxs_resampling_Yi = [np.random.randint(low=0, high=n, size=R_B*n).reshape(R_B, n) for n in n_Yi]

        idx_start = i * R_B
        for j in range(R_B):
            Xi_resampled = [x[idxs_resampling_Xi[k][j]] for k, x in enumerate(Xi)]
            Yi_resampled = [y[idxs_resampling_Yi[k][j]] for k, y in enumerate(Yi)]
            Xij = np.array([aggregator(x) for x in Xi_resampled])
            Yij = np.array([aggregator(y) for y in Yi_resampled])
            boot_sample[idx_start + j] = func(Xij, Yij)
    return boot_sample

# Maybe numba adds compatibility for arrays with dtype=np.ndarray in the future.
# @njit
# def resample_block_nb(X, Y, func, output_len=1, R=int(1e4), R_B=int(1e3), seed=0, aggregator=_nb_mean):
#
#     This function follows the following procedure:
#     1. Resamples paired blocks of data (X_k, Y_k) R times. k denotes the block label.
#     2. For each subset  X_k and Y_k, resample their contents R_B times.
#     3. Calculate the aggregated values of X_k and Y_k. Let's call them X_k^* and Y_k^*.
#     4. Compute the statistic of interest (func) using X_k^* and Y_k^*. Notice that now paired statistics can be used.

#     X, Y:         ragged arrays or tuples. Each element is an array containing the data for a block.
#     func:         numba function f: X,Y  ->  Z,   Z: 1D array of size output_len.
#     aggregator:   numba function for aggregating data from a block.
#
#     np.random.seed(seed)
#     R_T = R * R_B
#     boot_sample = np.empty((R_T, output_len))

#     X = np.array(X, dtype=object)
#     Y = np.array(Y, dtype=object)
#     data = np.vstack((X, Y)).T
#     num_blocks = data.shape[0]
#     idxs_resampling_blocks = np.random.randint(low=0, high=num_blocks, size=R*num_blocks)
#     data_resampled = data[idxs_resampling_blocks].reshape(R, num_blocks, 2)
#     data_resampled = np.swapaxes(data_resampled, 1, 2)

#     for i, (Xi, Yi) in enumerate(data_resampled):
#         n_Xi = [len(x) for x in Xi]
#         n_Yi = [len(y) for y in Yi]
#         idxs_resampling_Xi = [np.random.randint(low=0, high=n, size=R_B*n) for n in n_Xi]
#         idxs_resampling_Yi = [np.random.randint(low=0, high=n, size=R_B*n) for n in n_Yi]
#         Xi_resampled = [x[idxs_resampling].reshape(R_B, n) for x, n, idxs_resampling in zip(Xi, n_Xi, idxs_resampling_Xi)]
#         Yi_resampled = [y[idxs_resampling].reshape(R_B, n) for y, n, idxs_resampling in zip(Yi, n_Yi, idxs_resampling_Yi)]

#         idx_start = i * R_B
#         for j in range(R_B):
#             Xij = np.array([aggregator(x[j]) for x in Xi_resampled])
#             Yij = np.array([aggregator(y[j]) for y in Yi_resampled])
#             boot_sample[idx_start + j] = func(Xij, Yij)
#     return boot_sample

def resample(X, func, output_len=1, R=int(1e4), seed=0, smooth=False, N=0):
    """X: array of shape (N, *dims)."""
    if X.ndim > 2:
        assert not smooth, "Multidimensional resampling does not support smoothing."
        data_resampled = resample_nb_X_multidim(X, R=R-1, seed=seed, N=N)
    else:
        data_resampled = resample_nb_X(X, R=R-1, seed=seed, smooth=smooth, N=N)

    boot_sample = np.empty((R, output_len))
    boot_sample[0] = func(X) # first element is the sample statistic.
    for i, r in enumerate(data_resampled, start=1):
        boot_sample[i] = func(r)
    return boot_sample


def resample_block(X, Y, func, output_len=1, R=int(1e5), seed=0):
    """
    X, Y:   ragged arrays or tuples. Each element is an array containing the data for a block.
    func:   numba function f: X,Y  ->  Z,   Z: 1D array of size output_len.
    """
    np.random.seed(seed)

    n_x = [len(x) for x in X]
    n_y = [len(y) for y in Y]
    idxs_resampling_x = [np.random.randint(low=0, high=n, size=R*n) for n in n_x]
    idxs_resampling_y = [np.random.randint(low=0, high=n, size=R*n) for n in n_y]
    X_resampled = [x[idxs_resampling].reshape(R, n) for x, n, idxs_resampling in zip(X, n_x, idxs_resampling_x)]
    Y_resampled = [y[idxs_resampling].reshape(R, n) for y, n, idxs_resampling in zip(Y, n_y, idxs_resampling_y)]

    boot_sample = np.empty((R, output_len))
    for i in range(R):
        Xi = np.hstack([x[i] for x in X_resampled])
        Yi = np.hstack([y[i] for y in Y_resampled])
        boot_sample[i] = func(Xi, Yi)
    return boot_sample

@njit
def jackknife_resampling_tuple(data):
    """
    Jackknife resampling for tuples of numpy arrays.
    """
    n = len(data)
    resamples = []
    idxs = np.arange(n)
    for i in range(n):
        valid_idxs = np.delete(idxs, i)
        resamples.append([data[j] for j in valid_idxs])
    return resamples

@njit
def jackknife_resampling(data):
    """Performs jackknife resampling on numpy arrays.

    Jackknife resampling is a technique to generate 'n' deterministic samples
    of size 'n-1' from a measured sample of size 'n'. The i-th
    sample  is generated by removing the i-th measurement
    of the original sample.
    """
    n = data.shape[0]
    if data.ndim > 1:
        resamples = np.empty((n, n - 1) + data.shape[1:])
        base_mask = np.ones((n), dtype=boolean)
        for i in range(n): # np.delete does not support 'axis' argument in numba.
            mask_i = base_mask.copy()
            mask_i[i] = False
            resamples[i] = data[mask_i]
    else:
        resamples = np.empty((n, n - 1))
        for i in range(n):
            resamples[i] = np.delete(data, i)
    return resamples

@njit
def jackknife_stat_nb(data, statistic):
    resamples = jackknife_resampling(data)
    stats = np.array([statistic(r) for r in resamples])
    return stats

def jackknife_stat(data, statistic):
    resamples = jackknife_resampling(data)
    stats = np.array([statistic(r) for r in resamples])
    return stats

def jackknife_stat_two_samples(data, data2, statistic, aggregator=None):
    if isinstance(data, np.ndarray): # not block
        jk_X = jackknife_resampling(data)
        jk_Y = jackknife_resampling(data2)
        jk_XY = [*product(jk_X, jk_Y)]
        stats = np.array([statistic(*r) for r in jk_XY])
    elif isinstance(data, tuple): # block
        jk_X = jackknife_resampling_tuple(data)
        jk_Y = jackknife_resampling_tuple(data2)
        jk_XY = product(jk_X, jk_Y)
        if aggregator is None:
            stats = np.array([statistic(*r) for r in jk_XY])
        else:
            def _preprocess(x):
                return np.array([aggregator(xi) for xi in x])
            stats = np.array([statistic(_preprocess(x), _preprocess(y)) for x, y in jk_XY])
    else:
        raise ValueError("data must be a tuple or np.ndarray.")
    return stats

def _percentile_of_score(a, score, axis, account_equal=False):
    """Vectorized, simplified `scipy.stats.percentileofscore`.

    Unlike `stats.percentileofscore`, the percentile returned is a fraction
    in [0, 1].
    """
    B = a.shape[axis]
    if account_equal:
        return ((a < score).sum(axis=axis) + (a <= score).sum(axis=axis)) / (2 * B)
    else:
        return (a < score).sum(axis=axis) / B

def _resample(data, data2, use_numba, statistic, R, n_min=1, smooth=False, aggregator=_nb_mean, **kwargs):
    """
    Resample using normal resampling if data2 is None.
    Else uses block resampling with data and data2.
    """
    if data2 is None:
        if data.ndim == 1:
            data = data[:, None]
        sample_stat = statistic(data)
        if hasattr(sample_stat, "__len__"):
            output_len = len(sample_stat)
        else:
            output_len = 1
        N = data.shape[0]
        if N < n_min:
            warnings.warn(f"N={N} < n_min={n_min}. Avoiding computation (returning NaNs) ...")
            theta_hat_b = None
        else:
            resample_func = resample_nb if use_numba else resample
            theta_hat_b = resample_func(data, statistic, R=R, output_len=output_len, smooth=smooth, **kwargs).squeeze()
    else:
        is_block = isinstance(data, tuple)
        if is_block:
            # if stack_data:
            #     sample_stat = statistic(np.hstack(data), np.hstack(data2))
            # else:
            # Take only common blocks (x, y) where x and y have at least 1 element.
            idxs_common_blocks = [i for i, (x, y) in enumerate(zip(data, data2)) if len(x) > 0 and len(y) > 0]
            if len(idxs_common_blocks) < len(data):
                warnings.warn("Removing some blocks because they were empty.", RuntimeWarning)
            if idxs_common_blocks:
                data = tuple([data[i] for i in idxs_common_blocks])
                data2 = tuple([data2[i] for i in idxs_common_blocks])
                sample_stat = statistic(np.array([aggregator(di) for di in data]), np.array([aggregator(di) for di in data2]))
                N = min(min([len(d) for d in data]),
                        min([len(d) for d in data2]))
                resample_func = resample_block_nb if use_numba else resample_block
                resample_kwargs = dict(aggregator=aggregator)
            else:
                N = 0
                sample_stat = np.nan
        else:
            if data.ndim == 1:
                data = data[:, None]
            if data2.ndim == 1:
                data2 = data2[:, None]
            sample_stat = statistic(data, data2)
            N = min([len(data), len(data2)])
            resample_func = resample_twosamples_nb if use_numba else resample_twosamples
            resample_kwargs = dict()

        if hasattr(sample_stat, "__len__"):
            output_len = len(sample_stat)
        else:
            output_len = 1
        if N < n_min:
            warnings.warn(f"N={N} < n_min={n_min}. Avoiding computation (returning NaNs) ...")
            theta_hat_b = None
        else:
            theta_hat_b = resample_func(data, data2, statistic, R=R, output_len=output_len, **resample_kwargs, **kwargs).squeeze()
            # if stack_data and is_block:
            #     data = np.hstack(data)
            #     data2 = np.hstack(data2)
    return data, data2, theta_hat_b, sample_stat, N

def CI_bca(data, statistic, data2=None, alternative='two-sided', alpha=0.05, R=int(1e5), account_equal=False, use_numba='auto', n_min=1, aggregator=_nb_mean, exclude_nans=False, return_resamples=False, **kwargs):
    """
    If data2 is provided, assumes a block resampling and statistic takes two arguments.
    Optional kwargs for aggregating data, data2 before computing the statistic:
            aggregator = @njit
                         def nb_mean(x):
                             return np.mean(x)
    """
    if use_numba == 'auto':
        use_numba = isinstance(statistic, CPUDispatcher)
    if alternative == 'two-sided':
        probs = np.array([alpha/2, 1 - alpha/2])
    elif alternative == 'less':
        probs = np.array([0, 1-alpha])
    elif alternative == 'greater':
        probs = np.array([alpha, 1])
    else:
        raise ValueError(f"alternative '{alternative}' not valid. Available: 'two-sided', 'less', 'greater'.")

    data, data2, theta_hat_b, sample_stat, N = _resample(data, data2, use_numba, statistic, R=R, n_min=n_min, aggregator=aggregator, **kwargs)

    if theta_hat_b is None:
        return np.array([np.nan, np.nan])

    alpha_bca = _bca_interval(data, data2, statistic, probs, theta_hat_b, account_equal, use_numba, aggregator=aggregator, exclude_nans=exclude_nans)[0]

    if np.isnan(alpha_bca).all():
        warnings.warn('CI shows there is only one value. Check data.', RuntimeWarning)
        if data2 is None:
            sample_stat = statistic(data)
        else:
            sample_stat = statistic(data, data2)
        ci = np.array([sample_stat, sample_stat])
    else:
        ci = _compute_CI_percentile(theta_hat_b, alpha_bca, alternative, to_ptg=True, exclude_nans=exclude_nans)

    if return_resamples:
        return ci, theta_hat_b
    else:
        return ci

def _atleast_2d_rev(arr):
    if arr.ndim == 1:
        return arr[:, None]
    else:
        return arr

def _bca_interval(data, data2, statistic, probs, theta_hat_b, account_equal, use_numba, aggregator=None, exclude_nans=False):
    """Bias-corrected and accelerated interval."""
    # calculate z0_hat
    if data2 is None:
        theta_hat = statistic(data)
    else:
        if aggregator is not None:
            theta_hat = statistic(np.array([aggregator(di) for di in data]),
                                  np.array([aggregator(di) for di in data2]))
        else:
            theta_hat = statistic(data, data2)
    if exclude_nans:
        valid = ~(np.isnan(_atleast_2d_rev(theta_hat_b)).any(axis=1))
        if not valid.all():
            print("excluded nans from the resampled statistics")
            theta_hat_b = theta_hat_b[valid]
    percentile = _percentile_of_score(theta_hat_b, theta_hat, axis=0, account_equal=account_equal)
    z0_hat = ndtri(percentile)

    # calculate a_hat
    if data2 is None:
        jackknife_computer = jackknife_stat_nb if use_numba else jackknife_stat
        theta_hat_jk = jackknife_computer(data, statistic)  # jackknife resample
    else:
        theta_hat_jk = jackknife_stat_two_samples(data, data2, statistic, aggregator=aggregator)
    if exclude_nans:
        valid = ~(np.isnan(_atleast_2d_rev(theta_hat_jk)).any(axis=1))
        theta_hat_jk = theta_hat_jk[valid]

    n = theta_hat_jk.shape[0]
    theta_hat_jk_dot = theta_hat_jk.mean(axis=0)

    U = (n - 1) * (theta_hat_jk_dot - theta_hat_jk)
    num = (U**3).sum(axis=0) / n**3
    den = (U**2).sum(axis=0) / n**2
    a_hat = 1/6 * num / (den**(3/2))

    # calculate alpha_1, alpha_2
    def compute_alpha(p):
        z0_hat_expanded = np.atleast_1d(z0_hat)[:, None] # compatibility with multiple outputs
        a_hat_expanded = np.atleast_1d(a_hat)[: , None]
        z_alpha = ndtri(p)
        num = z0_hat_expanded + z_alpha[None]
        return ndtr(z0_hat_expanded + num/(1 - a_hat_expanded*num))
    alpha_bca = compute_alpha(probs[(probs != 0) & (probs != 1)])
    alpha_bca = np.atleast_1d(alpha_bca.squeeze())
    if (alpha_bca > 1).any() or (alpha_bca < 0).any():
        warnings.warn('percentiles must be in [0, 1]. bca percentiles: {}\nForcing percentiles in [0,1]...'.format(alpha_bca), RuntimeWarning)
        alpha_bca = np.clip(alpha_bca, 0, 1)
    return alpha_bca, a_hat  # return a_hat for testing

def vs_transform(data, bootstrap_estimates, se_bootstrap, precision=1e-3, frac=2/3):
    """
    Variance-stabilizing transformation.
    """
    n_stats = bootstrap_estimates.shape[1]
    g = np.empty((data.shape[0], n_stats))
    lowess_linear_interp = []
    for i, (b, se, d) in enumerate(zip(bootstrap_estimates.T,  se_bootstrap.T, data.T)):
        x, y = lowess(se, b, frac=frac).T
        f_linear = interp1d(np.unique(x), y=np.unique(y), bounds_error=False, kind='linear', fill_value='extrapolate')
        z_min = d.min()
        for k, z in enumerate(d):
            g[k, i] = simpson3oct_vec(vs_integrand, z_min, z, precision, f_linear)[0]
        lowess_linear_interp.append(f_linear)
    return g, lowess_linear_interp

def invert_CI(CI, z, g, lowess_linear_interp, frac=1/10, min_n=100, integration_precision=1e-4):
    CIs = np.empty(CI.shape)
    for k, (ci, zi, gi, f_linear) in enumerate(zip(CI, z.T, g.T, lowess_linear_interp)):
        n = zi.size
        if n < min_n:
            z_std = zi.std() / np.sqrt(zi.size)
            z_min = zi.min()
            extra_z = np.unique(np.linspace(z_min - z_std/2, z.max()+z_std/2, min_n - n))
            extra_g = np.empty((extra_z.size))
            for j, extra_zi in enumerate(extra_z):
                extra_g[j] = simpson3oct_vec(vs_integrand, z_min, extra_zi, integration_precision, f_linear)[0]
            zi = np.hstack((zi, extra_z))
            gi = np.hstack((gi, extra_g))
        g_l, z_l = lowess(zi, gi, frac=frac).T
        f_inv = interp1d(np.unique(g_l), y=np.unique(z_l), bounds_error=False, kind='linear', fill_value='extrapolate')
        finite_ci = np.isfinite(ci) # account for single-tail.
        CIs[k, finite_ci] = f_inv(ci[finite_ci])
        CIs[k, ~finite_ci] = ci[~finite_ci]
    return CIs

def compute_CI_studentized(base, results, studentized_results, alpha=0.05, alternative='two-sided'):
    R, output_len = results.shape
    bootstrap_estimate = results.mean(axis=0)
    errors = results - bootstrap_estimate
    std_err = np.asarray(np.sqrt(np.diag(errors.T.dot(errors) / R)))

    lower = np.empty((output_len))
    upper = np.empty((output_len))
    alpha_tails = alpha / 2 if alternative == 'two-sided' else alpha
    percentiles = 100 * np.array([[alpha_tails, 1.0 - alpha_tails]] * output_len)
    for i in range(output_len):
        lower[i], upper[i] = np.percentile(studentized_results[:, i], percentiles[i])
    if alternative == 'less':
        upper.fill(np.inf)
    elif alternative == 'greater':
        lower.fill(-1 * np.inf)

    # Basic and studentized use the lower empirical quantile to compute upper and vice versa.
    lower_copy = lower + 0.0
    lower = base - upper * std_err
    upper = base - lower_copy * std_err
    CI = np.vstack((lower, upper)).T
    return CI

def vs_integrand(x, f_linear):
    """Integrand of the variance-stabilizing transformation."""
    clipped_f = np.clip(f_linear(x), 1e-8, None)
    if np.isnan(clipped_f).any():
        clipped_f = numpy_fill(clipped_f)
    return 1 / clipped_f

def cov(results, base=None, recenter=False):
    """
    reps : Number of bootstrap replications
    recenter : Whether to center the bootstrap variance estimator on the average of the bootstrap samples (True), or
                       to center on the original sample estimate (False).
    """
    if recenter:
        errors = results - np.mean(results, 0)
    else:
        assert base is not None
        errors = results - base
    return errors.T.dot(errors) / results.shape[0]

def _bootstrap_studentized_resampling(data, statistic, alpha=0.05, R=10000, studentized_reps=100, recenter=False, se_func=None, seed=0, divide_by_se=True, smooth=False):
    base = np.asarray(statistic(data))
    output_len = base.size
    studentized_results = np.empty((R, output_len))
    results = np.empty((R, output_len))
    se_bootstrap = np.empty((R, output_len))
    n = data.shape[0]
    if divide_by_se:
        def get_studentized(data_r, result, seed):
            nested_resampling = resample_nb(data_r, statistic, R=studentized_reps, output_len=output_len, seed=seed, smooth=False)
            std_err = np.sqrt(np.diag(cov(nested_resampling, result, recenter=recenter)))
            err = result - base
            t_result = err /std_err
            return t_result, std_err
    else:
        def get_studentized(data_r, result, seed):
            return result - base, np.nan

    data_r = resample_nb_X(data, R=R, seed=seed, smooth=smooth)
    if se_func is None:
        for i, d_r in enumerate(data_r):
            result = statistic(d_r)
            t_result, std_err = get_studentized(d_r, result, i)
            results[i] = result
            studentized_results[i] = t_result # t = (x^ - x) / s
            se_bootstrap[i] = std_err
    else:
        for i, d_r in enumerate(data_r):
            result = statistic(d_r)
            se = se_func(d_r)
            results[i] = result
            studentized_results[i] = (result - base) / se
            se_bootstrap[i] = se
    return base, results, studentized_results, se_bootstrap

def CI_studentized(data, statistic, R=int(1e5), alpha=0.05, alternative='two-sided', smooth=False, vs=False,
                   frac_g=2/3, frac_invert=1/10, studentized_reps=100,
                   integration_precision=1e-4, **kwargs):
    assert alternative in ['two-sided', 'less', 'greater'], f"alternative '{alternative}' not valid. Available: 'two-sided', 'less', 'greater'."
    base, results, studentized_results, se_bootstrap = _bootstrap_studentized_resampling(data, statistic, smooth=smooth, R=R, studentized_reps=studentized_reps, **kwargs)
    if vs:
        g, lowess_linear_interp = vs_transform(data, results, se_bootstrap, precision=integration_precision, frac=frac_g)
        base_g, results_g, studentized_results_g, _ = _bootstrap_studentized_resampling(g, statistic, R=R, divide_by_se=False, smooth=False)
        CI = invert_CI(compute_CI_studentized(base_g, results_g, studentized_results_g, alpha=alpha, alternative=alternative),
                       data, g, lowess_linear_interp, frac=frac_invert, integration_precision=integration_precision)
    else:
        CI = compute_CI_studentized(base, results, studentized_results, alpha=alpha, alternative=alternative)
    return CI

def _compute_CI_percentile(boot_sample, alpha, alternative, to_ptg=False, exclude_nans=False):
    if isinstance(alpha, np.ndarray) and alpha.ndim == 2: # variable alpha for each output. Used for CI_bca
        return np.vstack(_compute_CI_percentile(boot_sample[:,i], alpha[i], alternative, to_ptg, exclude_nans) for i in range(alpha.shape[0]))
    alpha_iter = isinstance(alpha, Iterable)
    if alpha_iter:
        alpha = np.asarray(alpha)
        if alpha.sum() < 1.1 or to_ptg: # TODO: modify the condition to allow percentages < 1.
            alpha_ptg = alpha * 100
        else:
            alpha_ptg = alpha
    else:
        alpha_ptg = alpha*100 if (alpha < 1 or to_ptg) else alpha
    if boot_sample.ndim == 1:
        output_len = 1
    else:
        output_len = boot_sample.shape[1]
    if exclude_nans:
        percentile = np.nanpercentile
    else:
        percentile = np.percentile

    if alternative == 'two-sided':
        CI = percentile(boot_sample, alpha_ptg if alpha_iter else [alpha_ptg/2, 100 - alpha_ptg/2], axis=0).T
        CI = np.atleast_2d(CI)
    elif alternative == 'less':
        CI = np.vstack((-np.inf * np.ones((output_len)), percentile(boot_sample, alpha_ptg[0] if alpha_iter else 100-alpha_ptg, axis=0))).T
    elif alternative == 'greater':
        CI = np.vstack((percentile(boot_sample, alpha_ptg[0] if alpha_iter else alpha_ptg, axis=0), np.inf * np.ones((output_len)))).T
    else:
        raise ValueError(f"alternative '{alternative}' not valid. Available: 'two-sided', 'less', 'greater'.")
    return CI

def CI_percentile(data, statistic, data2=None, R=int(1e5), alpha=0.05, smooth=False, alternative='two-sided', n_min=1, use_numba='auto', return_resamples=False, exclude_nans=False, **kwargs):
    """
    If data2 is provided, statistic takes two arguments and assumes block resampling if the input data are tuples.
    Optional kwargs for aggregating data, data2 before computing the statistic:
            aggregator = @njit
                         def nb_mean(x):
                             return np.mean(x)
    """
    if use_numba == 'auto':
        use_numba = isinstance(statistic, CPUDispatcher)
    data, data2, boot_sample, sample_stat, N = _resample(data, data2, use_numba, statistic, R=R, n_min=n_min, smooth=smooth, **kwargs)
    if boot_sample is None:
        CI = np.array([np.nan, np.nan])
    else:
        CI = _compute_CI_percentile(boot_sample, alpha, alternative, exclude_nans=exclude_nans)
    if return_resamples:
        return CI, boot_sample
    else:
        return CI

def CI_all(data, statistic, R=int(1e5), alpha=0.05, alternative='two-sided', coverage_iters=int(1e5), coverage_seed=42, avg_len=3, exclude=['studentized_vs', 'studentized_vs_smooth']):
    """
    Computes all CIs.
    exclude: CIs to exclude. Available: percentile
                                        percentile_smooth
                                        bca
                                        bca_smooth
                                        studentized
                                        studentized_smooth
                                        studentized_vs
                                        studentized_vs_smooth
    """
    specs = dict(percentile = (CI_percentile, {}),
                 percentile_smooth = (CI_percentile, dict(smooth=True)),
                 bca = (CI_bca, {}),
                 bca_smooth = (CI_bca, dict(smooth=True)),
                 studentized = (CI_studentized, {}),
                 studentized_smooth = (CI_studentized, dict(smooth=True)),
                 studentized_vs = (CI_studentized, dict(vs=True)),
                 studentized_vs_smooth = (CI_studentized, dict(vs=True, smooth=True))
                )
    specs = {k: v for k, v in specs.items() if k not in exclude}

    CIs = defaultdict(list)
    for label, (func, kws) in tqdm(specs.items()):
        CI = func(data, statistic, R=R, alpha=alpha, alternative=alternative, **kws)
        CIs['CI'].append(label)
        if CI.shape[0] == 1 or CI.ndim == 1:
            CI = CI.squeeze()
            CIs['low'].append(CI[0])
            CIs['high'].append(CI[1])
        else:
            CIs['low'].append(CI[:, 0])
            CIs['high'].append(CI[:, 1])
    return conf_interval.CI_specs(pd.DataFrame(CIs).set_index('CI'), data, statistic, coverage_iters=coverage_iters, seed=coverage_seed, avg_len=avg_len)

def power_analysis_naive(data, statistic, low, high, N_values=np.array([5, 10, 25, 50, 100, 200]), R=int(1e4), seed=0):
    """
    Naive bootstrap power and sample-size calculation for accepting H0.
    Computes violations on the low and high bound of H0.
    See Efron-Tshibirani: An introduction to the bootstrap,  p. 379-381.

    Returns: dataframe with index=N_values, columns=[low_fails, high_fails, power].
    """
    results = defaultdict(list)
    n = data.shape[0]
    if n not in N_values:
        N_values = np.sort(np.hstack((n, N_values)))
    for N in N_values:
        data_resampled = resample_nb(data, statistic, R=int(1e4), N=N, seed=seed)
        fail_low = (data_resampled < low).mean()
        fail_high = (data_resampled > high).mean()
        power = 1 - fail_low - fail_high
        results['violations-low'].append(fail_low)
        results['violations-high'].append(fail_high)
        results['power'].append(power)
    return pd.DataFrame(results, index=N_values)

def power_analysis(data, statistic, low, high, output_len=1, N_values=np.array([5, 10, 25, 50, 100, 200]), add_n=True, recenter=False, seed=0, seed_N=int(1e9),
                   R=int(1e4), R_se=int(1e5), R_se_nested=int(1e3), R_N=int(1e3), alpha_low=0.05, alpha_high=0.05, method='percentile', exact_CI_p=None, tol=1e-8):
    """
    Stable bootstrap power and sample-size calculation for accepting
        H0: stat in [low, high] with confidence (1 - alpha_low - alpha_high).

    Computes violations on the studentized equivalent for the low and high bound of H0.
    Takes into account the variability in
            the original sample (size n):        bootstrap estimate, SE of the bootstrap estimate.
            and in the future sample (size N):   bootstrap quantile estimate.
    See Efron-Tshibirani: An introduction to the bootstrap,  p. 381-384.

    Returns: dataframe with index=N_values, columns=[low_fails, high_fails, power].
    """
    seed_n = seed+1
    seed_N = seed+2
    seed_n_se = seed+3

    n = data.shape[0]
    if n not in N_values and add_n:
        N_values = np.sort(np.hstack((n, N_values)))
    base = statistic(data)
    se_estimate = np.sqrt(np.diag(cov(resample_nb(data, statistic, seed=seed, R=R_se, output_len=output_len),
                                      base,
                                      recenter=recenter)
                                 ))
    low_studentized = (base - low) / (se_estimate + tol)
    high_studentized = (base - high) / (se_estimate + tol)

    # Estimation of SE (datasize = n). This is the computational bottleneck.
    data_n = resample_nb_X(data, R=R, seed=seed_n)
    se_estimate_n = np.empty((R, output_len))
    estimate_n = np.empty((R, output_len))
    for i, d_n in enumerate(tqdm(data_n)):
        estimate_n_i = statistic(d_n)
        nested_estimate_n = resample_nb(d_n, statistic, seed=seed_n_se+i, R=R_se_nested, output_len=output_len)
        estimate_n[i] = estimate_n_i
        se_estimate_n[i] = np.sqrt(np.diag(cov(nested_estimate_n, estimate_n_i, recenter=recenter)))

    # Violations of studentized endpoints.
    results = defaultdict(list)
    np.random.seed(seed_N)
    for N in N_values:
        estimate_N_low = np.empty((R, output_len))
        estimate_N_high = np.empty((R, output_len))
        for i in range(R):
            data_N = data[np.random.randint(0, n, size=N)]
            if method == 'exact':
                data_N = data_N.squeeze()
                if exact_CI_p is None:
                    raise ValueError('exact_CI_p must be specified for exact method.')
                estimate_N_low[i] = conf_interval.ci_percentile_equal_tailed(data_N, exact_CI_p, alpha=alpha_low, alternative='greater')[0][0]
                estimate_N_high[i] = conf_interval.ci_percentile_equal_tailed(data_N, exact_CI_p, alpha=alpha_high, alternative='less')[0][1]
            elif method == 'percentile':
                estimate_N = resample_nb(data_N, statistic, R=R_N, seed=seed_N+i, output_len=output_len)
                estimate_N_low[i] = np.percentile(estimate_N, 100*alpha_low, axis=0)
                estimate_N_high[i] = np.percentile(estimate_N, 100*(1-alpha_high), axis=0)
            else:
                raise ValueError('method must be either "exact" or "percentile".')
        T_l = (estimate_n - estimate_N_low) / (se_estimate_n + tol)
        T_h = (estimate_n - estimate_N_high) / (se_estimate_n + tol)
        low_violations = (T_l > low_studentized).mean()
        high_violations = (T_h < high_studentized).mean()
        # power = 1 - low_violations - high_violations. Wrong, there can be overlap
        power = 1 - ( (T_l > low_studentized) | (T_h < high_studentized) ).mean()
        results['violations-low'].append(low_violations)
        results['violations-high'].append(high_violations)
        results['power'].append(power)

    return pd.DataFrame(results, index=N_values)
