# SPDX-FileCopyrightText: 2025 Laurent Modolo <laurent@modolo.fr>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Copula models for dependency structure modeling in the IDR package.

This module provides implementations of various copula models for capturing
dependencies between random variables.

Copulas are mathematical functions that join multivariate distribution functions to
their one-dimensional marginal distribution functions, allowing for flexible modeling
of dependencies separate from the marginal distributions.

Available Copula Models:
------------------------
- Base Copula: Abstract base class defining common copula functionality.
- Archimedean Copulas: Family of copulas including Gumbel, Frank, and Clayton.
- Independence Copula: Models complete independence between variables.
- Mixture Copulas: Weighted combinations of other copulas for modeling complex dependencies.
- Gaussian Copula: Captures dependencies using a multivariate normal structure.
- Empirical Beta Copula: Nonparametric copula based on Beta kernel density estimation.

These copula models enable flexible and interpretable modeling of multivariate dependencies,
which is essential for high-dimensional data analysis and intrinsic dependency discovery.
"""

from .archimedean import ArchimedeanCopula, GumbelCopula, FrankCopula, ClaytonCopula
from .independence import IndependenceCopula
from .mixture import ArchMixtureCopula, IndepMixtureCopula, MixtureCopula
from .copula import Copula
from .gaussian import GaussianCopula
from .empirical_beta import EmpiricalBetaCopula

__all__ = ['Copula', 'ArchimedeanCopula', 'GumbelCopula', 'FrankCopula', 'ClaytonCopula', 'IndependenceCopula', 'ArchMixtureCopula', 'IndepMixtureCopula', 'MixtureCopula', 'GaussianCopula', 'EmpiricalBetaCopula']

__version__ = "0.0.1"
