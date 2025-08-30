# SPDX-FileCopyrightText: 2025 Laurent Modolo <laurent@modolo.fr>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
False Discovery Rate (FDR) utility for the IDR package.

This module provides a function to compute the False Discovery Rate (FDR)
for a given set of p-values, using the Benjamini-Hochberg procedure.

Functions:
    fdr: Compute the FDR threshold and return a boolean mask of discoveries.
"""

import torch


def fdr(p: torch.Tensor) -> torch.Tensor:
    """
    Compute the False Discovery Rate (FDR) threshold using the Benjamini-Hochberg procedure.

    Parameters:
        p (torch.Tensor): 1D tensor of p-values.

    Returns:
        padjust (torch.Tensor): 1D tensor of corrected p-values.

    Example:
        >>> p = torch.tensor([0.01, 0.04, 0.03, 0.2, 0.5])
        >>> fdr(p)
    """
    n = p.shape[0]
    idx = torch.arange(n, 0, -1)
    o = torch.argsort(p, descending=True)
    ro = torch.argsort(o)
    cmin = torch.cummin(n / idx * p[o], dim=0).values
    padjust = torch.min(torch.ones_like(cmin), cmin)[ro]
    return padjust
