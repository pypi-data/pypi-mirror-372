# SPDX-FileCopyrightText: 2025 Laurent Modolo <laurent@modolo.fr>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Archimedean Copula submodule for the IDR package.

This module provides implementations of the Archimedean copula family, including:
- ArchimedeanCopula: Abstract base class for Archimedean copulas
- GumbelCopula: Gumbel family copula
- FrankCopula: Frank family copula
- ClaytonCopula: Clayton family copula

These copulas are used to model dependencies between random variables in a flexible and interpretable way.
"""

from .archimedean import ArchimedeanCopula
from .gumbel import GumbelCopula
from .frank import FrankCopula
from .clayton import ClaytonCopula

__all__ = ['ArchimedeanCopula', 'GumbelCopula', 'FrankCopula', 'ClaytonCopula']
