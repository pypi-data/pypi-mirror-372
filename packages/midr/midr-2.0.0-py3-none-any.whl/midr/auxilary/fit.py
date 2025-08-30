# SPDX-FileCopyrightText: 2025 Laurent Modolo <laurent@modolo.fr>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Optimization and fitting utilities for the IDR package.

This module provides functions for fitting models using various optimization algorithms
including LBFGS, SGD, and Adam. It supports both single-tensor and batch optimization,
with optional multi-threading capabilities and visualization tools.

Functions:
    fit_set_tensor: Prepare a tensor for optimization.
    fit_closure: Create a closure function for optimization.
    fit_closure_batch: Create a closure function for batch optimization.
    fit_step: Perform a single optimization step with learning rate scheduling.
    fit: Main fitting function supporting multiple optimization algorithms.
    fit_LBFGS: Optimize parameters using the L-BFGS algorithm.
    fit_SGD: Optimize parameters using Stochastic Gradient Descent (SGD).
    fit_Adam: Optimize parameters using the Adam optimizer.
"""

from typing import List

import torch


def fit_set_tensor(
    tensor: torch.Tensor, gpu: bool = False, thread: int = 1
) -> torch.Tensor:
    """
    Prepare a tensor for optimization by setting requires_grad and moving to appropriate device.

    This function sets the requires_grad flag to True and moves the tensor to the GPU if available
    and thread is 1, otherwise keeps it on the CPU.

    Parameters:
        tensor (torch.Tensor): Input tensor to prepare
        thread (int): Number of threads. If 1 and CUDA is available, uses GPU. Default is 1

    Returns:
        torch.Tensor: Prepared tensor with requires_grad=True on appropriate device
    """
    device = torch.device("cpu")
    if gpu:
        if torch.cuda.is_available() and thread == 1:
            device = torch.device("cuda")
    return tensor.to(device).requires_grad_(True)


def fit_closure(
    compute_loss,
    optimizer: torch.optim.Optimizer,
    theta: torch.Tensor,
    losses: List[float],
    params: List[torch.Tensor],
    plot: bool,
) -> torch.Tensor:
    """
    Create a closure function for optimization that computes loss and gradients.

    This closure is used by optimizers like LBFGS to repeatedly evaluate the loss and its gradients.

    Parameters:
        compute_loss (callable): Function to compute the loss value
        optimizer (torch.optim.Optimizer): PyTorch optimizer instance
        theta (torch.Tensor): Parameters being optimized
        losses (List[float]): List to store loss values if plotting
        params (List[torch.Tensor]): List to store parameter values if plotting
        plot (bool): Whether to store values for plotting

    Returns:
        torch.Tensor: Computed loss value
    """
    optimizer.zero_grad()
    loss = compute_loss(theta)
    if plot:
        losses.append(loss.item())
        params.append(theta.clone())
    loss.backward()
    if loss.isnan():
        return torch.tensor(float("inf"))
    return loss


def fit_step(closure, optimizer, scheduler) -> torch.Tensor:
    """
    Perform a single optimization step with learning rate scheduling.

    This function executes one optimizer step and updates the learning rate scheduler.
    Returns Inf if the loss is NaN.

    Parameters:
        closure (callable): Closure function that computes loss and gradients
        optimizer (torch.optim.Optimizer): PyTorch optimizer instance
        scheduler (torch.optim.lr_scheduler._LRScheduler): Learning rate scheduler

    Returns:
        torch.Tensor: Loss value from the optimization step, or inf if optimization failed
    """
    loss = optimizer.step(closure)
    scheduler.step()
    if loss is not None:
        return loss
    return torch.tensor(float("inf"))


def fit(
    compute_loss,
    theta: torch.Tensor,
    tol: torch.Tensor = torch.tensor(1e-6),
    max_iter: int = 1000,
    start_lr: float = 1.0,
    lr_decay: float = 1.0,
    plot: bool = False,
    tensor_name: List[str] | None = None,
    plot_err: bool = False,
    print_progress: bool = False,
    algorithm: str = "LBFGS",
    gpu: bool = False,
) -> torch.Tensor:
    """
    Main fitting function that supports multiple optimization algorithms.

    This function selects and runs the appropriate optimizer based on the algorithm argument.

    Parameters:
        compute_loss (callable): Function to compute the loss value
        theta (torch.Tensor): Initial parameters to optimize
        tol (torch.Tensor): Tolerance for convergence. Default is 1e-6
        max_iter (int): Maximum number of iterations. Default is 1000
        start_lr (float): Initial learning rate. Default is 1.0
        lr_decay (float): Learning rate decay factor. Default is 1.0
        plot (bool): Whether to plot optimization progress. Default is False
        tensor_name (List[str]|None): Names of parameters for plotting. Default is None
        plot_err (bool): Whether to plot parameter errors. Default is False
        print_progress (bool): Whether to print progress during optimization. Default is False
        algorithm (str): Optimization algorithm to use ("LBFGS", "SGD", "Adam", or "SGD_LBFGS"). Default is "LBFGS"

    Returns:
        torch.Tensor: Optimized parameters

    Raises:
        ValueError: If an unknown algorithm is specified
    """
    if algorithm == "LBFGS":
        return fit_LBFGS(
            compute_loss,
            theta,
            tol,
            max_iter,
            start_lr,
            lr_decay,
            plot,
            tensor_name,
            plot_err,
            print_progress,
            gpu,
        )
    if algorithm == "SGD":
        return fit_SGD(
            compute_loss,
            theta,
            tol,
            max_iter,
            start_lr,
            lr_decay,
            plot,
            tensor_name,
            plot_err,
            print_progress,
            gpu,
        )
    if algorithm == "Adam":
        return fit_Adam(
            compute_loss,
            theta,
            tol,
            max_iter,
            start_lr,
            lr_decay,
            plot,
            tensor_name,
            plot_err,
            print_progress,
            gpu,
        )
    if algorithm == "SGD_LBFGS":
        theta = fit_LBFGS(
            compute_loss,
            theta,
            tol,
            max_iter,
            start_lr,
            lr_decay,
            plot,
            tensor_name,
            plot_err,
            print_progress,
            gpu,
        )
        return fit_SGD(
            compute_loss,
            theta,
            tol,
            max_iter,
            start_lr,
            lr_decay,
            plot,
            tensor_name,
            plot_err,
            print_progress,
            gpu,
        )
    raise ValueError(f"Unknown algorithm: {algorithm}")


def fit_LBFGS(
    compute_loss,
    theta: torch.Tensor,
    tol: torch.Tensor = torch.tensor(1e-6),
    max_iter: int = 1000,
    start_lr: float = 0.5,
    lr_decay: float = 0.99,
    plot: bool = False,
    tensor_name: List[str] | None = None,
    plot_err: bool = False,
    print_progress: bool = False,
    gpu: bool = False,
) -> torch.Tensor:
    """
    Optimize parameters using the L-BFGS algorithm with line search.

    Parameters:
    compute_loss (callable): Function to compute the loss value
    theta (torch.Tensor): Initial parameters to optimize
    tol (torch.Tensor): Tolerance for convergence. Default is 1e-6
    max_iter (int): Maximum number of iterations. Default is 1000
    start_lr (float): Initial learning rate. Default is 0.5
    lr_decay (float): Learning rate decay factor. Default is 0.99
    plot (bool): Whether to plot optimization progress. Default is False
    tensor_name (List[str]|None): Names of parameters for plotting. Default is None
    plot_err (bool): Whether to plot parameter errors. Default is False
    print_progress (bool): Whether to print progress during optimization. Default is False

    Returns:
    torch.Tensor: Optimized parameters

    Notes:
    Uses the Strong Wolfe line search method for step size selection.
    """
    theta = fit_set_tensor(theta, gpu)
    optimizer = torch.optim.LBFGS(
        params=[theta], lr=start_lr, line_search_fn="strong_wolfe", max_iter=10
    )
    scheduler = torch.optim.lr_scheduler.ExponentialLR(optimizer, gamma=lr_decay)
    params = []
    losses = []
    old_theta = theta.clone()
    old_loss = torch.tensor(-float("inf"))

    def closure():
        return fit_closure(compute_loss, optimizer, theta, losses, params, plot)

    for i in range(max_iter):
        try:
            loss = optimizer.step(closure)
            if print_progress:
                print(f"Iteration {i}: Loss = {loss.item()}, theta = {theta}")
            scheduler.step()
            if any(torch.isnan(theta)) or torch.isnan(loss):
                theta = old_theta.clone()
                print("fit_LBFGS() stop because of Nan")
                break
            if torch.abs(old_loss - loss) < tol:
                break
            old_theta = theta.clone()
            old_loss = loss.clone()
        except Exception as e:
            print("Optimization error:")
            print(f"Iteration {i}")
            print(f"previous Loss = {old_loss}")
            print(f"previous theta = {old_theta}")
            print(f"current theta = {theta}")
            print(f"Exception: {e}")
    if plot:
        from .plot import plot_optim

        plot_optim(params, losses, tensor_name)
    if plot_err:
        from .plot import plot_parameters_error

        plot_parameters_error(compute_loss, theta)
    return theta


def fit_SGD(
    compute_loss,
    theta: torch.Tensor,
    tol: torch.Tensor = torch.tensor(1e-6),
    max_iter: int = 1000,
    start_lr: float = 0.5,
    lr_decay: float = 0.99,
    plot: bool = False,
    tensor_name: List[str] | None = None,
    plot_err: bool = False,
    print_progress: bool = False,
    gpu: bool = False,
) -> torch.Tensor:
    """
    Optimize parameters using Stochastic Gradient Descent (SGD).

    Parameters:
    compute_loss (callable): Function to compute the loss value
    theta (torch.Tensor): Initial parameters to optimize
    tol (torch.Tensor): Tolerance for convergence. Default is 1e-6
    max_iter (int): Maximum number of iterations. Default is 1000
    start_lr (float): Initial learning rate. Default is 0.5
    lr_decay (float): Learning rate decay factor. Default is 0.99
    plot (bool): Whether to plot optimization progress. Default is False
    tensor_name (List[str]|None): Names of parameters for plotting. Default is None
    plot_err (bool): Whether to plot parameter errors. Default is False
    print_progress (bool): Whether to print progress during optimization. Default is False

    Returns:
    torch.Tensor: Optimized parameters

    Notes:
    Uses exponential learning rate decay during optimization.
    """
    theta = fit_set_tensor(theta, gpu)
    optimizer = torch.optim.SGD(
        params=[theta],
        lr=start_lr,
    )
    scheduler = torch.optim.lr_scheduler.ExponentialLR(optimizer, gamma=lr_decay)
    params = []
    losses = []
    old_theta = theta.clone()
    old_loss = torch.tensor(-float("inf"))

    def closure() -> torch.Tensor:
        return fit_closure(compute_loss, optimizer, theta, losses, params, plot)

    def step() -> torch.Tensor:
        return fit_step(closure, optimizer, scheduler)

    for i in range(max_iter):
        try:
            loss = step()
            if print_progress:
                print(f"Iteration {i}: Loss = {loss.item()}, theta = {theta}")
            scheduler.step()
            if any(torch.isnan(theta)) or torch.isnan(loss):
                theta = old_theta.clone()
                print("fit_SGD() stop because of Nan")
                break
            if torch.abs(old_loss - loss) < tol:
                break
            old_theta = theta.clone()
            old_loss = loss.clone()
        except Exception as e:
            print("Optimization error:")
            print(f"Iteration {i}")
            print(f"previous Loss = {old_loss}")
            print(f"previous theta = {old_theta}")
            print(f"Exception: {e}")
    if plot:
        from .plot import plot_optim

        plot_optim(params, losses, tensor_name)
    if plot_err:
        from .plot import plot_parameters_error

        plot_parameters_error(compute_loss, theta)
    return theta


def fit_Adam(
    compute_loss,
    theta: torch.Tensor,
    tol: torch.Tensor = torch.tensor(1e-6),
    max_iter: int = 1000,
    start_lr: float = 0.5,
    lr_decay: float = 0.99,
    plot: bool = False,
    tensor_name: List[str] | None = None,
    plot_err: bool = False,
    print_progress: bool = False,
    gpu: bool = False,
) -> torch.Tensor:
    """
    Optimize parameters using the Adam optimizer.

    Parameters:
    compute_loss (callable): Function to compute the loss value
    theta (torch.Tensor): Initial parameters to optimize
    tol (torch.Tensor): Tolerance for convergence. Default is 1e-6
    max_iter (int): Maximum number of iterations. Default is 1000
    start_lr (float): Initial learning rate. Default is 0.5
    lr_decay (float): Learning rate decay factor. Default is 0.99
    plot (bool): Whether to plot optimization progress. Default is False
    tensor_name (List[str]|None): Names of parameters for plotting. Default is None
    plot_err (bool): Whether to plot parameter errors. Default is False
    print_progress (bool): Whether to print progress during optimization. Default is False

    Returns:
    torch.Tensor: Optimized parameters

    Notes:
    Uses adaptive moment estimation with exponential learning rate decay.
    """
    theta = fit_set_tensor(theta, gpu)
    optimizer = torch.optim.Adam(
        params=[theta],
        lr=start_lr,
    )
    scheduler = torch.optim.lr_scheduler.ExponentialLR(optimizer, gamma=lr_decay)
    params = []
    losses = []
    old_theta = theta.clone()
    old_loss = torch.tensor(-float("inf"))

    def closure():
        return fit_closure(compute_loss, optimizer, theta, losses, params, plot)

    def step() -> torch.Tensor:
        return fit_step(closure, optimizer, scheduler)

    for i in range(max_iter):
        try:
            loss = step()
            if print_progress:
                print(f"Iteration {i}: Loss = {loss.item()}, theta = {theta}")
            scheduler.step()
            if any(torch.isnan(theta)) or torch.isnan(loss):
                theta = old_theta.clone()
                print("fit_Adam() stop because of Nan")
                break
            if torch.abs(old_loss - loss) < tol:
                break
            old_theta = theta.clone()
            old_loss = loss.clone()
        except Exception as e:
            print("Optimization error:")
            print(f"Iteration {i}")
            print(f"previous Loss = {old_loss}")
            print(f"previous theta = {old_theta}")
            print(f"Exception: {e}")
    if plot:
        from .plot import plot_optim

        plot_optim(params, losses, tensor_name)
    if plot_err:
        from .plot import plot_parameters_error

        plot_parameters_error(compute_loss, theta)
    return theta
