# SPDX-FileCopyrightText: 2025 Laurent Modolo <laurent@modolo.fr>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Auxiliary utilities for the IDR package.

This module provides a collection of utility functions to support the core IDR functionality.

Features:
- Optimization and fitting functions for model training and parameter estimation
- Plotting and visualization tools for diagnostics and results
- Empirical cumulative distribution functions (ECDF) for nonparametric statistics
- Tensor transformation utilities for reshaping and manipulating data
- Mathematical operations for statistical analysis and copula computations
- Data handling and manipulation functions for input/output and preprocessing

Each submodule is documented individually. See their respective docstrings for details.
"""

from .ecdf import ecdf, list_ecdf
from .fdr import fdr
from .fit import fit, fit_closure, fit_set_tensor, fit_step
from .transform import (
    bounded_transform,
    clr,
    clr1,
    clr1_inv,
    clr_inv,
    inverse_bounded_transform,
    inverse_cdf_interpolation,
    inverse_cdf_optimization,
    inverse_positive_transform,
    list2tensor,
    merge_parameters,
    positive_transform,
    tensor2list,
)
from .utils import (
    check_gpu,
    confusion_matrix,
    flatten_list,
    multiple_of_3_filter,
    partial_derivative,
    r_gaussian_mixture,
    r_indep_mixture,
    summary,
    zeros_proportion,
)

__all__ = [
    "check_gpu",
    "partial_derivative",
    "fit",
    "fit_set_tensor",
    "fit_step",
    "fit_closure",
    "ecdf",
    "list_ecdf",
    "tensor2list",
    "list2tensor",
    "clr",
    "clr1",
    "clr_inv",
    "clr1_inv",
    "positive_transform",
    "inverse_positive_transform",
    "inverse_cdf_optimization",
    "inverse_cdf_interpolation",
    "bounded_transform",
    "inverse_bounded_transform",
    "merge_parameters",
    "summary",
    "flatten_list",
    "r_gaussian_mixture",
    "r_indep_mixture",
    "confusion_matrix",
    "fdr",
    "zeros_proportion",
    "multiple_of_3_filter",
]
