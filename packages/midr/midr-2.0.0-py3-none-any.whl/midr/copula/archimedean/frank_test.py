# SPDX-FileCopyrightText: 2025 Laurent Modolo <laurent@modolo.fr>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Unit tests for the FrankCopula class and related functions.

This module provides tests for the FrankCopula implementation,
including its generator, inverse generator, CDF, PDF, likelihood, and fitting.
"""

import torch

from . import frank

torch.set_default_dtype(torch.float64)
torch.set_printoptions(precision=10)
torch.set_printoptions(sci_mode=False)


def test_frank_copula_psi():
    """
    Test the generator function (psi) of the FrankCopula.

    This test checks that the psi function returns the expected values for given inputs.
    """
    u = torch.tensor([0.2])
    theta = torch.tensor(38)
    copula = frank.FrankCopula(2)
    psi = copula.psi(u, theta)
    expected = torch.tensor([0.0449413632])
    assert torch.isclose(psi, expected)  # type: ignore
    u = torch.tensor([0.1, 0.2, 0.3])
    copula = frank.FrankCopula(2)
    psi = copula.psi(u, theta)
    expected = torch.tensor([0.0618991740, 0.0449413632, 0.0355322510])
    assert all(torch.isclose(psi, expected))  # type: ignore


def test_frank_copula_ipsi():
    """
    Test the inverse generator function (ipsi) of the FrankCopula.

    This test checks that the ipsi function returns the expected values for given inputs.
    """
    u = torch.tensor([0.2])
    theta = torch.tensor(38)
    copula = frank.FrankCopula(2)
    ipsi = copula.ipsi(u, theta)
    expected = torch.tensor([0.0005005767])
    assert torch.isclose(ipsi, expected)  # type: ignore
    u = torch.tensor([0.1, 0.2, 0.3])
    copula = frank.FrankCopula(2)
    ipsi = copula.ipsi(u, theta)
    expected = torch.tensor([0.0226247932, 0.0005005767, 0.0000111955])
    assert all(torch.isclose(ipsi, expected))  # type: ignore


def test_frank_copula_cdf():
    """
    Test the CDF computation of the FrankCopula.

    This test checks that the CDF returns the expected values for given inputs.
    """
    theta = torch.tensor(38)
    u = torch.tensor([[0.1, 0.2], [0.3, 0.4], [0.4, 0.5]])
    copula = frank.FrankCopula(2)
    cdf = copula.cdf(u, theta)
    expected = torch.tensor([0.0994306685, 0.2994177902, 0.3994177839])
    assert all(torch.isclose(cdf, expected))


def test_frank_copula_pdf():
    """
    Test the PDF computation of the FrankCopula.

    This test checks that the PDF returns the expected values for given inputs,
    and that the median PDF for random samples is as expected.
    """
    theta = torch.tensor(38)
    u = torch.tensor([[0.1, 0.2], [0.3, 0.4], [0.4, 0.5]], requires_grad=True)
    copula = frank.FrankCopula(2)
    pdf = copula.pdf(u, theta)
    expected = torch.tensor([0.8140910765, 0.8132946734, 0.8132942842])
    assert all(torch.isclose(pdf, expected))
    copula = frank.FrankCopula(2)
    u = copula.random(1000, torch.tensor([20.0]))
    pdf = copula.pdf(u, theta)
    assert torch.allclose(pdf.median(), torch.tensor(9.0), atol=1, rtol=1)


def test_frank_copula_likelihood():
    """
    Test the log-likelihood computation of the FrankCopula.

    This test checks that the log-likelihood matches the expected value for given inputs.
    """
    u = torch.tensor([[0.1, 0.2], [0.3, 0.4], [0.4, 0.5]], requires_grad=True)
    copula = frank.FrankCopula(2)
    theta = torch.tensor(38)
    likelihood = copula.likelihood(u, theta, True)
    expected = torch.tensor(-0.6190070767)
    assert torch.isclose(likelihood, expected)


def test_frank_copula_fit():
    """
    Test the parameter fitting of the FrankCopula.

    This test checks that the fitted parameter converges to the expected value for simulated data.
    """
    # torch.manual_seed(123)
    copula = frank.FrankCopula(2)
    expected = torch.tensor([24.0])
    u = copula.random(1000, torch.tensor([24.0]))
    theta = torch.tensor([5.0])
    theta = copula.fit(u, theta)[0]
    assert torch.isclose(theta, expected, rtol=1e-1, atol=1e-1)
    theta = torch.tensor([5.0])
    theta = copula.fit(u, theta, algorithm="SGD", start_lr=0.1)[0]
    assert torch.isclose(theta, expected, rtol=0.5, atol=0.5)
    theta = torch.tensor([5.0])
    theta = copula.fit(u, theta, algorithm="Adam", start_lr=0.1)[0]
    assert torch.isclose(theta, expected, rtol=0.5, atol=0.5)
    theta = torch.tensor([5.0])
    theta = copula.fit(u, theta, algorithm="SGD_LBFGS", start_lr=0.1)[0]
    assert torch.isclose(theta, expected, rtol=0.5, atol=0.5)
    copula = frank.FrankCopula(4)
    expected = torch.tensor([34.0])
    u = copula.random(1000, torch.tensor([34.0]))
    theta = torch.tensor([5.0])
    theta = copula.fit(u, theta)[0]
    assert torch.isclose(theta, expected, rtol=1e-1, atol=1e-1)
    copula = frank.FrankCopula(2)
    u = copula.random(100, torch.tensor([0.8]))
    expected = torch.tensor([0.4])
    theta = torch.tensor([5.0])
    theta = copula.fit(u, theta)[0]
    assert torch.isclose(theta, expected, rtol=1.0, atol=1.0)
