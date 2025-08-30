# SPDX-FileCopyrightText: 2025 Laurent Modolo <laurent@modolo.fr>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Unit tests for the GaussianMixtureMarginal class in the IDR package.

This module provides tests for the GaussianMixtureMarginal implementation,
including its CDF, inverse CDF, PDF, log-CDF, log-PDF, and parameter handling.
"""

import torch

from .gaussian_mixture import GaussianMixtureMarginal

torch.set_default_dtype(torch.float64)
torch.set_printoptions(precision=10)
torch.set_printoptions(sci_mode=False)


def test_gaussian_params():
    """
    Test the initialization and parameter attributes of GaussianMixtureMarginal.

    This test checks that the family name and parameter size are set correctly.
    """
    marginal = GaussianMixtureMarginal()
    assert marginal._family == "GaussianMixture"
    assert marginal._parameters_size == 4
    assert torch.allclose(
        marginal.theta_transform(torch.tensor([0.5, 1.0, 1.0, 1.0])),
        torch.tensor([0.0, 1.0, 1.0, 1.0]),
    )
    assert torch.allclose(
        marginal.theta_transform_inverse(torch.tensor([0.5, 1.0, 1.0, 1.0])),
        torch.tensor([0.1863237232, 1.0, 1.0, 1.0]),
    )


def test_gaussian_cdf():
    """
    Test the CDF computation of GaussianMixtureMarginal.

    This test checks that the CDF returns expected values for given inputs.
    """
    marginal = GaussianMixtureMarginal()
    x = torch.tensor([0.0, 1.0, 2.0])

    theta = torch.tensor([0.5, 1.0, 1.0, 1.0])
    assert torch.allclose(
        marginal.cdf(x, theta), torch.tensor([0.3293276715, 0.6706723285, 0.9092972427])
    )


def test_gaussian_cdf_inv():
    marginal = GaussianMixtureMarginal()
    x = torch.tensor([0.0, 1.0, 2.0])
    theta = torch.tensor([0.5, 1.0, 1.0, 1.0])
    assert torch.allclose(
        marginal.cdf_inv(marginal.cdf(x, theta), theta, num_samples=10000),
        x,
        rtol=0.01,
        atol=0.01,
    )
    assert torch.allclose(
        marginal.cdf_inv(marginal.cdf(x, theta), theta, num_samples=1000, optim=True),
        x,
        rtol=0.01,
        atol=0.01,
    )
    if False:
        import time

        x = torch.distributions.Normal(0, 1).sample((10000,))
        time_start = time.time()
        marginal.cdf_inv(marginal.cdf(x, theta), theta)
        time_stop = time.time()
        print(f"Interpolation : {time_stop - time_start} seconds")
        time_start = time.time()
        marginal.cdf_inv(marginal.cdf(x, theta), theta, optim=True)
        time_stop = time.time()
        print(f"Optimization : {time_stop - time_start} seconds")
        assert False


def test_gaussian_pdf():
    marginal = GaussianMixtureMarginal()
    x = torch.tensor([0.0, 1.0, 2.0])

    theta = torch.tensor([0.5, 1.0, 1.0, 1.0])
    assert torch.allclose(
        marginal.pdf(x, theta), torch.tensor([0.3204564291, 0.3204564291, 0.1479808753])
    )


def test_gaussian_logcdf():
    marginal = GaussianMixtureMarginal()
    x = torch.tensor([0.0, 1.0, 2.0])

    theta = torch.tensor([0.5, 1.0, 1.0, 1.0])
    assert torch.allclose(
        marginal.cdf(x, theta, True),
        torch.tensor([-1.1107020619, -0.3994745943, -0.0950832386]),
    )


def test_gaussian_logcdf_inv():
    marginal = GaussianMixtureMarginal()
    x = torch.tensor([0.5, 1.0, 2.0])
    theta = torch.tensor([0.0, 1.0, 1.0, 1.0])
    assert torch.allclose(
        marginal.cdf_inv(marginal.cdf(x, theta), theta, True, num_samples=10000),
        x.log(),
        atol=0.01,
        rtol=0.01,
    )


def test_gaussian_logpdf():
    marginal = GaussianMixtureMarginal()
    x = torch.tensor([0.0, 1.0, 2.0])

    theta = torch.tensor([0.5, 1.0, 1.0, 1.0])
    assert torch.allclose(
        marginal.pdf(x, theta, True),
        torch.tensor([-1.1380089586, -1.1380089586, -1.9106722345]),
    )
