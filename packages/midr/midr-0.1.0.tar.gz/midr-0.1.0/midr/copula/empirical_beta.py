# SPDX-FileCopyrightText: 2025 Laurent Modolo <laurent@modolo.fr>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Empirical Beta Copula implementation for the IDR package.

This module provides an empirical copula based on Beta kernel density estimation,
suitable for modeling dependencies in multivariate data on the unit hypercube [0,1]^d.
It uses the ranks of the data to construct a nonparametric copula density estimate.

Classes:
    EmpiricalBetaCopula: Empirical copula using Beta kernel density estimation.

Functions:
    beta_kernel: Compute the log-probability of a value under a Beta kernel.
    beta_kernel_iner_sum: Compute the sum of Beta kernel log-probabilities for a single observation.
    beta_kde: Compute the Beta kernel density estimate for a set of observations.
"""

from typing import Dict, Optional

import torch

from .copula import Copula


class EmpiricalBetaCopula(Copula):
    """
    Empirical Beta Copula for modeling dependencies in multivariate data.

    This copula estimates the joint distribution using Beta kernel density estimation
    based on the empirical ranks of the data. It is particularly useful for modeling
    dependencies in data on the unit hypercube [0,1]^d.

    Parameters:
        dim (int): Dimension of the copula (number of variables)
        rank (Optional[torch.Tensor]): Precomputed rank tensor for the data (optional)
    """

    def __init__(
        self,
        dim: int,
        rank: Optional[torch.Tensor] = None,
        gpu: torch.device = torch.device("cpu"),
    ):
        """
        Initialize the Empirical Beta Copula.

        Parameters:
            dim (int): Dimension of the copula
            rank (Optional[torch.Tensor]): Precomputed rank tensor (optional)
        """
        super().__init__(dim, "EmpiricalBeta", 2, gpu=gpu)
        if rank is None:
            self._rank = None
        else:
            self._rank = rank.to(gpu)

    def split_parameters(self, theta: torch.Tensor) -> Dict[str, torch.Tensor]:
        """
        Split the parameter tensor into bandwidth and resolution.

        Parameters:
            theta (torch.Tensor): Parameter tensor

        Returns:
            Dict[str, torch.Tensor]: Dictionary with 'bandwidth' and 'resolution'
        """
        parameters = {}
        parameters["bandwidth"] = theta[0].to(self._gpu)
        parameters["resolution"] = theta[1].to(self._gpu)
        return parameters

    def cdf(
        self, u: torch.Tensor, theta: torch.Tensor, log: bool = False
    ) -> torch.Tensor:
        """
        Compute the cumulative distribution function (CDF) of the empirical beta copula.

        Parameters:
            u (torch.Tensor): Input tensor of shape (n, dim) containing points in [0,1]^d space
            theta (torch.Tensor): Parameters for the distribution
            log (bool): If True, return the log-CDF. Default is False

        Returns:
            torch.Tensor: CDF values at points u (or log-CDF if log=True)
        """
        return torch.zeros_like(u[:, 0])

    def pdf(
        self, u: torch.Tensor, theta: torch.Tensor, log: bool = False
    ) -> torch.Tensor:
        """
        Compute the probability density function (PDF) of the empirical beta copula.

        Parameters:
            u (torch.Tensor): Input tensor of shape (n, dim) containing points in [0,1]^d space
            theta (torch.Tensor): Parameters for the distribution
            log (bool): If True, return the log-PDF. Default is False

        Returns:
            torch.Tensor: PDF values at points u (or log-PDF if log=True)
        """
        u.to(self._gpu)
        if self._rank is None:
            rank = u.argsort(dim=0, stable=True).argsort(dim=0, stable=True) + 1.0
        else:
            rank = self._rank
        pdf = beta_kde(x=u, rank=rank)
        if log:
            return pdf.log()
        else:
            return pdf

    def theta_transform(self, theta: torch.Tensor) -> torch.Tensor:
        """
        Transform parameters for optimization.

        This method can be overridden to transform parameters to an unconstrained space
        for optimization purposes. The default implementation returns parameters unchanged.

        Parameters:
            theta (torch.Tensor): Original parameters

        Returns:
            torch.Tensor: Transformed parameters
        """
        return theta

    def theta_transform_inverse(self, theta: torch.Tensor) -> torch.Tensor:
        """
        Inverse transform parameters after optimization.

        This method can be overridden to transform parameters back from an unconstrained space
        to their original constrained space after optimization. The default implementation
        returns parameters unchanged.

        Parameters:
            theta (torch.Tensor): Transformed parameters

        Returns:
            torch.Tensor: Original parameters with constraints satisfied
        """
        return theta

    def random(self, n: int, theta: torch.Tensor) -> torch.Tensor:
        """
        Generate random samples from the empirical beta copula.

        Parameters:
            n (int): Number of samples to generate
            theta (torch.Tensor): Parameters of the copula

        Returns:
            torch.Tensor: 2D tensor of shape (n, dim) containing samples from the copula
        """
        return torch.rand(n, self._dim)


def beta_kernel(x_i: torch.Tensor, rank: torch.Tensor, n: int) -> torch.Tensor:
    """
    Compute the log-probability of x_i under a Beta kernel with given rank and sample size.

    Parameters:
        x_i (torch.Tensor): Input tensor for a single observation
        rank (torch.Tensor): Rank tensor for the observation
        n (int): Sample size

    Returns:
        torch.Tensor: Log-probability of x_i under the Beta kernel
    """
    alpha = rank
    beta = n + 1 - rank
    return torch.distributions.beta.Beta(alpha, beta).log_prob(x_i)


def beta_kernel_iner_sum(x_i: torch.Tensor, rank: torch.Tensor, n: int) -> torch.Tensor:
    """
    Compute the sum of Beta kernel log-probabilities for a single observation.

    Parameters:
        x_i (torch.Tensor): Input tensor for a single observation
        rank (torch.Tensor): Rank tensor for the observation
        n (int): Sample size

    Returns:
        torch.Tensor: Sum of exponentiated log-probabilities for the observation
    """
    vec_func = torch.func.vmap(
        lambda rank: beta_kernel(x_i=x_i, rank=rank, n=n).sum().exp()
    )
    return vec_func(rank).sum()


def beta_kde(x: torch.Tensor, rank: torch.Tensor) -> torch.Tensor:
    """
    Compute the Beta kernel density estimate for a set of observations.

    Parameters:
        x (torch.Tensor): Input tensor of shape (n, dim) containing points in [0,1]^d space
        rank (torch.Tensor): Rank tensor for the observations

    Returns:
        torch.Tensor: Beta kernel density estimate for each observation
    """
    n = x.shape[0]
    vec_func = torch.func.vmap(lambda x_i: beta_kernel_iner_sum(x_i, rank, n + 1))
    return vec_func(x) / n
