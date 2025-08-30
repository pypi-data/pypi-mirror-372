# SPDX-FileCopyrightText: 2025 Laurent Modolo <laurent@modolo.fr>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Archimedean Mixture Copula implementation for the IDR package.

This module provides the ArchMixtureCopula class, which represents a mixture of Archimedean copulas
(Clayton, Frank, and Gumbel) for flexible dependency modeling.

Classes:
    ArchMixtureCopula: Mixture copula combining multiple Archimedean copulas.
"""

import torch

from ..archimedean.clayton import ClaytonCopula
from ..archimedean.frank import FrankCopula
from ..archimedean.gumbel import GumbelCopula
from .mixture import MixtureCopula


class ArchMixtureCopula(MixtureCopula):
    """
    Mixture copula model combining multiple Archimedean copulas (Clayton, Frank, Gumbel).

    This class allows for flexible modeling of complex dependency structures by mixing
    several Archimedean copulas with learnable weights.

    Parameters:
        dim (int): Dimension of the copula (number of variables)
        copulas (list): List of Archimedean copula classes to include in the mixture.
                        Default is [ClaytonCopula, FrankCopula, GumbelCopula].
    """

    def __init__(
        self,
        dim: int,
        copulas: list = [ClaytonCopula(2), FrankCopula(2), GumbelCopula(2)],
        gpu: torch.device = torch.device("cpu"),
    ):
        """
        Initialize an Archimedean Mixture Copula.

        Parameters:
            dim (int): Dimension of the copula (number of variables)
            copulas (list): List of Archimedean copula classes to include in the mixture.
        """
        super().__init__(dim, "ArchMixture", copulas, gpu=gpu)
