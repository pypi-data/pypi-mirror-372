"""
Numba-compatible permutation tests, with/without pairing (including block pairing), for the difference and the ratio.

For statistics other than mean & median, pass the statistic function to 'get_permutation_test'.
"""
import types
import inspect
import numpy as np
from numba import njit

@njit
def _permutation_pvalue(alternative, perm_sample, stat_0, tolerance):
    R = perm_sample.shape[0]
    if alternative == "greater":
        return (1 + (perm_sample >= stat_0 - tolerance).sum()) / (R + 1)
    elif alternative == "less":
        return (1 + (perm_sample <= stat_0 + tolerance).sum()) / (R + 1)
    elif alternative == "two-sided":
        return min(2 * np.fmin((1 + (perm_sample >= stat_0 - tolerance).sum()) / (R + 1),
                               (1 + (perm_sample <= stat_0 + tolerance).sum()) / (R + 1)),
                   1)
    else:
        raise ValueError("alternative not valid. Available: 'two-sided', 'less', 'greater'.")

def _compile_func(func_string, env_global, use_numba):
    if func_string.startswith("    "): # Unexpected indentation.
        func_string = func_string[4:].replace("\n    ", "\n")
    code_obj = compile(func_string, '<string>', 'exec')
    if isinstance(code_obj.co_consts[-1], tuple):
        try:
            f = types.FunctionType(code_obj.co_consts[-4], env_global, argdefs=code_obj.co_consts[-1])
        except:
            f = types.FunctionType(code_obj.co_consts[1], env_global, argdefs=code_obj.co_consts[-1])
    else:
        f = types.FunctionType(code_obj.co_consts[-3], env_global, argdefs=code_obj.co_consts[:-3])
    if use_numba:
        return njit(f)
    else:
        return f

def _get_permutation_test_not_paired(stat_func, use_numba=True):
    """
    Generate a function for the permutation test using the statistic 'stat_func'.
    This statistic can or not be numba compatible. Set 'use_numba' accordingly.
    """
    def permutation_test_STAT_FUNC_NAME(X1, X2, ratio=False, R=100000, alternative="two-sided", tolerance=1.5e-8, seed=0):
        """
        Permutation test for 'STAT_FUNC_NAME'. Permutations occur among all elements of X1 and X2.

        H0: X1 and X2 come from the same distribution F. The joint distribution would be independent on the variables: g(x, y) = f(x)f(y)

        Attrs:
            - alternative: one of 'two-sided', 'less', 'greater'.
                           Example of calculation for the mean mu:
                                                - greater:    H0 compatible: mu_1 / mu_2 < observed,       H1 compatible: mu_1 / mu_2  >= observed
                              ratio             - less:       H0 compatible: mu_1 / mu_2 > observed,       H1 compatible: mu_1 / mu_2  <= observed
                                                - two-sided:  H0 compatible: mu_1 / mu_2 = observed,       H1 compatible: mu_1 / mu_2  != observed

                                                - greater:    H0 compatible: mu_1 - mu_2 < observed,       H1 compatible: mu_1 - mu_2  >= observed
                              not ratio         - less:       H0 compatible: mu_1 - mu_2 > observed,       H1 compatible: mu_1 - mu_2  <= observed
                                                - two-sided:  H0 compatible: mu_1 - mu_2 = observed,       H1 compatible: mu_1 - mu_2  != observed
            - R:           number of resamples (permutations).
            - tolerance:   tolerance for numerical stability.
            - seed: seed   for random number generation.
        Returns: p-value
        """
        n1 = X1.size
        if ratio:
            def aux(X, n1): # pass n1 to avoid numba error.
                return stat_func(X[:n1]) / stat_func(X[n1:])
        else:
            def aux(X, n1):
                return stat_func(X[:n1]) - stat_func(X[n1:])
        X = np.hstack((X1, X2))
        stat_0 = aux(X, n1)

        perm_sample = np.empty((R)) # permutation distribution
        np.random.seed(seed)
        for i in range(R):
            np.random.shuffle(X)
            perm_sample[i] = aux(X, n1)
        return _permutation_pvalue(alternative, perm_sample, stat_0, tolerance)

    func_source_edit = inspect.getsource(permutation_test_STAT_FUNC_NAME).replace("STAT_FUNC_NAME", stat_func.__name__)
    env = globals()
    env.update(locals())
    return _compile_func(func_source_edit, env, use_numba)

def _get_permutation_test_paired(stat_func, use_numba=True):
    """
    Generate a function for the paired permutation test using the statistic 'stat_func'.
    This statistic can or not be numba compatible. Set 'use_numba' accordingly.
    """
    def permutation_test_paired_STAT_FUNC_NAME(X1, X2, ratio=False, R=100000, alternative="two-sided", tolerance=1.5e-8, seed=0):
        """
        Paired permutation test for 'STAT_FUNC_NAME'. Permutations occur only between each pair:   (x1, x2)  <->  (x2, x1).

        H0: (X1, X2) come from a symmetric joint distribution: p(x, y) = p(y, x).

        Attrs:
            - alternative: one of 'two-sided', 'less', 'greater'.
                           Example of calculation for the mean mu:
                                                - greater:    H0 compatible: mu_1 / mu_2 < observed,       H1 compatible: mu_1 / mu_2  >= observed
                              ratio             - less:       H0 compatible: mu_1 / mu_2 > observed,       H1 compatible: mu_1 / mu_2  <= observed
                                                - two-sided:  H0 compatible: mu_1 / mu_2 = observed,       H1 compatible: mu_1 / mu_2  != observed

                                                - greater:    H0 compatible: mu_1 - mu_2 < observed,       H1 compatible: mu_1 - mu_2  >= observed
                              not ratio         - less:       H0 compatible: mu_1 - mu_2 > observed,       H1 compatible: mu_1 - mu_2  <= observed
                                                - two-sided:  H0 compatible: mu_1 - mu_2 = observed,       H1 compatible: mu_1 - mu_2  != observed
            - R:           number of resamples (permutations).
            - tolerance:   tolerance for numerical stability.
            - seed: seed   for random number generation.
        Returns: p-value
        """
        if ratio:
            def aux(X_paired):
                return stat_func(X_paired[0]) / stat_func(X_paired[1])
        else:
            def aux(X_paired):
                return stat_func(X_paired[0]) - stat_func(X_paired[1])

        n = X1.size
        X_paired = np.vstack((X1, X2))
        stat_0 = aux(X_paired)

        perm_sample = np.empty((R))
        np.random.seed(seed)
        for i in range(R):
            shuffle = np.random.randint(0, 2, size=n) == 1
            X_shifted = X_paired[:, shuffle][::-1]
            X_still = X_paired[:, ~shuffle]
            X_perm = np.hstack((X_shifted, X_still))
            perm_sample[i] = aux(X_perm)
        return _permutation_pvalue(alternative, perm_sample, stat_0, tolerance)

    func_source_edit = inspect.getsource(permutation_test_paired_STAT_FUNC_NAME).replace("STAT_FUNC_NAME", stat_func.__name__)
    env = globals()
    env.update(locals())
    return _compile_func(func_source_edit, env, use_numba)

def _get_permutation_test_block(stat_func, use_numba=True):
    """
    Generate a function for the block permutation test using the statistic 'stat_func'.
    This statistic can or not be numba compatible. Set 'use_numba' accordingly.
    Permutations occur only between blocks: X1(block i) <-> X2(block i).
    """
    def permutation_test_block_STAT_FUNC_NAME(X, Y, ratio=False, R=100000, alternative="two-sided", tolerance=1.5e-8, seed=0):
        """
        Block permutation test for 'STAT_FUNC_NAME'. Permutations occur only between blocks: X1(block i) <-> X2(block i).

        H0: (X, Y) come from a joint distribution symmetric between each block:   p(x, y) = p(y, x)  <=> y, x belong to the same block.

        Attrs:
            - X, Y:        ragged arrays or tuples. Each element is an array containing the results for a block.
            - alternative: one of 'two-sided', 'less', 'greater'.
                           Example of calculation for the mean mu:
                                                - greater:    H0 compatible: mu_1 / mu_2 < observed,       H1 compatible: mu_1 / mu_2  >= observed
                              ratio             - less:       H0 compatible: mu_1 / mu_2 > observed,       H1 compatible: mu_1 / mu_2  <= observed
                                                - two-sided:  H0 compatible: mu_1 / mu_2 = observed,       H1 compatible: mu_1 / mu_2  != observed

                                                - greater:    H0 compatible: mu_1 - mu_2 < observed,       H1 compatible: mu_1 - mu_2  >= observed
                              not ratio         - less:       H0 compatible: mu_1 - mu_2 > observed,       H1 compatible: mu_1 - mu_2  <= observed
                                                - two-sided:  H0 compatible: mu_1 - mu_2 = observed,       H1 compatible: mu_1 - mu_2  != observed
            - R:           number of resamples (permutations).
            - tolerance:   tolerance for numerical stability.
            - seed: seed   for random number generation.
        Returns: p-value
        """
        if ratio:
            def aux(X1, X2):
                return stat_func(X1) / stat_func(X2)
        else:
            def aux(X1, X2):
                return stat_func(X1) - stat_func(X2)

        def stack(arr_list):
            return np.array([a for arr in arr_list for a in arr])

        stat_0 = aux(stack(X), stack(Y))
        perm_sample = np.empty((R))
        np.random.seed(seed)
        for i in range(R):
            Xi = []
            Yi = []
            for xi, yi in zip(X, Y):
                z = np.hstack((xi, yi))
                np.random.shuffle(z)
                Xi.append(z[:xi.size])
                Yi.append(z[xi.size:])
            perm_sample[i] = aux(stack(Xi), stack(Yi))
        return _permutation_pvalue(alternative, perm_sample, stat_0, tolerance)

    func_source_edit = inspect.getsource(permutation_test_block_STAT_FUNC_NAME).replace("STAT_FUNC_NAME", stat_func.__name__)
    env = globals()
    env.update(locals())
    return _compile_func(func_source_edit, env, use_numba)

def get_permutation_test(stat_func, pairing=None, use_numba=True):
    """
    Generate a function for the permutation test using the statistic 'stat_func'.
    This statistic can or not be numba compatible. Set 'use_numba' accordingly.

    pairing:
        - None:     Permutations occur among all elements of X1 and X2.
        - 'paired': Permutations occur only between each pair:   (x1, x2)  <->  (x2, x1).   (x1, x2) are elements of (X1, X2).
        - 'block':  Permutations occur only between blocks:      (x1_b, x2_b)  <->  (x2_b, x1_b).   x1_b in X1(block b), x2_b in X2(block b).

    Returns: function that computes the permutation test using the statistic 'stat_func'.
    """
    if pairing is None:
        return _get_permutation_test_not_paired(stat_func, use_numba)
    elif pairing == 'paired':
        return _get_permutation_test_paired(stat_func, use_numba)
    elif pairing == 'block':
        return _get_permutation_test_block(stat_func, use_numba)
    else:
        raise ValueError(f"pairing '{pairing}' is not valid. Available: None, 'paired', 'block'.")

permutation_test_mean = get_permutation_test(np.mean)
permutation_test_mean = get_permutation_test(np.median)
permutation_test_paired_mean = get_permutation_test(np.mean, pairing='paired')
permutation_test_paired_mean = get_permutation_test(np.median, pairing='paired')
permutation_test_block_mean = get_permutation_test(np.mean, pairing='block')
permutation_test_block_mean = get_permutation_test(np.median, pairing='block')


## Permutation test for mean/median of the difference or ratio

@njit
def permutation_test_paired_diffmean(X1, X2, R=int(1e5)-1, alternative="two-sided", tolerance=1.5e-8, seed=0):
    """
    Paired permutation test optimized for the mean of the differences. about 2x faster than the default _permutation_test_2sample_paired with stat_func = np.mean.
    Coincides with the test for the differences in means. (Not as the median)
    Attrs:
            alternative:  - greater:    H0: mu(X1-X2) < <X1-X2>_sample,       H1: mu(X1-X2) >= <X1-X2>_sample
                          - less:       H0: mu(X1-X2) > <X1-X2>_sample,       H1: mu(X1-X2) <= <X1-X2>_sample
                          - two-sided:  H0: mu(X1-X2) = <X1-X2>_sample,       H1: mu(X1-X2) != <X1-X2>_sample
    Returns: p-value
    """
    dX = X1 - X2
    n = dX.size
    stat_0 = dX.mean()

    perm_sample = np.empty((R))
    np.random.seed(seed)
    for i in range(R):
        shuffle = np.random.randint(0, 2, size=n) == 1
        dX_perm = dX.copy()
        dX_perm[shuffle] *= -1
        perm_sample[i] = (dX_perm).mean()

    return _permutation_pvalue(alternative, perm_sample, stat_0, tolerance)

@njit
def permutation_test_paired_diffmedian(X1, X2, R=int(1e5)-1, alternative="two-sided", tolerance=1.5e-8, seed=0):
    """
    Paired permutation test optimized for the median of the differences. about 2x faster than the default _permutation_test_2sample_paired with stat_func = np.mean.
    NOTE: Does not coincide with the test for the differences in medians.

    Attrs:
            alternative:  - greater:    H0: me(X1-X2) < observed,       H1: me(X1-X2) >= observed
                          - less:       H0: me(X1-X2) > observed,       H1: me(X1-X2) <= observed
                          - two-sided:  H0: me(X1-X2) = observed,       H1: me(X1-X2) != observed.
    Returns: p-value
    """
    dX = X1 - X2
    n = dX.size
    stat_0 = np.median(dX)

    perm_sample = np.empty((R))
    np.random.seed(seed)
    for i in range(R):
        shuffle = np.random.randint(0, 2, size=n) == 1
        dX_perm = dX.copy()
        dX_perm[shuffle] *= -1
        perm_sample[i] = np.median(dX_perm)

    return _permutation_pvalue(alternative, perm_sample, stat_0, tolerance)

@njit
def permutation_test_paired_ratio_median(X1, X2, R=int(1e5)-1, alternative="two-sided", tolerance=1.5e-8, seed=0):
    """
    Paired permutation test for the median ratio.

    Attrs:
            alternative:
                                           - greater:    H0: me_1 / me_2 < observed,       H1: me_1 / me_2  >= observed
                                           - less:       H0: me_1 / me_2 > observed,       H1: me_1 / me_2  <= observed
                                           - two-sided:  H0: me_1 / me_2 = observed,       H1: me_1 / me_2  != observed

    Returns: p-value
    """
    def aux(X_paired):
            return np.median(X_paired[0] / X_paired[1])

    n = X1.size
    X_paired = np.vstack((X1, X2))
    stat_0 = aux(X_paired)

    perm_sample = np.empty((R))
    np.random.seed(seed)
    for i in range(R):
        shuffle = np.random.randint(0, 2, size=n) == 1
        X_shifted = X_paired[:, shuffle][::-1]
        X_still = X_paired[:, ~shuffle]
        X_perm = np.hstack((X_shifted, X_still))
        perm_sample[i] = aux(X_perm)

    return _permutation_pvalue(alternative, perm_sample, stat_0, tolerance)

@njit
def permutation_test_paired_ratio_mean(X1, X2, R=int(1e5)-1, alternative="two-sided", tolerance=1.5e-8, seed=0):
    """
    Paired permutation test for the median ratio.

    Attrs:
            alternative:
                                           - greater:    H0: me_1 / me_2 < observed,       H1: me_1 / me_2  >= observed
                                           - less:       H0: me_1 / me_2 > observed,       H1: me_1 / me_2  <= observed
                                           - two-sided:  H0: me_1 / me_2 = observed,       H1: me_1 / me_2  != observed

    Returns: p-value
    """
    def aux(X_paired):
            return np.mean(X_paired[0] / X_paired[1])

    n = X1.size
    X_paired = np.vstack((X1, X2))
    stat_0 = aux(X_paired)

    perm_sample = np.empty((R))
    np.random.seed(seed)
    for i in range(R):
        shuffle = np.random.randint(0, 2, size=n) == 1
        X_shifted = X_paired[:, shuffle][::-1]
        X_still = X_paired[:, ~shuffle]
        X_perm = np.hstack((X_shifted, X_still))
        perm_sample[i] = aux(X_perm)

    return _permutation_pvalue(alternative, perm_sample, stat_0, tolerance)
