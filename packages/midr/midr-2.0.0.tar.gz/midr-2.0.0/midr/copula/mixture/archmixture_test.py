# SPDX-FileCopyrightText: 2025 Laurent Modolo <laurent@modolo.fr>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Unit tests for the ArchMixtureCopula class in the IDR package.

This module provides tests for the ArchMixtureCopula implementation,
including its CDF, PDF, likelihood, and parameter fitting.
"""

import torch

from . import archmixture

torch.set_default_dtype(torch.float64)
torch.set_printoptions(precision=10)
torch.set_printoptions(sci_mode=False)


def test_archmixture():
    copula = archmixture.ArchMixtureCopula(2)
    assert copula._family == "ArchMixture"
    assert copula._parameters_size == 6
    assert copula.bounds() == [
        (None, None),
        (None, None),
        (0.0, 36.0),
        (0.0, 398.0),
        (1.0, 100.0),
    ]
    assert torch.allclose(
        copula.theta_transform(torch.tensor([1 / 3, 1 / 3, 1 / 3, 18.0, 28.0, 10.0])),
        torch.tensor([0.0, 0.0, 18.0, 28.0, 10.0]),
    )
    assert torch.allclose(
        copula.theta_transform_inverse(torch.tensor([1 / 3, 1 / 3, 18.0, 28.0, 10.0])),
        torch.tensor([0.1553624035, 0.4223187983, 0.4223187983, 18.0, 28.0, 10.0]),
    )
    assert torch.allclose(
        copula.barrier_method(torch.tensor([1 / 3, 1 / 3, 18.0, 28.0, 10.0]), 2, 0.1),
        torch.tensor(-21723.4852792723),
    )


def test_archmixture_copula_cdf():
    """
    Test the CDF computation of the ArchMixtureCopula.

    This test checks that the CDF returns expected values for given inputs.
    """
    theta = torch.tensor([1 / 3, 1 / 3, 1 / 3, 18.0, 38.0, 10.0])
    u = torch.tensor([[0.1, 0.2], [0.3, 0.4], [0.4, 0.5]])
    copula = archmixture.ArchMixtureCopula(2)
    cdf = copula.cdf(u, theta)
    expected = torch.tensor([0.09959987, 0.29901488, 0.39894596])
    assert all(torch.isclose(cdf, expected))


def test_archmixture_copula_pdf():
    """
    Test the PDF computation of the ArchMixtureCopula.

    This test checks that the PDF returns expected values for given inputs,
    and that the median PDF for random samples is as expected.
    """
    theta = torch.tensor([1 / 3, 1 / 3, 1 / 3, 18.0, 28.0, 10.0])
    u = torch.tensor([[0.1, 0.2], [0.3, 0.4], [0.4, 0.5]], requires_grad=True)
    copula = archmixture.ArchMixtureCopula(2)
    pdf = copula.pdf(u, theta)
    expected = torch.tensor([0.8154633863, 1.1254792645, 1.2444006933])
    assert all(torch.isclose(pdf, expected))
    copula = archmixture.ArchMixtureCopula(2)
    u = copula.random(1000, theta)
    pdf = copula.pdf(u, theta)
    assert torch.allclose(pdf.median(), torch.tensor(7.0), atol=1, rtol=1)


def test_archmixture_copula_likelihood():
    """
    Test the log-likelihood computation of the ArchMixtureCopula.

    This test checks that the log-likelihood matches the expected value for given inputs.
    """
    u = torch.tensor([[0.1, 0.2], [0.3, 0.4], [0.4, 0.5]], requires_grad=True)
    theta = torch.tensor([1 / 3, 1 / 3, 1 / 3, 18.0, 38.0, 10.0])
    copula = archmixture.ArchMixtureCopula(2)
    likelihood = copula.likelihood(u, theta, True)
    expected = torch.tensor(-0.6495368)
    assert torch.isclose(likelihood, expected)


def test_archmixture_copula_fit():
    """
    Test parameter fitting for the ArchMixtureCopula.

    This test checks that the copula fitting procedure recovers the expected parameter values
    for simulated data, and works for different dimensions and parameter settings.
    """
    torch.manual_seed(123)
    copula = archmixture.ArchMixtureCopula(2)
    expected = torch.tensor([1 / 3, 1 / 3, 1 / 3, 18.0, 28.0, 10.0])
    u = copula.random(1000, expected)
    theta = torch.tensor([1 / 3, 1 / 3, 1 / 3, 5.0, 18.0, 8.0])
    theta = copula.fit(u, theta)
    expected = torch.tensor(
        [
            0.0000164178,
            0.7809758331,
            0.2190077491,
            10.6818237692,
            29.7460280669,
            26.9754457565,
        ]
    )
    assert all(torch.isclose(theta[:3], expected[:3], rtol=0.1, atol=0.1))
    assert all(torch.isclose(theta[3:], expected[3:], rtol=0.5, atol=0.5))
    copula = archmixture.ArchMixtureCopula(4)
    expected = torch.tensor([0.5, 0.2, 0.3, 18.0, 28.0, 10.0])
    u = copula.random(1000, expected)
    theta = torch.tensor([1 / 3, 1 / 3, 1 / 3, 5.0, 18.0, 8.0])
    theta = copula.fit(u, theta)
    assert all(torch.isclose(theta[:3], expected[:3], rtol=0.1, atol=0.1))
    assert all(torch.isclose(theta[3:], expected[3:], rtol=0.5, atol=0.5))
    n = 1000
    correlation = 0.7
    mean = torch.tensor([1.0, 1.0])
    covariance_matrix = torch.tensor([[1.0, correlation], [correlation, 1.0]])
    x = torch.distributions.MultivariateNormal(mean, covariance_matrix).sample((n,))
    from ...auxilary import ecdf

    u = ecdf(x)
    copula = archmixture.ArchMixtureCopula(2)
    expected = torch.tensor(
        [0.3, 0.7, 0.0003, 1.3553799110, 6.2205450018, 50.9709948413]
    )
    theta = torch.tensor([1 / 3, 1 / 3, 1 / 3, 5.0, 18.0, 8.0])
    theta = copula.fit(
        u,
        theta,
    )
    assert all(torch.isclose(theta[:3], expected[:3], rtol=0.1, atol=0.1))
    assert all(torch.isclose(theta[3:], expected[3:], rtol=0.5, atol=0.5))
