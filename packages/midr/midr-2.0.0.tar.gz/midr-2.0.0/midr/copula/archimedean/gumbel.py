# SPDX-FileCopyrightText: 2025 Laurent Modolo <laurent@modolo.fr>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Gumbel Copula implementation for the IDR package.

This module provides the GumbelCopula class, an Archimedean copula that models upper tail dependence.
It includes methods for the copula generator, inverse generator, and random sample generation.

Classes:
    GumbelCopula: Archimedean copula with Gumbel generator.
"""

from .archimedean import ArchimedeanCopula
import torch

class GumbelCopula(ArchimedeanCopula):
    r"""
    Gumbel Copula (Archimedean family).

    The Gumbel copula is an Archimedean copula that allows modeling of upper tail dependence
    between variables. It is exchangeable and defined as:

        C_\theta (u_1, ..., u_d) = exp(-((sum_i (-log u_i)^\theta)^{1/\theta}))

    Parameters:
        dim (int): Dimension of the copula.
    """
    def __init__(self, dim, gpu: torch.device = torch.device("cpu")):
        """
        Initialize a Gumbel copula.

        Parameters:
            dim (int): Dimension of the copula.
        """
        super().__init__(dim, "Gumbel", gpu=gpu)
        self._bound = [torch.tensor(1.0).to(self._gpu), torch.tensor(100.0).to(self._gpu)]

    def psi(self, u: torch.Tensor, theta: torch.Tensor, log: bool=False) -> torch.Tensor:
        """
        Generator function for the Gumbel copula.

        Parameters:
            u (torch.Tensor): Input tensor.
            theta (torch.Tensor): Copula parameter.
            log (bool): If True, return log of the generator (not used here).

        Returns:
            torch.Tensor: Generator value.
        """
        return torch.exp(-torch.pow(u, 1.0 / theta))

    def ipsi(self, u: torch.Tensor, theta: torch.Tensor, log: bool=False) -> torch.Tensor:
        """
        Inverse generator function for the Gumbel copula.

        Parameters:
            u (torch.Tensor): Input tensor.
            theta (torch.Tensor): Copula parameter.
            log (bool): If True, return log of the inverse generator (not used here).

        Returns:
            torch.Tensor: Inverse generator value.
        """
        return torch.pow(-torch.log(u), theta)

    def random(self, n: int, theta: torch.Tensor) -> torch.Tensor:
        """
        Generate random samples from the Gumbel copula.

        Parameters:
            n (int): Number of samples to generate.
            theta (torch.Tensor): Copula parameter.

        Returns:
            torch.Tensor: Samples from the Gumbel copula of shape (n, dim).
        """
        u = torch.rand(n, self._dim)
        u = -torch.log(u) / r_pos_stable_s(n, 1.0 / theta, self._gpu).unsqueeze(1)
        return self.psi(u, theta)

def r_pos_stable_s(n: int, alpha: torch.Tensor, gpu):
    """
    Generate random samples from the positive stable distribution.

    Parameters:
        n (int): Number of samples to generate.
        alpha (float or torch.Tensor): Parameter of the distribution, must be < 1.

    Returns:
        torch.Tensor: Samples from the positive stable distribution.
    """
    theta = torch.rand(n) * torch.pi
    W = torch.distributions.Exponential(rate = torch.tensor(1.0).to(gpu)).sample((n,)).to(gpu)
    I_a = 1 - alpha
    sin_I_a_theta = torch.sin(I_a * theta)
    sin_alpha_theta = torch.sin(alpha * theta)
    sin_theta = torch.sin(theta)
    a = sin_I_a_theta * torch.pow(torch.pow(sin_alpha_theta, alpha) / sin_theta, 1/I_a)
    return torch.pow(a / W, I_a/alpha)
