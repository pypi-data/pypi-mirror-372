# SPDX-FileCopyrightText: 2025 Laurent Modolo <laurent@modolo.fr>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from abc import ABC, abstractmethod

import torch


class Marginal(ABC):
    """
    Abstract base class for marginal distributions.

    This class defines the interface for all marginal distributions in the IDR package.
    Concrete implementations must provide methods for computing CDFs, inverse CDFs,
    and PDFs.

    Parameters:
    family (str): Name of the distribution family
    parameters_size (int): Number of parameters in the distribution
    """

    def __init__(
        self, family: str, parameters_size: int, gpu: torch.device = torch.device("cpu")
    ):
        """
        Initialize a marginal distribution.

        Parameters:
        family (str): Name of the distribution family
        parameters_size (int): Number of parameters in the distribution
        """
        self._family = family
        self._parameters_size = parameters_size
        self._gpu = gpu

    @abstractmethod
    def cdf(
        self, x: torch.Tensor, theta: torch.Tensor, log: bool = False
    ) -> torch.Tensor:
        """
        Compute the cumulative distribution function.

        Parameters:
        x (torch.Tensor): Input tensor of values to evaluate the CDF at
        theta (torch.Tensor): Parameters of the distribution
        log (bool): If True, return the log-CDF. Default is False

        Returns:
        torch.Tensor: CDF values at points x (or log-CDF if log=True)
        """
        pass

    @abstractmethod
    def cdf_inv(
        self, x: torch.Tensor, theta: torch.Tensor, log: bool = False
    ) -> torch.Tensor:
        """
        Compute the inverse CDF (quantile function).

        Parameters:
        x (torch.Tensor): Input tensor of probabilities in [0,1] to find quantiles for
        theta (torch.Tensor): Parameters of the distribution
        log (bool): If True, input is treated as log-probabilities. Default is False

        Returns:
        torch.Tensor: Quantiles corresponding to probabilities in x
        """
        pass

    @abstractmethod
    def pdf(
        self, x: torch.Tensor, theta: torch.Tensor, log: bool = False
    ) -> torch.Tensor:
        """
        Compute the probability density function.

        Parameters:
        x (torch.Tensor): Input tensor of values to evaluate the PDF at
        theta (torch.Tensor): Parameters of the distribution
        log (bool): If True, return the log-PDF. Default is False

        Returns:
        torch.Tensor: PDF values at points x (or log-PDF if log=True)
        """
        pass

    def pdf_cdf_inv(
        self, u: torch.Tensor, theta: torch.Tensor, log: bool = False
    ) -> torch.Tensor:
        """
        Compute PDF values at quantiles corresponding to probabilities u.

        This is a convenience method that computes quantiles using cdf_inv
        and then evaluates the PDF at those quantiles.

        Parameters:
        u (torch.Tensor): Input tensor of probabilities in [0,1]
        theta (torch.Tensor): Parameters of the distribution
        log (bool): If True, return the log-PDF. Default is False

        Returns:
        torch.Tensor: PDF values at quantiles corresponding to probabilities u
        """
        return self.pdf(self.cdf_inv(u, theta), theta, log)

    def parameters_size(self) -> int:
        """
        Get the number of parameters in the distribution.

        Returns:
        int: Number of parameters
        """
        return self._parameters_size

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass
