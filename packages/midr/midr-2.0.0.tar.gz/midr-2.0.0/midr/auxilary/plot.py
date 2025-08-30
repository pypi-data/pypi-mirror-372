# SPDX-FileCopyrightText: 2025 Laurent Modolo <laurent@modolo.fr>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Visualization utilities for the IDR package.

This module provides functions for plotting optimization progress and parameter errors
using plotnine (Python implementation of ggplot2) and Polars DataFrames.

Functions:
    plot_optim: Plot optimization progress showing parameter values and losses.
    plot_parameters_error: Plot the inverse Hessian matrix of the loss function.
    plot_tile_from_2d_tensor: Create a heatmap visualization of a 2D tensor.
"""

import torch
import polars as pl
from typing import List
from plotnine import ggplot, aes, geom_line, facet_wrap, labs, geom_tile, scale_fill_gradient2, coord_equal, scale_y_reverse

def plot_optim(params: List[torch.Tensor], losses: List[float], tensor_name: List[str]|None = None):
    """
    Plot optimization progress showing parameter values and losses over iterations.

    Parameters:
        params (List[torch.Tensor]): List of parameter tensors from each optimization iteration.
        losses (List[float]): List of loss values from each iteration.
        tensor_name (List[str]|None): Optional list of names for each parameter. If None,
                                      parameters will be named 'tensor_0', 'tensor_1', etc.

    Returns:
        None. Displays a multi-faceted line plot showing the evolution of each parameter
        and the loss value over optimization iterations.
    """
    data = torch.stack(params, dim=0).detach().numpy()
    if tensor_name is None:
        df = pl.DataFrame(data, schema=[f"tensor_{i}" for i in range(data.shape[1])])
    else:
        df = pl.DataFrame(data, schema=tensor_name)
    df = df.with_columns(pl.Series("loss", losses))
    df = df.with_row_index("index")
    df = df.unpivot(
        index=["index"],
        on=df.columns[1:])

    # Create the plot using plotnine
    plot = (ggplot(df, aes(x='index', y='value', color='variable'))
            + geom_line()
            + facet_wrap('~variable', scales='free_y')
            + labs(title='Line Plot of Tensors', x='Index', y='Value')
    )
    # Display the plot
    print(plot)
    plot.show()

def plot_parameters_error(compute_loss, theta: torch.Tensor):
    """
    Plot the inverse Hessian matrix of the loss function to visualize parameter errors.

    Parameters:
        compute_loss (callable): Function that computes the loss value.
        theta (torch.Tensor): Parameter tensor at which to compute the Hessian.

    Returns:
        None. Displays a heatmap visualization of the inverse Hessian matrix,
        where colors indicate the magnitude and sign of error correlations
        between parameters.

    Notes:
        The inverse Hessian provides information about parameter uncertainties
        and their correlations in the neighborhood of the optimum.
    """
    split = [len(t) for t in theta]
    def compute_loss_cat(params: torch.Tensor) -> torch.Tensor:
        return compute_loss(torch.split(params, split))
    theta.requires_grad_(True)
    inv_hessian = torch.inverse(torch.autograd.functional.hessian(compute_loss_cat, theta)) # type: ignore
    plot_tile_from_2d_tensor(inv_hessian.detach())

def plot_tile_from_2d_tensor(x: torch.Tensor):
    """
    Create a heatmap visualization of a 2D tensor.

    Parameters:
        x (torch.Tensor): 2D tensor to visualize.

    Returns:
        None. Displays a heatmap where colors represent tensor values,
        with blue for negative values, white for values near zero,
        and red for positive values.
    """
    n_rows, n_cols = x.shape
    rows, cols = x.shape
    row_indices, col_indices = torch.meshgrid(
        torch.arange(rows),
        torch.arange(cols),
        indexing='ij'
    )
    data = pl.DataFrame({
        "row": row_indices.flatten().numpy(),
        "column": col_indices.flatten().numpy(),
        "value": x.flatten().numpy()
    })
    plot = (ggplot(data, aes('column', 'row', fill='value'))
                + geom_tile()
                + scale_fill_gradient2(low="blue", mid="white", high="red")
                + coord_equal()
                + scale_y_reverse()
        )
    print(plot)
    plot.show()
