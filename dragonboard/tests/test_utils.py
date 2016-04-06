import pytest


def test_cell2sample():
    from dragonboard import cell2sample

    assert cell2sample(cell=10, stop_cell=5, total_cells=4096) == 5
    assert cell2sample(cell=5, stop_cell=4090, total_cells=4096) == 11

    assert cell2sample(cell=0, stop_cell=10, total_cells=4096) >= 40


def test_cell_in_samples():
    from dragonboard import cell_in_samples

    assert cell_in_samples(cell=10, stop_cell=5, roi=40, total_cells=4096)
    assert cell_in_samples(cell=5, stop_cell=4090, roi=40, total_cells=4096)

    assert not cell_in_samples(cell=0, stop_cell=10, roi=40, total_cells=4096)
