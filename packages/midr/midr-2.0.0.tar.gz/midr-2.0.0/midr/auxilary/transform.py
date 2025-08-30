# SPDX-FileCopyrightText: 2025 Laurent Modolo <laurent@modolo.fr>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Transformation utilities for the IDR package.

This module provides various tensor transformation functions including:
- Tensor-list conversions
- Compositional data transforms (CLR)
- Bounded value transforms
- CDF transformations and their inverses
- Parameter merging utilities

Functions:
    tensor2list: Convert a 2D tensor into a list of column tensors.
    list2tensor: Convert a list of column tensors into a 2D tensor.
    clr: Centered log-ratio transform for compositional data.
    clr_inv: Inverse centered log-ratio transform.
    clr1: Centered log-ratio transform, omitting the first component.
    clr1_inv: Inverse of clr1.
    positive_transform: Ensure all tensor values are positive using softplus.
    inverse_positive_transform: Inverse of positive_transform.
    bounded_transform: Map from ℝ to (a, b).
    bounded_transform_list: Map a list of tensors from ℝ to (a, b).
    inverse_bounded_transform: Map from (a, b) back to ℝ.
    inverse_bounded_transform_list: Map a list of tensors from (a, b) back to ℝ.
    inverse_cdf_interpolation: Compute inverse CDF using interpolation.
    inverse_cdf_optimization: Compute inverse CDF using optimization.
    merge_parameters: Merge multiple parameter tensors into a single tensor.
"""

from typing import Dict, List

import torch


def tensor2list(u: torch.Tensor, dim=1) -> List[torch.Tensor]:
    """
    Convert a 2D tensor into a list of column tensors.

    Args:
        u (torch.Tensor): A 2D tensor.
        dim (int): The dimension along which to unbind (default: 1).

    Returns:
        List[torch.Tensor]: List of column tensors.
    """
    return list(torch.unbind(u, dim=dim))


def list2tensor(u: List[torch.Tensor], dim=1) -> torch.Tensor:
    """
    Convert a list of column tensors into a 2D tensor.

    Args:
        u (List[torch.Tensor]): List of column tensors.
        dim (int): The dimension along which to concatenate (default: 1).

    Returns:
        torch.Tensor: A 2D tensor.
    """
    if dim == 1:
        u = [col.unsqueeze(1) for col in u]
    return torch.cat(u, dim=dim)


def clr(x: torch.Tensor) -> torch.Tensor:
    """
    Compute the centered log-ratio (CLR) transform for compositional data.

    Args:
        x (torch.Tensor): PyTorch tensor of compositional data.

    Returns:
        torch.Tensor: CLR transformed tensor.
    """
    g_mean = torch.exp(torch.mean(torch.log(x), dim=-1, keepdim=True))
    return torch.log(x / g_mean)


def clr_inv(x: torch.Tensor) -> torch.Tensor:
    """
    Compute the inverse of the centered log-ratio (CLR) transform.

    Args:
        x (torch.Tensor): PyTorch tensor of CLR transformed data.

    Returns:
        torch.Tensor: Original compositional data.
    """
    return torch.softmax(x, dim=0)


def clr1(x: torch.Tensor) -> torch.Tensor:
    """
    Compute the centered log-ratio (CLR) transform and omit the first component.

    Args:
        x (torch.Tensor): PyTorch tensor of compositional data.

    Returns:
        torch.Tensor: CLR transformed tensor (excluding the first component).
    """
    return clr(x)[1:]


def clr1_inv(x: torch.Tensor) -> torch.Tensor:
    """
    Compute the inverse of the centered log-ratio (CLR) transform (for clr1).

    Args:
        x (torch.Tensor): PyTorch tensor of CLR transformed data (excluding the first component).

    Returns:
        torch.Tensor: Original compositional data.
    """
    px = torch.exp(torch.cat((-x.sum().unsqueeze(0), x)))
    return px / px.sum()


def positive_transform(x: torch.Tensor, eps: float = 1e-6) -> torch.Tensor:
    """
    Transform a tensor to ensure all values are positive using softplus.

    Args:
        x (torch.Tensor): Input tensor.
        eps (float): Small positive value added to ensure strictly positive output. Default is 1e-6.

    Returns:
        torch.Tensor: Transformed tensor with all values > eps.
    """
    return torch.nn.functional.softplus(x) + eps


def inverse_positive_transform(
    y: torch.Tensor, eps: float = 1e-6, threshold: float = 20.0
) -> torch.Tensor:
    """
    Inverse of the positive_transform function.

    Args:
        y (torch.Tensor): Input tensor (must be > eps).
        eps (float): Small positive value that was added in positive_transform. Default is 1e-6.
        threshold (float): Threshold for large values to avoid numerical instability.

    Returns:
        torch.Tensor: Original tensor before positive_transform was applied.
    """
    if all(y > torch.ones_like(y) * threshold):
        return y
    else:
        return torch.log(torch.exp(y) - 1) - eps


def bounded_transform(
    x: torch.Tensor, a: torch.Tensor, b: torch.Tensor
) -> torch.Tensor:
    """
    Map from ℝ to (a, b) using a sigmoid transformation.

    Args:
        x (torch.Tensor): Input tensor.
        a (torch.Tensor): Lower bound.
        b (torch.Tensor): Upper bound.

    Returns:
        torch.Tensor: Transformed tensor in (a, b).
    """
    return a + (b - a) * torch.sigmoid(x)


def bounded_transform_list(
    x: List[torch.Tensor], a: torch.Tensor, b: torch.Tensor
) -> List[torch.Tensor]:
    """
    Map a list of tensors from ℝ to (a, b) using a sigmoid transformation.

    Args:
        x (List[torch.Tensor]): List of input tensors.
        a (torch.Tensor): Lower bound.
        b (torch.Tensor): Upper bound.

    Returns:
        List[torch.Tensor]: List of transformed tensors in (a, b).
    """
    return [bounded_transform(xi, a, b) for xi in x]


def inverse_bounded_transform(
    x: torch.Tensor, a: torch.Tensor, b: torch.Tensor
) -> torch.Tensor:
    """
    Map from (a, b) back to ℝ (inverse of bounded_transform).

    Args:
        x (torch.Tensor): Input tensor in (a, b).
        a (torch.Tensor): Lower bound.
        b (torch.Tensor): Upper bound.

    Returns:
        torch.Tensor: Transformed tensor in ℝ.
    """
    return torch.log((x - a) / (b - x))


def inverse_bounded_transform_list(
    y: List[torch.Tensor], a: torch.Tensor, b: torch.Tensor
) -> List[torch.Tensor]:
    """
    Map a list of tensors from (a, b) back to ℝ (inverse of bounded_transform_list).

    Args:
        y (List[torch.Tensor]): List of input tensors in (a, b).
        a (torch.Tensor): Lower bound.
        b (torch.Tensor): Upper bound.

    Returns:
        List[torch.Tensor]: List of transformed tensors in ℝ.
    """
    return [inverse_bounded_transform(yi, a, b) for yi in y]


def inverse_cdf_interpolation(
    cdf_func,
    p_values: torch.Tensor,
    domain_min: float = -10,
    domain_max: float = 10,
    num_samples: int = 1000,
) -> torch.Tensor:
    """
    Compute inverse CDF using interpolation over a grid of values.

    Args:
        cdf_func (callable): Function that computes the CDF for a given value.
        p_values (torch.Tensor): Probability values to find inverse CDF for.
        domain_min (float): Minimum value of the domain to search. Default is -10.
        domain_max (float): Maximum value of the domain to search. Default is 10.
        num_samples (int): Number of points to use in the interpolation grid. Default is 1000.

    Returns:
        torch.Tensor: Inverse CDF values corresponding to the input probabilities.
    """
    # Create a fine grid of x values
    x_values = torch.linspace(domain_min, domain_max, num_samples)

    # Compute CDF at these points
    cdf_values = torch.cat([cdf_func(x) for x in x_values])

    # For each probability p, find the x where CDF(x) is closest to p
    results = []
    for p in p_values:
        idx = torch.abs(cdf_values - p).argmin()
        results.append(x_values[idx])

    return torch.tensor(results)


def inverse_cdf_optimization(
    cdf_func,
    p_values: torch.Tensor,
    initial_guesses: torch.Tensor | None = None,
    tol: float = 1e-6,
    max_iter: int = 100,
) -> torch.Tensor:
    """
    Compute inverse CDF using optimization with LBFGS.

    Args:
        cdf_func (callable): Function that computes the CDF for a given value.
        p_values (torch.Tensor): Probability values to find inverse CDF for.
        initial_guesses (torch.Tensor|None): Initial values for optimization. Default is zeros.
        tol (float): Tolerance for optimization convergence. Default is 1e-6.
        max_iter (int): Maximum number of optimization iterations. Default is 100.

    Returns:
        torch.Tensor: Inverse CDF values corresponding to the input probabilities.
    """
    if initial_guesses is None:
        initial_guesses = torch.zeros_like(p_values)
    results = []
    for p, guess in zip(p_values, initial_guesses):
        x = guess.clone().detach().requires_grad_(True)
        optimizer = torch.optim.LBFGS([x], lr=1, line_search_fn="strong_wolfe")

        def closure():
            optimizer.zero_grad()
            loss = torch.pow(cdf_func(x) - p, 2)
            loss.backward()
            return loss

        for i in range(max_iter):
            loss = optimizer.step(closure)
            if loss.item() < tol:
                break
        results.append(x.detach())
    return torch.tensor(results)


def merge_parameters(
    theta: List[torch.Tensor] | Dict[str, torch.Tensor],
) -> torch.Tensor:
    """
    Merge multiple parameter tensors into a single tensor.

    Args:
        theta (List[torch.Tensor] | Dict[str, torch.Tensor]): Parameters to merge, either as:
            - List of tensors: concatenated in order
            - Dict of tensors: concatenated in sorted key order

    Returns:
        torch.Tensor: Single tensor containing all parameters concatenated.
    """
    if isinstance(theta, dict):
        return torch.cat([theta[key] for key in sorted(theta.keys())])
    else:
        return torch.cat(theta)
