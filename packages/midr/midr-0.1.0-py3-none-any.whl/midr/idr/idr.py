#! /usr/bin/env python3
# SPDX-FileCopyrightText: 2025 Laurent Modolo <laurent@modolo.fr>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from typing import List

import polars as pl
import torch

from ..auxilary import check_gpu, ecdf, fdr, multiple_of_3_filter, zeros_proportion
from ..copula import (
    ClaytonCopula,
    EmpiricalBetaCopula,
    FrankCopula,
    GaussianCopula,
    GumbelCopula,
    IndependenceCopula,
    IndepMixtureCopula,
)
from ..pseudo_mixture import IndepMixture as PseudoIndepMixtureCopula


def load_csv(
    csv: str, header: bool = True, pseudo_data: bool = False, p_zeros=0.1
) -> List:
    """
    Load data from a CSV file and convert it to PyTorch tensors.

    Args:
        csv (str): Path to the CSV file to load
        header (bool, optional): Whether the CSV file has a header row. Defaults to True.
        p_zeros (float, optional): Proportion of zeros above which we print a warning. Defaults to 0.1.

    Returns:
        List: A list containing [torch.Tensor, column_names] where:
            - torch.Tensor: The data as a PyTorch tensor
            - column_names: List of column names from the CSV
    """
    df = pl.read_csv(csv, has_header=header)
    data = torch.tensor(df.to_numpy())
    obs_p_zeros = zeros_proportion(data)
    if obs_p_zeros > p_zeros and not pseudo_data:
        print(f"Warning: There are {obs_p_zeros * 100:.2f}% zeros in the data.")
        print(
            "you should consider using pseudo-data approach with the option \033[1m--pseudo_data\033[0m."
        )
    return [data, df.columns]


def write_csv(csv: str, data: torch.Tensor, columns: List[str], header: bool = True):
    """
    Write PyTorch tensor data to a CSV file.

    Args:
        csv (str): Path for the output CSV file (currently unused - hardcoded to 'output.csv')
        data (torch.Tensor): The data tensor to write to CSV
        columns (List[str]): List of column names for the CSV
        header (bool, optional): Whether to include column headers in the output. Defaults to True.
    """
    df = pl.DataFrame(data.cpu().detach().numpy())
    if header:
        df.columns = columns
    df.write_csv(csv)


def parse_copula(
    copula: str, data: torch.Tensor, gpu: torch.device = torch.device("cpu")
) -> List:
    """
    Parse copula specification and return appropriate copula models with initial parameters.

    Args:
        copula (str): The copula model type. Supported values:
            - "empiricalBeta": Empirical beta copula
            - "archmixture": Mixture of Archimedean copulas (Clayton, Frank, Gumbel)
            - "gaussian": Gaussian copula
        data (torch.Tensor): Input data tensor used to determine dimensions and ranks
        gpu (torch.device, optional): Device to use for computations. Defaults to CPU.

    Returns:
        List: A list containing [copula_models, initial_parameters] where:
            - copula_models: List of instantiated copula objects
            - initial_parameters: PyTorch tensor with initial parameter values

    Raises:
        ValueError: If an unsupported copula model is specified.

    Note:
        - For empiricalBeta: Uses beta kernel for the copula fit
        - For archmixture: Creates Clayton, Frank, and Gumbel copulas with mixing weights
        - For gaussian: Creates a single Gaussian copula
    """
    match copula:
        case "empiricalBeta":
            return [
                [
                    EmpiricalBetaCopula(
                        dim=data.shape[1],
                        rank=data.argsort(dim=0, stable=True).argsort(
                            dim=0, stable=True
                        )
                        + 1.0,
                        gpu=gpu,
                    )
                ],
                torch.tensor([0.5, 0.5] + [1.0] * data.shape[1] + [1.0, 1.0]).to(gpu),
            ]
        case "archmixture":
            return [
                [
                    ClaytonCopula(dim=data.shape[1], gpu=gpu),
                    FrankCopula(dim=data.shape[1], gpu=gpu),
                    GumbelCopula(dim=data.shape[1], gpu=gpu),
                ],
                torch.tensor(
                    [0.5, 0.5 * 1.0 / 3.0, 0.5 * 1.0 / 3.0, 0.5 * 1.0 / 3.0]
                    + [1.0] * data.shape[1]
                    + [15.0, 28.0, 10.0],
                ).to(gpu),
            ]
        case "gaussian":
            return [
                [GaussianCopula(dim=data.shape[1], gpu=gpu)],
                torch.tensor(
                    [0.5, 0.5] + [1.0] * data.shape[1] + [1.0] * data.shape[1] ** 2
                ).to(gpu),
            ]
        case _:
            raise ValueError(f"Invalid model: {copula}")


def compute_idr(
    data: torch.Tensor,
    ecdf_method: str = "adjustedDistributionalTransform",
    copula: str = "archmixture",
    pseudo_data: bool = False,
    gpu: bool = True,
    header: bool = True,
    verbose: bool = False,
    progress: bool = False,
):
    """
    Compute Irreproducible Discovery Rate (IDR) for data

    This is the main function that performs the compute the  IDR
    1. Parse and initialize the specified copula model
    2. Fit the independence mixture model
    3. Compute IDR values
    4. Apply False Discovery Rate (FDR) correction

    Args:
        data: 2d torch tensor containing the data
        ecdf (str): The ECDF method to use. Options: "linear", "distributional transform", "adjusted distributional transform"
        copula (str): The copula model to use. Options: "empiricalBeta", "archmixture", "gaussian"
        pseudo_data (bool): Whether to use pseudo-data approach (True) or standard approach (False)
        gpu (bool, optional): Whether to use GPU acceleration if available. Defaults to True.
        header (bool, optional): Whether the CSV files have headers. Defaults to True.
        verbose (bool, optional): Whether to print the model parameters. Defaults to False.
        progress (bool, optional): Whether to print the progress of the optimization. Defaults to False.

    Note:
        - The function uses empirical CDF (ECDF) transformation on the raw data
        - For pseudo_data=True: Uses PseudoIndepMixtureCopula
        - For pseudo_data=False: Uses IndepMixtureCopula with IndependenceCopula
    """
    if torch.get_default_dtype() != torch.float64:
        print("Not using torch.float64, computation results may be inaccurate.")
        print(
            "Consider using torch.float64 for better accuracy by using the following command:"
        )
        print("torch.set_default_dtype(torch.float64)")
    data = data.to(torch.float64)
    device = check_gpu(gpu=gpu)
    copula_model, init_parameters = parse_copula(copula=copula, data=data, gpu=device)
    if pseudo_data:
        model = PseudoIndepMixtureCopula(
            dim=data.shape[1], copula=copula_model, family="indep_{model}", gpu=device
        )
    else:
        model = IndepMixtureCopula(
            dim=data.shape[1],
            copulas=[IndependenceCopula(data.shape[1])] + copula_model,
            family="indep_{model}",
            gpu=device,
        )
    u = ecdf(data, method=ecdf_method)
    theta = model.fit(
        u=multiple_of_3_filter(u), theta=init_parameters, print_progress=progress
    )
    if verbose:
        print(f"Model parameters: {model.split_parameters(theta)}")
    idr = model.idr(u=u, theta=theta)
    adjusted_pvalue = fdr(idr)
    return idr, adjusted_pvalue


def idr_from_csv(
    csv_input: str,
    csv_output: str,
    ecdf_method: str = "adjustedDistributionalTransform",
    copula: str = "empiricalBeta",
    pseudo_data: bool = False,
    gpu: bool = True,
    header: bool = True,
):
    """
    This is the main function that performs the complete IDR analysis pipeline:
    1. Load data from CSV
    2. Compute IDR values and corresoinding FDR values
    3. Save results to CSV
    Args:
        csv_input (str): Path to the input CSV file containing the data
        csv_output (str): Path for the output CSV file (currently unused - outputs to 'output.csv')
        ecdf (str): The ECDF method to use. Options: "linear", "distributional transform", "adjusted distributional transform"
        copula (str): The copula model to use. Options: "empiricalBeta", "archmixture", "gaussian"
        pseudo_data (bool): Whether to use pseudo-data approach (True) or standard approach (False)
        gpu (bool, optional): Whether to use GPU acceleration if available. Defaults to True.
        header (bool, optional): Whether the CSV files have headers. Defaults to True.

    Output includes original data plus IDR and FDR columns
    """
    data, columns = load_csv(csv=csv_input, header=header, pseudo_data=pseudo_data)
    idr, adjusted_pvalue = compute_idr(
        data=data,
        ecdf_method=ecdf_method,
        copula=copula,
        pseudo_data=pseudo_data,
        gpu=gpu,
    )
    columns += ["idr", "fdr"]
    data = torch.cat([data, idr.unsqueeze(1), adjusted_pvalue.unsqueeze(1)], dim=1)
    write_csv(csv=csv_output, data=data, columns=columns, header=header)
