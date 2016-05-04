import numpy as np
from .io import max_roi


def cell2sample(cell, stop_cell, total_cells=max_roi):
    '''
    Converts a hardware cell to the sample id for given stop_cell and roi

    This makes no assumption about the roi, so if the returned value is >= roi,
    the cell was not sampled
    '''
    assert np.all(cell < total_cells)

    return (cell - stop_cell) % total_cells


def sample2cell(sample, stop_cell, total_cells=max_roi):
    ''' Convert a sample id to the physical cell id for given stop_cell '''
    return (sample + stop_cell) % total_cells


def cell_in_samples(cell, stop_cell, roi, total_cells=max_roi):
    ''' Test if the hardware cell was read out for given stop_cell and roi '''
    assert np.all(cell < total_cells)

    return cell2sample(cell, stop_cell, total_cells) < roi
