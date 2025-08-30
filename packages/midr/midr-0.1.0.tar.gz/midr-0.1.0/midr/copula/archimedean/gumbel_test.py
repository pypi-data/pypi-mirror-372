# SPDX-FileCopyrightText: 2025 Laurent Modolo <laurent@modolo.fr>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Unit tests for the GumbelCopula class and related functions.

This module provides tests for the GumbelCopula implementation,
including its psi, ipsi, cdf, pdf, likelihood, and fit computations.
"""

import torch

from . import gumbel

torch.set_default_dtype(torch.float64)
torch.set_printoptions(precision=10)
torch.set_printoptions(sci_mode=False)


def test_gumbel_copula_psi():
    """
    Test the psi (generator) function of the GumbelCopula.

    This test checks that the psi function returns expected values for given inputs.
    """
    u = torch.tensor([0.2])
    theta = torch.tensor(20)
    copula = gumbel.GumbelCopula(2)
    psi = copula.psi(u, theta)
    expected = torch.tensor([0.3974521082])
    assert torch.isclose(psi, expected)  # type: ignore
    u = torch.tensor([0.1, 0.2, 0.3])
    copula = gumbel.GumbelCopula(2)
    psi = copula.psi(u, theta)
    expected = torch.tensor([0.4101423919, 0.3974521160, 0.3900121152])
    assert all(torch.isclose(psi, expected))  # type: ignore


def test_gumbel_copula_ipsi():
    """
    Test the ipsi (inverse generator) function of the GumbelCopula.

    This test checks that the ipsi function returns expected values for given inputs.
    """
    u = torch.tensor([0.2])
    theta = torch.tensor(20)
    copula = gumbel.GumbelCopula(2)
    ipsi = copula.ipsi(u, theta)
    expected = torch.tensor([13598.2978600523])
    assert torch.isclose(ipsi, expected)  # type: ignore
    u = torch.tensor([0.1, 0.2, 0.3])
    copula = gumbel.GumbelCopula(2)
    ipsi = copula.ipsi(u, theta)
    expected = torch.tensor([17551486.0, 13598.3027343750, 40.9575195312])
    assert all(torch.isclose(ipsi, expected))  # type: ignore


def test_gumbel_copula_cdf():
    """
    Test the CDF computation of the GumbelCopula.

    This test checks that the CDF returns expected values for given inputs.
    """
    theta = torch.tensor(20)
    u = torch.tensor([[0.1, 0.2], [0.3, 0.4], [0.4, 0.5]])
    copula = gumbel.GumbelCopula(2)
    cdf = copula.cdf(u, theta)
    expected = torch.tensor([0.09999108, 0.29992342, 0.39993112])
    assert all(torch.isclose(cdf, expected))


def test_gumbel_copula_pdf():
    """
    Test the PDF computation of the GumbelCopula.

    This test checks that the PDF returns expected values for given inputs,
    and that the median PDF for random samples is as expected.
    """
    theta = torch.tensor(20)
    u = torch.tensor([[0.1, 0.2], [0.3, 0.4], [0.4, 0.5]], requires_grad=True)
    copula = gumbel.GumbelCopula(2)
    pdf = copula.pdf(u, theta)
    expected = torch.tensor([0.0511924513, 0.2322623730, 0.2147843391])
    assert all(torch.isclose(pdf, expected))
    copula = gumbel.GumbelCopula(2)
    u = copula.random(1000, torch.tensor([20.0]))
    pdf = copula.pdf(u, theta)
    assert torch.allclose(pdf.median(), torch.tensor(13.0), atol=1, rtol=1)


def test_gumbel_copula_likelihood():
    """
    Test the log-likelihood computation of the GumbelCopula.

    This test checks that the log-likelihood matches the expected value for given inputs.
    """
    u = torch.tensor([[0.1, 0.2], [0.3, 0.4], [0.4, 0.5]], requires_grad=True)
    copula = gumbel.GumbelCopula(2)
    theta = torch.tensor(20)
    likelihood = copula.likelihood(u, theta, True)
    expected = torch.tensor(-5.9701711137)
    assert torch.isclose(likelihood, expected)


def test_gumbel_copula_fit():
    """
    Test the parameter fitting for the GumbelCopula.

    This test checks that the fitted parameter is close to the expected value
    for simulated data from the Gumbel copula.
    """
    torch.manual_seed(123)
    copula = gumbel.GumbelCopula(2)
    expected = torch.tensor([20.0])
    u = copula.random(1000, torch.tensor([20.0]))
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
    copula = gumbel.GumbelCopula(4)
    expected = torch.tensor([10.0])
    u = copula.random(1000, torch.tensor([10.0]))
    theta = torch.tensor([5.0])
    theta = copula.fit(u, theta)[0]
    assert torch.isclose(theta, expected, rtol=1e-1, atol=1e-1)
