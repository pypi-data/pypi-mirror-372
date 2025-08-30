#!/usr/bin/env python
# SPDX-FileCopyrightText: 2025 Laurent Modolo <laurent@modolo.fr>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import rich_click as click
import torch

from midr.idr import idr_from_csv

torch.set_default_dtype(torch.float64)
torch.set_printoptions(precision=10)
torch.set_printoptions(sci_mode=False)


@click.command()
@click.option(
    "--csv_input",
    help="csv file with data, observation as rows and dimensions as columns",
    required=True,
)
@click.option(
    "--csv_output",
    help="csv file with data, and two additional columns for IDR and FDR",
    required=True,
)
@click.option(
    "--ecdf",
    default="adjustedDistributionalTransform",
    type=click.Choice(
        ["adjustedDistributionalTransform", "distributionalTransform", "linear"]
    ),
    help="(default: adjustedDistributionalTransform) choise of eCDF method, to handle ties, linear use the data order, distributional transform randomize ties between upper and lower non-tie values, adjusted distributional transform randomize while keeping ties closer together than their are to the upper and lower values",
)
@click.option(
    "--copula",
    default="archmixture",
    type=click.Choice(["empiricalBeta", "archmixture", "gaussian"]),
    help="(default: archmixture) copula model to use",
)
@click.option(
    "--pseudo_data",
    is_flag=True,
    help="use pseudo data (a prior to consider higher values more reproducible)",
)
@click.option("--gpu", is_flag=True, help="run on GPU if available")
@click.option(
    "--no_header",
    is_flag=True,
    default=True,
    help="do not use header in csable header parsing in csv input file",
)
def main(csv_input, csv_output, ecdf, copula, pseudo_data, gpu, no_header):
    idr_from_csv(
        csv_input=csv_input,
        csv_output=csv_output,
        ecdf_method=ecdf,
        copula=copula,
        pseudo_data=pseudo_data,
        gpu=gpu,
        header=no_header,
    )


if __name__ == "__main__":
    main()
