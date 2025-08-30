# PhD-utils

For people that have to compute and store a large variety of data and/or perform statistical inference.
Check the [tidypath and PhD-utils slides](https://github.com/medinajorge/PhD-utils/blob/master/tidypath_and_phdu.odp) for an overview.

## Keep your files tidy!

Don't spend time creating directories, deciding filenames, saving, loading, etc. Decorators `savefig` & `savedata` will do it for you with optimal compression. More info at the `tidypath` [repository](https://github.com/medinajorge/tidypath).

## Estimate confidence intervals
The module `phdu.resample` allows calls to the `resample` [R package](https://cran.r-project.org/web/packages/resample/resample.pdf).
- Provides CI and permutation tests.
- CIs can account narrowness bias, skewness and other errors in CI estimation, as indicated in the [article](https://arxiv.org/abs/1411.5279)
- Alternatively, use `phdu.stats.bootstrap` for numba-accelerated computation (does not call `resample`).

## Bootstrap-based power analysis.
Calculate the power for accepting H0 and estimate the needed sample size.
Function `power_analysis` in `phdu.stats.bootstrap` follows Efron-Tshibirani: An introduction to the bootstrap,  p. 381-384.

## Numba-accelerated permutation tests
Module `phdu.stats.tests.permutation`.
- Permutation tests for any statistic.
- Includes paired and block cases.

## Demo
- [tidypath and PhD-utils slides](https://github.com/medinajorge/PhD-utils/blob/master/tidypath_and_phdu.odp): instructions and use cases.
- [Example notebook](https://github.com/medinajorge/PhD-utils/blob/master/tests/Example.ipynb)

## Documentation
[Github pages](https://medinajorge.github.io/PhD-utils/phdu.html)

## Install
- For the R compatible installation first install R:

  ```conda install -c conda-forge r r-essentials r-base```

- Install with dependencies:

  ```pip install phdu[dependencies]```

  Where `dependencies` can be `base` (recommended), `all`, `r` (needed for `resample` to work), `statsmodels`, `matplotlib` or `plotly`.
