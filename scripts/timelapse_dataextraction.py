'''
Save (cell, sample, time_since_last_readout, adc_counts) to an hdf5 file
for all given inputfiles.

Usage:
  offset_calculation.py <inputfiles> ... [options]
  offset_calculation.py (-h | --help)
  offset_calculation.py --version

Options:
  -h --help     Show this screen.
  --version     Show version.
  --outpath N   Outputfile path [default: data.hdf5]
  -c --calib P  Path to calibration file

'''

import dragonboard as dr
from tqdm import tqdm
import os
from docopt import docopt
import pandas as pd
from collections import defaultdict
import numpy as np
from dragonboard.calibration import TimelapseCalibration

def write(store, data):
    for (pixel, gain), value in data.items():
        df = pd.DataFrame(value)
        df['sample'] = df['sample'].astype('int16')
        df['adc_counts'] = df['adc_counts'].astype('int16')
        df['cell'] = df['cell'].astype('int16')
        df['delta_t'] = df['delta_t'].astype('float32')

        store.append(
            'pixel_{}_{}'.format(pixel, gain),
            df,
        )


def extract_data(inputfiles, outpath, calibpath=None):
    ''' calculate time lapse dependence for a given capacitor '''
    if not calibpath is None:
        calib = TimelapseCalibration(calibpath)
    else:
        calib = lambda x: x

    with pd.HDFStore(outpath, mode='w', comp_level=5, comp_lib='blosc') as store:

        sample_ids = None
        for filename in sorted(inputfiles):
            data = defaultdict(lambda: defaultdict(list))

            for event in tqdm(
                    iterable=dr.EventGenerator(filename),
                    desc=os.path.basename(filename),
                    leave=True,
                    unit=' events',
                    ):

                event = calib(event)

                if sample_ids is None or sample_ids.shape != event.roi:
                    sample_ids = np.arange(event.roi)

                for pixel, pixel_data in enumerate(event.data):
                    for gain in pixel_data.dtype.names:

                        stop_cell = event.header.stop_cells[pixel][gain]

                        delta_ts = event.time_since_last_readout[pixel][gain]
                        valid = np.logical_not(np.isnan(delta_ts))
                        if not np.any(valid):
                            continue

                        data[(pixel, gain)]['delta_t'].extend(delta_ts[valid])
                        data[(pixel, gain)]['cell'].extend(
                            dr.sample2cell(sample_ids[valid], stop_cell)
                        )
                        data[(pixel, gain)]['sample'].extend(sample_ids[valid])
                        data[(pixel, gain)]['adc_counts'].extend(pixel_data[gain][valid])

                if (event.header.event_counter + 1) % 10000 == 0:

                    write(store, data)
                    data = defaultdict(lambda: defaultdict(list))

            write(store, data)


if __name__ == '__main__':
    arguments = docopt(
        __doc__, version='Dragon Board Time-Dependent Offset Calculation v.1.0'
    )
    if os.path.isfile(arguments["--calib"]):
        extract_data(arguments['<inputfiles>'], outpath=arguments['--outpath'], calibpath=arguments["--calib"])
    else:
        extract_data(arguments['<inputfiles>'], outpath=arguments['--outpath'])

