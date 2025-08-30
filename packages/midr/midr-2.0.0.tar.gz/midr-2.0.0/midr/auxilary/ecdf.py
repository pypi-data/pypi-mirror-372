# SPDX-FileCopyrightText: 2025 Laurent Modolo <laurent@modolo.fr>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Empirical Cumulative Distribution Function (ECDF) utilities for the IDR package.

This module provides functions to compute the ECDF for 1D and 2D tensors, as well as for lists of tensors.
The ECDF is a nonparametric estimator of the cumulative distribution function and is useful for transforming
data to the uniform scale, which is a common preprocessing step in copula modeling and other statistical analyses.

Functions:
    ecdf_1d: Compute the ECDF for a 1D tensor.
    ecdf: Compute the ECDF for 1D or 2D tensor data.
    list_ecdf: Compute the ECDF for a list of 1D tensors.
"""

from typing import List

import torch


def adjusted_distributional_transform(
    sorted_data: torch.Tensor, adjustment: float = 1.0
) -> torch.Tensor:
    unique_value, counts = torch.unique(sorted_data, return_counts=True)
    n = len(unique_value)
    # we build the ecdf with the unique values
    unique_ecdf_values_sorted = torch.arange(1.0, n + 1.0) / (n + 1.0)
    # in case of ties, we randomize the ties at 0.5 the step of the ecdf
    # for the unique values
    randomize_equality = torch.distributions.Uniform(
        0.0,
        (unique_ecdf_values_sorted[1] - unique_ecdf_values_sorted[0])
        / (1.0 / adjustment),
    )
    randomize_equality_last = torch.distributions.Uniform(
        0.0,
        (1.0 - unique_ecdf_values_sorted[-1]) / (1.0 / adjustment),
    )
    ecdf_values_sorted = torch.ones_like(sorted_data) * -1.0
    n = len(sorted_data)
    i = 0
    j = 0
    while i < n:
        if counts[j] == 1:
            ecdf_values_sorted[i] = unique_ecdf_values_sorted[j]
        elif i == n - 1:
            ecdf_values_sorted[i : (i + counts[j])] = (
                randomize_equality_last.sample((counts[j],))
                + unique_ecdf_values_sorted[j]
            )
            i += counts[j] - 1
        else:
            # in case of ties, we randomize the ties
            ecdf_values_sorted[i : (i + counts[j])] = (
                randomize_equality.sample((counts[j],)) + unique_ecdf_values_sorted[j]
            )
            i += counts[j] - 1
        j += 1
        i += 1
    ecdf_values_sorted = ecdf_values_sorted
    return ecdf_values_sorted


def ecdf_1d(
    data: torch.Tensor, method: str = "adjustedDistributionalTransform"
) -> torch.Tensor:
    """
    Compute the empirical cumulative distribution function (ECDF) for a 1D tensor
    and return the results in the same order as the input data.

    Parameters:
        data (torch.Tensor): 1D tensor of data points.

    Returns:
        torch.Tensor: ECDF values corresponding to the input data points, in the same order as input.

    Raises:
        ValueError: If input is not a 1D tensor.
    """
    if data.dim() != 1:
        raise ValueError("Input data must be a 1D tensor")
    sorted_data, sorted_indices = torch.sort(data)
    match method:
        case "linear":
            n = len(data)
            ecdf_values_sorted = torch.arange(1.0, n + 1.0) / n
            ecdf_values_sorted = ecdf_values_sorted * n / (n + 1)
        case "distributionalTransform":
            ecdf_values_sorted = adjusted_distributional_transform(sorted_data)
        case "adjustedDistributionalTransform":
            ecdf_values_sorted = adjusted_distributional_transform(sorted_data, 0.5)
        case _:
            raise ValueError(f"Invalid method: {method}")
    ecdf_values = torch.empty_like(ecdf_values_sorted)
    ecdf_values[sorted_indices] = ecdf_values_sorted
    ecdf_values.requires_grad_(True)
    return ecdf_values


def ecdf(
    data: torch.Tensor, method: str = "adjustedDistributionalTransform"
) -> torch.Tensor:
    """
    Compute the empirical cumulative distribution function (ECDF) for 1D or 2D tensor data.

    Parameters:
        data (torch.Tensor): Input tensor of data points. Can be either:
            - 1D tensor: Computes ECDF directly using ecdf_1d
            - 2D tensor: Computes ECDF separately for each column and stacks results

    Returns:
        torch.Tensor: ECDF values corresponding to the input data points.
            - For 1D input: Returns 1D tensor of ECDF values
            - For 2D input: Returns 2D tensor where each column contains ECDF values for corresponding input column

    Raises:
        ValueError: If input tensor has dimension other than 1 or 2.
    """
    if data.dim() == 1:
        return ecdf_1d(data, method=method)
    if data.dim() == 2:
        return torch.stack(
            list_ecdf(list(torch.unbind(data, dim=1)), method=method), dim=1
        )
    raise ValueError("Input data must be a 1D or 2D tensor")


def list_ecdf(
    data: List[torch.Tensor], method: str = "adjustedDistributionalTransform"
) -> List[torch.Tensor]:
    """
    Compute the empirical cumulative distribution function (ECDF) for a list of 1D tensors.

    Parameters:
        data (List[torch.Tensor]): List of 1D tensors containing data points

    Returns:
        List[torch.Tensor]: List of tensors containing ECDF values corresponding to each input tensor
    """
    return [ecdf_1d(d, method=method) for d in data]
