# SPDX-FileCopyrightText: 2025 Laurent Modolo <laurent@modolo.fr>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import torch

from .gaussian import GaussianMarginal

torch.set_default_dtype(torch.float64)
torch.set_printoptions(precision=10)
torch.set_printoptions(sci_mode=False)


def test_gaussian_params():
    marginal = GaussianMarginal()
    assert marginal._family == "Gaussian"
    assert marginal._parameters_size == 2
    assert torch.allclose(
        marginal.theta_transform(torch.tensor([0.0, 1.0])),
        torch.tensor([0.0, torch.tensor(1.0)]),
    )
    assert torch.allclose(
        marginal.theta_transform_inverse(torch.tensor([0.0, 1.0])),
        torch.tensor([0.0, torch.tensor(1.0)]),
    )


def test_gaussian_cdf():
    marginal = GaussianMarginal()
    x = torch.tensor([0.0, 1.0, 2.0])
    theta = torch.tensor([0.0, torch.tensor(1.0)])
    assert torch.allclose(
        marginal.cdf(x, theta), torch.tensor([0.5000000000, 0.8413447461, 0.9772498681])
    )


def test_gaussian_cdf_inv():
    marginal = GaussianMarginal()
    x = torch.tensor([0.0, 1.0, 2.0])
    theta = torch.tensor([0.0, torch.tensor(1.0)])
    assert torch.allclose(marginal.cdf_inv(marginal.cdf(x, theta), theta), x)


def test_gaussian_pdf():
    marginal = GaussianMarginal()
    x = torch.tensor([0.0, 1.0, 2.0])
    theta = torch.tensor([0.0, torch.tensor(1.0)])
    assert torch.allclose(
        marginal.pdf(x, theta), torch.tensor([0.3989422804, 0.2419707245, 0.0539909665])
    )


def test_gaussian_pdf_cdf_inv():
    marginal = GaussianMarginal()
    x = torch.tensor([0.0, 1.0, 2.0])
    theta = torch.tensor([0.0, torch.tensor(1.0)])
    assert torch.allclose(
        marginal.pdf_cdf_inv(marginal.cdf(x, theta), theta),
        torch.tensor([0.3989422804, 0.2419707245, 0.0539909665]),
    )


def test_gaussian_logcdf():
    marginal = GaussianMarginal()
    x = torch.tensor([0.0, 1.0, 2.0])
    theta = torch.tensor([0.0, torch.tensor(1.0)])
    assert torch.allclose(
        marginal.cdf(x, theta, True),
        torch.tensor([-0.6931471806, -0.1727537790, -0.0230129093]),
    )


def test_gaussian_logpdf():
    marginal = GaussianMarginal()
    x = torch.tensor([0.0, 1.0, 2.0])
    theta = torch.tensor([0.0, torch.tensor(1.0)])
    assert torch.allclose(
        marginal.pdf(x, theta, True),
        torch.tensor([-0.9189385332, -1.4189385332, -2.9189385332]),
    )


def test_gaussian_logpdf_cdf_inv():
    marginal = GaussianMarginal()
    x = torch.tensor([0.0, 1.0, 2.0])
    theta = torch.tensor([0.0, torch.tensor(1.0)])
    assert torch.allclose(
        marginal.pdf_cdf_inv(marginal.cdf(x, theta), theta, True),
        torch.tensor([-0.9189385332, -1.4189385332, -2.9189385332]),
    )
