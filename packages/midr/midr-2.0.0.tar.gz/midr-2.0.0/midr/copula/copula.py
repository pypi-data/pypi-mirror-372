# SPDX-FileCopyrightText: 2025 Laurent Modolo <laurent@modolo.fr>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Abstract base class and utilities for copula models in the IDR package.

This module defines the Copula abstract base class and provides a common interface
for all copula models. It includes methods for computing the CDF, PDF, likelihood,
parameter transformations, and fitting procedures.

Classes:
    Copula: Abstract base class for copula models.
"""

from abc import ABC, abstractmethod
from typing import Dict, List

import torch

from ..auxilary import fit as fit_auxilary
from ..auxilary import merge_parameters as merge


class Copula(ABC):
    """
    Abstract base class for copula models.

    A copula is a multivariate probability distribution where the marginal
    probability distribution of each variable is uniform. Copulas are used
    to describe the dependence between random variables.

    Parameters:
        dim (int): Dimension of the copula (number of variables)
        family (str): Name of the copula family
        parameter_size (int): Number of parameters in the copula model
    """

    def __init__(
        self,
        dim: int,
        family: str,
        parameter_size: int,
        gpu: torch.device = torch.device("cpu"),
    ):
        """
        Initialize a copula model.

        Args:
            dim (int): Dimension of the copula (number of variables)
            family (str): Name of the copula family
            parameter_size (int): Number of parameters in the copula model
        """
        self._dim = dim
        self._family = family
        self._parameters_size = parameter_size
        self._gpu = gpu

    def set_dim(self, dim: int):
        """
        Set the dimension of the copula.
        """
        self._dim = dim

    def dim(self) -> int:
        """
        Get the dimension of the copula.

        Returns:
            int: The dimension of the copula
        """
        return self._dim

    @abstractmethod
    def split_parameters(
        self, theta: torch.Tensor
    ) -> List[torch.Tensor] | Dict[str, torch.Tensor]:
        """
        Split the parameter tensor into individual components.

        Args:
            theta (torch.Tensor): Combined parameter tensor

        Returns:
            List[torch.Tensor] | Dict[str, torch.Tensor]: Split parameters as a list or dictionary
        """
        pass

    def merge_parameters(
        self, theta: List[torch.Tensor] | Dict[str, torch.Tensor]
    ) -> torch.Tensor:
        """
        Merge individual parameter components into a single tensor.

        Args:
            theta (List[torch.Tensor] | Dict[str, torch.Tensor]): Individual parameter components

        Returns:
            torch.Tensor: Combined parameter tensor
        """
        return merge(theta)

    def theta_transform(self, theta: torch.Tensor) -> torch.Tensor:
        """
        Transform parameters for optimization.

        This method can be overridden to transform parameters to an unconstrained space
        for optimization purposes.

        Args:
            theta (torch.Tensor): Original parameters

        Returns:
            torch.Tensor: Transformed parameters
        """
        return theta

    def theta_transform_inverse(self, theta: torch.Tensor) -> torch.Tensor:
        """
        Inverse transform parameters after optimization.

        This method can be overridden to transform parameters back from an unconstrained space
        to their original constrained space after optimization.

        Args:
            theta (torch.Tensor): Transformed parameters

        Returns:
            torch.Tensor: Original parameters
        """
        return theta

    @abstractmethod
    def cdf(
        self, u: torch.Tensor, theta: torch.Tensor, log: bool = False
    ) -> torch.Tensor:
        """
        Cumulative distribution function (CDF) of the copula.

        Args:
            u (torch.Tensor): 2D tensor of points in [0,1]^d space (each row is an observation)
            theta (torch.Tensor): Parameters of the copula
            log (bool, optional): If True, return log-CDF. Default is False.

        Returns:
            torch.Tensor: 1D tensor of CDF values (or log-CDF if log=True)
        """
        pass

    @abstractmethod
    def pdf(
        self, u: torch.Tensor, theta: torch.Tensor, log: bool = False
    ) -> torch.Tensor:
        """
        Probability density function (PDF) of the copula.

        Args:
            u (torch.Tensor): 2D tensor of points in [0,1]^d space (each row is an observation)
            theta (torch.Tensor): Parameters of the copula
            log (bool, optional): If True, return log-PDF. Default is False.

        Returns:
            torch.Tensor: 1D tensor of PDF values (or log-PDF if log=True)
        """
        pass

    def likelihood(
        self, u: torch.Tensor, theta: torch.Tensor, log: bool = False
    ) -> torch.Tensor:
        """
        Calculate the likelihood of the copula for the given data.

        Args:
            u (torch.Tensor): 2D tensor of data points in [0,1]^d space (each row is an observation)
            theta (torch.Tensor): Parameters of the copula
            log (bool, optional): If True, return the log-likelihood. Default is False

        Returns:
            torch.Tensor: Scalar tensor containing the (log-)likelihood of the data
        """
        lpdf = self.pdf(u, theta, True)
        if log:
            return lpdf.sum()
        return torch.exp(lpdf.sum())

    def compute_loss(self, theta: torch.Tensor, u: torch.Tensor):
        """
        Compute the negative log-likelihood loss for optimization.

        Args:
            theta (torch.Tensor): Parameters of the copula
            u (torch.Tensor): Data points in [0,1]^d space

        Returns:
            torch.Tensor: Negative log-likelihood value
        """
        return -self.likelihood(u, theta, log=True)

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
        Fit the copula parameters to the given data.

        Args:
            u (torch.Tensor): Data points in [0,1]^d space
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
            torch.Tensor: Fitted parameter values
        """
        u.to(self._gpu)
        theta.to(self._gpu)

        def compute_loss(theta: torch.Tensor) -> torch.Tensor:
            return self.compute_loss(theta, u)

        return fit_auxilary(
            compute_loss,
            theta=theta,
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

    @abstractmethod
    def random(self, n: int, theta: torch.Tensor) -> torch.Tensor:
        """
        Generate random samples from the copula.

        Args:
            n (int): Number of samples to generate
            theta (torch.Tensor): Parameters of the copula

        Returns:
            torch.Tensor: 2D tensor of shape (n, dim) containing samples from the copula
        """
        pass

    def parameters_size(self) -> int:
        """
        Get the number of parameters in the copula model.

        Returns:
            int: Number of parameters
        """
        return self._parameters_size
