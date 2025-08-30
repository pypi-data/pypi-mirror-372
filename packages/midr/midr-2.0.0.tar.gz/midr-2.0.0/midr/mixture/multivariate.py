# SPDX-FileCopyrightText: 2025 Laurent Modolo <laurent@modolo.fr>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from typing import Dict, List

import torch

from ..auxilary import fit
from ..auxilary import merge_parameters as merge
from ..copula import Copula
from ..marginal import Marginal


class Multivariate:
    """
    Multivariate distribution combining marginal distributions with a copula.

    This class represents a multivariate distribution by combining univariate
    marginal distributions with a copula that captures the dependency structure.

    Parameters:
    dim (int): Dimension of the multivariate distribution
    copula (Copula): Copula capturing the dependency structure
    marginals (List[Marginal]): List of marginal distributions for each dimension
    family (str): Family name for the multivariate distribution
    """

    def __init__(
        self,
        dim: int,
        copula: Copula,
        marginals: List[Marginal],
        family: str,
        gpu: torch.device = torch.device("cpu"),
    ):
        self._family = family
        self._copula = copula
        self.set_dim(dim)
        if len(marginals) != dim:
            raise ValueError("Number of marginals must match dimension")
        self._marginals = marginals
        self._gpu = gpu

    def set_dim(self, dim: int):
        """
        Set the dimension of the multivariate distribution.
        """
        self._dim = dim
        self._copula.set_dim(dim)

    def cdf(
        self, x: torch.Tensor, theta: torch.Tensor, log: bool = False
    ) -> torch.Tensor:
        """
        Compute the cumulative distribution function of the multivariate distribution.

        Parameters:
        x (torch.Tensor): Input tensor of shape (n, dim) containing points to evaluate
        theta (torch.Tensor): Parameters for the distribution
        log (bool): If True, return the log-CDF. Default is False

        Returns:
        torch.Tensor: CDF values at points x (or log-CDF if log=True)
        """
        parameters = self.split_parameters(theta)
        return self._copula.cdf(
            torch.stack(
                [
                    self._marginals[j].cdf(x[:, j], parameters["marginals"][j])
                    for j in range(self._dim)
                ],
                dim=1,
            ),
            parameters["copula"][0],
            log=log,
        )

    def pdf(
        self, x: torch.Tensor, theta: torch.Tensor, log: bool = False
    ) -> torch.Tensor:
        """
        Compute the probability density function of the multivariate distribution.

        Parameters:
        x (torch.Tensor): Input tensor of shape (n, dim) containing points to evaluate
        theta (torch.Tensor): Parameters for the distribution
        log (bool): If True, return the log-PDF. Default is False

        Returns:
        torch.Tensor: PDF values at points x (or log-PDF if log=True)
        """
        t = self.split_parameters(theta)
        return self.pdf_split(x, t, log=log)

    def pdf_split(
        self,
        x: torch.Tensor,
        parameters: Dict[str, List[torch.Tensor]],
        log: bool = False,
    ) -> torch.Tensor:
        """
        Compute PDF using pre-split parameters.

        This method computes the PDF (or log-PDF) using already split parameters,
        avoiding repeated parameter splitting for efficiency.

        Parameters:
        x (torch.Tensor): Input tensor of shape (n, dim) containing points to evaluate
        theta (Dict[str, torch.Tensor|List[torch.Tensor]]): Split parameters dictionary
        log (bool): If True, return the log-PDF. Default is False

        Returns:
        torch.Tensor: PDF values at points x (or log-PDF if log=True)
        """
        pdf = self._copula.pdf(
            torch.stack(
                [
                    self._marginals[j].cdf(x[:, j], parameters["marginals"][j])
                    for j in range(self._dim)
                ],
                dim=1,
            ),
            parameters["copula"][0],
            log=True,
        ) + torch.sum(
            torch.stack(
                [
                    self._marginals[j].pdf(
                        x[:, j], parameters["marginals"][j], log=True
                    )
                    for j in range(self._dim)
                ],
                dim=1,
            ),
            dim=1,
        )
        if log:
            return pdf
        return torch.exp(pdf)

    def split_parameters(self, theta: torch.Tensor) -> Dict[str, list[torch.Tensor]]:
        """
        Split combined parameter tensor into separate components.

        This method splits the parameter tensor into separate components for
        each marginal distribution and the copula.

        Parameters:
        theta (torch.Tensor): Combined parameter tensor

        Returns:
        Dict[str, torch.Tensor|list[torch.Tensor]]: Dictionary containing:
            - "marginals": List of parameter tensors for each marginal
            - "copula": Parameter tensor for the copula
        """
        parameters: Dict[str, list[torch.Tensor]] = dict()
        i = 0
        parameters["marginals"] = []
        for d in range(self._dim):
            j = i + self._marginals[d].parameters_size()
            parameters["marginals"].append(theta[i:j])
            i += self._marginals[d].parameters_size()
        parameters["copula"] = [theta[i:]]
        return parameters

    def merge_parameters(
        self, parameters: Dict[str, List[torch.Tensor]]
    ) -> torch.Tensor:
        """
        Merge separate parameter components into a single tensor.

        Parameters:
        theta (Dict[str, torch.Tensor|List[torch.Tensor]]): Dictionary containing
                                                           separate parameter components

        Returns:
        torch.Tensor: Combined parameter tensor
        """
        return torch.cat([merge(parameters["marginals"]), parameters["copula"][0]])

    def parameters_size(self) -> int:
        """
        Get the total number of parameters in the multivariate distribution.

        Returns:
        int: Total number of parameters (sum of marginals and copula parameters)
        """
        size = 0
        for d in range(self._dim):
            size += self._marginals[d].parameters_size()
        size += self._copula.parameters_size()
        return size

    def likelihood(
        self, x: torch.Tensor, theta: torch.Tensor, log: bool = False
    ) -> torch.Tensor:
        """
        Calculate the likelihood of the data under the multivariate distribution.

        Parameters:
        x (list[torch.Tensor]): List of data tensors
        theta (torch.Tensor): Parameters for the distribution
        log (bool): If True, return the log-likelihood. Default is False

        Returns:
        torch.Tensor: Likelihood or log-likelihood of the data
        """
        if log:
            return self.pdf(x, theta, log).sum()
        return torch.exp(self.pdf(x, theta, True).sum())

    def likelihood_split(
        self, x: torch.Tensor, theta: Dict[str, List[torch.Tensor]], log: bool = False
    ) -> torch.Tensor:
        """
        Calculate likelihood using pre-split parameters.

        This method computes the likelihood (or log-likelihood) using already split
        parameters, avoiding repeated parameter splitting for efficiency.

        Parameters:
        x (list[torch.Tensor]): List of data tensors
        theta (Dict[str, torch.Tensor|List[torch.Tensor]]): Split parameters dictionary
        log (bool): If True, return the log-likelihood. Default is False

        Returns:
        torch.Tensor: Likelihood or log-likelihood of the data
        """
        if log:
            return self.pdf_split(x, theta, log).sum()
        return torch.exp(self.pdf_split(x, theta, True).sum())

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
        parameters["copula"][0] = self._copula.theta_transform(parameters["copula"][0])
        for i in range(len(parameters["marginals"])):
            parameters["marginals"][i] = self._marginals[i].theta_transform(
                parameters["marginals"][i]
            )
        return torch.cat(
            [
                *[marginal for marginal in parameters["marginals"]],
                parameters["copula"][0],
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
        parameters = self.split_parameters(theta)
        parameters["copula"][0] = self._copula.theta_transform_inverse(
            parameters["copula"][0]
        )
        for i in range(len(parameters["marginals"])):
            parameters["marginals"][i] = self._marginals[i].theta_transform_inverse(
                parameters["marginals"][i]
            )
        return torch.cat(
            [
                *[marginal for marginal in parameters["marginals"]],
                parameters["copula"][0],
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
        return -self.likelihood(x, theta=theta, log=True)

    def fit(
        self,
        x: torch.Tensor,
        theta: torch.Tensor,
        tol: torch.Tensor = torch.tensor(1e-6),
        max_iter: int = 1000,
        start_lr: float = 0.5,
        lr_decay: float = 0.9,
        plot: bool = False,
        algorithm: str = "LBFGS",
    ) -> torch.Tensor:
        """
        Fit the multivariate distribution parameters to the given data.

        Parameters:
        x (list[torch.Tensor]): List of data tensors
        theta (torch.Tensor): Initial parameter values
        tol (torch.Tensor): Tolerance for convergence. Default is 1e-6
        max_iter (int): Maximum number of iterations. Default is 1000
        start_lr (float): Initial learning rate. Default is 0.5
        lr_decay (float): Learning rate decay factor. Default is 0.9
        plot (bool): Whether to plot optimization progress. Default is False
        thread (int): Number of threads for parallel processing. Default is 1

        Returns:
        List: Fitted parameters, with copula parameters split into components
        """

        def compute_loss(theta):
            return -self.compute_loss(theta=theta, x=x)

        theta = fit(
            compute_loss,
            self.theta_transform(theta),
            tol=tol,
            max_iter=max_iter,
            start_lr=start_lr,
            lr_decay=lr_decay,
            plot=plot,
            algorithm=algorithm,
        )
        return self.theta_transform_inverse(theta)
