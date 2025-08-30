# SPDX-FileCopyrightText: 2025 Laurent Modolo <laurent@modolo.fr>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Marginal distribution models for the IDR package.

This module provides various marginal distribution implementations used in the IDR framework.

Features:
- Base Marginal: Abstract base class for implementing marginal distributions.
- Gaussian: Standard Gaussian (normal) distribution.
- Fixed Gaussian: Gaussian distribution with fixed mean (set to zero).
- Gaussian Mixture: Mixture of Gaussian distributions for modeling complex shapes.

Marginal distributions are used to model individual variables before combining them
with copulas to form multivariate distributions.
"""

from .marginal import Marginal
from .gaussian import GaussianMarginal
from .fixed_gaussian import FixedGaussianMarginal
from .gaussian_mixture import GaussianMixtureMarginal

__all__ = ['Marginal', 'GaussianMarginal', 'FixedGaussianMarginal', 'GaussianMixtureMarginal']
