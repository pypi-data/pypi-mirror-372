import inspect
import warnings
try:
    import rpy2.robjects as ro
    from rpy2.robjects import r, pandas2ri, numpy2ri
    from rpy2.robjects.packages import importr
    pandas2ri.activate()
    ro.numpy2ri.activate()
except:
    pass

def load_R_pkg(pkg):
    """Loads R package, installing it if needed."""
    if not ro.packages.isinstalled(pkg):
        warnings.warn(f"Package '{pkg}' not found. Proceeding to install it ...", RuntimeWarning)
        utils = importr("utils")
        utils.install_packages(pkg)
    r(f"library({pkg})")
    return

def attr_preprocess(func, attrs, clear_env=False):
    """
    Python enviroment -> R environment.
    Returns: str version of **kwargs.
    """
    var_kwd_names = [p.name for p in inspect.signature(func).parameters.values() if p.kind.name == "VAR_KEYWORD"]
    if var_kwd_names:
        var_kwd_name = var_kwd_names[0]
        attrs.update(attrs[var_kwd_name])
        if len(attrs[var_kwd_name]) > 0:
            kwargs_str = ", " + ", ".join([f"{k}={k}" for k in attrs[var_kwd_name].keys()])
        else:
            kwargs_str = ""
        del attrs[var_kwd_name]

    if clear_env:
        ro.globalenv.clear()
    for k, v in attrs.items():
        if v is not None:
            ro.globalenv[k.replace("_", ".")] = v
    return kwargs_str
