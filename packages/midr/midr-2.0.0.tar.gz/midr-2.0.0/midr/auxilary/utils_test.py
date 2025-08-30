# SPDX-FileCopyrightText: 2025 Laurent Modolo <laurent@modolo.fr>
#
# SPDX-License-Identifier: AGPL-3.0-or-later
import torch

from midr.auxilary.utils import multiple_of_3_filter, zeros_proportion


def test_zeros_proportion():
    data = torch.tensor([1, 2, 3, 4, 0, 6, 7, 8, 9, 0])
    assert zeros_proportion(data) == 0.2


def test_multiple_of_3_filter():
    data = torch.tensor([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    assert multiple_of_3_filter(data).numel() == 10
    data = torch.tensor([1, 2, 3, 4, 5, 6, 7, 8, 9])
    assert multiple_of_3_filter(data).numel() == 8
