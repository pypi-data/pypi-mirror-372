# SPDX-FileCopyrightText: 2025 Laurent Modolo <laurent@modolo.fr>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Frank Copula implementation for the IDR package.

This module provides the FrankCopula class, an Archimedean copula that allows for modeling
dependencies with a flexible tail structure. It includes methods for the generator, inverse generator,
random sampling, and utility functions for the logarithmic series distribution.

Classes:
    FrankCopula: Archimedean Frank copula for dependency modeling.

Functions:
    rlogseries_LS: Generate a random variate from the logarithmic series distribution (Algorithm LS).
    rlogseries_LK_ln1p: Generate a random variate from the logarithmic series distribution (Algorithm LK).
    rlogseries_ln1p: Generate random variates from the logarithmic series distribution using log(1-alpha) parameterization.
"""

import torch

from .archimedean import ArchimedeanCopula


class FrankCopula(ArchimedeanCopula):
    r"""
    The Frank copula is an Archimedean copula that allows for flexible modeling of dependencies,
    including both positive and negative dependence, with no tail dependence.

    Mathematical definition:
        C_θ(u₁, ..., u_d) = -1/θ * log(1 + Π_{j=1}^d (exp(-θ u_j) - 1) / (exp(-θ) - 1))

    Parameters:
        dim (int): Dimension of the copula.

    Methods:
        psi: Generator function for the Frank copula.
        ipsi: Inverse generator function for the Frank copula.
        random: Generate random samples from the Frank copula.
    """

    def __init__(self, dim, gpu: torch.device = torch.device("cpu")):
        """
        Initialize a Frank copula.

        Parameters:
            dim (int): Dimension of the copula.
        """
        super().__init__(dim, "Frank", gpu=gpu)
        self._bound = [
            torch.tensor(0.0).to(self._gpu),
            torch.tensor(398.0).to(self._gpu),
        ]

    def psi(
        self, u: torch.Tensor, theta: torch.Tensor, log: bool = False
    ) -> torch.Tensor:
        """
        Generator function for the Frank copula.

        Parameters:
            u (torch.Tensor): Input tensor.
            theta (torch.Tensor): Copula parameter.
            log (bool): If True, return log of the generator (not used here).

        Returns:
            torch.Tensor: Generator value.
        """
        return -1.0 / theta * torch.log(1.0 + torch.exp(-u) * (torch.exp(-theta) - 1.0))

    def ipsi(
        self, u: torch.Tensor, theta: torch.Tensor, log: bool = False
    ) -> torch.Tensor:
        """
        Inverse generator function for the Frank copula.

        Parameters:
            u (torch.Tensor): Input tensor.
            theta (torch.Tensor): Copula parameter.
            log (bool): If True, return log of the inverse generator (not used here).

        Returns:
            torch.Tensor: Inverse generator value.
        """
        return -torch.log((torch.exp(-theta * u) - 1.0) / (torch.exp(-theta) - 1.0))

    def random(self, n: int, theta: torch.Tensor) -> torch.Tensor:
        """
        Generate random samples from the Frank copula.

        Parameters:
            n (int): Number of samples to generate.
            theta (torch.Tensor): Copula parameter.

        Returns:
            torch.Tensor: Samples from the Frank copula of shape (n, dim).
        """
        u = torch.rand(n, self._dim)
        fr = rlogseries_ln1p(n, -theta, self._gpu)
        fr = fr.view(-1, 1).repeat(1, self._dim)
        u = -torch.log(u) / fr
        return self.psi(u, theta)


def rlogseries_LS(alpha, gpu):
    """
    Algorithm LS of Kemp (1981).
    Generate a random variate following the logarithmic series distribution Log(alpha).

    Parameters:
        alpha (float): Parameter in the range (0, 1).

    Returns:
        int: A random variate.
    """
    t = -alpha / torch.log(torch.tensor(1.0).to(gpu) - alpha)
    u = torch.rand(1).item()
    p = t
    x = 1
    while u > p:
        u = u - p
        x = x + 1
        p = p * alpha * (x - 1) / x
    return x


def rlogseries_LK_ln1p(h, gpu):
    """
    Algorithm LK of Kemp (1981) using h = log(1 - alpha) as parameter.
    Generate a random variate following the logarithmic series distribution Log(1 - exp(h)).

    Parameters:
        h (float): Parameter in the range (-∞, 0).

    Returns:
        float: A random variate.
    """
    alpha = -torch.expm1(h)  # alpha = 1 - exp(h)
    u2 = torch.rand(1)
    if u2 > alpha:
        return 1.0
    u1 = torch.rand(1).item()
    h_ = u1 * h
    q = -torch.expm1(h_)
    if u2 < q * q:
        log_q = (
            torch.log1p(-torch.exp(h_))
            if h_ > -torch.log(torch.tensor(2.0).to(gpu))
            else torch.log(-torch.expm1(h_))
        )
        if log_q == 0.0:
            return float("Inf")
        return 1.0 + torch.floor(torch.log(u2) / log_q).item()
    else:
        return 1.0 if u2 > q else 2.0


def rlogseries_ln1p(n, h, gpu):
    """
    Generate random variates from the logarithmic series distribution using h = log(1 - alpha) as parameter.

    Parameters:
        n (int): Sample size.
        h (float): Parameter in the range (-∞, 0), where h = log(1 - alpha).

    Returns:
        torch.Tensor: A tensor of random variates.
    """
    # h == log(1 - alpha) < 0 <==> alpha = 1 - exp(h) = -expm1(h)
    # alpha < 0.95 <==> 1 - exp(h) < 0.95 <==> exp(h) > 0.05 <==> h > log(0.05) = -2.995732
    samples = []
    if h > -3.0:  # alpha < 0.9502
        alpha = -torch.expm1(h)
        for _ in range(n):
            samples.append(rlogseries_LS(alpha, gpu))
    else:  # h <= -3
        for _ in range(n):
            samples.append(rlogseries_LK_ln1p(h, gpu))
    return torch.tensor(samples).to(gpu)
