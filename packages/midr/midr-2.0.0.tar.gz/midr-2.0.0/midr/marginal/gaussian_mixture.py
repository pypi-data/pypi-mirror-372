# SPDX-FileCopyrightText: 2025 Laurent Modolo <laurent@modolo.fr>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import torch

from ..auxilary import (
    clr1,
    clr1_inv,
    inverse_cdf_interpolation,
    inverse_cdf_optimization,
)
from .marginal import Marginal


class GaussianMixtureMarginal(Marginal):
    """
    Gaussian mixture marginal distribution.

    This class implements a mixture of two Gaussian distributions:
    1. A zero-mean Gaussian component (independent component)
    2. A Gaussian component with estimated mean (dependent component)

    The mixture is controlled by a weight parameter that determines
    the probability of each component.

    Parameters:
    -----------
    None
    """

    def __init__(self, gpu: torch.device = torch.device("cpu")):
        """
        Initialize a Gaussian mixture marginal distribution.

        The distribution has four parameters:
        - weight: Mixture weight for the zero-mean component
        - indep_sigma: Standard deviation for the zero-mean (independent) component
        - dep_mu: Mean for the dependent component
        - dep_sigma: Standard deviation for the dependent component
        """
        super().__init__(family="GaussianMixture", parameters_size=4, gpu=gpu)

    def cdf(
        self, x: torch.Tensor, theta: torch.Tensor, log: bool = False
    ) -> torch.Tensor:
        """
        Compute the cumulative distribution function of the Gaussian mixture.

        The CDF is a weighted sum of the CDFs of the two Gaussian components.

        Parameters:
        -----------
        x (torch.Tensor): Input tensor of values to evaluate the CDF at
        theta (torch.Tensor): Parameter tensor with four components:
            - theta[0]: weight - Mixture weight for the zero-mean component
            - theta[1]: indep_sigma - Standard deviation for zero-mean component
            - theta[2]: dep_mu - Mean for the dependent component
            - theta[3]: dep_sigma - Standard deviation for dependent component
        log (bool): If True, return the log-CDF. Default is False

        Returns:
        --------
        torch.Tensor: CDF values at points x (or log-CDF if log=True)
        """
        weight = theta[0]
        indep_sigma = theta[1]
        dep_mu = theta[2]
        dep_sigma = theta[3]
        if any(torch.isnan(theta)):
            return torch.zeros(x.shape[0]) * torch.nan
        cdf = weight * torch.distributions.normal.Normal(
            loc=torch.tensor([0.0]).to(self._gpu), scale=indep_sigma
        ).cdf(x).to(self._gpu)
        cdf += (1.0 - weight) * torch.distributions.normal.Normal(
            loc=dep_mu, scale=dep_sigma
        ).cdf(x)
        if log:
            return cdf.log()
        else:
            return cdf

    def cdf_inv(
        self,
        x: torch.Tensor,
        theta: torch.Tensor,
        log: bool = False,
        tol: float = 1e-9,
        optim: bool = False,
        num_samples=1000,
    ) -> torch.Tensor:
        """
        Compute the inverse CDF (quantile function) of the Gaussian mixture.

        Since the mixture CDF doesn't have a simple analytical inverse, this method
        uses either numerical optimization or interpolation to compute the inverse.

        Parameters:
        -----------
        x (torch.Tensor): Input tensor of probabilities in [0,1] to find quantiles for
        theta (torch.Tensor): Parameter tensor with four components (see cdf method)
        log (bool): If True, input is treated as log-probabilities. Default is False
        tol (float): Tolerance for optimization convergence. Default is 1e-9
        optim (bool): If True, use optimization; otherwise use interpolation. Default is False
        num_samples (int): Number of samples for interpolation grid. Default is 1000

        Returns:
        --------
        torch.Tensor: Quantiles corresponding to probabilities in x
        """
        if any(torch.isnan(theta)):
            return torch.zeros(x.shape[0]) * torch.nan

        def cdf(x: torch.Tensor):
            return self.cdf(x, theta, False)

        if optim:
            cdf_inv = inverse_cdf_optimization(cdf, x, tol=tol)
        else:
            cdf_inv = inverse_cdf_interpolation(cdf, x, num_samples=num_samples)
        if log:
            return cdf_inv.log()
        else:
            return cdf_inv

    def pdf(
        self, x: torch.Tensor, theta: torch.Tensor, log: bool = False
    ) -> torch.Tensor:
        """
        Compute the probability density function of the Gaussian mixture.

        The PDF is a weighted sum of the PDFs of the two Gaussian components.
        The calculation is performed in log space for numerical stability.

        Parameters:
        -----------
        x (torch.Tensor): Input tensor of values to evaluate the PDF at
        theta (torch.Tensor): Parameter tensor with four components:
            - theta[0]: weight - Mixture weight for the zero-mean component
            - theta[1]: indep_sigma - Standard deviation for zero-mean component
            - theta[2]: dep_mu - Mean for the dependent component
            - theta[3]: dep_sigma - Standard deviation for dependent component
        log (bool): If True, return the log-PDF. Default is False

        Returns:
        --------
        torch.Tensor: PDF values at points x (or log-PDF if log=True)
        """
        weight = theta[0]
        indep_sigma = theta[1]
        dep_mu = theta[2]
        dep_sigma = theta[3]
        if any(torch.isnan(theta)):
            return torch.zeros(x.shape[0]) * torch.nan
        pdf_1 = torch.log(weight) + torch.distributions.normal.Normal(
            loc=torch.tensor([0.0]).to(self._gpu), scale=indep_sigma
        ).log_prob(x).to(self._gpu)
        pdf_2 = torch.log(1.0 - weight) + torch.distributions.normal.Normal(
            loc=dep_mu, scale=dep_sigma
        ).log_prob(x)
        pdf = torch.logsumexp(torch.stack([pdf_1, pdf_2]), dim=0)
        if log:
            return pdf
        else:
            return pdf.exp()

    def theta_transform(self, theta: torch.Tensor) -> torch.Tensor:
        """
        Transform parameters for optimization.

        Transforms parameters to ensure constraints are satisfied:
        - Weight is transformed using centered log-ratio (CLR) to ensure it's in [0,1]
        - Standard deviations are transformed to ensure they remain positive
        - Mean is left unchanged as it's unconstrained

        Parameters:
        -----------
        theta (torch.Tensor): Original parameters [weight, indep_sigma, dep_mu, dep_sigma]

        Returns:
        --------
        torch.Tensor: Transformed parameters suitable for unconstrained optimization
        """
        return torch.cat(
            [
                clr1(torch.cat([theta[0].unsqueeze(0), 1.0 - theta[0].unsqueeze(0)]))[0]
                .unsqueeze(0)
                .to(self._gpu),
                torch.abs(theta[1]).unsqueeze(0),
                theta[2].unsqueeze(0),
                torch.abs(theta[3]).unsqueeze(0),
            ]
        )

    def theta_transform_inverse(self, theta: torch.Tensor) -> torch.Tensor:
        """
        Inverse transform parameters after optimization.

        Transforms parameters back from unconstrained space:
        - Weight is transformed from CLR space back to [0,1]
        - Standard deviations are transformed back to positive values
        - Mean is left unchanged as it was unconstrained

        Parameters:
        -----------
        theta (torch.Tensor): Transformed parameters

        Returns:
        --------
        torch.Tensor: Original parameters with constraints satisfied:
            - theta[0]: weight in [0,1]
            - theta[1]: positive indep_sigma
            - theta[2]: dep_mu (unchanged)
            - theta[3]: positive dep_sigma
        """
        return torch.cat(
            [
                clr1_inv(torch.cat([torch.tensor([0.0]), theta[0].unsqueeze(0)]))[0]
                .unsqueeze(0)
                .to(self._gpu),
                torch.abs(theta[1]).unsqueeze(0),
                theta[2].unsqueeze(0),
                torch.abs(theta[3]).unsqueeze(0),
            ]
        )
