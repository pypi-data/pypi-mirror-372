# SPDX-FileCopyrightText: 2025 Laurent Modolo <laurent@modolo.fr>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Unit tests for auxiliary utilities in the IDR package.

This module provides tests for auxiliary functions such as ECDF computation.
"""

import torch

from .ecdf import ecdf

torch.set_default_dtype(torch.float64)
torch.set_printoptions(sci_mode=False)


def test_ecdf_1d():
    data = torch.tensor([1.0, 2.0, 3.0, 4.0, 5.0])
    ecdf_values = ecdf(data)
    expected_values = torch.tensor(
        [0.1666666667, 0.3333333333, 0.5000000000, 0.6666666667, 0.8333333333]
    )
    assert torch.allclose(ecdf_values, expected_values)


def test_ecdf_2d():
    data = torch.tensor(
        [
            [1.0, 2.0],
            [2.0, 3.0],
            [3.0, 4.0],
            [4.0, 5.0],
            [5.0, 6.0],
        ]
    )
    ecdf_values = ecdf(data)
    expected_values = torch.tensor(
        [
            [0.1666666667, 0.1666666667],
            [0.3333333333, 0.3333333333],
            [0.5000000000, 0.5000000000],
            [0.6666666667, 0.6666666667],
            [0.8333333333, 0.8333333333],
        ]
    )
    assert torch.allclose(ecdf_values, expected_values)


def test_ecdf_3d():
    data = torch.tensor(
        [
            [1.0, 2.0, 3.0],
            [2.0, 3.0, 4.0],
            [3.0, 4.0, 5.0],
            [4.0, 5.0, 6.0],
            [5.0, 6.0, 7.0],
        ]
    )
    ecdf_values = ecdf(data)
    expected_values = torch.tensor(
        [
            [0.1666666667, 0.1666666667, 0.1666666667],
            [0.3333333333, 0.3333333333, 0.3333333333],
            [0.5000000000, 0.5000000000, 0.5000000000],
            [0.6666666667, 0.6666666667, 0.6666666667],
            [0.8333333333, 0.8333333333, 0.8333333333],
        ]
    )
    assert torch.allclose(ecdf_values, expected_values)


def test_ecdf_identical():
    torch.manual_seed(123)
    # linear
    data = torch.tensor([1.0, 1.0, 2.0, 3.0, 3.0, 4.0, 5.0])
    ecdf_values = ecdf(data, method="linear")
    expected_values = torch.tensor([0.125, 0.25, 0.375, 0.5, 0.625, 0.75, 0.875])
    assert torch.allclose(ecdf_values, expected_values)
    data = torch.tensor([5.0, 1.0, 3.0, 3.0, 1.0, 2.0, 4.0])
    ecdf_values = ecdf(data, method="linear")
    expected_values = torch.tensor([0.875, 0.125, 0.5, 0.625, 0.25, 0.375, 0.75])
    assert torch.allclose(ecdf_values, expected_values)

    # distributional transform
    data = torch.tensor([1.0, 1.0, 2.0, 3.0, 3.0, 4.0, 5.0])
    ecdf_values = ecdf(data, method="distributionalTransform")
    expected_values = torch.tensor(
        [0.2281, 0.1689, 0.3333, 0.5986, 0.5154, 0.6667, 0.8333]
    )
    assert torch.allclose(ecdf_values, expected_values, rtol=1e-4, atol=1e-4)
    data = torch.tensor([5.0, 1.0, 3.0, 3.0, 1.0, 2.0, 4.0])
    ecdf_values = ecdf(data, method="distributionalTransform")
    expected_values = torch.tensor(
        [0.8333, 0.2454, 0.6008, 0.5885, 0.2537, 0.3333, 0.6667]
    )
    assert torch.allclose(ecdf_values, expected_values, rtol=1e-4, atol=1e-4)

    # adjusted distributional transform
    data = torch.tensor([1.0, 1.0, 2.0, 3.0, 3.0, 4.0, 5.0])
    ecdf_values = ecdf(data, method="adjustedDistributionalTransform")
    expected_values = torch.tensor(
        [0.2457, 0.1714, 0.3333, 0.5690, 0.5078, 0.6667, 0.8333]
    )
    assert torch.allclose(ecdf_values, expected_values, rtol=1e-4, atol=1e-4)
    data = torch.tensor([5.0, 1.0, 3.0, 3.0, 1.0, 2.0, 4.0])
    ecdf_values = ecdf(data, method="adjustedDistributionalTransform")
    expected_values = torch.tensor(
        [0.8333, 0.1830, 0.5162, 0.5345, 0.1850, 0.3333, 0.6667]
    )
    assert torch.allclose(ecdf_values, expected_values, rtol=1e-4, atol=1e-4)
