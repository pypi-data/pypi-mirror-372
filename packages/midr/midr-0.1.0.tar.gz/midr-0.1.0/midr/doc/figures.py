# SPDX-FileCopyrightText: 2025 Laurent Modolo <laurent@modolo.fr>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Visualization utilities for creating figures demonstrating IDR concepts.

This module provides functions for generating illustrative plots that help visualize
the transformations and models used in the IDR package.

Functions:
    transform_plot: Create visualization plots showing various data transformations in the IDR process.
"""

from plotnine import aes, geom_point, theme_bw, geom_histogram, facet_wrap, coord_trans, theme
from plotnine.ggplot import ggplot
import pandas as pd
import polars as pl
import torch
from ..pseudo_mixture.indep_mixture import IndepMixture
from ..copula import ClaytonCopula, FrankCopula, GumbelCopula
from ..auxilary import ecdf, r_gaussian_mixture

torch.set_default_dtype(torch.float64)
torch.set_printoptions(precision=10)
torch.set_printoptions(sci_mode=False)

def transform_plot(theta = torch.tensor(
            [0.5, 0.5*1/3, 0.5*1/3, 0.5*1/3, 10.0, 18.0, 5.0]
        ),
        ratio=0.5, correlation=0.8, dep_mu=[5.0, 5.0], dep_sigma=[3.0, 3.0], indep_sigma=[5.0, 5.0], size = 1000):
    """
    Create visualization plots showing various data transformations in the IDR process.

    This function demonstrates the effect of different transformations applied in
    the IDR workflow by:
    1. Creating synthetic mixture data with dependent and independent components
    2. Applying empirical CDF transformations
    3. Transforming between copula space and data space
    4. Applying marginal distribution transformations

    Generates and displays two sets of plots:
    - Scatter plots showing transformed data, colored by dependency type
    - Histograms of the transformed data, separated by dependency type

    Returns:
    None: Displays plots directly
    """
    mixture = IndepMixture(dim=2, copula=[ClaytonCopula(dim=2), FrankCopula(dim=2), GumbelCopula(dim=2)], family="indep_archmixture")
    id, x = r_gaussian_mixture(size=size, ratio=ratio, correlation=correlation, dep_mu=dep_mu, dep_sigma=dep_sigma, indep_sigma=indep_sigma)
    data = pl.DataFrame(ecdf(x).detach().numpy(), schema=["x", "y"])
    data = data.with_columns([
        pl.Series(name='label', values=id.numpy()),
        pl.Series(name='type', values=[r"$eCDF(x)$"] * id.shape[0])
    ]).with_row_index(name="id")

    df = pl.DataFrame(x.detach().numpy(), schema=["x", "y"])
    df = df.with_columns([
        pl.Series(name='label', values=id.numpy()),
        pl.Series(name='type', values=[r"$x$"] * id.shape[0])
    ]).with_row_index(name="id")
    data = pl.concat([data, df])

    parameters=mixture.split_parameters(theta)
    print(parameters)
    df = pl.DataFrame((mixture.u_to_x(u=ecdf(x), parameters=parameters)).detach().numpy(), schema=["x", "y"])
    df = df.with_columns([
        pl.Series(name='label', values=id.numpy()),
        pl.Series(name='type', values=[r"$G^{-1}(eCDF(x))$"] * id.shape[0])
    ]).with_row_index(name="id")
    data = pl.concat([data, df])

    df = pl.DataFrame(
        torch.stack([1.0 - mixture._indep_marginal.cdf(
                x=mixture.u_to_x(u=ecdf(x), parameters=parameters)[:, j],
                theta=torch.cat([
                    torch.tensor([1.0])
                ])
            ) for j in range(mixture._dim)]
            , dim=1).detach().numpy(),
            schema=["x", "y"]
        )
    df = df.with_columns([
        pl.Series(name='label', values=id.numpy()),
        pl.Series(name='type', values=[r"$F_{indep}(G^{-1}(eCDF(x))$"] * id.shape[0])
    ]).with_row_index(name="id")
    data = pl.concat([data, df])

    df = pl.DataFrame(
        torch.stack([mixture._dep_marginal.cdf(
                x=mixture.u_to_x(u=ecdf(x), parameters=parameters)[:, j],
                theta=torch.cat([
                    torch.tensor([parameters["dep_mu"][j]]),
                    torch.tensor([1.0])
                ])
            ) for j in range(mixture._dim)]
            , dim=1).detach().numpy(),
            schema=["x", "y"]
        )
    df = df.with_columns([
        pl.Series(name='label', values=id.numpy()),
        pl.Series(name='type', values=[r"$F_{dep}(G^{-1}(eCDF(x))$"] * id.shape[0])
    ]).with_row_index(name="id")
    data = pl.concat([data, df])

    df = pl.DataFrame(
        torch.stack([mixture._indep_marginal.pdf(
                x=mixture.u_to_x(u=ecdf(x), parameters=parameters)[:, j],
                theta=torch.cat([
                    torch.tensor([1.0])
                ])
            ) for j in range(mixture._dim)]
            , dim=1).detach().numpy(),
            schema=["x", "y"]
        )
    df = df.with_columns([
        pl.Series(name='label', values=id.numpy()),
        pl.Series(name='type', values=[r"$f_{indep}(G^{-1}(eCDF(x))$"] * id.shape[0])
    ]).with_row_index(name="id")
    data = pl.concat([data, df])

    df = pl.DataFrame(
        torch.stack([mixture._dep_marginal.pdf(
                x=mixture.u_to_x(u=ecdf(x), parameters=parameters)[:, j],
                theta=torch.cat([
                    torch.tensor([parameters["dep_mu"][j]]),
                    torch.tensor([1.0])
                ])
            ) for j in range(mixture._dim)]
            , dim=1).detach().numpy(),
            schema=["x", "y"]
        )
    df = df.with_columns([
        pl.Series(name='label', values=id.numpy()),
        pl.Series(name='type', values=[r"$f_{dep}(G^{-1}(eCDF(x))$"] * id.shape[0])
    ]).with_row_index(name="id")
    data = pl.concat([data, df])


    data_w = data.pivot(
        on="type",
        index=["id", "label"],
        values="x"
    )

    def clean_column(data):
        data = data.with_columns([
            pl.Series(name='label', values=["indep" if x == 0 else "dep" for x in list(data["label"])]),
        ])
        data = data.to_pandas()
        data["label"] = pd.Categorical(data["label"])
        data["label"] = data["label"].cat.reorder_categories(["indep", "dep"])
        return data

    data = clean_column(data)
    data["type"] = pd.Categorical(data["type"])
    data["type"] = data["type"].cat.reorder_categories([
        r"$x$",
        r"$eCDF(x)$",
        r"$G^{-1}(eCDF(x))$",
        r"$F_{indep}(G^{-1}(eCDF(x))$",
        r"$F_{dep}(G^{-1}(eCDF(x))$",
        r"$f_{indep}(G^{-1}(eCDF(x))$",
        r"$f_{dep}(G^{-1}(eCDF(x))$",
    ])
    data_w = clean_column(data_w)

    plot = (
        ggplot(data, aes(x="x", y="y", color="label"))
        + geom_point()
        + facet_wrap("~type", scales="free")
        + theme_bw()
        + coord_trans(x='identity', y='identity')
        + theme(figure_size=(16, 8))

    )
    print(plot)
    plot.show()

    plot = (
        ggplot(data, aes(x="x", fill="label"))
        + geom_histogram(bins=torch.sqrt(torch.tensor(x.shape[0])))
        + facet_wrap("~type+label", scales="free")
        + theme_bw()
        + theme(figure_size=(16, 8))
    )
    print(plot)
    plot.show()
    plot = (
        ggplot(data_w, aes(x="$x$", y="$eCDF(x)$", color="label"))
        + geom_point()
        + theme_bw()
        + theme(figure_size=(16, 8))
    )
    print(plot)
    plot.show()
    plot = (
        ggplot(data_w, aes(x="$x$", y="$G^{-1}(eCDF(x))$", color="label"))
        + geom_point()
        + theme_bw()
        + theme(figure_size=(16, 8))
    )
    print(plot)
    plot.show()
    plot = (
        ggplot(data_w, aes(x="$x$", y="$F_{indep}(G^{-1}(eCDF(x))$", color="label"))
        + geom_point()
        + theme_bw()
        + theme(figure_size=(16, 8))
    )
    print(plot)
    plot.show()
    plot = (
        ggplot(data_w, aes(x="$x$", y="$F_{dep}(G^{-1}(eCDF(x))$", color="label"))
        + geom_point()
        + theme_bw()
        + theme(figure_size=(16, 8))
    )
    print(plot)
    plot.show()
    plot = (
        ggplot(data_w, aes(x="$x$", y="$f_{indep}(G^{-1}(eCDF(x))$", color="label"))
        + geom_point()
        + theme_bw()
        + theme(figure_size=(16, 8))
    )
    print(plot)
    plot.show()
    plot = (
        ggplot(data_w, aes(x="$x$", y="$f_{dep}(G^{-1}(eCDF(x))$", color="label"))
        + geom_point()
        + theme_bw()
        + theme(figure_size=(16, 8))
    )
    print(plot)
    plot.show()



if __name__ == "__main__":
    # Generate and display transformation visualization plots when run as a script
    transform_plot(
        theta = torch.tensor(
                [0.5, 0.5*1/3, 0.5*1/3, 0.5*1/3, 2.0, 2.0, 18.0, 36.0, 18.0]
            ),
        ratio=0.5, correlation=0.8, dep_mu=[2.0, 2.0], dep_sigma=[5.0, 5.0], indep_sigma=[5.0, 5.0]
    )
