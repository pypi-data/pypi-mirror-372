.. _usage:

=====
Usage
=====

The package contains two functions that compute the non-parametric estimators presented in Appendix C of `Rose, Schellenberg, and Shem-Tov (2022) <https://www.nber.org/papers/w30274>`__.

The first, ``ustat.varcovar()``, estimates the variance-covariance, taking in two matrices as inputs::

    import ustat_var as ustat
    import numpy as np

    # Seed and data
    np.random.seed(18341)
    X,Y = ustat.generate_test_data.generate_data(n_teachers = 10, n_time = 5, n_arrays = 2, var_fixed = 1, var_noise = 1.0, cov_factor = 0.5)

    # Variance-covariance
    ustat.varcovar(X, X) # Var(X)
    ustat.varcovar(X, Y) # Cov(X, Y)

The second, ustat_samp_covar, estimates the sampling variance/covariance of varcovar. It takes four matrices as inputs, where ``ustat_samp_covar(A, B, C, D)`` yields :math:`\hat{\operatorname{Cov}}(\hat{\operatorname{Cov}}(A, B) − \operatorname{Cov}(A, B), \hat{\operatorname{Cov}} (C,D) − \operatorname{Cov}(C,D))` . For example, using the :math:`X,Y` generated above::

    # Base implementation through ustat_samp_covar.ustat_samp_covar() functions:
    ustat.ustat_samp_covar.ustat_samp_covar(X, X, X, X) # Sampling variance of Var(X)
    ustat.ustat_samp_covar.ustat_samp_covar(X, Y, X, Y) # Sampling variance of Cov(X, Y)

    # Faster implementation available in ustat_samp_covar.ustat_samp_covar_fast() function
    ustat.ustat_samp_covar.ustat_samp_covar_fast(X, X, X, X) # Also computes sampling variance of Var(X), but faster than above
    ustat.ustat_samp_covar.ustat_samp_covar_fast(X, Y, X, Y) # Also computes sampling variance of Cov(X, Y), but faster than above


For further details about these two functions and the required empirical setup, please see the |user manual|.

   


.. |user manual| replace::
   :download:`user manual </_downloads/ustat_var_user_manual.pdf>`

