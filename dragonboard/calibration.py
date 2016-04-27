import numpy as np
import pandas as pd
from copy import deepcopy

from .utils import sample2cell


class TimelapseCalibration:

    def __init__(self, filename):
        self.calib_constants = pd.read_hdf(filename).set_index(
            ['pixel', 'channel', 'cell']
        ).sort_index()
        self.roi = None
        self.sample = None

    def offset(self, delta_t, a, b, c):
        o = a * delta_t ** b + c
        o[np.isnan(o)] = c
        o[np.isnan(o)] = 0

        return o

    def __call__(self, event):
        ''' calibrate data in event '''
        event = deepcopy(event)

        if self.roi is None:
            self.roi = event.roi
            self.sample = np.arange(event.roi)

        assert self.roi == event.roi

        for pixel in range(len(event.data)):
            for channel in event.data.dtype.names:
                sc = event.header.stop_cells[pixel][channel]
                cells = sample2cell(self.sample, sc)

                dt = event.time_since_last_readout[pixel][channel]
                c = self.calib_constants.loc[pixel, channel].loc[cells]
                event.data[pixel][channel] -= self.offset(dt, c['a'], c['b'], c['c']).astype('>i2')

        return event
