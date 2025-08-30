from numba import njit
import numpy as np
import pandas as pd
import math
import warnings
from . import bootstrap
try:
    import statsmodels.stats.api as sms
except:
    pass

def t_interval(x, alpha=0.05, alternative="two-sided"):
    return sms.DescrStatsW(x).tconfint_mean(alpha=alpha, alternative=alternative)

@njit
def compute_coverage(CI, data, stat, N, seed=0, num_iters=1000, closed_right=True, closed_left=True, tol=1e-8):
    low, high = CI
    estimates = bootstrap.resample_nb(data, stat, R=num_iters, N=N, seed=seed)[:, 0]
    if closed_left:
        low_fails = (estimates < low).mean()
    else:
        low_fails = (estimates <= (low+tol)).mean()
    if closed_right:
        high_fails = (estimates > high).mean()
    else:
        high_fails = (estimates >= (high-tol)).mean()
    coverage = 1 - (low_fails + high_fails)
    return np.array([low_fails, high_fails, coverage])

def coverage(*args, num_N=20, **kwargs):
    Ns = np.unique(np.linspace(2, args[1].shape[0], num_N, dtype=int))
    covg_data = np.vstack([compute_coverage(*args, N=N, **kwargs) for N in Ns]).T # shape: (3, num_N).  3: low_fails, high_fails, coverage
    return Ns, covg_data

def CI_specs(CIs, data, stat, coverage_iters=int(1e4), seed=42, avg_len=3, **coverage_kws):
    CI_arr = CIs.values
    sample_stat = stat(data)
    coverages = np.stack([coverage(CI, data, stat, num_iters=coverage_iters, seed=seed, **coverage_kws)[1] for CI in CI_arr], axis=1)
    # coverages shape: (3, #CI, num_N)
    low_fails_last, high_fails_last, coverage_last = coverages[:, :, -1]
    low_fails_avg, high_fails_avg, coverage_avg = coverages[:, :, -avg_len:].mean(axis=-1)

    CIs2 = CIs.copy()
    CIs2['width'] = np.hstack([np.diff(CI) for CI in CI_arr])
    CIs2['asymmetry'] = np.hstack([(CI[1] - sample_stat) / (sample_stat - CI[0]) for CI in CI_arr])
    env = locals()
    for end in ['avg', 'last']:
        for k in ['low_fails', 'high_fails', 'coverage']:
            key = f"{k}_{end}"
            CIs2[key.replace("_", "-")] = env[key]
    return CIs2

def find_best(CIs, data=None, stat=None, alpha=0.05, alternative=None, alpha_margin_last=0.0075, alpha_margin_avg=0.015, **kwargs):
    alpha_expanded_last = alpha + alpha_margin_last
    alpha_expanded_avg = alpha + alpha_margin_avg
    if 'coverage-last' not in CIs.columns:
        CIs = CI_specs(CIs, data, stat, **kwargs)
    if alternative is None:
        if (~np.isfinite(CIs['low'].values)).all():
            alternative = 'less'
        elif (~np.isfinite(CIs['high'].values)).all():
            alternative = 'greater'
        else:
            alternative = 'two-sided'

    coverages_last, coverages_avg = CIs[['coverage-last', 'coverage-avg']].values.T
    valid = np.unique(np.hstack([np.where(coverages_last >= (1-alpha_expanded_last))[0],
                                 np.where(coverages_avg >= (1-alpha_expanded_avg))[0],
                                 np.abs(coverages_last - (1-alpha)).argmin()]))
    if alternative == 'two-sided':
        best_interval = CIs['width'].values[valid].argmin()
    elif alternative == 'less':
        best_interval = CIs['high'].values[valid].argmin()
    elif alternative == 'greater':
        best_interval = CIs['low'].values[valid].argmax()
    return CIs.iloc[valid].iloc[best_interval]

def ci_percentile_equal_tailed(x, p, alpha=0.05, alternative='two-sided', x_H1=None):
    """
    Exact confidence interval for percentiles.
    Attrs:
        - x: data
        - p:  percentile in (0, 1)
        - alpha: significance level
        - alternative: 'two-sided', 'less', 'greater'
        - x_H1: if provided, returns the p_value:
            - 'two-sided': 2 * min(p_value_less, p_value_greater). H1: x != x_H1
            - 'less': upper bound. H1: x < x_H1
            - 'greater': lower bound. H1: x > x_H1

    Returns CI [Yi, Yj] such that Prob(x in CI) => 1 - alpha. Yi, Yj are order statistics.
    https://online.stat.psu.edu/stat415/book/export/html/835
    """
    n = x.size
    if n <= 2:
        warnings.warn(f"n = {n} is too small. Returning NaN", RuntimeWarning)
        return np.nan
    else:
        if n < 500:
            def binom_cdf(x):
                return np.array([math.comb(n, k) * p**k * (1-p)**(n-k) for k in range(x+1)]).sum()
            binom_cdf = np.vectorize(binom_cdf)
            #def binom_pmf(x):
            #    return math.comb(n, x) * p**x * (1-p)**(n-x)
        else:
            try:
                from scipy.stats import binom
                binom_cdf = lambda x: binom.cdf(x, n, p)
            except:
                raise ImportError('scipy not found. Please install it for n > 500. Alternatively, use the normal aproximation for the binomial.')

        p_below_percentile = binom_cdf(np.arange(n+1))

        if alternative == 'two-sided':
            lows = np.where(p_below_percentile <= alpha/2)[0]
            if lows.size > 0:
                l = lows[-1] + 1
            else:
                warnings.warn('n is too small to warrantee an exact lower bound other than the minimum.', RuntimeWarning)
                l = 0
            uppers = np.where(p_below_percentile >= (1- alpha/2))[0]
            if uppers.size > 0:
                u = uppers[0] - 1
            else:
                warnings.warn('n is too small to warrantee an exact upper end other than the maximum.', RuntimeWarning)
                u = -1
            ci_equal_tailed = [l, u]
            if l == 0:
                q0 = 0
                CI_prob0 = 0
            else:
                q0 = p_below_percentile[l-1] #  p(X < l) = p(x <= l-1) = cdf(l-1)
                CI_prob0 = l/n # add 1 to both endpoints (indexing in python starts at 0)
            if u == -1:
                q1 = 1
                CI_prob1 = 1
            else:
                q1 = p_below_percentile[u+1]
                CI_prob1 = (u+1) / n # add 1 to both endpoints (indexing in python starts at 0)
            quantiles = np.array([q0, q1])
            CI_prob = np.array([CI_prob0, CI_prob1])
            CI = np.sort(x)[ci_equal_tailed]
        elif alternative == 'less':
            uppers = np.where(p_below_percentile >= (1-alpha))[0]
            if uppers.size > 0:
                u = min(uppers[0] - 1, x.size - 1)
            else:
                warnings.warn('n is too small to warrantee an exact CI other than the full range of the data.', RuntimeWarning)
                return np.array([-np.inf, x.max()]), [0, 1], [0, 1]
            quantiles = p_below_percentile[u+1]
            CI = np.array([-np.inf, np.sort(x)[u]])
            CI_prob = (u+1) / n
        elif alternative == 'greater':
            lows = np.where(p_below_percentile <= alpha)[0]
            if lows.size > 0:
                l = lows[-1] + 1
            else:
                warnings.warn('n is too small to warrantee an exact CI other than the full range of the data.', RuntimeWarning)
                return np.array([x.min(), np.inf]), [0, 1], [0, 1]
            quantiles = p_below_percentile[l-1]
            CI = np.array([np.sort(x)[l], np.inf])
            CI_prob = l / n
        if x_H1 is not None:
            observed_k_less = (x < x_H1).sum()
            p_value_less = 1 - p_below_percentile[observed_k_less] # probability of obtaining at least k successes assuming the null hypothesis is true

            observed_k_greater = (x > x_H1).sum()
            p_value_greater = 1 - p_below_percentile[observed_k_greater] # probability of obtaining at least k successes assuming the null hypothesis is true
            if alternative == 'less':
                p_value = p_value_less
            elif alternative == 'greater':
                p_value = p_value_greater
            else:
                p_value = 2 * min(p_value_less, p_value_greater)
            return CI, p_value, CI_prob, quantiles
        else:
            return CI, CI_prob, quantiles


def _exact_ci_percentile(x, p, alpha=0.05, alternative='two-sided', d_alpha=0.005):
    """
    DO NOT USE. This does not guarantee equal tailed. It is here as a reminder.

    Confidence 1 - alpha that the interval (Yi, Yj) contains the percentile p. Yi, Yj are order statistics.
    Attrs:
        - p:  percentile in (0, 1)
    https://online.stat.psu.edu/stat415/book/export/html/835
    """
    x_sorted = np.sort(x)
    n = x.size
    def confidence(low, high):
        return np.array([math.comb(n, k) * p**k * (1-p)**(n-k) for k in range(low, high)]).sum()
    c = {}
    if alternative == 'two-sided':
        for low in range(1, n):
            for high in range(low+1, n+1):
                c[(low-1, high-1)] = confidence(low, high)
    elif alternative == 'less':
        for high in range(1, n+1):
            c[high-1] = confidence(0, high)
    elif alternative == 'greater':
        for low in range(1, n+1):
            c[low-1] = 1 - confidence(0, low)
    c = pd.Series(c)
    c_pruned = c[(c - (1-alpha)).abs() < d_alpha]
    c_pruned = c_pruned.to_frame(name='confidence')
    if alternative == 'two-sided':
        low, high = [np.array(_) for _ in zip(*[x_sorted[list(i)] for i in c_pruned.index])]
        sample_stat = np.percentile(x, p*100)
        c_pruned['low'] = low
        c_pruned['high'] = high
        c_pruned['width'] = high - low
        c_pruned['asymmetry'] = (high - sample_stat) / (sample_stat - low)
        c_pruned = c_pruned.sort_values(['width', 'confidence'], ascending=[True, False])
    else:
        bound = [x_sorted[i] for i in c_pruned.index]
        if alternative == 'greater':
            c_pruned['low'] = bound
            c_pruned['high'] = np.inf
        else:
            c_pruned['low'] = -1 * np.inf
            c_pruned['high'] = bound
    return c_pruned

def _find_ci_percentile_exact_confidence(ci, x, p, tol=1e-3):
    """
    DO NOT USE. This does not guarantee equal tailed CI.

    Given a CI 'ci' from data 'x' of a percentile statistic, return the exact confidence it provides.
    """
    if not math.isfinite(ci[0]):
        alternative = 'less'
        prune = lambda c: c[(c['high'] - ci[1]).abs() < tol]
    elif not math.isfinite(ci[1]):
        alternative = 'greater'
        prune = lambda c: c[(c['low'] - ci[0]).abs() < tol]
    else:
        alternative = 'two-sided'
        prune = lambda c: c[((c['low'] - ci[0]).abs() < tol) & ((c['high'] - ci[1]).abs() < tol)]
    c = _exact_ci_percentile(x, p, alternative=alternative, d_alpha=0.5)
    return prune(c)
