.. ustat_var documentation master file, created by
   sphinx-quickstart on Wed Jul 16 11:30:32 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. _index:

Overview
=======================

This package implements non-parametric, unbiased estimators of the distribution of teacher effects described in `Rose, Schellenberg, and Shem-Tov (2022) <https://www.nber.org/papers/w30274>`__. 
These unbiased estimators are :math:`U\text{-}\mathrm{statistics}`, which provide minimum-variance unbiased estimators of population variances and covariances of latent parameters. 
The approach overcomes several issues experienced by Empirical Bayes (EB) techniques when estimating the distribution of teachers' 'value-added,' but can applied in any setting where the researcher seeks to estimate the distribution of agent-specific effects.

Brief introduction
------------------

`Rose, Schellenberg, and Shem-Tov (2022) <https://www.nber.org/papers/w30274>`__ employ this approach in the context of estimating teachers' effects on students across multiple outcomes (e.g., test scores, suspensions, and future crime). 
Throughout the package and its documentation, we use the same 'teacher' vocabulary, but the estimators in the ``ustat_var`` package would also apply in other settings.

The package assumes the researcher observes for each teacher :math:`j = 1, 2, ..., J` and outcome :math:`k = 1, 2, ..., K` 

.. math::
   
   y^k_j = (y^k_{j1}, ..., y^k_{jT_j})

where :math:`y^k_{jt} = a_j^k + e_{jt}^k`. The parameter :math:`a_j^k` represents teacher j's effect on outcome :math:`k`. Different outcomes could refer to separate measures (e.g., math test scores and reading test scores) or separate sub-populations (e.g., male and female students). The term :math:`e_{jt}^k` represents estimation error. The key asumptions are that: 

- :math:`\operatorname{E}[e_{jt}^k | a_j^k] = 0` for all :math:`j,k,t` 
- :math:`\operatorname{E}[e_{jt}^ke_{jt'}^{l}] = 0` for :math:`t \neq t` and all :math:`j,k,l`.

The package produces estimates of :math:`\operatorname{Var}(a_j^k)` and :math:`Cov(a_j^k,a_j^l)`, as well as estimates of their sampling variance. There are options to equally weight each of these variance/covariance parameters as well as to apply user-given weights. The package can also accomodate heavily unbalanced data, where :math:`T_j` differs across teachers and/or across outcomes within teacher.

- The |user manual| summarises the formulae for the estimators (used in the core ``ustat_var`` package functions) for transparency.
- `Rose, Schellenberg, and Shem-Tov (2022) <https://www.nber.org/papers/w30274>`__ contains the full discussion of the empirical setup and the required assumptions to interpret the estimates causally. 

**Authors**

- `Evan K. Rose <https://ekrose.github.io/>`__ (University of Chicago)
- `Jonathan T. Schellenberg <https://sites.google.com/view/jonathanschellenberg/>`__ (Amazon Web Services)
- `Yotam Shem-Tov <https://yotamshemtov.github.io/>`__ (UCLA)
- `Jack Mulqueeney <https://jkmulq.github.io/>`__ (University of Chicago)

Installation
------------

To install, execute 

.. code-block:: bash

    python3 -m pip install ustat_var


Contents
--------

- :ref:`usage` offers a brief explanation of how to use the core functions.
- :ref:`reference` offers a reference guide for each of the package's functions, including helper functions.

Suggested Citation
------------------

If you use this package, please cite the original paper:

.. code-block:: bibtex

    @workingpaper{rss2022effects,
      title        = {The Effects of Teacher Quality on Adult Criminal Justice Contact},
      author       = {Rose, Evan K. and Schellenberg, Jonathan T. and Shem-Tov, Yotam},
      institution  = {National Bureau of Economic Research},
      number       = {30274},
      year         = {2022},
      month        = jul,
      doi          = {10.3386/w30274},
      url          = {https://www.nber.org/papers/w30274},
      type         = {NBER Working Paper}
    }


.. toctree::
   :maxdepth: 1
   :caption: Pages:
   :hidden:

   usage
   reference

.. |user manual| replace::
   :download:`user manual </_downloads/ustat_var_user_manual.pdf>`
