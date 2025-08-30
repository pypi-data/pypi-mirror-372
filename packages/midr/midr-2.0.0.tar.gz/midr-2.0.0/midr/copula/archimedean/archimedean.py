# SPDX-FileCopyrightText: 2025 Laurent Modolo <laurent@modolo.fr>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Archimedean Copula base class for the IDR package.

This module provides an abstract base class for Archimedean copulas, which are a family of copulas
used to model dependencies between random variables. It defines the interface and common methods
for Archimedean copulas, including parameter bounds, generator and inverse generator functions,
CDF, PDF, and fitting routines.

Classes:
    ArchimedeanCopula: Abstract base class for Archimedean copulas.
"""

from abc import ABC, abstractmethod
from typing import List
from ...auxilary import tensor2list

from ..copula import Copula
import torch
from ..independence import IndependenceCopula

class ArchimedeanCopula(Copula, ABC):
    """
    Abstract base class for Archimedean copulas.

    Archimedean copulas are a family of copulas characterized by a generator function.
    This class defines the interface and common methods for Archimedean copulas,
    including parameter bounds, generator and inverse generator functions, CDF, PDF,
    and fitting routines.

    Parameters:
        dim (int): Dimension of the copula (number of variables)
        family (str): Name of the specific Archimedean copula family
    """
    def __init__(self, dim: int, family: str, gpu: torch.device = torch.device("cpu")):
        """
        Initialize an Archimedean copula.

        Parameters:
            dim (int): Dimension of the copula (number of variables)
            family (str): Name of the specific Archimedean copula family
        """
        super().__init__(dim, family, 1, gpu=gpu)
        self._bound = []

    def lower_bound(self):
        """
        Get the lower bound of the parameter space.

        Returns:
            torch.Tensor: Lower bound for the copula parameter
        """
        return self._bound[0]

    def upper_bound(self):
        """
        Get the upper bound of the parameter space.

        Returns:
            torch.Tensor: Upper bound for the copula parameter
        """
        return self._bound[1]

    def split_parameters(self, theta: torch.Tensor) -> List:
        """
        Split the parameter tensor into individual components.

        For Archimedean copulas, this transforms the parameter from bounded
        to unbounded space for optimization.

        Parameters:
            theta (torch.Tensor): Combined parameter tensor

        Returns:
            List[torch.Tensor]: List containing the transformed parameter
        """
        return [theta]

    def theta_transform(self, theta: torch.Tensor) -> torch.Tensor:
        """
        Transform the copula parameter for optimization.

        Ensures the parameter stays within the allowed bounds.

        Parameters:
            theta (torch.Tensor): Parameter to transform

        Returns:
            torch.Tensor: Transformed parameter
        """
        if theta < self.lower_bound():
            return self.lower_bound()
        if theta > self.upper_bound():
            return self.upper_bound()
        return theta

    def theta_transform_inverse(self, theta: torch.Tensor) -> torch.Tensor:
        """
        Inverse transform the copula parameter after optimization.

        Ensures the parameter stays within the allowed bounds.

        Parameters:
            theta (torch.Tensor): Parameter to inverse transform

        Returns:
            torch.Tensor: Inverse transformed parameter
        """
        if theta < self.lower_bound():
            return self.lower_bound()
        if theta > self.upper_bound():
            return self.upper_bound()
        return theta

    @abstractmethod
    def psi(self, u: torch.Tensor, theta: torch.Tensor, log: bool=False) -> torch.Tensor:
        """
        Generator function for the Archimedean copula.

        Parameters:
            u (torch.Tensor): Input tensor (1D or scalar)
            theta (torch.Tensor): Copula parameter
            log (bool): If True, return the log of the generator

        Returns:
            torch.Tensor: Generator value for the Archimedean copula
        """
        pass

    @abstractmethod
    def ipsi(self, u: torch.Tensor, theta: torch.Tensor, log: bool=False) -> torch.Tensor:
        """
        Inverse generator function for the Archimedean copula.

        Parameters:
            u (torch.Tensor): Input tensor (1D or scalar)
            theta (torch.Tensor): Copula parameter
            log (bool): If True, return the log of the inverse generator

        Returns:
            torch.Tensor: Inverse generator value for the Archimedean copula
        """
        pass

    def cdf(self, u: torch.Tensor, theta: torch.Tensor, log: bool=False) -> torch.Tensor:
        """
        Cumulative distribution function (CDF) of the Archimedean copula.

        Parameters:
            u (torch.Tensor): 2D tensor of points in [0,1]^d space (each row is an observation)
            theta (torch.Tensor): Parameter of the Archimedean copula
            log (bool): If True, return the log-CDF

        Returns:
            torch.Tensor: CDF values at points u, or log-CDF values if log=True
        """
        if theta == self.lower_bound():
            return IndependenceCopula(self._dim).cdf(u, log)
        return self.psi(torch.sum(self.ipsi(u, theta), dim=1), theta)

    def pdf(self, u: torch.Tensor, theta: torch.Tensor, log: bool=False) -> torch.Tensor:
        """
        Probability density function (PDF) of the Archimedean copula.

        Parameters:
            u (torch.Tensor): 2D tensor of points in [0,1]^d space (each row is an observation)
            theta (torch.Tensor): Parameter of the Archimedean copula
            log (bool): If True, return the log-PDF

        Returns:
            torch.Tensor: PDF values at points u, or log-PDF values if log=True
        """
        if theta == self.lower_bound():
            return IndependenceCopula(self._dim).pdf(u, log)

        ul = tensor2list(u)
        for i in range(len(ul)):
            ul[i].requires_grad_(True)

        def cdf_fn(u: List[torch.Tensor]):
            cdf = torch.stack([self.ipsi(uj, theta) for uj in u], dim=1).sum(dim=1)
            return self.psi(cdf, theta)
        pdf = cdf_fn(ul)
        for i in range(len(ul)):
            pdf = torch.autograd.grad(
                pdf,
                ul[i],
                grad_outputs=torch.ones_like(ul[i]),
                create_graph=True,
                retain_graph=True,
                )[0]
        if log:
            return torch.log(pdf)
        return pdf

    def compute_loss(self, theta: torch.Tensor, u: torch.Tensor):
        """
        Compute the negative log-likelihood loss for optimization.

        Parameters:
            theta (torch.Tensor): Parameter of the Archimedean copula
            u (torch.Tensor): Data points in [0,1]^d space

        Returns:
            torch.Tensor: Negative log-likelihood value
        """
        return -self.likelihood(u=u, theta=theta, log=True)

    def fit(self, u: torch.Tensor, theta: torch.Tensor, tol: torch.Tensor = torch.tensor(1e-3), max_iter: int= 1000, start_lr: float = 1.0, lr_decay: float = 1.0, plot: bool=False, tensor_name: List[str]|None = None, plot_err: bool=False, print_progress: bool=False, algorithm: str="LBFGS") -> torch.Tensor:
        """
        Fit the Archimedean copula parameters to the given data.

        Parameters:
            u (torch.Tensor): Data points in [0,1]^d space
            theta (torch.Tensor): Initial parameter value
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
            torch.Tensor: Fitted parameter value
        """
        return super().fit(
                u=u, theta=theta, tol=tol, max_iter=max_iter, start_lr=start_lr, lr_decay=lr_decay, plot=plot, tensor_name=tensor_name, plot_err = plot_err, print_progress=print_progress, algorithm=algorithm
            )
