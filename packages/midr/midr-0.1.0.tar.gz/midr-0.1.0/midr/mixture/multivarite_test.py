# SPDX-FileCopyrightText: 2025 Laurent Modolo <laurent@modolo.fr>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import torch
from .multivariate import Multivariate
from ..copula import ArchMixtureCopula
from ..marginal import GaussianMarginal
import time


torch.set_default_dtype(torch.float64)
torch.set_printoptions(precision=10)
torch.set_printoptions(sci_mode=False)

def test_multivariate_cdf():
    multivariate = Multivariate(dim=2, copula=ArchMixtureCopula(dim=2), marginals=[GaussianMarginal()] * 2, family="archmixture_gaussian")
    x = torch.tensor([
        [0.0, 0.0],
        [1.0, 1.0],
        [2.0, 2.0],
    ])
    theta = torch.tensor([1.0, 2.0, 2.0, 3.0, 1/3, 1/3, 1/3, 18.0, 38.0, 10.0])
    assert torch.allclose(multivariate.cdf(x, theta, False), torch.tensor([0.2492089876, 0.3690274508, 0.4999458844]))
    assert torch.allclose(multivariate.cdf(x, theta, True), torch.tensor([-1.3894634270, -0.9968842452, -0.6932554177]))

def test_multivariate_pdf():
    multivariate = Multivariate(dim=2, copula=ArchMixtureCopula(dim=2), marginals=[GaussianMarginal()] * 2, family="archmixture_gaussian")
    x = torch.tensor([
        [0.0, 0.0],
        [1.0, 1.0],
        [2.0, 2.0],
    ])
    theta = torch.tensor([1.0, 2.0, 2.0, 3.0, 1/3, 1/3, 1/3, 18.0, 38.0, 10.0])
    assert torch.allclose(multivariate.pdf(x, theta, False), torch.tensor([0.0576983677, 0.0096672323, 0.0013669471]))
    assert torch.allclose(multivariate.pdf(x, theta, True), torch.tensor([-2.8525263958, -4.6390132238, -6.5951753953]))

def test_split_parameters():
    multivariate = Multivariate(dim=2, copula=ArchMixtureCopula(dim=2), marginals=[GaussianMarginal()] * 2, family="archmixture_gaussian")
    theta = torch.tensor([0.0, 1.0, 0.0, 1.0, 1/3, 1/3, 1/3, 18.0, 38.0, 10.0])
    expected = [torch.tensor([0., 1.]), torch.tensor([0., 1.]), torch.tensor([1/3, 1/3, 1/3, 18., 38., 10.])]
    parameters = multivariate.split_parameters(theta)
    assert torch.equal(
        parameters["marginals"][0],
        expected[0]
    )
    assert torch.equal(
        parameters["marginals"][1],
        expected[1]
    )
    if isinstance(parameters["copula"], torch.Tensor):
        assert torch.equal(
            parameters["copula"],
            expected[2]
        )

def test_fit():
    multivariate = Multivariate(dim=2, copula=ArchMixtureCopula(dim=2), marginals=[GaussianMarginal()] * 2, family="archmixture_gaussian")
    correlation = 0.7
    mean = torch.tensor([1.0, 2.0])
    covariance_matrix = torch.tensor([[1.0, correlation],
                                      [correlation, 1.0]])
    x = torch.distributions.MultivariateNormal(mean, covariance_matrix).sample((1000,))
    start_time = time.time()
    theta = torch.tensor([1.0, 1.0, 2.0, 1.0, 1/3, 1/3, 1/3, 10.0, 18.0, 5.0])
    theta = multivariate.fit(x, theta)
    print(theta)
    end_time = time.time()
    print(f"Execution time: {end_time - start_time} seconds")
    expected = [
        torch.tensor([1.0, 0.4]),
        torch.tensor([2.0, 0.4]),
        [
            torch.tensor([0.3, 0.3, 0.3]),
            torch.tensor([10.0, 18.0, 5.0]),
        ]
    ]
    theta = multivariate.split_parameters(theta)
    assert torch.allclose(theta["marginals"][0][0], expected[0][0], rtol=0.1, atol=0.1)
    assert torch.allclose(theta["marginals"][1][0], expected[1][0], rtol=0.1, atol=0.1)
    if isinstance(theta["copula"], torch.Tensor):
        assert torch.allclose(theta["copula"][0][0:3], expected[2][0], rtol=0.1, atol=0.1)
        assert torch.allclose(theta["copula"][0][3:], expected[2][1], rtol=1.0, atol=1.0)
