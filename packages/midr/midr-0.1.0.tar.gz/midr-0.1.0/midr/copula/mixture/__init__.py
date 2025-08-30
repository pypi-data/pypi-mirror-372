# SPDX-FileCopyrightText: 2025 Laurent Modolo <laurent@modolo.fr>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Mixture Copula submodule for the IDR package.

This module provides implementations of mixture copula models, including:
- MixtureCopula: General mixture of copulas
- ArchMixtureCopula: Mixture of Archimedean copulas
- IndepMixtureCopula: Mixture including the independence copula

These models allow for flexible modeling of complex dependency structures by combining multiple copulas.
"""

from .mixture import MixtureCopula
from .archmixture import ArchMixtureCopula
from .indepmixture import IndepMixtureCopula

__all__ = ['MixtureCopula', 'ArchMixtureCopula', 'IndepMixtureCopula']
