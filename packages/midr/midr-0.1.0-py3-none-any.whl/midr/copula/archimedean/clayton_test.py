# SPDX-FileCopyrightText: 2025 Laurent Modolo <laurent@modolo.fr>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Unit tests for the ClaytonCopula class in the IDR package.

This module provides tests for the ClaytonCopula implementation, including its
generator functions (psi, ipsi), CDF, PDF, likelihood, and parameter fitting.
"""

import torch

from . import clayton

torch.set_default_dtype(torch.float64)
torch.set_printoptions(precision=10)
torch.set_printoptions(sci_mode=False)


def test_theta():
    copula = clayton.ClaytonCopula(2)
    assert copula.split_parameters(torch.tensor([18.0]))[0] == torch.tensor(18.0)


def test_bounds():
    """
    Test the bounds of the ClaytonCopula.

    This test checks that the bounds are correctly set for the ClaytonCopula.
    """
    copula = clayton.ClaytonCopula(2)
    assert copula.lower_bound() == torch.tensor(0.0)
    assert copula.upper_bound() == torch.tensor(36.0)


def test_clayton_copula_psi():
    """
    Test the generator function (psi) of the ClaytonCopula.

    This test checks that the psi function returns expected values for given inputs.
    """
    u = torch.tensor([0.2])
    copula = clayton.ClaytonCopula(2)
    theta = torch.tensor(18)
    psi = copula.psi(u, theta)
    expected = torch.tensor([0.9899221])
    assert torch.isclose(psi, expected)  # type: ignore
    u = torch.tensor([0.1, 0.2, 0.3])
    copula = clayton.ClaytonCopula(2)
    psi = copula.psi(u, theta)
    expected = torch.tensor([0.9947190, 0.9899221, 0.9855299])
    assert all(torch.isclose(psi, expected))  # type: ignore


def test_clayton_copula_ipsi():
    """
    Test the inverse generator function (ipsi) of the ClaytonCopula.

    This test checks that the ipsi function returns expected values for given inputs.
    """
    u = torch.tensor([0.2])
    theta = torch.tensor(18)
    copula = clayton.ClaytonCopula(2)
    ipsi = copula.ipsi(u, theta)
    expected = torch.tensor([3.814697e12])
    assert torch.isclose(ipsi, expected)  # type: ignore
    u = torch.tensor([0.1, 0.2, 0.3])
    copula = clayton.ClaytonCopula(2)
    ipsi = copula.ipsi(u, theta)
    expected = torch.tensor([1.000000e18, 3.814697e12, 2.581175e09])
    assert all(torch.isclose(ipsi, expected))  # type: ignore


def test_clayton_copula_cdf():
    """
    Test the cumulative distribution function (CDF) of the ClaytonCopula.

    This test checks that the CDF returns expected values for various input tensors and parameters.
    """
    theta = torch.tensor(18)
    u = torch.tensor([[0.1, 0.2], [0.3, 0.4], [0.4, 0.5]])
    copula = clayton.ClaytonCopula(2)
    cdf = copula.cdf(u, theta)
    expected = torch.tensor([0.09999998, 0.29990632, 0.39960344])
    assert all(torch.isclose(cdf, expected))
    u = torch.tensor(
        [
            [0.0000823699, 0.0144055813],
            [0.0002568781, 0.1099687194],
            [0.0001082383, 0.1083932891],
            [0.0739549261, 0.0001539759],
            [0.0002443889, 0.0165795237],
            [0.0287368625, 0.0002794216],
            [0.0162095142, 0.0001021657],
        ]
    )
    cdf = copula.cdf(u, torch.tensor([56]))
    expected = torch.tensor(
        [
            0.0000823699,
            0.0002568781,
            0.0001082383,
            0.0001539759,
            0.0002443889,
            0.0002794216,
            0.0001021657,
        ]
    )
    assert all(torch.isclose(cdf, expected))
    u = torch.tensor(
        [
            [0.05310835247059809278, 0.00007070419062254315],
            [0.00021338707946744195, 0.18645972278191849658],
            [0.00006658283065226642, 0.00005867076567795072],
        ]
    )
    cdf = copula.cdf(u, torch.tensor([88]))
    expected = torch.tensor([0.0, 0.0, 0.0])
    assert all(torch.isclose(cdf, expected))

    cdf = copula.cdf(u, torch.tensor([0.0]), log=True)
    expected = torch.tensor([-12.4924267796, -10.1319427939, -19.3606327962])
    assert all(torch.isclose(cdf, expected))


def test_clayton_copula_pdf():
    """
    Test the probability density function (PDF) of the ClaytonCopula.

    This test checks that the PDF returns expected values for various input tensors and parameters.
    """
    theta = torch.tensor(18)
    u = torch.tensor([[0.1, 0.2], [0.3, 0.4], [0.4, 0.5]], requires_grad=True)
    copula = clayton.ClaytonCopula(2)
    pdf = copula.pdf(u, theta)
    expected = torch.tensor([0.0003623934, 0.2647144254, 0.6598797606])
    assert all(torch.isclose(pdf, expected))
    # Additional log-PDF and edge case tests can be enabled if needed.
    copula = clayton.ClaytonCopula(2)
    u = copula.random(1000, torch.tensor([10.0]))
    pdf = copula.pdf(u, theta)
    assert torch.allclose(pdf.median(), torch.tensor(9.0), atol=1, rtol=1)


def test_clayton_copula_likelihood():
    """
    Test the log-likelihood computation of the ClaytonCopula.

    This test checks that the log-likelihood matches the expected value for given inputs.
    """
    u = torch.tensor([[0.1, 0.2], [0.3, 0.4], [0.4, 0.5]], requires_grad=True)
    copula = clayton.ClaytonCopula(2)
    theta = torch.tensor(18)
    likelihood = copula.likelihood(u, theta, True)
    expected = torch.tensor(-9.667582)
    assert torch.isclose(likelihood, expected)
    likelihood = copula.likelihood(u, theta, False)
    expected = torch.tensor(-9.667582).exp()
    assert torch.isclose(likelihood, expected)


def test_clayton_copula_fit():
    """
    Test parameter fitting for the ClaytonCopula.

    This test checks that the copula fitting procedure recovers the expected parameter values
    for simulated data.
    """
    torch.manual_seed(123)
    copula = clayton.ClaytonCopula(2)
    expected = torch.tensor([18.0])
    u = copula.random(1000, torch.tensor(18.0))
    theta = torch.tensor([5.0])
    theta = copula.fit(u, theta)[0]
    assert torch.isclose(theta, expected, rtol=0.5, atol=0.5)
    theta = torch.tensor([5.0])
    theta = copula.fit(u, theta, algorithm="SGD", start_lr=0.1)[0]
    assert torch.isclose(theta, expected, rtol=0.5, atol=0.5)
    theta = torch.tensor([5.0])
    theta = copula.fit(u, theta, algorithm="Adam", start_lr=0.1)[0]
    assert torch.isclose(theta, expected, rtol=0.5, atol=0.5)
    theta = torch.tensor([5.0])
    theta = copula.fit(u, theta, algorithm="SGD_LBFGS", start_lr=0.1)[0]
    assert torch.isclose(theta, expected, rtol=0.5, atol=0.5)
    copula = clayton.ClaytonCopula(4)
    expected = torch.tensor([10.0])
    u = copula.random(1000, torch.tensor(10))
    theta = torch.tensor([5.0])
    theta = copula.fit(u, theta)[0]
    assert torch.isclose(theta, expected, rtol=0.5, atol=0.5)
