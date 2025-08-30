"""
pandas utils
"""
import pandas as pd
import numpy as np
import re
from functools import reduce
from .stats.rtopy import resample
from .stats.test import permutation

def latex_table(DF, index=False, CI_table=False, **kwargs):
    """Pandas DataFrame -> Latex table."""
    if CI_table:
        df = DF.map(lambda x: x.replace('[', '\n\n['))
    else:
        df = DF.copy()
    col_format = "c" if isinstance(df, pd.core.series.Series) else "c"*len(df.columns)
    if index:
        col_format += "c"
    table_replacements = (("\\toprule", "\\toprule "*2),
                          ("\\bottomrule", "\\bottomrule "*2)
    )
    text_replacements = (("\\textbackslash ", "\\"),
                         ("\{", "{"),
                         ("\}", "}"),
                         ("\$", "$"),
                         ("\_", "_"),
                         ("\\textasciicircum ", "^")
    )
    table_formatter = lambda x:  reduce(lambda a, kv: a.replace(*kv), table_replacements, x)
    text_formatter = lambda x: reduce(lambda a, kv: a.replace(*kv), text_replacements, x)
    formatter = lambda x: text_formatter(table_formatter(x))
    print(formatter(df.to_latex(index=index, column_format=col_format, **kwargs)))
    return

def parse_stat_ci(cell):
    """
    Parses a cell to extract sample_stat, CI_low, and CI_up,
    and applies exponent if present.
    """
    match = re.match(r"([\d\.]+) \[([\d\.]+), ([\d\.]+)\]( e([+-]\d+))?", cell)
    if match:
        stat = float(match.group(1))
        ci_low = float(match.group(2))
        ci_up = float(match.group(3))
        if match.group(5):  # Exponent part is present
            exponent = int(match.group(5))
            factor = 10 ** exponent
            stat *= factor
            ci_low *= factor
            ci_up *= factor
        return stat, ci_low, ci_up
    else:
        raise ValueError("Cell format is incorrect")

def highlight_best(df, criteria):
    """
    Highlights the best values for each column according to the given criteria.

    if the best value is unique (no CI overlap), it is highlighted in bold. Else, all best values are underlined.

    Parameters:
    df (pd.DataFrame): The input DataFrame with cells in 'sample_stat [CI_low, CI_up]' format.
    criteria_dict (dict|str): Dictionary where key is column name and value is 'lower' or 'upper' criteria. If str, the same criteria is applied to all columns.

    Returns:
    pd.DataFrame: DataFrame with highlighted cells.
    """
    df_copy = df.copy()

    if isinstance(criteria, str):
        criteria_dict = {column: criteria for column in df.columns}
    else:
        criteria_dict = criteria

    for k, (column, criteria) in enumerate(criteria_dict.items()):
        # Parse each cell in the column
        parsed_values = df[column].apply(parse_stat_ci)

        # Determine the best value according to the criteria
        if criteria == 'lower':
            best_value = min(parsed_values, key=lambda x: x[0])
        elif criteria == 'upper':
            best_value = max(parsed_values, key=lambda x: x[0])
        else:
            raise ValueError("Criteria must be 'lower' or 'upper'")

        best_stat, best_ci_low, best_ci_up = best_value

        # Check for CI overlap
        overlap = False
        for i, (stat, ci_low, ci_up) in enumerate(parsed_values):
            if stat == best_stat:
                for j, (other_stat, other_ci_low, other_ci_up) in enumerate(parsed_values):
                    if i != j and not (best_ci_up < other_ci_low or best_ci_low > other_ci_up):
                        overlap = True
                        df_copy.iloc[j,k] = f"\\underline{{{df.iloc[j,k]}}}"
                if overlap:
                    df_copy.iloc[i,k] = f"\\underline{{{df.iloc[i,k]}}}"
                else:
                    df_copy.iloc[i,k] = f"\\textbf{{{df.iloc[i,k]}}}"
                break

    return df_copy

def format_CI_results(df, exponential=False, simplify=True, integer=False):
    """
    Formats the confidence interval results in a DataFrame.

    Parameters:
    df (pandas.DataFrame): DataFrame containing columns: ['sample_stat', 'CI']
    exponential (bool, optional): If True, formats the numbers in exponential notation. Defaults to False.
    simplify (bool, optional): If True and exponential is True, simplifies the exponential notation if possible. Defaults to True.
    integer (bool, optional): If True, formats the numbers as integers. Defaults to False.

    Returns:
    pandas.Series: A series with the formatted confidence intervals: 'sample_stat [CI_low, CI_high]'.
    """
    def process_row(row):
        if exponential:
            if simplify:
                num_without_exp = lambda f: f'{f:.2e}'.split('e')[0]
                exp_low_str = f'{row.CI[0]:.2e}'.split('e')[1]
                exp_high_str = f'{row.CI[1]:.2e}'.split('e')[1]
                exp_low = int(exp_low_str)
                exp_high = int(exp_high_str)
                diff = exp_high - exp_low
                if not diff:
                    return f'{num_without_exp(row.sample_stat)} [{num_without_exp(row.CI[0])}, {num_without_exp(row.CI[1])}] e{exp_low_str}'
                else:
                    # everything in terms of exp_low
                    sample_stat = row.sample_stat / 10**exp_low
                    CI = row.CI / 10**exp_low
                    return f'{sample_stat:.1f} [{CI[0]:.1f}, {CI[1]:.1f}] e{exp_low_str}'
            else:
                return f'{row.sample_stat:.2e} [{row.CI[0]:.2e}, {row.CI[1]:.2e}]'
        elif integer:
            return f'{int(row.sample_stat)} [{int(row.CI[0])}, {int(row.CI[1])}]'
        else:
            return f'{row.sample_stat:.2f} [{row.CI[0]:.2f}, {row.CI[1]:.2f}]'
    return df.apply(process_row, axis=1)

def insert_level_sep(df, row_seps=1, col_seps=1):
    """
    Insert NaN rows and cols when the outer level of the MultiIndex changes.
    Example for three columns with col_seps=1:   c1, c2, c3    =>   c1, NANs, c2, NaNs, c3.

    This is useful when plotting a matrix and you want to visually separate different groups.
    """
    df_c = df.copy()
    col_levels = df.columns.get_level_values(0).unique() # respect the order
    row_levels = df.index.get_level_values(0).unique()
    for l in col_levels[:-1]:
        for k in range(col_seps):
            df_c[(l, " "*k)] = np.nan
    for l in row_levels[:-1]:
        for k in range(row_seps):
            df_c.loc[(l, " "*k), :] = np.nan
    return df_c[col_levels].loc[row_levels]

def expand_sequences(df, dt=1, maxlen=None):
    """
    Input: DataFrame. Each element is an array and all arrays start at the same time and have the same time step dt.

    Returns: MultiColumn DataFrame: (df.index,  (df.columns, time_steps))
    """
    if df.isna().values.any():
        if maxlen is None:
            maxlen = int(df.applymap(lambda x: x.size if isinstance(x, np.ndarray) else np.nan).max().max())
        df_padded = df.applymap(lambda x: np.hstack((x, np.nan*np.empty((maxlen-x.size)))) if isinstance(x, np.ndarray) else np.nan*np.empty((maxlen)))
    else:
        if maxlen is None:
            maxlen = int(df.applymap(lambda x: x.size).values.max())
        df_padded = df.applymap(lambda x: np.hstack((x, np.nan*np.empty((maxlen-x.size)))))
    df_padded_arr = np.stack([np.vstack(x) for x in df_padded.values]) # shape (df.shape[0], df.shape[1], time_steps)
    return pd.DataFrame(df_padded_arr.reshape((df.shape[0], -1)),
                        index = df.index,
                        columns = pd.MultiIndex.from_product([df.columns, dt*np.arange(maxlen)]))

def _ensure_df(dfs):
    is_series = all(isinstance(df, pd.Series) for df in dfs)
    dfs = [df.to_frame() if isinstance(df, pd.Series) else df for df in dfs]
    return dfs, is_series

def _revert_to_series(out, df_0):
    if out.shape[0] == 1:
        out = out.iloc[:, 0]
        out.name = df_0.iloc[:, 0].name
    else:
        out = out.squeeze()
    return out

def tuple_wise(*dfs, check_index=True, check_columns=True):
    """
    Attributes: Dataframes with same indices and columns. If the input are Series, they are converted to DataFrames.

    Returns dataframe where each element is a tuple containing the elements from other dataframes.
    If the input were Series, the output is a Series.
    """
    dfs, is_series = _ensure_df(dfs)
    df = dfs[0]
    if check_index:
        assert all(df.index.intersection(df2.index).size == df.shape[0] for df2 in dfs[1:]), "Indices do not match. To ignore this, set check_index=False."
    if check_columns:
        assert all(df.columns.intersection(df2.columns).size == df.shape[1] for df2 in dfs[1:]), "Columns do not match. To ignore this, set check_columns=False."
    out = pd.DataFrame(np.rec.fromarrays(tuple(df.values for df in dfs)).tolist(),
                       columns=df.columns,
                       index=df.index)
    if is_series:
        out = _revert_to_series(out, df)
    return out

def vstack_wise(*dfs):
    """
    Attributes: Dataframes where elements are arrays with equal length and have same indices and columns. If the input are Series, they are converted to DataFrames.

    Returns: DataFrame where df_ij = np.vstack((df1_ij, df2_ij, ...))
    """
    dfs, is_series = _ensure_df(dfs)
    R = np.rec.fromarrays(tuple(df.values for df in dfs))
    df1_df2 = pd.Series([np.vstack(i) if all(isinstance(j, np.ndarray) for j in i) else np.nan for i in R.flatten()], dtype=object,
                        index=dfs[0].stack(dropna=False).index).unstack()
    if is_series:
        df1_df2 = _revert_to_series(df1_df2, dfs[0])
    return df1_df2

def column_diffs(df, mode="to", mod_col=lambda x: "".join(np.array([*x])[[0, -1]])):
    """
    mode: '-'   (col2 - col1)
          'to' r'$col1 \to col2
    """
    N = df.shape[1]
    data = {}
    if mode == "-":
        label = lambda col1, col2: f"{col2} - {col1}"
    elif mode == "to":
        if callable(mod_col):
            label = lambda col1, col2: r"$\Huge {{{}}} \to {{{}}}$".format(mod_col(col1.replace(" ", "\ ")), mod_col(col2.replace(" ", "\ ")))
        else:
            label = lambda col1, col2: r"$\Huge {{{}}} \to {{{}}}$".format(col1.replace(" ", "\ "), col2.replace(" ", "\ "))
    for i, col1 in enumerate(df.columns):
        if i < N:
            for col2 in df.columns[i+1:]:
                data[label(col1, col2)] = df[col2] - df[col1]
    return pd.DataFrame(data)

def CI_by_col(df, stat, return_sample_stat=True, fillna=None, **kwargs):
    CI = pd.Series({col: resample.CI_bootstrap(df[col].dropna().values, stat=stat, **kwargs) for col in df.columns})
    if fillna is not None:
        def aux(x):
            x[np.isnan(x)] = fillna
            return x
        CI = CI.apply(aux)
    if return_sample_stat:
        return CI, getattr(df, stat)()
    else:
        return CI

def permtest_by_col(df, alternative, stat="mean", paired=True, diff=True, label="c", **kwargs):
    """
    Test directionality accross columns.
        col_i  (direction in [<, >, !=])  col_j

    Attributes:
        alternative:    'less', 'greater', 'two-sided'.
    """
    P = {}
    N = df.shape[1]
    is_paired = "paired" if paired else "not_paired"
    is_diff = "diff" if diff else ""
    for i in range(N):
        for j in range(i+1, N):
            yi, yj = df.iloc[:, [i,j]].dropna().values.T
            P[r"$\Huge {}_{{{}{}}}$".format(label, i+1, j+1)] = getattr(permutation, f"permutation_test_2sample_{is_paired}_{is_diff}{stat}")(yi, yj, alternative=alternative, **kwargs)
    return pd.Series(P)
