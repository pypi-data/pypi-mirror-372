# SPDX-FileCopyrightText: 2025 Laurent Modolo <laurent@modolo.fr>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from typing import Dict, List

import torch

from ..auxilary import clr1, clr1_inv, fit
from .multivariate import Multivariate


class Mixture:
    """
    General mixture model that combines multiple multivariate distributions.

    A mixture model is a probabilistic model that represents the presence of
    subpopulations within an overall population. This class implements a mixture
    of multiple multivariate distributions with weights.

    Parameters:
    dim (int): Dimension of the distribution (number of variables)
    multivariates (List[Multivariate]): List of multivariate distributions
    family (str): Name/identifier for this mixture model
    """

    def __init__(
        self,
        dim: int,
        multivariates: List[Multivariate],
        family: str,
        gpu: torch.device = torch.device("cpu"),
    ):
        """
        Initialize a mixture model with multiple multivariate distributions.

        Parameters:
        dim (int): Dimension of the distribution (number of variables)
        multivariates (List[Multivariate]): List of multivariate distributions to mix
        family (str): Name/identifier for this mixture model
        """
        self._family = family
        self._multivariates = multivariates
        self.set_dim(dim)
        self._gpu = gpu

    def set_dim(self, dim: int):
        """
        Set the dimension of the mixture model.
        """
        self._dim = dim
        for i in range(len(self._multivariates)):
            self._multivariates[i].set_dim(dim)

    def cdf(
        self, x: torch.Tensor, theta: torch.Tensor, log: bool = False
    ) -> torch.Tensor:
        """
        Compute the cumulative distribution function of the mixture model.

        Parameters:
        x (List[torch.Tensor]): List of data tensors, one for each dimension
        theta (torch.Tensor): Parameters for the mixture model
        log (bool): If True, return the log-CDF. Default is False

        Returns:
        torch.Tensor: CDF values at points x (or log-CDF if log=True)
        """
        parameters = self.split_parameters(theta)
        cdf = torch.column_stack(
            [
                multivariate.cdf(x, parameters["multivariates"][i], log=True)
                for i, multivariate in enumerate(self._multivariates)
            ]
        )
        cdf[cdf.isinf()] = torch.log(
            torch.tensor(torch.finfo(torch.float64).tiny).to(self._gpu)
        )
        cdf = cdf + torch.log(parameters["weights"][0].t())
        cdf = torch.logsumexp(cdf, dim=1)
        if log:
            return cdf
        return torch.exp(cdf)

    def pdf(
        self, x: torch.Tensor, theta: torch.Tensor, log: bool = False
    ) -> torch.Tensor:
        """
        Compute the probability density function of the mixture model.

        Parameters:
        x (List[torch.Tensor]): List of data tensors, one for each dimension
        theta (torch.Tensor): Parameters for the mixture model
        log (bool): If True, return the log-PDF. Default is False

        Returns:
        torch.Tensor: PDF values at points x (or log-PDF if log=True)
        """
        return self.pdf_split(x, self.split_parameters(theta), log)

    def pdf_split(
        self,
        x: torch.Tensor,
        parameters: Dict[str, list[torch.Tensor]],
        log: bool = False,
    ) -> torch.Tensor:
        """
        Compute PDF using pre-split parameters.

        This method computes the PDF (or log-PDF) using already split parameters,
        avoiding repeated parameter splitting for efficiency.

        Parameters:
        x (List[torch.Tensor]): List of data tensors, one for each dimension
        theta (List[torch.Tensor]): List of split parameter tensors
        log (bool): If True, return the log-PDF. Default is False

        Returns:
        torch.Tensor: PDF values at points x (or log-PDF if log=True)
        """
        pdf = torch.column_stack(
            [
                multivariate.pdf(x=x, theta=parameters["multivariates"][i], log=True)
                for i, multivariate in enumerate(self._multivariates)
            ]
        )
        pdf[pdf.isinf()] = torch.log(
            torch.tensor(torch.finfo(torch.float64).tiny).to(self._gpu)
        )
        pdf = pdf + torch.log(parameters["weights"][0].t())
        pdf = torch.logsumexp(pdf, dim=1)
        if log:
            return pdf
        return torch.exp(pdf)

    def likelihood(
        self, x: torch.Tensor, theta: torch.Tensor, log: bool = False
    ) -> torch.Tensor:
        """
        Calculate the likelihood of the data under the mixture model.

        Parameters:
        x (list[torch.Tensor]): List of data tensors, one for each dimension
        theta (torch.Tensor): Parameters for the mixture model
        log (bool): If True, return the log-likelihood. Default is False

        Returns:
        torch.Tensor: Likelihood or log-likelihood of the data
        """
        if log:
            return self.pdf(x, theta, log).sum()
        return torch.exp(self.pdf(x, theta, True).sum())

    def likelihood_split(
        self, x: torch.Tensor, theta: Dict[str, list[torch.Tensor]], log: bool = False
    ) -> torch.Tensor:
        """
        Calculate likelihood using pre-split parameters.

        This method computes the likelihood (or log-likelihood) using already split
        parameters, avoiding repeated parameter splitting for efficiency.

        Parameters:
        x (list[torch.Tensor]): List of data tensors, one for each dimension
        theta (List[torch.Tensor]): List of split parameter tensors
        log (bool): If True, return the log-likelihood. Default is False

        Returns:
        torch.Tensor: Likelihood or log-likelihood of the data
        """
        if log:
            return self.pdf_split(x, theta, log).sum()
        return torch.exp(self.pdf_split(x, theta, True).sum())

    def split_parameters(self, theta: torch.Tensor) -> Dict[str, list[torch.Tensor]]:
        """
        Split combined parameter tensor into separate components.

        This method splits the parameter tensor into weights for each component
        and parameters for each multivariate distribution.

        Parameters:
        theta (torch.Tensor): Combined parameter tensor

        Returns:
        List: List containing weights and parameters for each component
        """
        i = len(self._multivariates)
        parameters: Dict[str, list[torch.Tensor]] = dict()
        parameters["weights"] = [theta[0:i]]
        parameters["multivariates"] = []
        for d in range(len(self._multivariates)):
            j = i + self._multivariates[d].parameters_size()
            parameters["multivariates"].append(theta[i:j])
            i += self._multivariates[d].parameters_size()
        return parameters

    def theta_transform(self, theta: torch.Tensor) -> torch.Tensor:
        """
        Transform parameters for optimization.

        This method transforms parameters to an unconstrained space for optimization,
        applying appropriate transformations to maintain constraints after inverse
        transformation.

        Parameters:
        theta (torch.Tensor): Original parameters

        Returns:
        torch.Tensor: Transformed parameters
        """
        parameters = self.split_parameters(theta)
        weight = clr1(parameters["weights"][0])
        for i, multivariate in enumerate(self._multivariates):
            parameters["multivariates"][i] = multivariate.theta_transform(
                parameters["multivariates"][i]
            )
        return torch.cat(
            [
                weight,
                *[multivariate for multivariate in parameters["multivariates"]],
            ]
        )

    def theta_transform_inverse(self, theta: torch.Tensor) -> torch.Tensor:
        """
        Inverse transform parameters after optimization.

        This method transforms parameters back from an unconstrained space
        to their original constrained space after optimization.

        Parameters:
        theta (torch.Tensor): Transformed parameters

        Returns:
        torch.Tensor: Original parameters with constraints satisfied
        """
        id_weight = len(self._multivariates) - 1
        weight = clr1_inv(theta[:id_weight])
        start = id_weight
        parameters = []
        for i, multivariate in enumerate(self._multivariates):
            stop = id_weight + (i + 1) * (multivariate.parameters_size() - 1)
            parameters.append(multivariate.theta_transform_inverse(theta[start:stop]))
            start = stop
        return torch.cat(
            [
                weight,
                *[multivariate for multivariate in parameters],
            ]
        )

    def compute_loss(self, theta: torch.Tensor, x: torch.Tensor) -> torch.Tensor:
        """
        Compute the negative log-likelihood loss for optimization.

        Applies inverse transformation to parameters before computing likelihood.

        Parameters:
        theta (torch.Tensor): Transformed parameters
        u (torch.Tensor): Data points in [0,1]^d space

        Returns:
        torch.Tensor: Negative log-likelihood value
        """
        theta = self.theta_transform_inverse(theta)
        return -self.likelihood(x=x, theta=theta, log=True)

    def fit(
        self,
        x: torch.Tensor,
        theta: torch.Tensor,
        tol: torch.Tensor = torch.tensor(1e-6),
        max_iter: int = 1000,
        start_lr: float = 0.5,
        lr_decay: float = 0.9,
        algorithm: str = "LBFGS",
        plot: bool = False,
    ) -> torch.Tensor:
        """
        Fit the mixture model parameters to the given data.

        Parameters:
        x (list[torch.Tensor]): List of data tensors, one for each dimension
        theta (torch.Tensor): Initial parameter values
        tol (torch.Tensor): Tolerance for convergence. Default is 1e-6
        max_iter (int): Maximum number of iterations. Default is 1000
        start_lr (float): Initial learning rate. Default is 0.5
        lr_decay (float): Learning rate decay factor. Default is 0.9
        plot (bool): Whether to plot optimization progress. Default is False

        Returns:
        List: Fitted parameters for the mixture model
        """

        def compute_loss(theta: torch.Tensor) -> torch.Tensor:
            return self.compute_loss(theta=theta, x=x)

        theta = fit(
            compute_loss,
            theta=self.theta_transform(theta),
            tol=tol,
            max_iter=max_iter,
            start_lr=start_lr,
            lr_decay=lr_decay,
            plot=plot,
            algorithm=algorithm,
        )
        return self.theta_transform_inverse(theta)
