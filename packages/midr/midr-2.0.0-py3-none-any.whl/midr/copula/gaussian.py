# SPDX-FileCopyrightText: 2025 Laurent Modolo <laurent@modolo.fr>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Gaussian Copula implementation for the IDR package.

This module provides the GaussianCopula class, which models dependencies between variables
using a multivariate normal copula structure. It includes methods for computing the PDF,
CDF, and generating random samples, as well as parameter transformations to ensure valid
covariance matrices.

Classes:
    GaussianCopula: Copula model based on the multivariate normal distribution.

Functions:
    make_positive_definite: Ensure a matrix is positive definite.
    sigmoid_scale_off_diagonal: Scale off-diagonal elements of a matrix to [0,1] using sigmoid.
"""

from typing import Dict

import torch

from ..auxilary import ecdf, merge_parameters
from .copula import Copula


def sigmoid_scale_off_diagonal(matrix):
    """
    Scale off-diagonal elements of a square matrix to [0,1] using the sigmoid function.

    Parameters:
        matrix (torch.Tensor): Input square matrix.

    Returns:
        torch.Tensor: Matrix with off-diagonal elements scaled to [0,1].
    """
    n = matrix.shape[0]
    eye = torch.eye(n, device=matrix.device)
    off_diag_mask = 1.0 - eye
    diag_part = matrix * eye
    off_diag_part = torch.sigmoid(matrix * off_diag_mask)
    result = diag_part + off_diag_part * off_diag_mask

    return result


class GaussianCopula(Copula):
    """
    Gaussian copula model for capturing dependencies between random variables.

    This class implements a copula based on the multivariate normal distribution,
    allowing for flexible modeling of dependencies via the covariance matrix.

    Parameters:
        dim (int): Dimension of the data (number of variables)
    """

    def __init__(self, dim: int, gpu: torch.device = torch.device("cpu")):
        """
        Initialize a GaussianCopula.

        Parameters:
            dim (int): Dimension of the copula (number of variables)
        """
        super().__init__(dim, "Gaussian", dim**2, gpu=gpu)

    def split_parameters(self, theta: torch.Tensor) -> Dict[str, torch.Tensor]:
        """
        Split the parameter tensor into a covariance matrix.

        Parameters:
            theta (torch.Tensor): Parameter tensor of length dim^2

        Returns:
            Dict[str, torch.Tensor]: Dictionary with 'sigma' as the covariance matrix
        """
        parameters = {}
        parameters["sigma"] = theta.reshape(self._dim, self._dim)
        parameters["sigma"] = parameters["sigma"] * (
            1 - torch.diag(torch.ones(self._dim))
        )
        parameters["sigma"] = parameters["sigma"] + torch.diag(torch.ones(self._dim))
        parameters["sigma"] = sigmoid_scale_off_diagonal(parameters["sigma"])
        upper = torch.triu(parameters["sigma"])
        parameters["sigma"] = (
            upper + upper.T - torch.diag(torch.diag(parameters["sigma"]))
        )
        return parameters

    def cdf(
        self, u: torch.Tensor, theta: torch.Tensor, log: bool = False
    ) -> torch.Tensor:
        """
        Compute the cumulative distribution function (CDF) of the Gaussian copula.

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
        Compute the probability density function (PDF) of the Gaussian copula.

        Parameters:
            u (torch.Tensor): Input tensor of shape (n, dim) containing points in [0,1]^d space
            theta (torch.Tensor): Parameters for the distribution
            log (bool): If True, return the log-PDF. Default is False

        Returns:
            torch.Tensor: PDF values at points u (or log-PDF if log=True)
        """
        parameters = self.split_parameters(theta)
        x = torch.stack(
            [
                torch.distributions.normal.Normal(
                    loc=torch.tensor([0.0]), scale=torch.tensor([1.0])
                )
                .icdf(u[:, j])
                .to(self._gpu)
                for j in range(self._dim)
            ],
            dim=1,
        )

        pdf = torch.distributions.multivariate_normal.MultivariateNormal(
            loc=torch.zeros(self._dim), covariance_matrix=parameters["sigma"]
        ).log_prob(x)
        if log:
            return pdf
        else:
            return pdf.exp()

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
        parameters = self.split_parameters(theta)
        return merge_parameters(parameters).flatten()

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
        parameters = self.split_parameters(theta)
        return merge_parameters(parameters).flatten()

    def random(self, n: int, theta: torch.Tensor) -> torch.Tensor:
        """
        Generate random samples from the Gaussian copula.

        Parameters:
            n (int): Number of samples to generate
            theta (torch.Tensor): Parameters of the copula

        Returns:
            torch.Tensor: 2D tensor of shape (n, dim) containing samples from the copula
        """
        parameters = self.split_parameters(theta)
        # Note: 'mu' is not defined in parameters; this may need to be set to zeros
        # for a standard Gaussian copula.
        return ecdf(
            torch.distributions.multivariate_normal.MultivariateNormal(
                loc=torch.zeros(self._dim), covariance_matrix=parameters["sigma"]
            ).sample((n,))
        )
