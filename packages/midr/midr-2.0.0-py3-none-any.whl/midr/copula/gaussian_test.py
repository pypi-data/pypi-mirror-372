# SPDX-FileCopyrightText: 2025 Laurent Modolo <laurent@modolo.fr>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import torch

from ..auxilary import ecdf, r_gaussian_mixture
from . import gaussian

torch.set_default_dtype(torch.float64)
torch.set_printoptions(precision=10)
torch.set_printoptions(sci_mode=False)


def test_gaussian_copula():
    copula = gaussian.GaussianCopula(2)
    assert copula._family == "Gaussian"
    assert copula._parameters_size == 4
    assert copula.theta_transform(
        torch.tensor([[0.0, 1.0], [0.0, 1.0]])
    ).shape == torch.Size([4])
    assert copula.theta_transform_inverse(
        torch.tensor([[0.0, 1.0], [0.0, 1.0]])
    ).shape == torch.Size([4])
    assert torch.allclose(
        copula.split_parameters(torch.tensor([[0.0, 1.0], [0.0, 1.0]]))["sigma"],
        torch.tensor([[1.0000000000, 0.7310585786], [0.7310585786, 1.0000000000]]),
    )


def test_gaussian_copula_cdf():
    u = torch.tensor([[0.1, 0.2], [0.3, 0.4], [0.4, 0.5]])
    copula = gaussian.GaussianCopula(2)
    theta = torch.tensor([1.0, 0.5, 0.5, 1.0])
    cdf = copula.cdf(u, theta)
    expected = torch.tensor([0.0, 0.0, 0.0])
    assert all(torch.isclose(cdf, expected))


def test_gaussian_copula_pdf():
    u = torch.tensor([[0.1, 0.2], [0.3, 0.4], [0.4, 0.5]], requires_grad=True)
    copula = gaussian.GaussianCopula(2)
    theta = torch.tensor([1.0, 0.5, 0.5, 1.0])
    pdf = copula.pdf(u, theta)
    expected = torch.tensor([0.0893163256, 0.1764590543, 0.1929735689])
    assert all(torch.isclose(pdf, expected))
    assert all(torch.isclose(pdf, expected))
    copula = gaussian.GaussianCopula(2)
    pdf = copula.pdf(u, theta, log=True)
    expected = torch.tensor([-2.4155709902, -1.7346664163, -1.6452020480])
    assert all(torch.isclose(pdf, expected))


def test_gaussian_copula_likelihood():
    u = torch.tensor([[0.1, 0.2], [0.3, 0.4], [0.4, 0.5]], requires_grad=True)
    copula = gaussian.GaussianCopula(2)
    theta = torch.tensor([1.0, 0.5, 0.5, 1.0])
    likelihood = copula.likelihood(u, theta, log=True)
    expected = torch.tensor(-5.7954394546)
    assert torch.isclose(likelihood, expected)


def test_gaussian_copula_fit():
    copula = gaussian.GaussianCopula(2)
    x = copula.random(n=1000, theta=torch.tensor([1.0, 0.1, 0.1, 1.0]))
    theta = torch.tensor([1.0, 0.1, 0.1, 1.0])
    copula = gaussian.GaussianCopula(2)
    theta = copula.fit(ecdf(x), theta)
    parameters = copula.split_parameters(theta)
    assert torch.isclose(
        parameters["sigma"][0, 1], torch.tensor(0.5), atol=0.3, rtol=0.3
    )
    assert torch.isclose(
        parameters["sigma"][1, 0], torch.tensor(0.5), atol=0.3, rtol=0.3
    )
    _, x = r_gaussian_mixture(size=1000, ratio=1.0, correlation=0.8, dep_mu=[5.0, 5.0])
    theta = torch.tensor([1.0, 0.1, 0.1, 1.0])
    copula = gaussian.GaussianCopula(2)
    theta = copula.fit(ecdf(x), theta)
    parameters = copula.split_parameters(theta)
    assert torch.isclose(
        parameters["sigma"][0, 1], torch.tensor(0.8), atol=0.05, rtol=0.05
    )
    assert torch.isclose(
        parameters["sigma"][1, 0], torch.tensor(0.8), atol=0.05, rtol=0.05
    )
