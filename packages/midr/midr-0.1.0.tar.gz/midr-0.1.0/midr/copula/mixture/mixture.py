# SPDX-FileCopyrightText: 2025 Laurent Modolo <laurent@modolo.fr>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Mixture Copula implementation for the IDR package.

This module provides the MixtureCopula class, which allows for flexible modeling of complex
dependency structures by combining multiple copulas with weights. It includes methods for
computing the CDF, PDF, likelihood, parameter transformations, and fitting routines.

Classes:
    MixtureCopula: Mixture copula model that combines multiple copulas with weights.
"""

from typing import List

import torch

from ...auxilary import clr1, clr1_inv
from ..copula import Copula


class MixtureCopula(Copula):
    """
    Mixture copula model that combines multiple copulas with weights.

    A mixture copula is a weighted sum of multiple copulas, allowing for flexible modeling
    of complex dependency structures. Each component copula can have its own parameters,
    and the mixture weights are constrained to sum to one.

    Parameters:
        dim (int): Dimension of the copula (number of variables)
        family (str): Name of the mixture copula family
        copulas (list): List of copula classes to include in the mixture
    """

    def __init__(
        self,
        dim: int,
        family: str,
        copulas: list,
        gpu: torch.device = torch.device("cpu"),
    ):
        """
        Initialize a MixtureCopula.

        Args:
            dim (int): Dimension of the copula (number of variables)
            family (str): Name of the mixture copula family
            copulas (list): List of copula classes to include in the mixture
        """
        self._copulas = []
        for copula in copulas:
            copula.set_dim(dim)
            self._copulas.append(copula)
        parameters = len(copulas)
        for i, copula in enumerate(self._copulas):
            parameters += copula.parameters_size()
        super().__init__(dim, family, parameters, gpu=gpu)

    def split_parameters(self, theta: torch.Tensor) -> List[torch.Tensor]:
        """
        Split the parameter tensor into weights and copula parameters.

        Args:
            theta (torch.Tensor): Combined parameter tensor

        Returns:
            List[torch.Tensor]: A list containing [weights, copula_parameters]
        """
        id_weight = len(self._copulas)
        return [theta[:id_weight], theta[id_weight:]]

    def bounds(self):
        """
        Get the bounds for all parameters in the mixture copula.

        Returns:
            list: List of (lower, upper) tuples for each parameter, where None indicates unbounded
        """
        id_weight = len(self._copulas)
        bounds = []
        for i in range(id_weight - 1):
            bounds.append((None, None))
        for i in range(id_weight):
            lower = self._copulas[i].lower_bound().item()
            upper = self._copulas[i].upper_bound().item()
            if torch.isinf(torch.tensor(lower).to(self._gpu)):
                lower = None
            if torch.isinf(torch.tensor(upper).to(self._gpu)):
                upper = None
            bounds.append((lower, upper))
        return bounds

    def barrier_method(
        self, theta: torch.Tensor, step: torch.Tensor, coef: torch.Tensor
    ) -> torch.Tensor:
        """
        Apply a barrier method penalty for constrained optimization.

        This method adds a penalty term to the loss function to enforce parameter
        constraints during optimization.

        Args:
            theta (torch.Tensor): Parameter tensor
            step (torch.Tensor): Current optimization step
            coef (torch.Tensor): Coefficient for the barrier method

        Returns:
            torch.Tensor: Barrier penalty term
        """
        id_weight = len(self._copulas) - 1
        theta = theta[id_weight:]
        penalty = torch.tensor(0.0).to(self._gpu)
        for i in range(len(self._copulas)):
            if self._copulas[i].lower_bound() is not None:
                penalty += torch.log(theta[i] - self._copulas[i].lower_bound())
            if self._copulas[i].upper_bound() is not None:
                penalty += torch.log(self._copulas[i].upper_bound() - theta[i])
        return -(1.0 / torch.pow(torch.tensor(coef), step + 1) * penalty)

    def cdf(
        self, u: torch.Tensor, theta: torch.Tensor, log: bool = False
    ) -> torch.Tensor:
        """
        Compute the cumulative distribution function (CDF) of the mixture copula.

        Args:
            u (torch.Tensor): 2D tensor of points in [0,1]^d space (each row is an observation)
            theta (torch.Tensor): Combined parameter tensor
            log (bool, optional): If True, return log-CDF. Default is False.

        Returns:
            torch.Tensor: 1D tensor of CDF values (or log-CDF if log=True)
        """
        weight, thetas = self.split_parameters(theta)
        cdf = torch.column_stack(
            [copula.cdf(u, thetas[i]) for i, copula in enumerate(self._copulas)]
        )
        if log:
            return torch.log(torch.matmul(cdf, weight))
        return torch.matmul(cdf, weight)

    def pdf(
        self, u: torch.Tensor, theta: torch.Tensor, log: bool = False
    ) -> torch.Tensor:
        """
        Compute the probability density function (PDF) of the mixture copula.

        Args:
            u (torch.Tensor): 2D tensor of points in [0,1]^d space (each row is an observation)
            theta (torch.Tensor): Combined parameter tensor
            log (bool, optional): If True, return log-PDF. Default is False.

        Returns:
            torch.Tensor: 1D tensor of PDF values (or log-PDF if log=True)
        """
        weight, thetas = self.split_parameters(theta)
        return self.pdf_split(u, weight, thetas, log)

    def pdf_split(
        self,
        u: torch.Tensor,
        weight: torch.Tensor,
        theta: torch.Tensor,
        log: bool = False,
    ) -> torch.Tensor:
        """
        Calculate PDF using pre-split parameters (weights and copula parameters).

        Args:
            u (torch.Tensor): 2D tensor of points in [0,1]^d space
            weight (torch.Tensor): Weights for each component copula
            theta (torch.Tensor): Parameters for each component copula
            log (bool): If True, return the log-PDF. Default is False

        Returns:
            torch.Tensor: PDF or log-PDF values at points u
        """
        pdf = torch.stack(
            [
                copula.pdf(u, theta[i], log=True)
                for i, copula in enumerate(self._copulas)
            ],
            dim=1,
        )
        inf_mask = pdf.isinf()
        tiny_val = torch.log(
            torch.tensor(torch.finfo(torch.float64).tiny).to(self._gpu)
        )
        pdf = torch.where(inf_mask, tiny_val, pdf)
        pdf = pdf + torch.log(weight.t())
        pdf = torch.logsumexp(pdf, dim=1)
        if log:
            return pdf
        return torch.exp(pdf)

    def likelihood_split(
        self,
        u: torch.Tensor,
        weight: torch.Tensor,
        theta: torch.Tensor,
        log: bool = False,
    ) -> torch.Tensor:
        """
        Calculate likelihood using pre-split parameters.

        Args:
            u (torch.Tensor): 2D tensor of points in [0,1]^d space
            weight (torch.Tensor): Weights for each component copula
            theta (torch.Tensor): Parameters for each component copula
            log (bool): If True, return the log-likelihood. Default is False

        Returns:
            torch.Tensor: Likelihood or log-likelihood of the data
        """
        if log:
            return self.pdf_split(u, weight=weight, theta=theta, log=log).sum()
        return self.pdf_split(u, weight=weight, theta=theta, log=True).sum().exp()

    def random(self, n: int, theta: torch.Tensor) -> torch.Tensor:
        """
        Generate random samples from the mixture copula.

        Args:
            n (int): Number of samples to generate
            theta (torch.Tensor): Combined parameter tensor

        Returns:
            torch.Tensor: 2D tensor of shape (n, dim) containing samples from the mixture copula
        """
        weight, thetas = self.split_parameters(theta)
        nj = torch.distributions.Multinomial(total_count=n, probs=weight).sample().int()
        ul = []
        for j in range(len(nj)):
            if nj[j] > 0:
                u = self._copulas[j].random(nj[j].item(), thetas[j])
                ul.append(u)
        u_combined = torch.cat(ul, dim=0)
        return u_combined[torch.randperm(u_combined.size(0))]

    def theta_transform(self, theta: torch.Tensor) -> torch.Tensor:
        """
        Transform parameters for optimization.

        Transforms weights using centered log-ratio (CLR) to ensure they
        sum to 1 after inverse transformation. Each copula's parameters are also
        transformed as needed for unconstrained optimization.

        Args:
            theta (torch.Tensor): Original parameters

        Returns:
            torch.Tensor: Transformed parameters suitable for unconstrained optimization
        """
        weight, theta = self.split_parameters(theta)
        weight = clr1(weight)
        theta = theta.clone()
        start = 0
        for i in range(len(self._copulas)):
            if isinstance(self._copulas[i], Copula):
                stop = start + self._copulas[i].parameters_size()
                theta[start:stop] = self._copulas[i].theta_transform(theta[start:stop])
                start = stop
        return torch.cat([weight, theta], dim=0)

    def theta_transform_inverse(self, theta: torch.Tensor) -> torch.Tensor:
        """
        Inverse transform parameters after optimization.

        Transforms weights back from CLR space to the probability simplex.
        Each copula's parameters are also inverse-transformed as needed.

        Args:
            theta (torch.Tensor): Transformed parameters

        Returns:
            torch.Tensor: Original parameters with constraints satisfied
        """
        id_weight = len(self._copulas) - 1
        weight = clr1_inv(theta[:id_weight])
        theta = theta[id_weight:].clone()
        start = 0
        for i in range(len(self._copulas)):
            if isinstance(self._copulas[i], Copula):
                stop = start + self._copulas[i].parameters_size()
                theta[start:stop] = self._copulas[i].theta_transform_inverse(
                    theta[start:stop]
                )
                start = stop
        return torch.cat([weight, theta], dim=0)

    def compute_loss(self, theta: torch.Tensor, u: torch.Tensor) -> torch.Tensor:
        """
        Compute the negative log-likelihood loss for optimization.

        Applies inverse transformation to parameters before computing likelihood.

        Args:
            theta (torch.Tensor): Transformed parameters
            u (torch.Tensor): Data points in [0,1]^d space

        Returns:
            torch.Tensor: Negative log-likelihood value
        """
        theta = self.theta_transform_inverse(theta)
        return -self.likelihood(u, theta=theta, log=True)

    def fit(
        self,
        u: torch.Tensor,
        theta: torch.Tensor,
        tol: torch.Tensor = torch.tensor(1e-3),
        max_iter: int = 1000,
        start_lr: float = 1.0,
        lr_decay: float = 1.0,
        plot: bool = False,
        tensor_name: List[str] | None = None,
        plot_err: bool = False,
        print_progress: bool = False,
        algorithm: str = "LBFGS",
    ) -> torch.Tensor:
        """
        Fit the mixture copula to the data.

        Args:
            u (torch.Tensor): 2D tensor of data points in [0,1]^d space
            theta (torch.Tensor): Initial parameter values
            tol (torch.Tensor): Tolerance for convergence. Default is 1e-3
            max_iter (int): Maximum number of iterations. Default is 1000
            start_lr (float): Initial learning rate. Default is 1.0
            lr_decay (float): Learning rate decay factor. Default is 1.0
            plot (bool): Whether to plot optimization progress. Default is False
            tensor_name (List[str]|None): Names of parameters for plotting. Default is None
            plot_err (bool): Whether to plot parameter errors. Default is False
            print_progress (bool): Whether to print progress during optimization. Default is False
            algorithm (str): Optimization algorithm to use. Default is "LBFGS"

        Returns:
            torch.Tensor: Fitted parameter tensor
        """
        theta = super().fit(
            u=u,
            theta=self.theta_transform(theta),
            tol=tol,
            max_iter=max_iter,
            start_lr=start_lr,
            lr_decay=lr_decay,
            plot=plot,
            tensor_name=tensor_name,
            plot_err=plot_err,
            print_progress=print_progress,
            algorithm=algorithm,
        )
        return self.theta_transform_inverse(theta)
