"""
Not implemented
"""
try:
    from statsmodels.stats.diagnostic import lilliefors
except:
    pass

def normality(df, path_dict={}, save=True):
    """Lilliefors test for each column"""
    S = pd.Series({col: lilliefors(df[col].values)[1] for col in df.columns})
    return S