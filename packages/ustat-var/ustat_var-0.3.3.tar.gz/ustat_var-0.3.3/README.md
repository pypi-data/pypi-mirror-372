## Overview

This package contains the non-parametric unbiased estimators of the variance of teacher effects described in [Rose, Schellenberg, and Shem-Tov (2022)](https://www.nber.org/papers/w30274). These unbiased estimators are $U$-statistics, which provide minimum-variance unbiased estimators of population parameters for arbitrary probability distributions. The $U$-statistic approach overcomes several issues experienced by Empirical Bayes (EB) techniques when estimating an agent's 'value-added'.
This readme is meant to be brief overview of how to install the package and how to use it -- the complete package documentation can be found [here](https://ustat-var.readthedocs.io/en/latest/).
### Authors

-   [Evan K. Rose](https://ekrose.github.io/) (University of Chicago)
-   [Jonathan T. Schellenberg](https://sites.google.com/view/jonathanschellenberg/) (Amazon Web Services)
-   [Yotam Shem-Tov](https://yotamshemtov.github.io/) (UCLA)
-   [Jack Mulqueeney](https://jkmulq.github.io) (University of Chicago)

## Installation

To install:

```         
python3 -m pip install ustat_var
```

## Usage

The package contains two functions that compute the non-parametric estimators presented in Appendix C of [Rose, Schellenberg, and Shem-Tov (2022)](https://www.nber.org/papers/w30274).

The first, `ustat.varcovar` estimates the variance-covariance, taking in two matrices as inputs:

``` python
import ustat_var as ustat
import numpy as np

# Seed and data
np.random.seed(18341)
X,Y = ustat.generate_test_data.generate_data(n_teachers = 10, n_time = 5, n_arrays = 2, var_fixed = 1, var_noise = 1.0, cov_factor = 0.5)

# Variance-covariance
ustat.varcovar(X, X) # Var(X)
ustat.varcovar(X, Y) # Cov(X, Y)
```

The second, `ustat_samp_covar`, estimates the sampling variance/covariance of `varcovar`. It takes four matrices as inputs, where `ustat_samp_covar(A, B, C, D)` yields $\hat{Cov}\big(\hat{Cov}(A,B) - Cov(A,B), \hat{Cov}(C,D) - Cov(C,D)\big)$. For example:

``` python
 # Base implementation through ustat_samp_covar.ustat_samp_covar() functions:
ustat.ustat_samp_covar.ustat_samp_covar(X, X, X, X) # Sampling variance of Var(X)
ustat.ustat_samp_covar.ustat_samp_covar(X, Y, X, Y) # Sampling variance of Cov(X, Y)

# Faster implementation available in ustat_samp_covar.ustat_samp_covar_fast() function
ustat.ustat_samp_covar.ustat_samp_covar_fast(X, X, X, X) # Also computes sampling variance of Var(X), but faster than above
ustat.ustat_samp_covar.ustat_samp_covar_fast(X, Y, X, Y) # Also computes sampling variance of Cov(X, Y), but faster than above
```

You can find further details about each function in the package [documentation](https://ustat-var.readthedocs.io/en/latest/).
