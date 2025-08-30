# SPDX-FileCopyrightText: 2025 Laurent Modolo <laurent@modolo.fr>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Utility functions for the IDR package.

This module provides various helper functions for:
- Computing partial derivatives for tensor operations
- Statistical summaries of tensors
- File I/O operations (CSV handling)
- List manipulation utilities
- Gaussian mixture data generation

Functions:
    partial_derivative: Compute the partial derivative of a function with respect to a tensor input.
    summary: Print a statistical summary of a tensor.
    csv_to_tensor_direct: Load CSV data directly into a PyTorch tensor.
    flatten_generator: Flatten a nested list of lists into a generator.
    flatten_list: Flatten a nested list of lists into a single list.
    r_gaussian_mixture: Generate a mixture of dependent and independent Gaussian distributions.
    confusion_matrix: Compute a confusion matrix using PyTorch operations.
"""

from typing import List

import numpy as np
import torch

from ..copula import Copula
from ..marginal import FixedGaussianMarginal, GaussianMarginal
from .transform import tensor2list


def check_gpu(gpu: bool = True) -> torch.device:
    """
    Check if CUDA is available and if the GPU is enabled.
    """
    device = torch.device("cpu")
    if gpu:
        if torch.mps.is_available():
            device = torch.device("mps")
        if torch.cuda.is_available():
            if not torch.cuda.is_initialized():
                torch.cuda.init()
            device = torch.device("cuda")
    return device


def partial_derivative(fn, u: torch.Tensor):
    """
    Calculate the partial derivative of a function with respect to a tensor input.

    This function is used to compute the density function of an n-dimensional CDF for a copula.
    It computes the partial derivative of the provided function `fn` with respect to the input tensor `u`.

    Parameters:
        fn (callable): Function to differentiate. Should take a tensor and return a tensor.
        u (torch.Tensor): Input tensor to compute the derivative with respect to.

    Returns:
        torch.Tensor: The partial derivative of fn with respect to u.
    """
    ul = tensor2list(u)
    for i in range(len(ul)):
        ul[i].requires_grad_(True)

    def fnl(ul: List[torch.Tensor]):
        return fn(torch.stack(ul, dim=1))

    res = fnl(ul)
    for i in range(len(ul)):
        res = torch.autograd.grad(
            res,
            ul[i],
            grad_outputs=torch.ones_like(ul[i]),
            create_graph=True,
            retain_graph=True,
        )[0]
    print(res)
    return res


def summary(tensor):
    """
    Generate and print a statistical summary of a PyTorch tensor.

    Parameters:
        tensor (torch.Tensor): Input tensor to summarize.

    Prints:
        - Count (number of elements)
        - Mean
        - Standard deviation
        - Minimum value
        - 25th percentile
        - 50th percentile (median)
        - 75th percentile
        - Maximum value

    Raises:
        TypeError: If input is not a PyTorch tensor
    """
    if not isinstance(tensor, torch.Tensor):
        raise TypeError("Input must be a PyTorch tensor")

    tensor_np = tensor.detach().numpy()

    summary_dict = {
        "count": tensor.numel(),
        "mean": torch.mean(tensor).item(),
        "std": torch.std(tensor).item(),
        "min": torch.min(tensor).item(),
        "25%": np.percentile(tensor_np, 25),
        "50% (median)": np.percentile(tensor_np, 50),
        "75%": np.percentile(tensor_np, 75),
        "max": torch.max(tensor).item(),
    }

    for key, value in summary_dict.items():
        print(f"{key}: {value}", end=", ")
    print("")


def flatten_generator(nested_list):
    """
    Flatten a nested list of lists into a single generator.

    Parameters:
        nested_list (list): A nested list of lists.

    Yields:
        item: Elements from the nested list.
    """
    for item in nested_list:
        if isinstance(item, list):
            yield from flatten_generator(item)
        else:
            yield item


def flatten_list(nested_list):
    """
    Flatten a nested list of lists into a single list.

    Parameters:
        nested_list (list): A nested list of lists.

    Returns:
        flat_list (list): A flattened list containing all elements from the nested list.
    """
    return [item for item in flatten_generator(nested_list)]


def r_gaussian_mixture(
    size=1000,
    ratio=0.5,
    indep_sigma=[1.0, 1.0],
    correlation=0.6,
    dep_mu=[1.0, 1.0],
    dep_sigma=[1.0, 1.0],
) -> List[torch.Tensor]:
    """
    Generate a mixture of dependent and independent Gaussian distributions.

    Parameters:
        size (int): Total number of samples to generate. Default is 1000.
        ratio (float): Ratio of dependent samples to total samples. Default is 0.5.
        indep_sigma (List[float]): Standard deviations for independent samples. Default is [1.0, 1.0].
        correlation (float): Correlation coefficient for dependent samples. Default is 0.6.
        dep_mu (List[float]): Mean values for dependent distribution. Default is [1.0, 1.0].
        dep_sigma (List[float]): Standard deviations for dependent samples. Default is [1.0, 1.0].

    Returns:
        List[torch.Tensor]: A list containing:
            - indices: Binary tensor indicating dependent (0) or independent (1) samples
            - samples: 2D tensor containing the generated samples
    """
    n_dep = int(torch.round(torch.tensor([size * ratio])).item())
    n_indep = size - n_dep
    mean = torch.tensor(dep_mu)
    covariance_matrix = torch.tensor(
        [[dep_sigma[0], correlation], [correlation, dep_sigma[1]]]
    )
    x = torch.distributions.MultivariateNormal(mean, covariance_matrix).sample((n_dep,))
    mean = torch.tensor([0.0, 0.0])
    covariance_matrix = torch.tensor([[indep_sigma[0], 0], [0, indep_sigma[1]]])
    indices = torch.cat([torch.ones(n_indep), torch.zeros(n_dep)])
    return [
        indices,
        torch.cat(
            [
                x,
                torch.distributions.MultivariateNormal(mean, covariance_matrix).sample(
                    (n_indep,)
                ),
            ],
            dim=0,
        ),
    ]


def r_indep_mixture(
    size=1000,
    dim=2,
    ratio=0.5,
    indep_sigma=[1.0, 1.0],
    dep_mu=[1.0, 1.0],
    dep_sigma=[1.0, 1.0],
    theta: torch.Tensor = None,
    copula: Copula = None,
) -> List[torch.Tensor]:
    """
        Generate a mixture of independent and Copula distributions with gaussian marginals.
    ) -> List[torch.Tensor]:
    """
    indep_unif = torch.rand(int(torch.round(torch.tensor(size * ratio)).item()), dim)
    copula = copula(dim)
    dep_unif = copula.random(
        int(torch.round(torch.tensor(size * (1.0 - ratio))).item()), theta
    )
    indep_data = []
    dep_data = []
    for i in range(dim):
        indep_data += [
            FixedGaussianMarginal().cdf_inv(
                indep_unif[:, i], theta=torch.tensor([indep_sigma[i]])
            )
        ]
        dep_data += [
            GaussianMarginal().cdf_inv(
                dep_unif[:, i], theta=torch.tensor([dep_mu[i], dep_sigma[i]])
            )
        ]
    indep_data = torch.stack(indep_data, dim=1)
    dep_data = torch.stack(dep_data, dim=1)
    mixed = torch.cat([indep_data, dep_data], dim=0)
    perm = torch.randperm(mixed.size(0))
    return [perm >= int(torch.round(torch.tensor(size * ratio)).item()), mixed[perm]]


def confusion_matrix(y_true, y_pred):
    """
    Compute confusion matrix using PyTorch operations.

    Args:
        y_true (torch.Tensor): Ground truth binary labels (0 or 1)
        y_pred (torch.Tensor): Predicted binary labels (0 or 1)

    Returns:
        torch.Tensor: 2x2 confusion matrix as a torch.Tensor
            [[tn, fp],
             [fn, tp]]
    """
    # Make sure inputs are binary
    assert torch.all((y_true == 0) | (y_true == 1)), "y_true must be binary (0 or 1)"
    assert torch.all((y_pred == 0) | (y_pred == 1)), "y_pred must be binary (0 or 1)"

    # Calculate matrix elements
    tp = torch.sum((y_true == 1) & (y_pred == 1)).item()
    tn = torch.sum((y_true == 0) & (y_pred == 0)).item()
    fp = torch.sum((y_true == 0) & (y_pred == 1)).item()
    fn = torch.sum((y_true == 1) & (y_pred == 0)).item()

    # Create and return the confusion matrix
    cm = torch.tensor([[tn, fp], [fn, tp]])
    return cm


def zeros_proportion(data: torch.Tensor) -> float:
    """
    Calculate the proportion of zeros in a tensor.

    Args:
        data (torch.Tensor): Input tensor.

    Returns:
        float: Proportion of zeros in the tensor.
    """
    return torch.sum(data == 0).item() / data.numel()


def multiple_of_3_filter(x: torch.Tensor) -> torch.Tensor:
    """
    Check if the dimention of a tensor is a multiple of 3.

    Args:
        x (torch.Tensor): Input tensor.

    Returns:
        torch.Tensor: a tensor of size (size - 1) if the dim was a multiple of 3, otherwise a tensor of size (size).
    """
    if torch.numel(x) % 3 == 0:
        return x[:-1]
    else:
        return x
