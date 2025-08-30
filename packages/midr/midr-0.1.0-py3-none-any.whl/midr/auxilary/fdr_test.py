# SPDX-FileCopyrightText: 2025 Laurent Modolo <laurent@modolo.fr>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import torch

from .fdr import fdr

torch.set_default_dtype(torch.float64)
torch.set_printoptions(precision=10)
torch.set_printoptions(sci_mode=False)


def test_fdr():
    p = torch.tensor([0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
    fdr_values = fdr(p)
    discoveries = fdr_values < 0.05
    assert torch.all(
        torch.isclose(
            fdr_values,
            torch.tensor(
                [
                    0.0000000,
                    0.5500000,
                    0.7333333,
                    0.8250000,
                    0.8800000,
                    0.9166667,
                    0.9428571,
                    0.9625000,
                    0.9777778,
                    0.9900000,
                    1.0000000,
                ]
            ),
        )
    )
    assert torch.all(
        discoveries
        == torch.tensor(
            [True, False, False, False, False, False, False, False, False, False, False]
        )
    )
