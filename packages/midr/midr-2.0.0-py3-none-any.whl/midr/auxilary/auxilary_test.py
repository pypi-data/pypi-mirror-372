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
torch.set_printoptions(precision=10)
torch.set_printoptions(sci_mode=False)

def test_ecdf():
    """
    Test the ECDF computation for a 1D tensor.

    This test checks that the ECDF values returned by the ecdf function
    match the expected values for a simple input tensor.
    """
    x = torch.tensor([1.0, 2.0, 3.0, 4.0, 5.0])
    expected = torch.tensor([0.1666666667, 0.3333333333, 0.5000000000, 0.6666666667, 0.8333333333])
    assert torch.allclose(ecdf(x), expected)
