# SPDX-FileCopyrightText: 2025 Laurent Modolo <laurent@modolo.fr>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Independence Copula implementation for the IDR package.

This module provides the IndependenceCopula class, which models complete independence
between variables. The independence copula is the product copula, representing the
case where all variables are mutually independent.

Classes:
    IndependenceCopula: Implements the independence copula and its methods.
"""

import torch


class IndependenceCopula:
    """
    Independence copula that models complete independence between variables.

    The independence copula is defined as the product of its arguments and represents
    the case where random variables are completely independent. It serves as a baseline
    model for comparison with other dependency structures.

    Parameters:
        dim (int): Dimension of the copula (number of variables)
    """

    def __init__(self, dim: int):
        """
        Initialize the IndependenceCopula.

        Parameters:
            dim (int): Dimension of the copula (number of variables)
        """
        self._dim = dim
        self._family = "Independence"

    def set_dim(self, dim: int):
        """
        Set the dimension of the copula.
        """
        self._dim = dim

    def cdf(self, u: torch.Tensor, log: bool = False) -> torch.Tensor:
        """
        Cumulative distribution function (CDF) of the independence copula.

        For the independence copula, the CDF is simply the product of the marginal CDFs.

        Parameters:
            u (torch.Tensor): 2D tensor of shape (n, dim) containing values in [0,1],
                              where each row represents a point to evaluate.
            log (bool): If True, return the log of the CDF. Default is False.

        Returns:
            torch.Tensor: 1D tensor of shape (n,) containing CDF values (or log-CDF if log=True)
        """
        if log:
            return u.log().sum(dim=1)
        return u.prod(dim=1)

    def pdf(self, u: torch.Tensor, log: bool = False) -> torch.Tensor:
        """
        Probability density function (PDF) of the independence copula.

        For the independence copula, the PDF is uniformly 1 over the entire domain,
        representing the fact that there is no dependency structure.

        Parameters:
            u (torch.Tensor): 2D tensor of shape (n, dim) containing values in [0,1],
                              where each row represents a point to evaluate.
            log (bool): If True, return the log of the PDF. Default is False.

        Returns:
            torch.Tensor: 1D tensor of shape (n,) containing PDF values (or log-PDF if log=True).
                          For independence copula: ones if log=False, zeros if log=True.
        """
        if log:
            return torch.zeros(u.shape[0])
        return torch.ones(u.shape[0])

    def likelihood(self, u: torch.Tensor, log: bool = False) -> torch.Tensor:
        """
        Likelihood of the independence copula for given data.

        For the independence copula, the likelihood is always 1 (or 0 in log space)
        since the joint PDF is 1 everywhere.

        Parameters:
            u (torch.Tensor): 2D tensor of shape (n, dim) containing values in [0,1],
                              where each row represents a data point.
            log (bool): If True, return the log-likelihood. Default is False.

        Returns:
            torch.Tensor: Scalar tensor containing the likelihood (or log-likelihood if log=True).
                         For independence copula: 1.0 if log=False, 0.0 if log=True.
        """
        if log:
            return torch.tensor(0.0)
        return torch.tensor(1.0)

    def random(self, n: int) -> torch.Tensor:
        """
        Generate random samples from the independence copula.

        For the independence copula, this simply generates uniform random variables
        since there is no dependency structure to model.

        Parameters:
            n (int): Number of samples to generate

        Returns:
            torch.Tensor: 2D tensor of shape (n, dim) containing uniform random samples in [0,1]
        """
        return torch.rand(n, self._dim)

    def parameters_size(self) -> int:
        """
        Get the number of parameters for the independence copula.

        The independence copula has no parameters since it represents the simplest
        dependency structure (complete independence).

        Returns:
            int: Number of parameters (always 0 for independence copula)
        """
        return 0
