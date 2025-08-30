# SPDX-FileCopyrightText: 2025 Laurent Modolo <laurent@modolo.fr>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Pseudo Mixture models for the IDR package.

This module provides alternative implementations of mixture models that focus on
modeling data as mixtures of independent and dependent components:

- IndepMixture: Models data as a mixture of independent variables and variables
  with dependency structure captured by a copula

These pseudo-mixture models provide a different approach to the mixture models in
the main mixture module, with a focus on directly modeling the contrast between
independence and dependence.
"""

from .indep_mixture import IndepMixture

__all__ = ["IndepMixture"]

__version__ = "0.0.1"
