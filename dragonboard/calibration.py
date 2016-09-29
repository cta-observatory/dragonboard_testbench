import numpy as np
import pandas as pd
from copy import deepcopy

from .utils import sample2cell


class NoCalibration:
    def __call__(self, event):
        return event


def read_calib_constants(filepath):
    return pd.read_hdf(filepath).set_index(
        ['pixel', 'channel', 'cell']
    ).sort_index()


class TakaOffsetCalibration:

    def __init__(self, filename):
        self.roi = None
        table = np.genfromtxt(filename)
        assert table.shape == (4096, 16)
        table = table.astype('i4')
        self.offsets = np.zeros(
            8,
            dtype=[
                ("low", 'i4', 4096),
                ("high", 'i4', 4096),
            ]
        )
        for i in range(8):
            self.offsets["high"][i] = table[:, i]
            self.offsets["low"][i] = table[:, i + 8]

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

                event.data[pixel][channel] -= self.offsets[pixel][channel][cells]

        return event


class TimelapseCalibration:
    ''' Performs timelapse correction of measured data of
    the form calibrated = data - a * time_since_last_readout**b +c
    where a, b and c come from the fits performed by scripts/fit_delta_t.py
    '''

    def __init__(self, filename):
        self.calib_constants = read_calib_constants(filename)
        self.roi = None
        self.sample = None

        self.a = np.zeros(
            8,
            dtype=[
                ("low", 'f4', 4096),
                ("high", 'f4', 4096),
            ]
        )
        self.b = np.zeros(
            8,
            dtype=[
                ("low", 'f4', 4096),
                ("high", 'f4', 4096),
            ]
        )
        self.c = np.zeros(
            8,
            dtype=[
                ("low", 'f4', 4096),
                ("high", 'f4', 4096),
            ]
        )
        for pixel in range(8):
            for channel in ["low", "high"]:
                a, b, c = self.calib_constants.loc[pixel, channel].values.T
                self.a[pixel][channel][:] = a
                self.b[pixel][channel][:] = b
                self.c[pixel][channel][:] = c

    def offset(self, delta_t, a, b, c):
        o = a * delta_t ** b + c
        mask = np.isnan(o)
        o[mask] = c[mask]

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

                a = self.a[pixel][channel][cells]
                b = self.b[pixel][channel][cells]
                c = self.c[pixel][channel][cells]

                dt = event.time_since_last_readout[pixel][channel]
                event.data[pixel][channel] -= self.offset(dt, a, b, c).astype('>i2')

        return event


def read_offsets(offsets_file):
    offsets = np.zeros(
            shape=(8, 2, 4096, 40),
            dtype='f4')

    def name_to_channel_gain_id(name):
        _, channel, gain = name.split('_')
        channel = int(channel)
        gain_id = {'high': 0, 'low': 1}[gain]
        return channel, gain_id

    with pd.HDFStore(offsets_file) as st:
        for name in st.keys():
            channel, gain_id = name_to_channel_gain_id(name)
            df = st[name]
            df.sort_values(["cell", "sample"], inplace=True)
            offsets[channel, gain_id] = df["median"].values.reshape(-1, 40)

    return offsets


class MedianTimelapseCalibration:
    ''' Performs timelapse correction of measured data of
    the form calibrated = data - a * time_since_last_readout**b +c
    where c comes from the fits performed by scripts/fit_delta_t.py
    and a,b are median values.
    '''

    def __init__(self, filename):
        self.calib_constants = read_calib_constants(filename)
        self.roi = None
        self.sample = None

    def offset(self, delta_t, a, b, c):
        o = a * delta_t ** b + c
        mask = np.isnan(o)
        o[mask] = c[mask]

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

                a, b, c = self.calib_constants.loc[pixel, channel].loc[cells].values.T
                a = 1.4599324285222228
                b = -0.37503250093991702
                dt = event.time_since_last_readout[pixel][channel]
                event.data[pixel][channel] -= self.offset(dt, a, b, c).astype('>i2')

        return event


class TimelapseCalibrationExtraOffsets:
    ''' Performs timelapse correction of measured data of
    the form calibrated = data - a * time_since_last_readout**b +c.
    Here, c is a function of sample_id. Takes 2 inputparameters:
    fits_file = file generated by scripts/fit_delta_t.py
    offsets_file = file generated by scripts/offset_cell_sample.py
    '''

    def __init__(self, fits_file, offsets_file):
        self.calib_constants = read_calib_constants(fits_file).drop('c', axis=1)
        self.offsets = read_offsets(offsets_file)
        self.roi = None
        self.sample = None

    def offset(self, delta_t, a, b):
        o = a * delta_t ** b
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
            for gain in event.data.dtype.names:
                gain_id = {'high': 0, 'low': 1}[gain]
                sc = event.header.stop_cells[pixel][gain]
                cells = sample2cell(self.sample, sc)

                dt = event.time_since_last_readout[pixel][gain]
                a, b = self.calib_constants.loc[pixel, gain].loc[cells].values.T
                delta_t_offset = self.offset(dt, a, b).astype('>i2')
                extra_offset = self.offsets[pixel, gain_id, cells, self.sample].astype('>i2')
                event.data[pixel][gain] -= delta_t_offset + extra_offset

        return event


class MedianTimelapseExtraOffsets:

    def __init__(self, offsets_file, a=1.4599324285222228, b=-0.37503250093991702):
        self.offsets = read_offsets(offsets_file)
        self.roi = None
        self.sample = None
        self.a = a
        self.b = b

    def offset(self, delta_t):
        o = self.a * delta_t ** self.b
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
            for gain in event.data.dtype.names:
                gain_id = {'high': 0, 'low': 1}[gain]
                sc = event.header.stop_cells[pixel][gain]
                cells = sample2cell(self.sample, sc)

                dt = event.time_since_last_readout[pixel][gain]
                delta_t_offset = self.offset(dt).astype('>i2')
                extra_offset = self.offsets[pixel, gain_id, cells, self.sample].astype('>i2')
                event.data[pixel][gain] -= delta_t_offset + extra_offset

        return event


class PatternSubtraction:
    def __init__(self, pattern_file):
        self.pattern_data = (
            pd.read_hdf(pattern_file)
            .reset_index()
            .set_index(['pixel', 'channel', 'cell', 'sample'])
            .sort_index()
        )['mean'].values.reshape(7, 2, 4096, 11)
        self.roi = None

    def __call__(self, event):
        ''' calibrate data in event '''
        event = deepcopy(event)

        if self.roi is None:
            self.roi = event.roi
            self.sample = np.arange(event.roi)[:10]

        assert self.roi == event.roi

        for pixel in range(len(event.data) - 1):
            for gain in event.data.dtype.names:
                gain_id = {'high': 0, 'low': 1}[gain]
                sc = event.header.stop_cells[pixel][gain]
                cells = sample2cell(self.sample, sc)

                offset = self.pattern_data[pixel, gain_id, cells, self.sample]
                event.data[pixel][gain][:10] -= np.round(offset).astype('>i2')

        return event
