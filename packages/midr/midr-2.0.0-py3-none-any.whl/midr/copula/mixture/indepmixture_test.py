# SPDX-FileCopyrightText: 2025 Laurent Modolo <laurent@modolo.fr>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import torch

from ...auxilary import ecdf, r_indep_mixture
from ..archimedean import ClaytonCopula, FrankCopula, GumbelCopula
from ..independence import IndependenceCopula
from . import archmixture, indepmixture

torch.set_default_dtype(torch.float64)
torch.set_printoptions(precision=10)
torch.set_printoptions(sci_mode=False)


def test_indepmixture_copula_cdf():
    """
    Test the CDF computation of the IndepMixtureCopula.

    This test checks that the CDF returns the expected values for given inputs.
    """
    theta = torch.tensor([1 / 4, 1 / 4, 1 / 4, 1 / 4, 18.0, 38.0, 10.0])
    u = torch.tensor([[0.1, 0.2], [0.3, 0.4], [0.4, 0.5]])
    copula = indepmixture.IndepMixtureCopula(2)
    cdf = copula.cdf(u, theta)
    expected = torch.tensor([0.0796999, 0.2542612, 0.3492095])
    assert all(torch.isclose(cdf, expected))


def test_indepmixture_copula_pdf():
    """
    Test the PDF computation of the IndepMixtureCopula.

    This test checks that the PDF returns the expected values for given inputs.
    """
    theta = torch.tensor([1 / 4, 1 / 4, 1 / 4, 1 / 4, 18.0, 38.0, 10.0])
    u = torch.tensor([[0.1, 0.2], [0.3, 0.4], [0.4, 0.5]], requires_grad=True)
    copula = indepmixture.IndepMixtureCopula(2)
    pdf = copula.pdf(u, theta)
    expected = torch.tensor([0.6842025, 0.9191566, 1.0083567])
    assert all(torch.isclose(pdf, expected))


def test_indepmixture_copula_likelihood():
    """
    Test the log-likelihood computation of the IndepMixtureCopula.

    This test checks that the log-likelihood matches the expected value for given inputs.
    """
    u = torch.tensor([[0.1, 0.2], [0.3, 0.4], [0.4, 0.5]], requires_grad=True)
    theta = torch.tensor([1 / 4, 1 / 4, 1 / 4, 1 / 4, 18.0, 38.0, 10.0])
    copula = indepmixture.IndepMixtureCopula(2)
    likelihood = copula.likelihood(u, theta, True)
    expected = torch.tensor(-0.4554783)
    assert torch.isclose(likelihood, expected)


def test_indepmixture_copula_fit():
    """
    Test parameter fitting for the IndepMixtureCopula.

    This test checks that the copula fitting procedure recovers the expected parameter values
    for simulated data and for various dimensions.
    """
    torch.manual_seed(123)

    copula = indepmixture.IndepMixtureCopula(2)
    expected = torch.tensor([1 / 2, 1 / 6, 1 / 6, 1 / 6, 12.0, 28.0, 15.0])
    u = copula.random(10000, expected)
    theta = torch.tensor([1 / 4, 1 / 4, 1 / 4, 1 / 4, 5.0, 18.0, 8.0])
    theta = copula.fit(u, theta)
    weight, theta = theta[:4], theta[4:]
    assert all(torch.isclose(weight, expected[:4], rtol=0.1, atol=0.1))
    assert all(torch.isclose(theta, expected[4:], rtol=0.5, atol=0.5))

    copula = indepmixture.IndepMixtureCopula(
        4,
        copulas=[
            IndependenceCopula(4),
            ClaytonCopula(4),
            FrankCopula(4),
            GumbelCopula(4),
        ],
    )
    expected = torch.tensor([0.4, 0.1, 0.3, 0.2, 15.0, 22.0, 17.0])
    u = copula.random(10000, expected)
    theta = torch.tensor([1 / 4, 1 / 4, 1 / 4, 1 / 4, 5.0, 18.0, 8.0])
    theta = copula.fit(u, theta)
    weight, theta = theta[:4], theta[4:]
    assert all(torch.isclose(weight, expected[:4], rtol=0.1, atol=0.1))
    assert all(torch.isclose(theta, expected[4:], rtol=0.5, atol=0.5))

    copula = indepmixture.IndepMixtureCopula(2)
    _, x = r_indep_mixture(
        size=10000,
        dim=2,
        ratio=0.4,
        indep_sigma=[1.0, 1.0],
        dep_mu=[0.0, 0.0],
        dep_sigma=[1.0, 1.0],
        copula=archmixture.ArchMixtureCopula,
        theta=torch.tensor([1 / 3, 1 / 3, 1 / 3, 18.0, 38.0, 10.0]),
    )
    u = ecdf(x)
    theta = torch.tensor([1 / 4, 1 / 4, 1 / 4, 1 / 4, 5.0, 18.0, 8.0])
    theta = copula.fit(u, theta)
    weight, theta = theta[:4], theta[4:]
    expected = torch.tensor(
        [
            0.4057224612,
            0.1943315215,
            0.1891143386,
            0.2108316786,
            15.2614765749,
            37.4069389334,
            10.5697626904,
        ]
    )
    assert all(torch.isclose(weight, expected[:4], rtol=0.1, atol=0.1))
    assert all(torch.isclose(theta, expected[4:], rtol=0.5, atol=0.5))

    copula = indepmixture.IndepMixtureCopula(3)
    _, x = r_indep_mixture(
        size=10000,
        dim=3,
        ratio=0.4,
        indep_sigma=[1.0, 1.0, 1.0],
        dep_mu=[0.0, 0.0, 0.0],
        dep_sigma=[1.0, 1.0, 1.0],
        copula=archmixture.ArchMixtureCopula,
        theta=torch.tensor([1 / 3, 1 / 3, 1 / 3, 18.0, 38.0, 10.0]),
    )
    u = ecdf(x)
    theta = torch.tensor([1 / 4, 1 / 4, 1 / 4, 1 / 4, 5.0, 18.0, 8.0])
    theta = copula.fit(u, theta)
    weight, theta = theta[:4], theta[4:]
    expected = torch.tensor(
        [
            0.3061366366,
            0.0994261872,
            0.5221438645,
            0.0722933117,
            16.7054244887,
            30.0440937751,
            28.2852956145,
        ]
    )
    assert all(torch.isclose(weight, expected[:4], rtol=0.1, atol=0.1))
    assert all(torch.isclose(theta, expected[4:], rtol=0.5, atol=0.5))


def test_indepmixture_copula_idr():
    """
    Test the Intrinsic Dependency Ratio (IDR) computation of the IndepMixtureCopula.

    This test checks that the IDR values are as expected for given inputs and dimensions.
    """
    torch.manual_seed(123)
    copula = indepmixture.IndepMixtureCopula(2)
    u = torch.tensor([[0.1, 0.2], [0.3, 0.4], [0.4, 0.5]], requires_grad=True)
    idr = copula.idr(u)
    assert torch.isclose(
        idr,
        torch.tensor([0.0000000028, 0.0000000030, 0.0000000030]),
        rtol=0.1,
        atol=0.1,
    ).all()
    copula = indepmixture.IndepMixtureCopula(4)
    u = torch.tensor(
        [[0.1, 0.2, 0.1, 0.2], [0.3, 0.4, 0.3, 0.4], [0.4, 0.5, 0.5, 0.5]],
        requires_grad=True,
    )
    idr = copula.idr(u)
    assert torch.isclose(
        idr,
        torch.tensor([0.0226935658, 0.0326413069, 0.0333306689]),
        rtol=0.1,
        atol=0.1,
    ).all()
