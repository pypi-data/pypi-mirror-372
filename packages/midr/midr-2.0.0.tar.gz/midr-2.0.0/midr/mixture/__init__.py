# SPDX-FileCopyrightText: 2025 Laurent Modolo <laurent@modolo.fr>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Mixture models for complex distribution modeling in the IDR package.

This module provides implementations of various mixture models for handling
complex multivariate distributions:

- Mixture: Base class for general mixture models
- Multivariate: Multivariate distribution combining marginals with a copula
- IndepMixture: Independence mixture model for separating dependent and independent components

Mixture models allow for modeling complex distributions by combining simpler
component distributions, providing flexibility for representing heterogeneous data.
"""

from .mixture import Mixture
from .multivariate import Multivariate

__all__ = ['Mixture', 'Multivariate']
