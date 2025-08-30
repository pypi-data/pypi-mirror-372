"""
Adaptation of resample R package: https://cran.r-project.org/web/packages/resample/resample.pdf
Based on the article: https://arxiv.org/abs/1411.5279
"""
import numpy as np
import pandas as pd
try:
    import rpy2.robjects as ro
    from rpy2.robjects import r, pandas2ri, numpy2ri
    from rpy2.robjects.packages import importr
    pandas2ri.activate()
    ro.numpy2ri.activate()
    from ._helper import attr_preprocess, load_R_pkg
except:
    pass

    
def stat_computer(obj_name, nsamples=1):
    load_R_pkg("data.table")
    if nsamples == 1:
        return r(f"{obj_name}$stats") 
    else:
        return dict(stats=r(f"{obj_name}$stats"),
                    individual_stats=r(f"rbindlist(lapply(lapply({obj_name}$resultsBoth, (function (l) l$stats)), as.data.frame.list), idcol=TRUE)").set_index(".id")
                   )

def bootstrap(x, method, y=None, stat="mean", N=int(1e5), seed=0, block_size=1000, **kwargs):
    """
    Attrs:
        - method: ["t", "percentile", "bca", "bootstrapT"]
        
    Returns: bootstrap object (R)
    """
    kwargs_str = attr_preprocess(bootstrap, locals())
    load_R_pkg("resample")
    if y is None: # one sample       
        if method == "bootstrapT":
            ro.globalenv["bs"] = r(f"bootstrap(x, c({stat} = {stat}(x), sd = sd(x)), R=N, seed=0, block.size=block.size {kwargs_str})")
        else:
            ro.globalenv["bs"] = r(f"bootstrap(x, c({stat} = {stat}(x)), R=N, seed=0, block.size=block.size {kwargs_str})")
    else:
        if method == "bootstrapT":
            raise ValueError(f"method {method} not implemented for the 2-sample case")
        else:
            ro.globalenv["DF"] = pd.concat([pd.DataFrame(dict(val=x)).assign(Group="x"),
                                            pd.DataFrame(dict(val=y)).assign(Group="y")
                                           ], ignore_index=True, axis=0)
            ro.globalenv["bs"] = r(f"bootstrap2(DF, {stat}(val), treatment=Group, R=N, seed=seed, block.size=block.size {kwargs_str})")
    return ro.globalenv["bs"]

def CI_bootstrap(x, y=None, stat="mean", method="bootstrapT", expand=True, alpha=0.05, probs=None, alternative="two-sided", return_stats=False, **kwargs):
    """
    Check for the stats. Unbiased, functional statistics such as the mean should have zero bootstrap bias. If not, increase N.
    NOTE: s2 will have non-zero bootstrap bias because it is not functional.
    
    Attrs:
        - method: ["t", "percentile", "bca", "bootstrapT"].
        - alternative: ["two-sided", "less", "greater"].
    """
    if probs is None:
        if alternative == "less":
            ro.globalenv["probs"] = np.array([1 - alpha])
        elif alternative == "greater":
            ro.globalenv["probs"] = np.array([alpha])
        elif alternative == "two-sided":
            ro.globalenv["probs"] = np.array([alpha/2, 1 - alpha/2])
        else:
            raise ValueError(f"alternative {alternative} not valid. Available: 'greater', 'less', 'two-sided'")
            
    bs = bootstrap(x, method, y=y, stat=stat, **kwargs)
    
    if method == "bootstrapT":
        CI = r(f"CI.{method}(bs, probs=probs)") # bootstrap T is not affected by narrowness bias. Table 6
    else:
        ro.globalenv["expand"] = expand
        CI = r(f"CI.{method}(bs, probs=probs, expand=expand)")
    if CI.shape[0] == 1:
        CI = CI[0]
    
    if probs is None:
        if alternative == "less":
            CI = np.array([-np.inf, CI[0]]) # Only implemented for one at a time.
        elif alternative == "greater":
            CI = np.array([CI[0], np.inf])
            
    if return_stats:
        return bs, stat_computer("bs", nsamples=1 + int(y is not None)), CI
    else:
        return CI
    
def permutation(x, y=None, stat="mean", N=int(1e5), seed=0, block_size=1000,  **kwargs):
    """
    Returns: permutationTest object (R) and the results of the test. 
    
    The implementation in numba is faster and includes pairing option, which this one does not.
    """
    kwargs_str = attr_preprocess(permutation, locals())
    load_R_pkg("resample")   
    if y is None: # one sample       
        ro.globalenv["perm"] = r(f"permutationTest(x, c({stat} = {stat}(x)), R=N, seed=0, block.size=block.size {kwargs_str})")
    else:
        ro.globalenv["DF"] = pd.concat([pd.DataFrame(dict(val=x)).assign(Group="x"),
                                        pd.DataFrame(dict(val=y)).assign(Group="y")
                                       ], ignore_index=True, axis=0)
        ro.globalenv["perm"] = r(f"permutationTest2(DF, {stat}(val), treatment=Group, R=N, seed=seed, block.size=block.size {kwargs_str})")
        
    return ro.globalenv["perm"], stat_computer("perm", nsamples= 1 + int(y is not None))
