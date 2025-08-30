"""
Functions related to multiple comparisons.

When performing multiple comparisons, the probability of making at least one Type I error (false positive) increases.
It is likely that at least 1 test will be significant by chance.
"""

from scipy.stats import binom

def probability_at_least_1_positive(x, N, alpha=0.05):
    """
    H0: all N tests are negative.
    H1: at least one test is positive

    Parameters
    ----------
    - x: number of positive tests
    - N: number of tests
    - alpha: significance level
    """
    return 1 - binom.cdf(x-1, N, alpha)
