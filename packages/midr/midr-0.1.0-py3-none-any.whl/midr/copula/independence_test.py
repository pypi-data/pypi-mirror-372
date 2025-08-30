# SPDX-FileCopyrightText: 2025 Laurent Modolo <laurent@modolo.fr>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Unit tests for the IndependenceCopula class in the IDR package.

This module provides tests for the IndependenceCopula implementation, including its
CDF, PDF, and likelihood computations.
"""

from . import independence
import torch

torch.set_default_dtype(torch.float64)
torch.set_printoptions(precision=10)
torch.set_printoptions(sci_mode=False)

def test_independence_copula_cdf():
    """
    Test the CDF computation of the IndependenceCopula.

    This test checks that the CDF returns the product of marginals for each row.
    """
    u = torch.tensor(
        [[0.1, 0.2],
        [0.3, 0.4],
        [0.4, 0.5]])
    copula = independence.IndependenceCopula(2)
    cdf = copula.cdf(u)
    expected = torch.tensor([0.02, 0.12, 0.20])
    assert all(torch.isclose(cdf, expected))

def test_independence_copula_pdf():
    """
    Test the PDF computation of the IndependenceCopula.

    This test checks that the PDF returns ones for all input rows, and zeros for log-PDF.
    """
    u = torch.tensor(
        [[0.1, 0.2],
        [0.3, 0.4],
        [0.4, 0.5]], requires_grad=True)
    copula = independence.IndependenceCopula(2)
    pdf = copula.pdf(u)
    expected = torch.tensor([1.0, 1.0, 1.0])
    assert all(torch.isclose(pdf, expected))
    assert all(torch.isclose(pdf, expected))
    copula = independence.IndependenceCopula(2)
    pdf = copula.pdf(u, log=True)
    expected = torch.tensor([0.0, 0.0, 0.0])
    assert all(torch.isclose(pdf, expected))

def test_independence_copula_likelihood():
    """
    Test the log-likelihood computation of the IndependenceCopula.

    This test checks that the log-likelihood is zero for any input.
    """
    u = torch.tensor(
        [[0.1, 0.2],
        [0.3, 0.4],
        [0.4, 0.5]], requires_grad=True)
    copula = independence.IndependenceCopula(2)
    likelihood = copula.likelihood(u, log=True)
    expected = torch.tensor(0.0)
    assert torch.isclose(likelihood, expected)
