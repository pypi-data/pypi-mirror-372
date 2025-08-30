# SPDX-FileCopyrightText: 2025 Laurent Modolo <laurent@modolo.fr>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import torch

from ..auxilary import (
    confusion_matrix,
    ecdf,
    fdr,
    r_gaussian_mixture,
    r_indep_mixture,
    summary,
)
from ..copula import (
    ArchMixtureCopula,
    ClaytonCopula,
    EmpiricalBetaCopula,
    FrankCopula,
    GaussianCopula,
    GumbelCopula,
)
from .indep_mixture import IndepMixture

torch.set_default_dtype(torch.float64)
torch.set_printoptions(precision=10)
torch.set_printoptions(sci_mode=False)


def test_split_parameters():
    mixture = IndepMixture(
        dim=2,
        copula=[ClaytonCopula(dim=2), FrankCopula(dim=2), GumbelCopula(dim=2)],
        family="indep_archmixture",
    )
    theta = torch.tensor([0.5, 1 / 3, 1 / 3, 1 / 3, 0.0, 0.0, 18.0, 38.0, 10.0])
    expected = [
        torch.tensor([0.5, 1 / 3, 1 / 3, 1 / 3]),
        torch.tensor([0.0, 0.0]),
        torch.tensor([18.0, 38.0, 10.0]),
    ]
    parameters = mixture.split_parameters(theta)
    assert torch.equal(parameters["weight"], expected[0])
    assert torch.equal(parameters["dep_mu"], expected[1])
    assert torch.equal(parameters["copula"], expected[2])


def test_mixture_pdf():
    mixture = IndepMixture(
        dim=2,
        copula=[ClaytonCopula(dim=2), FrankCopula(dim=2), GumbelCopula(dim=2)],
        family="indep_archmixture",
    )
    dep_w = 0.5 * (1 / 3)
    theta = torch.tensor([0.5, dep_w, dep_w, dep_w, 0.0, 0.0, 18.0, 38.0, 10.0])
    u = torch.tensor([[0.1, 0.2], [0.3, 0.4], [0.4, 0.5]], requires_grad=True)
    assert torch.allclose(
        mixture.pdf(u, theta, False),
        torch.tensor([0.0383092939, 0.1209754390, 0.1685101214]),
    )
    assert torch.allclose(
        mixture.pdf(u, theta, True),
        torch.tensor([-3.2620627509, -2.1121677372, -1.7807594634]),
    )


def test_mixture_idr():
    mixture = IndepMixture(
        dim=2,
        copula=[ClaytonCopula(dim=2), FrankCopula(dim=2), GumbelCopula(dim=2)],
        family="indep_archmixture",
    )
    dep_w = 0.5 * (1 / 3)
    theta = torch.tensor([0.5, dep_w, dep_w, dep_w, 0.0, 0.0, 18.0, 38.0, 10.0])
    u = torch.tensor([[0.1, 0.2], [0.3, 0.4], [0.4, 0.5]], requires_grad=True)
    assert torch.allclose(
        mixture.idr(u, theta), torch.tensor([0.6283539349, 0.5538283789, 0.4576605726])
    )


def test_fit_gausian_2d():
    n = 1000
    id, x = r_gaussian_mixture(size=n, ratio=0.43, correlation=0.8, dep_mu=[2.0, 2.0])
    mixture = IndepMixture(
        dim=2, copula=[GaussianCopula(dim=2)], family="indep_gaussian"
    )
    dep_w = 0.5
    theta = torch.tensor([0.5, dep_w, 1.0, 1.0, 1.0, 0.1, 0.1, 1.0])
    theta = mixture.fit(u=ecdf(x), theta=theta)
    idr = mixture.idr(ecdf(x), theta)
    print(summary(idr))

    y_true = id.type(torch.int64)
    y_pred = (fdr(idr) <= 0.05).type(torch.int64)
    cm = confusion_matrix(y_true, y_pred) / n
    print("Confusion Matrix (PyTorch) FDR:")
    print("[[tn, fp], [fn, tp]]")
    print(cm)

    y_pred = (idr < 0.5).type(torch.int64)
    cm = confusion_matrix(y_true, y_pred) / n
    print("Confusion Matrix (PyTorch):")
    print("[[tn, fp], [fn, tp]]")
    print(cm)
    assert torch.allclose(
        cm, torch.tensor([[0.42, 0.0], [0.30, 0.20]]), atol=0.1, rtol=0.1
    )


def test_fit_archmixture_2d():
    n = 1000
    id, x = r_gaussian_mixture(size=n, ratio=0.43, correlation=0.8, dep_mu=[2.0, 2.0])
    mixture = IndepMixture(
        dim=2,
        copula=[ClaytonCopula(dim=2), FrankCopula(dim=2), GumbelCopula(dim=2)],
        family="indep_archmixture",
    )
    dep_w = 0.5 * (1 / 3)
    theta = torch.tensor([0.5, dep_w, dep_w, dep_w, 1.0, 1.0, 15.0, 28.0, 10.0])
    theta = mixture.fit(u=ecdf(x), theta=theta)
    idr = mixture.idr(ecdf(x), theta)
    print(summary(idr))

    y_true = id.type(torch.int64)
    y_pred = (fdr(idr) <= 0.05).type(torch.int64)
    cm = confusion_matrix(y_true, y_pred) / n
    print("Confusion Matrix (PyTorch) FDR:")
    print("[[tn, fp], [fn, tp]]")
    print(cm)

    y_pred = (idr < 0.5).type(torch.int64)
    cm = confusion_matrix(y_true, y_pred) / n
    print("Confusion Matrix (PyTorch):")
    print("[[tn, fp], [fn, tp]]")
    print(cm)
    assert torch.allclose(
        cm, torch.tensor([[0.3, 0.15], [0.2, 0.4]]), atol=0.1, rtol=0.1
    )


def test_fit_archmixture_3d():
    n = 1000
    id, x = r_indep_mixture(
        size=n,
        dim=3,
        ratio=0.4,
        indep_sigma=[1.0, 1.0, 1.0],
        dep_mu=[0.0, 0.0, 0.0],
        dep_sigma=[1.0, 1.0, 1.0],
        copula=ArchMixtureCopula,
        theta=torch.tensor([1 / 3, 1 / 3, 1 / 3, 18.0, 38.0, 10.0]),
    )
    mixture = IndepMixture(
        dim=3,
        copula=[ClaytonCopula(dim=2), FrankCopula(dim=2), GumbelCopula(dim=2)],
        family="indep_archmixture",
    )
    dep_w = 0.5 * (1 / 3)
    theta = torch.tensor([0.5, dep_w, dep_w, dep_w, 1.0, 1.0, 1.0, 15.0, 28.0, 10.0])
    theta = mixture.fit(u=ecdf(x), theta=theta)
    print(theta)
    idr = mixture.idr(ecdf(x), theta)
    print(summary(idr))

    y_true = id.type(torch.int64)
    y_pred = (fdr(idr) <= 0.05).type(torch.int64)
    cm = confusion_matrix(y_true, y_pred) / n
    print("Confusion Matrix (PyTorch) FDR:")
    print("[[tn, fp], [fn, tp]]")
    print(cm)

    y_pred = (idr < 0.5).type(torch.int64)
    cm = confusion_matrix(y_true, y_pred) / n
    print("Confusion Matrix (PyTorch):")
    print("[[tn, fp], [fn, tp]]")
    print(cm)
    assert torch.allclose(
        cm, torch.tensor([[0.4, 0.1], [0.1, 0.5]]), atol=0.1, rtol=0.1
    )


def test_fit_beta_2d():
    n = 1000
    id, x = r_gaussian_mixture(size=n, ratio=0.43, correlation=0.8, dep_mu=[2.0, 2.0])
    mixture = IndepMixture(
        dim=2,
        copula=[
            EmpiricalBetaCopula(
                dim=2,
                rank=x.argsort(dim=0, stable=True).argsort(dim=0, stable=True) + 1,
            )
        ],
        family="indep_beta",
    )
    theta = mixture.init_theta()
    theta = mixture.fit(u=ecdf(x), theta=theta)
    idr = mixture.idr(ecdf(x), theta)

    y_true = id.type(torch.int64)
    y_pred = (fdr(idr) <= 0.05).type(torch.int64)
    cm = confusion_matrix(y_true, y_pred) / n
    print("Confusion Matrix (PyTorch) FDR:")
    print("[[tn, fp], [fn, tp]]")
    print(cm)

    y_pred = (idr < 0.5).type(torch.int64)
    cm = confusion_matrix(y_true, y_pred) / n
    print("Confusion Matrix (PyTorch):")
    print("[[tn, fp], [fn, tp]]")
    print(cm)
    assert torch.allclose(
        cm, torch.tensor([[0.3, 0.1], [0.15, 0.40]]), atol=0.1, rtol=0.1
    )


def test_fit_beta_3d():
    print(torch.get_rng_state())
    # torch.set_rng_state(state)
    n = 1001
    id, x = r_indep_mixture(
        size=n,
        dim=3,
        ratio=0.4,
        indep_sigma=[1.0, 1.0, 1.0],
        dep_mu=[0.0, 0.0, 0.0],
        dep_sigma=[1.0, 1.0, 1.0],
        copula=ArchMixtureCopula,
        theta=torch.tensor([1 / 3, 1 / 3, 1 / 3, 18.0, 38.0, 10.0]),
    )
    mixture = IndepMixture(
        dim=3,
        copula=[
            EmpiricalBetaCopula(
                dim=3,
                rank=x.argsort(dim=0, stable=True).argsort(dim=0, stable=True) + 1,
            )
        ],
        family="indep_beta",
    )
    theta = mixture.init_theta()
    theta = mixture.fit(u=ecdf(x), theta=theta)
    print(theta)
    idr = mixture.idr(ecdf(x), theta)

    y_true = id.type(torch.int64)
    y_pred = (fdr(idr) <= 0.05).type(torch.int64)
    cm = confusion_matrix(y_true, y_pred) / n
    print("Confusion Matrix (PyTorch) FDR:")
    print("[[tn, fp], [fn, tp]]")
    print(cm)

    y_pred = (idr < 0.5).type(torch.int64)
    cm = confusion_matrix(y_true, y_pred) / n
    print("Confusion Matrix (PyTorch):")
    print("[[tn, fp], [fn, tp]]")
    print(cm)
    assert torch.allclose(
        cm, torch.tensor([[0.4, 0.1], [0.1, 0.5]]), atol=0.1, rtol=0.1
    )


# def test_fit_beta_4d():
#     print(torch.get_rng_state())
#     # torch.set_rng_state(state)
#     n = 1001
#     id, x = r_indep_mixture(
#         size=n,
#         dim=4,
#         ratio=0.4,
#         indep_sigma=[1.0, 1.0, 1.0, 1.0],
#         dep_mu=[0.0, 0.0, 0.0, 0.0],
#         dep_sigma=[1.0, 1.0, 1.0, 1.0],
#         copula=ArchMixtureCopula,
#         theta=torch.tensor([1 / 3, 1 / 3, 1 / 3, 18.0, 38.0, 10.0]),
#     )
#     mixture = IndepMixture(
#         dim=4,
#         copula=[
#             EmpiricalBetaCopula(
#                 dim=4,
#                 rank=x.argsort(dim=0, stable=True).argsort(dim=0, stable=True) + 1,
#             )
#         ],
#         family="indep_beta",
#     )
#     theta = mixture.init_theta()
#     theta = mixture.fit(u=ecdf(x), theta=theta)
#     print(theta)
#     idr = mixture.idr(ecdf(x), theta)

#     y_true = id.type(torch.int64)
#     y_pred = (fdr(idr) <= 0.05).type(torch.int64)
#     cm = confusion_matrix(y_true, y_pred) / n
#     print("Confusion Matrix (PyTorch) FDR:")
#     print("[[tn, fp], [fn, tp]]")
#     print(cm)

#     y_pred = (idr < 0.5).type(torch.int64)
#     cm = confusion_matrix(y_true, y_pred) / n
#     print("Confusion Matrix (PyTorch):")
#     print("[[tn, fp], [fn, tp]]")
#     print(cm)
#     assert torch.allclose(
#         cm, torch.tensor([[0.4, 0.1], [0.1, 0.5]]), atol=0.1, rtol=0.1
#     )


# def test_fit_beta_5d():
#     n = 1000
#     id, x = r_indep_mixture(
#         size=n,
#         dim=5,
#         ratio=0.4,
#         indep_sigma=[1.0, 1.0, 1.0, 1.0, 1.0],
#         dep_mu=[0.0, 0.0, 0.0, 0.0, 0.0],
#         dep_sigma=[1.0, 1.0, 1.0, 1.0, 1.0],
#         copula=ArchMixtureCopula,
#         theta=torch.tensor([1 / 3, 1 / 3, 1 / 3, 18.0, 38.0, 10.0]),
#     )
#     mixture = IndepMixture(
#         dim=5,
#         copula=[
#             EmpiricalBetaCopula(
#                 dim=5,
#                 rank=x.argsort(dim=0, stable=True).argsort(dim=0, stable=True) + 1,
#             )
#         ],
#         family="indep_beta",
#     )
#     theta = mixture.init_theta()
#     theta = mixture.fit(u=ecdf(x), theta=theta)
#     idr = mixture.idr(ecdf(x), theta)

#     y_true = id.type(torch.int64)
#     y_pred = (fdr(idr) <= 0.05).type(torch.int64)
#     cm = confusion_matrix(y_true, y_pred) / n
#     print("Confusion Matrix (PyTorch) FDR:")
#     print("[[tn, fp], [fn, tp]]")
#     print(cm)

#     y_pred = (idr < 0.5).type(torch.int64)
#     cm = confusion_matrix(y_true, y_pred) / n
#     print("Confusion Matrix (PyTorch):")
#     print("[[tn, fp], [fn, tp]]")
#     print(cm)
#     assert torch.allclose(
#         cm, torch.tensor([[0.4, 0.1], [0.1, 0.5]]), atol=0.1, rtol=0.1
#     )


# def test_fit_beta_6d():
#     n = 1001
#     id, x = r_indep_mixture(
#         size=n,
#         dim=6,
#         ratio=0.4,
#         indep_sigma=[1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
#         dep_mu=[0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
#         dep_sigma=[1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
#         copula=ArchMixtureCopula,
#         theta=torch.tensor([1 / 3, 1 / 3, 1 / 3, 18.0, 38.0, 10.0]),
#     )
#     mixture = IndepMixture(
#         dim=6,
#         copula=[
#             EmpiricalBetaCopula(
#                 dim=6,
#                 rank=x.argsort(dim=0, stable=True).argsort(dim=0, stable=True) + 1,
#             )
#         ],
#         family="indep_beta",
#     )
#     theta = mixture.init_theta()
#     theta = mixture.fit(u=ecdf(x), theta=theta)
#     idr = mixture.idr(ecdf(x), theta)

#     y_true = id.type(torch.int64)
#     y_pred = (fdr(idr) <= 0.05).type(torch.int64)
#     cm = confusion_matrix(y_true, y_pred) / n
#     print("Confusion Matrix (PyTorch) FDR:")
#     print("[[tn, fp], [fn, tp]]")
#     print(cm)

#     y_pred = (idr < 0.5).type(torch.int64)
#     cm = confusion_matrix(y_true, y_pred) / n
#     print("Confusion Matrix (PyTorch):")
#     print("[[tn, fp], [fn, tp]]")
#     print(cm)
#     assert torch.allclose(
#         cm, torch.tensor([[0.4, 0.1], [0.1, 0.5]]), atol=0.1, rtol=0.1
#     )


# def test_fit_beta_7d():
#     n = 1000
#     id, x = r_indep_mixture(
#         size=n,
#         dim=7,
#         ratio=0.4,
#         indep_sigma=[1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
#         dep_mu=[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
#         dep_sigma=[1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
#         copula=ArchMixtureCopula,
#         theta=torch.tensor([1 / 3, 1 / 3, 1 / 3, 18.0, 38.0, 10.0]),
#     )
#     mixture = IndepMixture(
#         dim=7,
#         copula=[
#             EmpiricalBetaCopula(
#                 dim=7,
#                 rank=x.argsort(dim=0, stable=True).argsort(dim=0, stable=True) + 1,
#             )
#         ],
#         family="indep_beta",
#     )
#     theta = mixture.init_theta()
#     theta = mixture.fit(u=ecdf(x), theta=theta)
#     idr = mixture.idr(ecdf(x), theta)

#     y_true = id.type(torch.int64)
#     y_pred = (fdr(idr) <= 0.05).type(torch.int64)
#     cm = confusion_matrix(y_true, y_pred) / n
#     print("Confusion Matrix (PyTorch) FDR:")
#     print("[[tn, fp], [fn, tp]]")
#     print(cm)

#     y_pred = (idr < 0.5).type(torch.int64)
#     cm = confusion_matrix(y_true, y_pred) / n
#     print("Confusion Matrix (PyTorch):")
#     print("[[tn, fp], [fn, tp]]")
#     print(cm)
#     assert torch.allclose(
#         cm, torch.tensor([[0.4, 0.1], [0.1, 0.5]]), atol=0.1, rtol=0.1
#     )


# def test_fit_beta_8d():
#     n = 1000
#     id, x = r_indep_mixture(
#         size=n,
#         dim=8,
#         ratio=0.4,
#         indep_sigma=[1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
#         dep_mu=[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
#         dep_sigma=[1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
#         copula=ArchMixtureCopula,
#         theta=torch.tensor([1 / 3, 1 / 3, 1 / 3, 18.0, 38.0, 10.0]),
#     )
#     mixture = IndepMixture(
#         dim=8,
#         copula=[
#             EmpiricalBetaCopula(
#                 dim=8,
#                 rank=x.argsort(dim=0, stable=True).argsort(dim=0, stable=True) + 1,
#             )
#         ],
#         family="indep_beta",
#     )
#     theta = mixture.init_theta()
#     theta = mixture.fit(u=ecdf(x), theta=theta)
#     idr = mixture.idr(ecdf(x), theta)

#     y_true = id.type(torch.int64)
#     y_pred = (fdr(idr) <= 0.05).type(torch.int64)
#     cm = confusion_matrix(y_true, y_pred) / n
#     print("Confusion Matrix (PyTorch) FDR:")
#     print("[[tn, fp], [fn, tp]]")
#     print(cm)

#     y_pred = (idr < 0.5).type(torch.int64)
#     cm = confusion_matrix(y_true, y_pred) / n
#     print("Confusion Matrix (PyTorch):")
#     print("[[tn, fp], [fn, tp]]")
#     print(cm)
#     assert torch.allclose(
#         cm, torch.tensor([[0.4, 0.1], [0.1, 0.5]]), atol=0.1, rtol=0.1
#     )


# def test_fit_beta_9d():
#     n = 1001
#     id, x = r_indep_mixture(
#         size=n,
#         dim=9,
#         ratio=0.4,
#         indep_sigma=[1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
#         dep_mu=[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
#         dep_sigma=[1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
#         copula=ArchMixtureCopula,
#         theta=torch.tensor([1 / 3, 1 / 3, 1 / 3, 18.0, 38.0, 10.0]),
#     )
#     mixture = IndepMixture(
#         dim=9,
#         copula=[
#             EmpiricalBetaCopula(
#                 dim=9,
#                 rank=x.argsort(dim=0, stable=True).argsort(dim=0, stable=True) + 1,
#             )
#         ],
#         family="indep_beta",
#     )
#     theta = mixture.init_theta()
#     theta = mixture.fit(u=ecdf(x), theta=theta)
#     idr = mixture.idr(ecdf(x), theta)

#     y_true = id.type(torch.int64)
#     y_pred = (fdr(idr) <= 0.05).type(torch.int64)
#     cm = confusion_matrix(y_true, y_pred) / n
#     print("Confusion Matrix (PyTorch) FDR:")
#     print("[[tn, fp], [fn, tp]]")
#     print(cm)

#     y_pred = (idr < 0.5).type(torch.int64)
#     cm = confusion_matrix(y_true, y_pred) / n
#     print("Confusion Matrix (PyTorch):")
#     print("[[tn, fp], [fn, tp]]")
#     print(cm)
#     assert torch.allclose(
#         cm, torch.tensor([[0.4, 0.1], [0.2, 0.4]]), atol=0.1, rtol=0.1
#     )
