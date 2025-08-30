# SPDX-FileCopyrightText: 2025 Laurent Modolo <laurent@modolo.fr>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import torch
from .marginal import Marginal
from .gaussian import GaussianMarginal

class FixedGaussianMarginal(Marginal):
    """
    Gaussian marginal distribution with fixed mean of zero.

    This class implements a Gaussian (normal) distribution with a fixed mean
    parameter of 0, leaving only the standard deviation as a parameter to
    be estimated. This is useful when data is expected to be centered at zero,
    or when working with standardized data.
    """
    def __init__(self, gpu: torch.device = torch.device("cpu")):
        """
        Initialize a Gaussian marginal with fixed mean of zero.

        The distribution has only one parameter (standard deviation),
        as the mean is fixed at zero.
        """
        super().__init__(family="FixedGaussian", parameters_size=1, gpu=gpu)
        self._gaussian = GaussianMarginal()

    def cdf(self, x: torch.Tensor, theta: torch.Tensor, log: bool = False) -> torch.Tensor:
        """
        Compute the cumulative distribution function of the fixed Gaussian.

        Parameters:
        x (torch.Tensor): Input tensor of values to evaluate the CDF at
        theta (torch.Tensor): Parameter tensor containing only standard deviation
        log (bool): If True, return the log-CDF. Default is False

        Returns:
        torch.Tensor: CDF values at points x (or log-CDF if log=True)
        """
        return self._gaussian.cdf(x, torch.cat([torch.tensor([0.0]).to(self._gpu), theta]), log).to(self._gpu)

    def cdf_inv(self, x: torch.Tensor, theta: torch.Tensor, log: bool = False) -> torch.Tensor:
        """
        Compute the inverse CDF (quantile function) of the fixed Gaussian.

        Parameters:
        x (torch.Tensor): Input tensor of probabilities in [0,1] to find quantiles for
        theta (torch.Tensor): Parameter tensor containing only standard deviation
        log (bool): If True, input is treated as log-probabilities. Default is False

        Returns:
        torch.Tensor: Quantiles corresponding to probabilities in x
        """
        return self._gaussian.cdf_inv(x, torch.cat([torch.tensor([0.0]).to(self._gpu), theta]), log).to(self._gpu)

    def pdf(self, x: torch.Tensor, theta: torch.Tensor, log: bool = False) -> torch.Tensor:
        """
        Compute the probability density function of the fixed Gaussian.

        Parameters:
        x (torch.Tensor): Input tensor of values to evaluate the PDF at
        theta (torch.Tensor): Parameter tensor containing only standard deviation
        log (bool): If True, return the log-PDF. Default is False

        Returns:
        torch.Tensor: PDF values at points x (or log-PDF if log=True)
        """
        return self._gaussian.pdf(x, torch.cat([torch.tensor([0.0]).to(self._gpu), theta]), log).to(self._gpu)

    def theta_transform(self, theta: torch.Tensor) -> torch.Tensor:
        """
        Transform standard deviation parameter for optimization.

        Transforms the standard deviation to ensure it remains positive
        after inverse transformation during optimization.

        Parameters:
        theta (torch.Tensor): Original standard deviation parameter

        Returns:
        torch.Tensor: Transformed parameter suitable for unconstrained optimization
        """
        return torch.abs(theta)

    def theta_transform_inverse(self, theta: torch.Tensor) -> torch.Tensor:
        """
        Inverse transform the standard deviation parameter after optimization.

        Converts the transformed parameter back to its original space,
        ensuring the standard deviation remains positive.

        Parameters:
        theta (torch.Tensor): Transformed standard deviation parameter

        Returns:
        torch.Tensor: Original parameter with positivity constraint enforced
        """
        return torch.abs(theta)
