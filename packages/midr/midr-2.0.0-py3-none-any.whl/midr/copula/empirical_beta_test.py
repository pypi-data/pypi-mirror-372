# SPDX-FileCopyrightText: 2025 Laurent Modolo <laurent@modolo.fr>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Unit tests for the EmpiricalBetaCopula class and related functions.

This module provides tests for the EmpiricalBetaCopula implementation,
including its CDF, PDF, and likelihood computations.
"""

import torch

from . import empirical_beta

torch.set_default_dtype(torch.float64)
torch.set_printoptions(precision=10)
torch.set_printoptions(sci_mode=False)


def test_empirical_beta_copula_cdf():
    """
    Test the CDF computation of the EmpiricalBetaCopula.

    This test checks that the CDF returns zeros as expected for the current implementation.
    """
    u = torch.tensor([[0.1, 0.2], [0.3, 0.4], [0.4, 0.5]])
    copula = empirical_beta.EmpiricalBetaCopula(2)
    theta = torch.tensor([1.0, 10])
    cdf = copula.cdf(u, theta)
    expected = torch.tensor([0.0, 0.0, 0.0])
    assert all(torch.isclose(cdf, expected))


def test_empirical_beta_copula_pdf():
    """
    Test the PDF and log-PDF computation of the EmpiricalBetaCopula.

    This test checks that the PDF and log-PDF match expected values for given inputs.
    """
    u = torch.tensor([[0.1, 0.2], [0.3, 0.4], [0.4, 0.5]], requires_grad=True)
    copula = empirical_beta.EmpiricalBetaCopula(2)
    theta = torch.tensor([1.0, 10])
    pdf = copula.pdf(u, theta, log=False)
    expected = torch.tensor([2.5021440000, 1.7015040000, 1.5840000000])
    assert all(torch.isclose(pdf, expected))
    copula = empirical_beta.EmpiricalBetaCopula(2)
    pdf = copula.pdf(u, theta, log=True)
    expected = torch.tensor([0.9171479643, 0.5315125658, 0.4599532934])
    assert all(torch.isclose(pdf, expected))
    u = torch.tensor(
        [[0.1, 0.2, 0.3], [0.3, 0.4, 0.4], [0.4, 0.5, 0.6]], requires_grad=True
    )
    copula = empirical_beta.EmpiricalBetaCopula(3)
    theta = torch.tensor([1.0, 10])
    pdf = copula.pdf(u, theta, log=False)
    expected = torch.tensor([3.6195102720, 2.4315863040, 2.0275200000])
    assert all(torch.isclose(pdf, expected))
    u = torch.tensor(
        [[0.1, 0.2, 0.3, 0.1], [0.3, 0.4, 0.4, 0.2], [0.4, 0.5, 0.6, 0.3]],
        requires_grad=True,
    )
    copula = empirical_beta.EmpiricalBetaCopula(4)
    theta = torch.tensor([1.0, 10])
    pdf = copula.pdf(u, theta, log=False)
    expected = torch.tensor([8.8185483510, 3.5244484854, 2.5588039680])
    assert all(torch.isclose(pdf, expected))


def test_empirical_beta_copula_likelihood():
    """
    Test the log-likelihood computation of the EmpiricalBetaCopula.

    This test checks that the log-likelihood matches the expected value for given inputs.
    """
    u = torch.tensor([[0.1, 0.2], [0.3, 0.4], [0.4, 0.5]], requires_grad=True)
    copula = empirical_beta.EmpiricalBetaCopula(2)
    theta = torch.tensor([1.0, 10])
    likelihood = copula.likelihood(u, theta, log=True)
    expected = torch.tensor(1.9086138236)
    assert torch.isclose(likelihood, expected)
