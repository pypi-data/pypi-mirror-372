# SPDX-FileCopyrightText: 2025 Laurent Modolo <laurent@modolo.fr>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import torch
from .marginal import Marginal

class GaussianMarginal(Marginal):
    """A class representing the Gaussian (Normal) distribution marginal.

    This class implements the Gaussian marginal distribution with parameters μ (location/mean)
    and σ (scale/standard deviation). It inherits from the base Marginal class and provides
    implementations for CDF, inverse CDF, PDF, and parameter transformations.

    Attributes:
        family (str): Name of the distribution family ("Gaussian")
        parameters_size (int): Number of parameters (2 for Gaussian: μ and σ)
    """
    def __init__(self, gpu: torch.device = torch.device("cpu")):
        """Initialize the GaussianMarginal distribution.

        Sets up the Gaussian marginal with family name and parameter size specification.
        """
        super().__init__(family="Gaussian", parameters_size=2, gpu=gpu)

    def cdf(self, x: torch.Tensor, theta: torch.Tensor, log: bool = False) -> torch.Tensor:
        """Compute the cumulative distribution function (CDF) of the Gaussian distribution.

        Args:
            x (torch.Tensor): Input values at which to evaluate the CDF
            theta (torch.Tensor): Parameters of the distribution [μ, σ]
            log (bool, optional): If True, return log-CDF. Defaults to False.

        Returns:
            torch.Tensor: CDF values (or log-CDF if log=True)
        """
        mu = theta[0]
        sigma = theta[1]
        if any(torch.isnan(theta)):
            return torch.zeros(x.shape[0]) * torch.nan
        if log:
            return torch.distributions.normal.Normal(loc = mu, scale = sigma).cdf(x).log()
        else:
            return torch.distributions.normal.Normal(loc = mu, scale = sigma).cdf(x)

    def cdf_inv(self, x: torch.Tensor, theta: torch.Tensor, log: bool = False) -> torch.Tensor:
        """Compute the inverse cumulative distribution function (quantile function) of the Gaussian distribution.

        Args:
            x (torch.Tensor): Probability values at which to evaluate the inverse CDF
            theta (torch.Tensor): Parameters of the distribution [μ, σ]
            log (bool, optional): If True, return log of inverse CDF. Defaults to False.

        Returns:
            torch.Tensor: Inverse CDF values (or log-inverse-CDF if log=True)
        """
        mu = theta[0]
        sigma = theta[1]
        if any(torch.isnan(theta)):
            return torch.zeros(x.shape[0]) * torch.nan
        if log:
            return torch.distributions.normal.Normal(loc = mu, scale = sigma).icdf(x).log()
        else:
            return torch.distributions.normal.Normal(loc = mu, scale = sigma).icdf(x)

    def pdf(self, x: torch.Tensor, theta: torch.Tensor, log: bool = False, eps: float = 1e-6) -> torch.Tensor:
        """Compute the probability density function (PDF) of the Gaussian distribution.

        Args:
            x (torch.Tensor): Input values at which to evaluate the PDF
            theta (torch.Tensor): Parameters of the distribution [μ, σ]
            log (bool, optional): If True, return log-PDF. Defaults to False.
            eps (float, optional): Small value for numerical stability. Defaults to 1e-6.

        Returns:
            torch.Tensor: PDF values (or log-PDF if log=True)
        """
        mu = theta[0]
        sigma = theta[1]
        if any(torch.isnan(theta)):
            return torch.zeros(x.shape[0]) * torch.nan
        if log:
            return torch.distributions.normal.Normal(loc = mu, scale = sigma).log_prob(x)
        else:
            return torch.distributions.normal.Normal(loc = mu, scale = sigma).log_prob(x).exp()

    def theta_transform(self, theta: torch.Tensor) -> torch.Tensor:
        """Transform the parameters to their constrained space.

        Applies necessary transformations to ensure parameters meet their constraints:
        - μ remains unchanged
        - σ is transformed to be positive

        Args:
            theta (torch.Tensor): Raw parameters [μ, σ]

        Returns:
            torch.Tensor: Transformed parameters [μ, σ'] where σ' > 0
        """
        return torch.cat([theta[0].unsqueeze(0), torch.abs(theta[1]).unsqueeze(0)])

    def theta_transform_inverse(self, theta: torch.Tensor) -> torch.Tensor:
        """Transform the parameters back to their unconstrained space.

        Applies inverse transformations to convert from constrained to unconstrained space:
        - μ remains unchanged
        - σ is inverse-transformed from positive space

        Args:
            theta (torch.Tensor): Constrained parameters [μ, σ]

        Returns:
            torch.Tensor: Unconstrained parameters [μ, σ']
        """
        return torch.cat([theta[0].unsqueeze(0), torch.abs(theta[1]).unsqueeze(0)])
