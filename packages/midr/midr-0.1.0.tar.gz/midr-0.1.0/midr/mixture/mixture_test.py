# SPDX-FileCopyrightText: 2025 Laurent Modolo <laurent@modolo.fr>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import torch

from ..auxilary import r_gaussian_mixture
from ..copula import ArchMixtureCopula
from ..marginal import GaussianMarginal
from .mixture import Mixture
from .multivariate import Multivariate

torch.set_default_dtype(torch.float64)
torch.set_printoptions(precision=10)
torch.set_printoptions(sci_mode=False)


def test_mixture_cdf():
    x = torch.tensor(
        [
            [0.0, 0.0],
            [1.0, 1.0],
            [2.0, 2.0],
        ]
    )
    multivariate = Multivariate(
        dim=2,
        copula=ArchMixtureCopula(dim=2),
        marginals=[GaussianMarginal()] * 2,
        family="archmixture_gaussian",
    )
    mixture = Mixture(
        dim=2, multivariates=[multivariate] * 2, family="archmixture_gaussian"
    )
    theta = torch.tensor([1.0, 2.0, 2.0, 3.0, 1 / 3, 1 / 3, 1 / 3, 18.0, 38.0, 10.0])
    theta = torch.cat([torch.tensor([0.5, 0.5]), theta, theta])
    assert torch.allclose(
        mixture.cdf(x, theta, False),
        torch.tensor([0.2492089876, 0.3690274508, 0.4999458844]),
    )
    assert torch.allclose(
        mixture.cdf(x, theta, True),
        torch.tensor([-1.3894634270, -0.9968842452, -0.6932554177]),
    )


def test_mixture_pdf():
    x = torch.tensor(
        [
            [0.0, 0.0],
            [1.0, 1.0],
            [2.0, 2.0],
        ]
    )
    multivariate = Multivariate(
        dim=2,
        copula=ArchMixtureCopula(dim=2),
        marginals=[GaussianMarginal()] * 2,
        family="archmixture_gaussian",
    )
    mixture = Mixture(
        dim=2, multivariates=[multivariate] * 2, family="archmixture_gaussian"
    )
    theta = torch.tensor([1.0, 2.0, 2.0, 3.0, 1 / 3, 1 / 3, 1 / 3, 18.0, 38.0, 10.0])
    theta = torch.cat([torch.tensor([0.5, 0.5]), theta, theta])
    assert torch.allclose(
        mixture.pdf(x, theta, False),
        torch.tensor([0.0576983677, 0.0096672323, 0.0013669471]),
    )
    assert torch.allclose(
        mixture.pdf(x, theta, True),
        torch.tensor([-2.8525263958, -4.6390132238, -6.5951753953]),
    )


def test_split_parameters():
    multivariate = Multivariate(
        dim=2,
        copula=ArchMixtureCopula(dim=2),
        marginals=[GaussianMarginal()] * 2,
        family="archmixture_gaussian",
    )
    mixture = Mixture(
        dim=2, multivariates=[multivariate] * 2, family="archmixture_gaussian"
    )
    theta = torch.tensor([1.0, 2.0, 2.0, 3.0, 1 / 3, 1 / 3, 1 / 3, 18.0, 38.0, 10.0])
    expected = [torch.tensor([0.5, 0.5]), theta, theta]
    parameters = torch.cat(expected)
    parameters = mixture.split_parameters(parameters)
    print(parameters)
    assert torch.equal(parameters["weights"][0], expected[0])
    assert torch.equal(parameters["multivariates"][0], expected[1])
    assert torch.equal(parameters["multivariates"][1], expected[1])


def test_fit():
    torch.manual_seed(123)
    x = torch.tensor(
        [
            [0.0, 0.0],
            [1.0, 1.0],
            [2.0, 2.0],
        ]
    )
    multivariate = Multivariate(
        dim=2,
        copula=ArchMixtureCopula(dim=2),
        marginals=[GaussianMarginal()] * 2,
        family="multivariate_gaussian",
    )
    mixture = Mixture(
        dim=2, multivariates=[multivariate, multivariate], family="archmixture_gaussian"
    )
    theta = torch.tensor([0.0, 1.0, 0.0, 1.0, 1 / 3, 1 / 3, 1 / 3, 5.0, 10.0, 2.0])
    theta = torch.cat([torch.tensor([0.5, 0.5]), theta, theta])

    _, x = r_gaussian_mixture(size=10000, ratio=0.4, correlation=0.7, dep_mu=[1.0, 1.0])
    theta = mixture.fit(x, theta)
    theta = mixture.split_parameters(theta)
    expected0 = torch.tensor([0.0, 1.0, 0.0, 1.0, 0.01, 0.01, 0.95, 4.8, 9.8, 1.0])
    expected1 = torch.tensor([0.8, 1.0, 0.8, 1.0, 0.01, 0.01, 0.95, 4.8, 9.8, 1.6])
    expected = torch.cat([torch.tensor([0.6, 0.4]), expected0, expected1])
    expected = mixture.split_parameters(expected)
    assert torch.allclose(
        theta["weights"][0], expected["weights"][0], atol=0.1, rtol=0.1
    )
    # assert torch.allclose(
    #     theta["multivariates"][0], expected["multivariates"][0], atol=0.2, rtol=0.2
    # )
    # assert torch.allclose(
    #     theta["multivariates"][1], expected["multivariates"][1], atol=0.2, rtol=0.2
    # )
