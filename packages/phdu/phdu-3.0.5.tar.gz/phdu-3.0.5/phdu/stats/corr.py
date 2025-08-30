"""
Correlation metrics
"""
import pandas as pd
import numpy as np
try:
    shell = get_ipython().__class__.__name__
    if shell == 'ZMQInteractiveShell': # script being run in Jupyter notebook
        from tqdm.notebook import tqdm
    elif shell == 'TerminalInteractiveShell': #script being run in iPython terminal
        from tqdm import tqdm
except NameError:
    from tqdm import tqdm # Probably runing on standard python terminal. If does not work => should be replaced by tqdm(x) = identity(x)

def corr_pruned(df, col=None, method='spearman', alpha=0.05, ns_to_nan=True, correct_by_multiple_comp='by'):
    """
    Compute correlation matrix with statistical significance testing.

    Returns correlation coefficients between DataFrame features where the
    corresponding p-value (optionally adjusted by multiple comparisons)
    is less than the specified significance level.
    Non-significant correlations can optionally be masked as NaN values.

    Parameters
    ----------
    df : pandas.DataFrame
        Input DataFrame containing numeric features for correlation analysis.
    col : str, optional
        Single column name to correlate with all other columns. If None,
        computes pairwise correlations between all columns. Default is None.
    method : {'spearman', 'pearson'}, optional
        Correlation method to use. Default is 'spearman'.
    alpha : float, optional
        Significance level for hypothesis testing. Correlations with (possibly adjusted) p-values
        greater than alpha are considered non-significant. Default is 0.05.
    ns_to_nan : bool, optional
        If True, non-significant correlations (p-value > alpha) are replaced
        with NaN values in the output. Default is True.
    correct_by_multiple_comp : {'bonferroni', 'bh', 'by', None}, optional
        Method for multiple comparison correction of p-values. Options are:
        - 'bonferroni': Bonferroni correction (Family-wise error rate)
        - 'bh': Benjamini-Hochberg (False Discovery Rate)
        - 'by': Benjamini-Yekutieli (more conservative FDR, valid under arbitrary dependence)
        - None: No correction applied
        Default is 'by'.

    Returns
    -------
    c : pandas.DataFrame
        Correlation matrix with the same index and columns as input DataFrame
        (or subset if `col` is specified). Non-significant correlations are
        set to NaN if `ns_to_nan=True`.
    p : pandas.DataFrame
        Matrix of uncorrected p-values corresponding to the correlation
        coefficients. Same shape as correlation matrix.
    p_corrected : pandas.DataFrame | None
        Matrix of p-values after multiple comparison correction (if applied).
        If `correct_by_multiple_comp=None`, this is set to None.
        Else, has the same shape as correlation matrix.
    """
    import scipy.stats as ss
    corr_func = getattr(ss, f"{method}r")
    c = {}
    p = {}
    coltypes = df.dtypes
    numerical_columns = coltypes != 'object'
    categorical_columns = coltypes == 'category'
    if method == 'spearman':
        valid_columns = numerical_columns | categorical_columns
    else:
        valid_columns = numerical_columns & (~categorical_columns)
    valid_columns = valid_columns[valid_columns].index
    if col is not None:
        col_iterator_1 = [col]
        col_iterator_2 = tqdm(valid_columns)
    else:
        col_iterator_1 = tqdm(valid_columns)
        col_iterator_2 = valid_columns

    for col1 in col_iterator_1:
        for col2 in col_iterator_2:
            if (col1, col2) in c or (col2, col1) in c:
                continue
            elif col1 == col2:
                c[(col1, col2)] = 1.0
                p[(col1, col2)] = 0
            else:
                corr, pval = corr_func(*(df[[col1, col2]].dropna().values.T))
                c[(col1, col2)] = corr
                c[(col2, col1)] = corr
                p[(col1, col2)] = pval
                p[(col2, col1)] = pval
    c = pd.Series(c).unstack()
    p = pd.Series(p).unstack()
    if correct_by_multiple_comp is not None:
        if correct_by_multiple_comp == 'bonferroni':
            N = df.shape[1]
            num_comparisons = N*(N-1) / 2
            p_corrected = pd.DataFrame(np.clip(p.values * num_comparisons, 0, 1),
                                       columns=p.columns, index=p.index)
        else:
            p_corrected = ss.false_discovery_control(p.values.ravel(), method=correct_by_multiple_comp)
            p_corrected = pd.DataFrame(p_corrected.reshape(p.shape), columns=p.columns, index=p.index)
        if ns_to_nan:
            c[p_corrected > alpha] = np.nan
    else:
        p_corrected = None
        if ns_to_nan:
            c[p > alpha] = np.nan
    return c, p, p_corrected
