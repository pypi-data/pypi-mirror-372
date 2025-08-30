# SPDX-FileCopyrightText: 2025 Laurent Modolo <laurent@modolo.fr>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from typing import Dict, List

import torch

from ..auxilary import clr, clr_inv
from ..auxilary import fit as fit_auxilary
from ..auxilary import merge_parameters as merge
from ..copula import Copula, IndependenceCopula
from ..marginal import FixedGaussianMarginal, GaussianMarginal, GaussianMixtureMarginal


class IndepMixture:
    """
    Independence Mixture model for separating independent and dependent components.

    This class models data as a mixture of independent components and dependent
    components, where the dependency structure is captured by a copula. It's designed
    for intrinsic dimension reduction (IDR) applications where identifying the truly
    dependent variables is the goal.

    Parameters:
    dim (int): Dimension of the data (number of variables)
    copula (Copula): Copula model to capture dependency structure
    family (str): Family name for the mixture model
    """

    def __init__(
        self,
        dim: int,
        copula: List[Copula],
        family: str = "indep_archmixture",
        gpu: torch.device = torch.device("cpu"),
    ):
        self._family = family
        self._copulas = copula
        self._independence_copula = IndependenceCopula(dim)
        self.set_dim(dim)
        self._indep_marginal = FixedGaussianMarginal(gpu=gpu)
        self._dep_marginal = GaussianMarginal(gpu=gpu)
        self._mix_marginal = GaussianMixtureMarginal(gpu=gpu)
        self._gpu = gpu

    def init_theta(self) -> torch.Tensor:
        """
        Initialize the parameter vector for the mixture model.
        """
        weight_number = len(self._copulas) + 1
        theta = torch.ones(weight_number, dtype=torch.float64) / weight_number
        theta = torch.cat(
            [
                theta,
                torch.ones(self._dim, dtype=torch.float64),
            ]
        )
        copula_parameters = sum(
            [self._copulas[i].parameters_size() for i in range(len(self._copulas))]
        )
        if self._copulas[0]._family != "EmpiricalBeta" and len(self._copula) > 1:
            theta = torch.cat(
                [theta, torch.ones(copula_parameters, dtype=torch.float64) * 5.0]
            )
        return theta

    def set_dim(self, dim: int):
        """
        Set the dimension of the mixture model.
        """
        self._dim = dim
        self._independence_copula.set_dim(dim)
        for i in range(len(self._copulas)):
            self._copulas[i].set_dim(dim)

    def split_parameters(self, theta: torch.Tensor) -> Dict[str, torch.Tensor]:
        """
        Split the parameter tensor into component-specific parameters.

        Parameters:
        theta (torch.Tensor): Combined parameter tensor

        Returns:
        Dict[str, torch.Tensor]: Dictionary containing:
            - "weight": Weight parameter for the mixture components
            - "indep_sigma": Standard deviations for independent component
            - "dep_mu": Mean parameters for dependent component
            - "dep_sigma": Standard deviation parameters for dependent component
            - "copula": Parameters for the dependency structure via copula
        """
        parameters: Dict[str, torch.Tensor] = dict()
        start, stop = (0, 1 + len(self._copulas))
        parameters["weight"] = theta[start:stop].to(self._gpu)
        start, stop = (1 + len(self._copulas), 1 + len(self._copulas) + self._dim)
        parameters["dep_mu"] = theta[start:stop].to(self._gpu)
        parameters["copula"] = theta[stop:].to(self._gpu)
        return parameters

    def pdf(
        self,
        u: torch.Tensor,
        theta: torch.Tensor,
        log: bool = False,
        marginal: bool = True,
    ) -> torch.Tensor:
        """
        Compute the probability density function of the independence mixture.

        Parameters:
        u (torch.Tensor): Input tensor of shape (n, dim) containing points in [0,1]^d space
        theta (torch.Tensor): Parameters for the distribution
        log (bool): If True, return the log-PDF. Default is False

        Returns:
        torch.Tensor: PDF values at points u (or log-PDF if log=True)
        """
        return self.pdf_split(
            u=u, parameters=self.split_parameters(theta), log=log, marginal=marginal
        ).to(self._gpu)

    def u_to_x(
        self, u: torch.Tensor, parameters: Dict[str, torch.Tensor]
    ) -> torch.Tensor:
        """
        Transform uniform variables to data space using inverse CDF transformation.

        This function transforms points from the copula space (uniform margins)
        to the original data space using inverse CDF of the mixture marginals.

        Parameters:
        u (torch.Tensor): Input tensor of shape (n, dim) containing points in [0,1]^d space
        parameters (Dict[str, torch.Tensor]): Dictionary of split parameters

        Returns:
        torch.Tensor: Transformed points in the original data space
        """
        x = [
            self._mix_marginal.cdf_inv(
                x=u[:, j],
                theta=torch.cat(
                    [
                        parameters["weight"][0].unsqueeze(0),
                        torch.tensor([1.0]),
                        parameters["dep_mu"][j : j + 1],
                        torch.tensor([1.0]),
                    ]
                ).to(self._gpu),
            )
            for j in range(self._dim)
        ]
        return torch.stack(x, dim=1).to(self._gpu)

    def dep_x_to_u(
        self, x: torch.Tensor, parameters: Dict[str, torch.Tensor]
    ) -> torch.Tensor:
        """
        Transform x to pseudo uniform distribution from the point of view of the dep compartment

        Parameters:
        x (torch.Tensor): Input tensor of shape (n, dim) containing points in R^d space
        parameters (Dict[str, torch.Tensor]): Dictionary of split parameters

        Returns:
        torch.Tensor: Transformed points in [0,1]^d space
        """
        u = [
            self._dep_marginal.cdf(
                x=x[:, j],
                theta=torch.cat(
                    [
                        parameters["dep_mu"][j : j + 1].to(self._gpu),
                        torch.tensor([1.0]),
                    ]
                ).to(self._gpu),
            )
            for j in range(self._dim)
        ]
        return torch.stack(u, dim=1).to(self._gpu)

    def indep_x_to_u(
        self, x: torch.Tensor, parameters: Dict[str, torch.Tensor]
    ) -> torch.Tensor:
        """
        Transform x to pseudo uniform distribution from the point of view of the dep compartment

        Parameters:
        x (torch.Tensor): Input tensor of shape (n, dim) containing points in R^d space
        parameters (Dict[str, torch.Tensor]): Dictionary of split parameters

        Returns:
        torch.Tensor: Transformed points in [0,1]^d space
        """
        u = [
            self._indep_marginal.cdf(
                x=x[:, j],
                theta=torch.tensor(
                    [
                        torch.tensor([1.0]),
                    ]
                ).to(self._gpu),
            )
            for j in range(self._dim)
        ]
        return torch.stack(u, dim=1).to(self._gpu)

    def pdf_split(
        self,
        u: torch.Tensor,
        parameters: Dict[str, torch.Tensor],
        log: bool = False,
        marginal: bool = True,
    ) -> torch.Tensor:
        """
        Calculate PDF using pre-split parameters.

        This method computes the PDF (or log-PDF) of the mixture model by combining
        the independent component (product of marginals) and the dependent component
        (copula-based joint distribution).

        Parameters:
        u (torch.Tensor): Input tensor of shape (n, dim) containing points in [0,1]^d space
        parameters (Dict[str, torch.Tensor]): Dictionary of split parameters
        log (bool): If True, return the log-PDF. Default is False

        Returns:
        torch.Tensor: PDF values at points u (or log-PDF if log=True)
        """
        u.to(self._gpu)
        x = self.u_to_x(u=u, parameters=parameters).to(self._gpu)
        u_dep = self.dep_x_to_u(x=x, parameters=parameters).to(self._gpu)

        pdf = [self._independence_copula.pdf(u, log=True).to(self._gpu)] + [
            copula.pdf(
                u_dep,
                parameters["copula"][
                    i * copula.parameters_size() : (i + 1) * copula.parameters_size()
                ],
                log=True,
            ).to(self._gpu)
            for i, copula in enumerate(self._copulas)
        ]
        pdf = torch.stack(pdf, dim=1).to(self._gpu)

        if marginal:
            indep_marginal = self.pdf_indep_marginal(x=x).to(self._gpu)
            dep_marginal = self.pdf_dep_marginal(x=x, parameters=parameters).to(
                self._gpu
            )
            marginal_pdf = torch.stack(
                [indep_marginal] + [dep_marginal for _ in range(len(self._copulas))],
                dim=1,
            ).to(self._gpu)
            pdf = torch.logsumexp(
                pdf + torch.log(parameters["weight"].t()) + marginal_pdf, dim=1
            )
        else:
            pdf = torch.logsumexp(pdf + torch.log(parameters["weight"].t()), dim=1)
        if log:
            return pdf
        return torch.exp(pdf).to(self._gpu)

    def pdf_indep_marginal(self, x: torch.Tensor) -> torch.Tensor:
        indep_marginal = torch.stack(
            [
                self._indep_marginal.pdf(
                    x=x[:, j], theta=torch.tensor([1.0]).to(self._gpu), log=True
                )
                for j in range(self._dim)
            ],
            dim=1,
        ).to(self._gpu)
        indep_marginal = torch.sum(indep_marginal, dim=1)
        return indep_marginal.to(self._gpu)

    def pdf_dep_marginal(
        self, x: torch.Tensor, parameters: Dict[str, torch.Tensor]
    ) -> torch.Tensor:
        dep_marginal = torch.stack(
            [
                self._dep_marginal.pdf(
                    x=x[:, j],
                    theta=torch.cat(
                        [parameters["dep_mu"][j : j + 1], torch.tensor([1.0])]
                    ).to(self._gpu),
                    log=True,
                )
                for j in range(self._dim)
            ],
            dim=1,
        ).to(self._gpu)
        dep_marginal = torch.sum(dep_marginal, dim=1)
        return dep_marginal.to(self._gpu)

    def pdf_split_class_proba(
        self,
        u: torch.Tensor,
        parameters: Dict[str, torch.Tensor],
        log: bool = False,
        marginal: bool = True,
    ) -> torch.Tensor:
        """
        Calculate PDF using pre-split parameters and class probabilities.

        This method computes the PDF (or log-PDF) of the mixture model by combining
        the independent component (product of marginals) and the dependent component
        (copula-based joint distribution).

        Parameters:
        u (torch.Tensor): Input tensor of shape (n, dim) containing points in [0,1]^d space
        p (torch.Tensor): Class probabilities for each row in u
        parameters (Dict[str, torch.Tensor]): Dictionary of split parameters
        log (bool): If True, return the log-PDF. Default is False

        Returns:
        torch.Tensor: PDF values at points u (or log-PDF if log=True)
        """
        x = self.u_to_x(u=u, parameters=parameters)
        u_dep = self.dep_x_to_u(x=x, parameters=parameters)
        p = self.log_class_proba(
            u=u, x=x, u_dep=u_dep, parameters=parameters, marginal=marginal
        )

        pdf = [self._independence_copula.pdf(u, log=True).to(self._gpu)] + [
            copula.pdf(
                u_dep,
                parameters["copula"][
                    i * copula.parameters_size() : (i + 1) * copula.parameters_size()
                ],
                log=True,
            ).to(self._gpu)
            for i, copula in enumerate(self._copulas)
        ]
        pdf = torch.stack(pdf, dim=1).to(self._gpu)

        if marginal:
            indep_marginal = self.pdf_indep_marginal(x=x)
            dep_marginal = self.pdf_dep_marginal(x=x, parameters=parameters)
            marginal_pdf = torch.stack(
                [indep_marginal] + [dep_marginal for _ in range(len(self._copulas))],
                dim=1,
            ).to(self._gpu)
            pdf = torch.logsumexp(pdf + p + marginal_pdf, dim=1)
        else:
            pdf = torch.logsumexp(pdf + p, dim=1)
        if log:
            return pdf
        return torch.exp(pdf).to(self._gpu)

    def likelihood(
        self,
        u: torch.Tensor,
        theta: torch.Tensor,
        log: bool = False,
        marginal: bool = True,
    ) -> torch.Tensor:
        """
        Calculate the likelihood of data under the independence mixture model.

        Parameters:
        u (torch.Tensor): Input tensor of shape (n, dim) containing points in [0,1]^d space
        theta (torch.Tensor): Parameters for the distribution
        log (bool): If True, return the log-likelihood. Default is False

        Returns:
        torch.Tensor: Likelihood or log-likelihood of the data
        """
        ll = self.pdf(u=u, theta=theta, log=True, marginal=marginal).sum()
        if log:
            return ll
        return torch.exp(ll).to(self._gpu)

    def likelihood_split(
        self,
        u: torch.Tensor,
        parameters: Dict[str, torch.Tensor],
        log: bool = False,
        marginal: bool = True,
    ) -> torch.Tensor:
        """
        Calculate likelihood using pre-split parameters.

        This method computes the likelihood (or log-likelihood) using already split
        parameters, avoiding repeated parameter splitting for efficiency.

        Parameters:
        u (torch.Tensor): Input tensor of shape (n, dim) containing points in [0,1]^d space
        parameters (Dict[str, torch.Tensor]): Dictionary of split parameters
        log (bool): If True, return the log-likelihood. Default is False

        Returns:
        torch.Tensor: Likelihood or log-likelihood of the data
        """
        ll = self.pdf_split(
            u=u, parameters=parameters, log=True, marginal=marginal
        ).sum()
        if log:
            return ll
        return torch.exp(ll).to(self._gpu)

    def likelihood_class_proba(
        self,
        u: torch.Tensor,
        parameters: Dict[str, torch.Tensor],
        log: bool = False,
        marginal: bool = True,
    ) -> torch.Tensor:
        """
        Calculate likelihood using pre-split parameters.

        This method computes the likelihood (or log-likelihood) using already split
        parameters, avoiding repeated parameter splitting for efficiency.

        Parameters:
        u (torch.Tensor): Input tensor of shape (n, dim) containing points in [0,1]^d space
        parameters (Dict[str, torch.Tensor]): Dictionary of split parameters
        log (bool): If True, return the log-likelihood. Default is False

        Returns:
        torch.Tensor: Likelihood or log-likelihood of the data
        """
        ll = self.pdf_split_class_proba(
            u=u, parameters=parameters, log=True, marginal=marginal
        ).sum()
        if log:
            return ll
        return torch.exp(ll).to(self._gpu)

    def idr(self, u: torch.Tensor, theta: torch.Tensor) -> torch.Tensor:
        """
        Calculate the Intrinsic Dependency Ratio (IDR) for the given data.

        The IDR measures the probability that a data point belongs to the
        independent component of the mixture, helping identify which observations
        exhibit dependency structure and which are likely independent.

        Parameters:
        u (torch.Tensor): Input tensor of shape (n, dim) containing points in [0,1]^d space
        theta (torch.Tensor): Parameters for the distribution

        Returns:
        torch.Tensor: IDR values for each point in u, representing the probability
                     of belonging to the independent component
        """
        return self.idr_split(u, self.split_parameters(theta)).to(self._gpu)

    def idr_split(
        self,
        u: torch.Tensor,
        parameters: Dict[str, torch.Tensor],
        marginal: bool = True,
    ) -> torch.Tensor:
        """
        Calculate IDR using pre-split parameters.

        This method computes the Intrinsic Dependency Ratio using already split
        parameters, which is the posterior probability that a data point belongs
        to the independent component given the observed data.

        Parameters:
        u (torch.Tensor): Input tensor of shape (n, dim) containing points in [0,1]^d space
        parameters (Dict[str, torch.Tensor]): Dictionary of split parameters

        Returns:
        torch.Tensor: IDR values for each point in u
        """
        x = self.u_to_x(u=u, parameters=parameters).to(self._gpu)
        u_dep = self.dep_x_to_u(x=x, parameters=parameters).to(self._gpu)

        pdf = [self._independence_copula.pdf(u, log=True)] + [
            copula.pdf(
                u_dep,
                parameters["copula"][
                    i * copula.parameters_size() : (i + 1) * copula.parameters_size()
                ],
                log=True,
            )
            for i, copula in enumerate(self._copulas)
        ]
        pdf = torch.stack(pdf, dim=1)

        partial_pdf = pdf
        if marginal:
            indep_marginal = self.pdf_indep_marginal(x=x)
            dep_marginal = self.pdf_dep_marginal(x=x, parameters=parameters)
            marginal_pdf = torch.stack(
                [indep_marginal] + [dep_marginal for _ in range(len(self._copulas))],
                dim=1,
            )
            partial_pdf = pdf + torch.log(parameters["weight"].t()) + marginal_pdf
        else:
            partial_pdf = pdf + torch.log(parameters["weight"].t())
        pdf = torch.logsumexp(partial_pdf, dim=1)
        idrs = partial_pdf[:, 0] - pdf
        return torch.exp(idrs).to(self._gpu)

    def log_class_proba(
        self,
        u: torch.Tensor,
        x: torch.Tensor,
        u_dep: torch.Tensor,
        parameters: Dict[str, torch.Tensor],
        marginal: bool = True,
    ) -> torch.Tensor:
        pdf = [self._independence_copula.pdf(u, log=True).to(self._gpu)] + [
            copula.pdf(
                u_dep,
                parameters["copula"][
                    i * copula.parameters_size() : (i + 1) * copula.parameters_size()
                ],
                log=True,
            ).to(self._gpu)
            for i, copula in enumerate(self._copulas)
        ]
        pdf = torch.stack(pdf, dim=1).to(self._gpu)

        partial_pdf = pdf
        if marginal:
            indep_marginal = self.pdf_indep_marginal(x=x)
            dep_marginal = self.pdf_dep_marginal(x=x, parameters=parameters)
            marginal_pdf = torch.stack(
                [indep_marginal] + [dep_marginal for _ in range(len(self._copulas))],
                dim=1,
            ).to(self._gpu)
            partial_pdf = pdf + torch.log(parameters["weight"].t()) + marginal_pdf
        else:
            partial_pdf = pdf + torch.log(parameters["weight"].t())
        pdf = torch.logsumexp(partial_pdf, dim=1)
        idrs = partial_pdf - torch.stack(
            [pdf for _ in range(len(self._copulas) + 1)], dim=1
        ).to(self._gpu)
        return idrs

    def merge_parameters(
        self, theta: List[torch.Tensor] | Dict[str, torch.Tensor]
    ) -> torch.Tensor:
        """
        Merge separate parameter components into a single tensor.

        Parameters:
        theta (List[torch.Tensor] | Dict[str, torch.Tensor]): Separate parameter components

        Returns:
        torch.Tensor: Combined parameter tensor
        """
        return merge(theta)

    def theta_transform(self, theta: torch.Tensor) -> Dict[str, torch.Tensor]:
        """
        Transform parameters for optimization.

        This method transforms parameters to an unconstrained space for optimization,
        applying appropriate transformations to maintain constraints after inverse
        transformation.

        Parameters:
        theta (torch.Tensor): Original parameters

        Returns:
        Dict[str, torch.Tensor]: Dictionary of transformed parameters
        """
        parameters = self.split_parameters(theta)
        parameters["weight"] = clr(parameters["weight"]).to(self._gpu)
        parameters["dep_mu"] = torch.nn.functional.softplus(parameters["dep_mu"]).to(
            self._gpu
        )
        copula = parameters["copula"].clone()
        for i in range(len(self._copulas)):
            start = i * self._copulas[i].parameters_size()
            stop = (i + 1) * self._copulas[i].parameters_size()
            copula[start:stop] = self._copulas[i].theta_transform(copula[start:stop])
        parameters["copula"] = copula.to(self._gpu)
        return parameters

    def theta_inverse_transform(self, theta: torch.Tensor) -> Dict[str, torch.Tensor]:
        """
        Inverse transform parameters after optimization.

        This method transforms parameters back from an unconstrained space
        to their original constrained space after optimization.

        Parameters:
        theta (torch.Tensor): Transformed parameters

        Returns:
        Dict[str, torch.Tensor]: Dictionary of original parameters with constraints satisfied
        """
        parameters = self.split_parameters(theta)
        parameters["weight"] = clr_inv(parameters["weight"]).to(self._gpu)
        parameters["dep_mu"] = torch.log(torch.exp(parameters["dep_mu"]) - 1.0).to(
            self._gpu
        )
        if torch.any(torch.isnan(parameters["dep_mu"])):
            ("NaN detected in dep_mu parameters")
            parameters["dep_mu"] = torch.ones_like(parameters["dep_mu"])
        copula = parameters["copula"].clone()
        for i in range(len(self._copulas)):
            start = i * self._copulas[i].parameters_size()
            stop = (i + 1) * self._copulas[i].parameters_size()
            copula[start:stop] = self._copulas[i].theta_transform_inverse(
                copula[start:stop]
            )
        parameters["copula"] = copula.to(self._gpu)
        return parameters

    def parameters2theta(self, parameters: Dict[str, torch.Tensor]) -> torch.Tensor:
        """
        Convert parameter dictionary to a single parameter tensor.

        Parameters:
        parameters (Dict[str, torch.Tensor]): Dictionary of parameter components

        Returns:
        torch.Tensor: Combined parameter tensor
        """
        return torch.cat(
            [parameters["weight"], parameters["dep_mu"], parameters["copula"]]
        ).to(self._gpu)

    def compute_loss(self, theta: torch.Tensor, u: torch.Tensor):
        """
        Compute the negative log-likelihood loss for optimization.

        Applies inverse transformation to parameters before computing likelihood.

        Parameters:
        theta (torch.Tensor): Transformed parameters
        u (torch.Tensor): Data points in [0,1]^d space

        Returns:
        torch.Tensor: Negative log-likelihood value
        """
        parameters = self.theta_inverse_transform(theta)
        ll = -self.likelihood_class_proba(
            u=u, parameters=parameters, log=True, marginal=True
        )
        return ll

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
        Fit the independence mixture model parameters to the given data.

        Parameters:
        u (torch.Tensor): Input tensor of shape (n, dim) containing points in [0,1]^d space
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
        parameters = self.theta_transform(theta)
        theta = self.parameters2theta(parameters)

        # tensor_name = [
        #     "01_indep_w0",
        #     "02_clayton_w",
        #     "03_frank_w",
        #     "04_gumbel_w",
        #     "21_dep_marginal1_mu",
        #     "22_dep_marginal2_mu",
        #     "41_clayton_theta",
        #     "42_frank_theta",
        #     "43_gumbel_theta",
        # ]
        # tensor_name = [
        #     "01_indep_w0",
        #     "02_dep_w",
        #     "21_dep_marginal1_mu",
        #     "22_dep_marginal2_mu",
        #     "41_gaussian1_sigma",
        #     "41_gaussian2_sigma",
        #     "41_gaussian3_sigma",
        #     "41_gaussian4_sigma",
        # ]
        u.to(self._gpu)

        def compute_loss(theta: torch.Tensor) -> torch.Tensor:
            return self.compute_loss(theta, u)

        theta = fit_auxilary(
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
        parameters = self.theta_inverse_transform(theta)
        return self.parameters2theta(parameters)
