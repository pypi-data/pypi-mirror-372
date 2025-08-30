# SPDX-FileCopyrightText: 2025 Laurent Modolo <laurent@modolo.fr>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Independence Mixture Copula implementation for the IDR package.

This module provides the IndepMixtureCopula class, which models a mixture of the independence copula
and various Archimedean copulas (Clayton, Frank, Gumbel) to flexibly capture both independent and
dependent structures in multivariate data.

Classes:
    IndepMixtureCopula: Mixture copula including the independence copula as a component.
"""

from typing import Optional

import torch

from ..archimedean.clayton import ClaytonCopula
from ..archimedean.frank import FrankCopula
from ..archimedean.gumbel import GumbelCopula
from ..independence import IndependenceCopula
from .mixture import MixtureCopula


class IndepMixtureCopula(MixtureCopula):
    """
    Mixture Copula that includes the independence copula as a component.

    This copula combines an independence copula with various Archimedean copulas,
    allowing for modeling a mix of dependent and independent structures.

    Parameters:
        dim (int): Dimension of the copula (number of variables)
        copulas (list): List of copula classes to include in the mixture,
                        default is [IndependenceCopula, ClaytonCopula, FrankCopula, GumbelCopula]
    """

    def __init__(
        self,
        dim: int,
        copulas: list = [
            IndependenceCopula(2),
            ClaytonCopula(2),
            FrankCopula(2),
            GumbelCopula(2),
        ],
        family: str = "IndepMixture",
        gpu: torch.device = torch.device("cpu"),
    ):
        """
        Initialize the IndepMixtureCopula.

        Parameters:
            dim (int): Dimension of the copula (number of variables)
            copulas (list): List of copula classes to include in the mixture
        """
        super().__init__(dim=dim, family=family, copulas=copulas)

    def cdf(
        self, u: torch.Tensor, theta: torch.Tensor, log: bool = False
    ) -> torch.Tensor:
        """
        Cumulative distribution function (CDF) of the Independence Mixture copula.

        This CDF is a weighted sum of the independence copula CDF and the other
        component copula CDFs.

        Parameters:
            u (torch.Tensor): 2D tensor of points in [0,1]^d space (each row is an observation)
            theta (torch.Tensor): Parameters of the copula including weights and component parameters
            log (bool, optional): If True, log of CDF will be returned

        Returns:
            torch.Tensor: 1D tensor of CDF values at points u, or log-CDF values if log=True
        """
        weights, theta = self.split_parameters(theta)
        weights.to(self._gpu)
        theta.to(self._gpu)
        cdf = torch.column_stack(
            [
                self._copulas[0].cdf(u).to(self._gpu),
                torch.column_stack(
                    [
                        copula.cdf(u, theta[i])
                        for i, copula in enumerate(self._copulas[1:])
                    ]
                ),
            ]
        ).to(self._gpu)
        if log:
            return torch.log(torch.matmul(cdf, weights))
        return torch.matmul(cdf, weights)

    def pdf(
        self, u: torch.Tensor, theta: torch.Tensor, log: bool = False
    ) -> torch.Tensor:
        """
        Probability density function (PDF) of the Independence Mixture copula.

        This calculates the weighted sum of PDFs from the independence copula
        and other component copulas.

        Parameters:
            u (torch.Tensor): 2D tensor of points in [0,1]^d space (each row is an observation)
            theta (torch.Tensor): Parameters of the copula including weights and component parameters
            log (bool, optional): If True, log of PDF will be returned

        Returns:
            torch.Tensor: 1D tensor of PDF values at points u, or log-PDF values if log=True
        """
        weight, theta = self.split_parameters(theta)
        return self.pdf_split(u=u, weight=weight, theta=theta, log=log)

    def pdf_split(
        self,
        u: torch.Tensor,
        weight: torch.Tensor,
        theta: torch.Tensor,
        log: bool = False,
    ) -> torch.Tensor:
        """
        Calculate PDF using pre-split parameters (weights and copula parameters).

        This is an optimized version that works with already split parameters
        to avoid repeated splitting operations.

        Parameters:
            u (torch.Tensor): 2D tensor of points in [0,1]^d space
            weight (torch.Tensor): Weights for each component copula
            theta (torch.Tensor): Parameters for each component copula
            log (bool): If True, return the log-PDF. Default is False

        Returns:
            torch.Tensor: PDF or log-PDF values at points u
        """
        weight.to(self._gpu)
        theta.to(self._gpu)
        pdf = [self._copulas[0].pdf(u, log=True).to(self._gpu)] + [
            copula.pdf(u, theta[i], log=True).to(self._gpu)
            for i, copula in enumerate(self._copulas[1:])
        ]
        pdf = torch.stack(pdf, dim=1).to(self._gpu)
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

    def random(self, n: int, theta: torch.Tensor) -> torch.Tensor:
        """
        Generate random samples from the Independence Mixture copula.

        Samples are drawn from each component copula according to their weights,
        then combined and randomly permuted.

        Parameters:
            n (int): Number of samples to generate
            theta (torch.Tensor): Parameters of the copula including weights and component parameters

        Returns:
            torch.Tensor: 2D tensor of shape (n, dim) containing samples from the mixture copula
        """
        weights, theta = self.split_parameters(theta)
        weights.to(self._gpu)
        theta.to(self._gpu)
        nj = (
            torch.distributions.Multinomial(total_count=n, probs=weights)
            .sample()
            .int()
            .to(self._gpu)
        )
        U = []
        for j in range(len(nj)):
            if nj[j] > 0:
                if j == 0:
                    u = self._copulas[j].random(nj[j].item()).to(self._gpu)
                else:
                    u = (
                        self._copulas[j]
                        .random(nj[j].item(), theta[j - 1])
                        .to(self._gpu)
                    )
                U.append(u)
        U_combined = torch.cat(U, dim=0).to(self._gpu)
        return U_combined[torch.randperm(n), :].to(self._gpu)

    def idr(
        self,
        u: torch.Tensor,
        theta: Optional[torch.Tensor] = None,
        tol: torch.Tensor = torch.tensor(0.000001),
        max_iter: int = 1000,
    ) -> torch.Tensor:
        """
        Calculate the Intrinsic Dependency Ratio (IDR) for the given data.

        The IDR measures the probability that a data point belongs to the
        independent component of the mixture. It helps identify which observations
        exhibit dependency structure and which are likely independent.

        Parameters:
            u (torch.Tensor): 2D tensor of points in [0,1]^d space
            tol (torch.Tensor): Tolerance for convergence in parameter fitting. Default is 0.000001
            max_iter (int): Maximum number of iterations for parameter fitting. Default is 1000

        Returns:
            torch.Tensor: IDR values for each point in u, representing the probability
                          of belonging to the independent component
        """
        u.to(self._gpu)
        if theta is None:
            theta = torch.tensor([1 / 4, 1 / 4, 1 / 4, 1 / 4, 5.0, 18.0, 8.0]).to(
                self._gpu
            )
            theta = self.fit(u=u, theta=theta, tol=tol, max_iter=max_iter).to(self._gpu)
        weight, theta = self.split_parameters(theta)
        weight.to(self._gpu)
        theta.to(self._gpu)
        idr = torch.log(weight[0]) - self.pdf_split(
            u=u, weight=weight, theta=theta, log=True
        )
        return torch.exp(idr)
