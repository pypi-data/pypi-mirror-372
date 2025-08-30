# SPDX-FileCopyrightText: 2025 Laurent Modolo <laurent@modolo.fr>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Clayton Copula implementation for the IDR package.

This module provides the Clayton copula, an Archimedean copula that models
dependencies with specific tail dependence properties. It is exchangeable and
suitable for modeling positive dependence.

Classes:
    ClaytonCopula: Implements the Clayton copula and its generator functions.
"""

import torch

from .archimedean import ArchimedeanCopula


class ClaytonCopula(ArchimedeanCopula):
    r"""
    Clayton Copula for modeling positive dependence with tail dependence.

    The Clayton copula is an Archimedean copula that allows for modeling
    lower tail dependence between variables. It is exchangeable and is defined as:

        C_θ(u₁, ..., u_d) = (∑_i u_i^{-θ} - d + 1)^{-1/θ}

    Parameters:
        dim (int): Dimension of the copula.

    Attributes:
        _bound (list): Lower and upper bounds for the copula parameter θ.
    """

    def __init__(self, dim, gpu: torch.device = torch.device("cpu")):
        """
        Initialize a Clayton copula.

        Parameters:
            dim (int): Dimension of the copula.
        """
        super().__init__(dim, "Clayton", gpu=gpu)
        self._bound = [
            torch.tensor(0.0).to(self._gpu),
            torch.tensor(36.0).to(self._gpu),
        ]  # torch.tensor(198.0)]

    def psi(
        self, u: torch.Tensor, theta: torch.Tensor, log: bool = False
    ) -> torch.Tensor:
        """
        Generator function for the Clayton copula.

        Parameters:
            u (torch.Tensor): Input tensor.
            theta (torch.Tensor): Copula parameter.
            log (bool): If True, return log of the generator (not used here).

        Returns:
            torch.Tensor: Generator value.
        """
        return torch.pow(1.0 + u, -1.0 / theta)

    def ipsi(
        self, u: torch.Tensor, theta: torch.Tensor, log: bool = False
    ) -> torch.Tensor:
        """
        Inverse generator function for the Clayton copula.

        Parameters:
            u (torch.Tensor): Input tensor.
            theta (torch.Tensor): Copula parameter.
            log (bool): If True, return log of the inverse generator (not used here).

        Returns:
            torch.Tensor: Inverse generator value.
        """
        return torch.pow(u, -theta) - 1.0

    def random(self, n: int, theta: torch.Tensor) -> torch.Tensor:
        """
        Generate random samples from the Clayton copula.

        Parameters:
            n (int): Number of samples to generate.
            theta (torch.Tensor): Copula parameter.

        Returns:
            torch.Tensor: 2D tensor of shape (n, dim) containing samples from the copula.
        """
        u = torch.rand(n, self._dim).to(self._gpu)
        gam = (
            torch.distributions.Gamma(
                concentration=torch.tensor(1.0 / theta.item()), rate=torch.tensor(1.0)
            )
            .sample((n,))
            .to(self._gpu)
        )
        u = -torch.log(u) / gam.unsqueeze(1)
        return self.psi(u, theta)
