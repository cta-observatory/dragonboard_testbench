from .io import read, EventGenerator, Event
from .plotting import DragonBrowser
from .runningstats import RunningStats

__all__ = [
    'read',
    'EventGenerator',
    'Event',
    'DragonBrowser',
    'RunningStats',
]


def cell2sample(cell, stop_cell, roi, total_cells=4096):
    '''
    Converts a hardware cell to the sample id for given stop_cell and roi
    Raises a ValueError if the cell is not in the data samples
    '''
    assert cell < total_cells

    if stop_cell <= cell < stop_cell + roi:
        return cell - stop_cell

    if cell < (stop_cell + roi) % total_cells:
        return total_cells - stop_cell + cell

    raise ValueError('Physical capacitor not in data')


def sample2cell(sample, stop_cell, total_cells=4096):
    ''' Convert a sample id to the physical cell id for given stop_cell '''
    return (sample + stop_cell) % total_cells


def cell_in_samples(cell, stop_cell, roi, total_cells=4096):
    ''' Test if the hardware cell was read out for given stop_cell and roi '''

    assert cell < total_cells

    # cap directly in roi
    if stop_cell <= cell < stop_cell + roi:
        return True

    # overlapping readout region
    if cell < stop_cell + roi - total_cells:
        return True

    return False
