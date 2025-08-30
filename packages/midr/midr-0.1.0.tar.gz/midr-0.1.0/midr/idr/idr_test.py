import torch

from ..auxilary import confusion_matrix, r_indep_mixture
from ..copula import ArchMixtureCopula
from .idr import compute_idr

torch.set_default_dtype(torch.float64)
torch.set_printoptions(precision=10)
torch.set_printoptions(sci_mode=False)


def test_idr_pseudo_data():
    n = 1000
    id, data = r_indep_mixture(
        size=n,
        dim=3,
        ratio=0.4,
        indep_sigma=[1.0, 1.0, 1.0],
        dep_mu=[0.0, 0.0, 0.0],
        dep_sigma=[1.0, 1.0, 1.0],
        copula=ArchMixtureCopula,
        theta=torch.tensor([1 / 3, 1 / 3, 1 / 3, 18.0, 38.0, 10.0]),
    )
    idr, fdr = compute_idr(
        data=data,
        ecdf_method="adjustedDistributionalTransform",
        copula="gaussian",
        pseudo_data=True,
        gpu=False,
    )
    y_true = id.type(torch.int64)
    y_pred = (fdr <= 0.05).type(torch.int64)
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
        cm, torch.tensor([[0.4, 0.0], [0.4, 0.15]]), atol=0.1, rtol=0.1
    )


def test_idr_data():
    n = 1000
    id, data = r_indep_mixture(
        size=n,
        dim=3,
        ratio=0.4,
        indep_sigma=[1.0, 1.0, 1.0],
        dep_mu=[0.0, 0.0, 0.0],
        dep_sigma=[1.0, 1.0, 1.0],
        copula=ArchMixtureCopula,
        theta=torch.tensor([1 / 3, 1 / 3, 1 / 3, 18.0, 38.0, 10.0]),
    )
    idr, fdr = compute_idr(
        data=data,
        ecdf_method="adjustedDistributionalTransform",
        copula="empiricalBeta",
        pseudo_data=False,
        gpu=False,
    )
    y_true = id.type(torch.int64)
    y_pred = (fdr <= 0.05).type(torch.int64)
    print(f"y_true: {y_true}")
    print(f"y_pred: {y_pred}")
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
        cm, torch.tensor([[0.0, 0.4], [0.0, 0.6]]), atol=0.1, rtol=0.1
    )
