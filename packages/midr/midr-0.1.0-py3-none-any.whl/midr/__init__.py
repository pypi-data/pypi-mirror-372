# SPDX-FileCopyrightText: 2025 Laurent Modolo <laurent@modolo.fr>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Irreproducible Discovery Rate (IDR) package.

This package provides tools for identifying and analyzing intrinsic dependencies
in multivariate data using copula-based methods.
"""

__version__ = "0.0.1"
from .auxilary import (
    bounded_transform,
    check_gpu,
    clr,
    clr1,
    clr1_inv,
    clr_inv,
    confusion_matrix,
    ecdf,
    fdr,
    fit,
    fit_closure,
    fit_set_tensor,
    fit_step,
    flatten_list,
    inverse_bounded_transform,
    inverse_cdf_interpolation,
    inverse_cdf_optimization,
    inverse_positive_transform,
    list2tensor,
    list_ecdf,
    merge_parameters,
    multiple_of_3_filter,
    partial_derivative,
    positive_transform,
    r_gaussian_mixture,
    r_indep_mixture,
    summary,
    tensor2list,
    zeros_proportion,
)
from .copula import (
    ArchimedeanCopula,
    ArchMixtureCopula,
    ClaytonCopula,
    Copula,
    EmpiricalBetaCopula,
    FrankCopula,
    GaussianCopula,
    GumbelCopula,
    IndependenceCopula,
    IndepMixtureCopula,
    MixtureCopula,
)
from .idr import compute_idr, idr_from_csv
from .marginal import (
    FixedGaussianMarginal,
    GaussianMarginal,
    GaussianMixtureMarginal,
    Marginal,
)
from .mixture import Mixture, Multivariate
from .pseudo_mixture import IndepMixture

__all__ = ["idr_from_csv", "compute_idr"]

__all__ += [
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

__all__ += [
    "Copula",
    "ArchimedeanCopula",
    "GumbelCopula",
    "FrankCopula",
    "ClaytonCopula",
    "IndependenceCopula",
    "ArchMixtureCopula",
    "IndepMixtureCopula",
    "MixtureCopula",
    "GaussianCopula",
    "EmpiricalBetaCopula",
]

__all__ += ["Mixture", "Multivariate"]
__all__ += ["IndepMixture"]
__all__ += [
    "Marginal",
    "GaussianMarginal",
    "FixedGaussianMarginal",
    "GaussianMixtureMarginal",
]
