'''
Save (cell, sample, time_since_last_readout, adc_counts) to an hdf5 file
for all given inputfiles.

Usage:
  dataextraction_ndarray.py <inputfiles> ... [options]
  dataextraction_ndarray.py (-h | --help)
  dataextraction_ndarray.py --version

Options:
  -h --help     Show this screen.
  --version     Show version.
  --outpath N   Outputfile path [default: data.hdf5]
  -c --calib P  Path to calibration file
  -e --extra P  Path to extra offset file
'''

import dragonboard as dr
from tqdm import tqdm
import os
from docopt import docopt
import pandas as pd
from collections import defaultdict
import numpy as np
import h5py

from dragonboard.calibration import NoCalibration
from dragonboard.calibration import TimelapseCalibration
from dragonboard.calibration import TimelapseCalibrationExtraOffsets
from dragonboard.calibration import MedianTimelapseExtraOffsets

def extract_data(inputfiles, outpath, calibpath=None, extrapath=None, a=None, b=None):
    ''' calculate time lapse dependence for a given capacitor '''
    if not extrapath is None and calibpath is None:
        calib = MedianTimelapseExtraOffsets(extrapath)
    elif not extrapath is None and not calibpath is None:
        calib = TimelapseCalibrationExtraOffsets(calibpath, extrapath)
    elif not calibpath is None and extrapath is None:
        calib = TimelapseCalibration(calibpath)
    else:
        calib = NoCalibration()

    print("using:", calib.__class__.__name__)
    inputfiles = {filename: dr.EventGenerator(filename) for filename in inputfiles}
    N_events = np.sum(len(x) for x in inputfiles.values())
    h5f = h5py.File(outpath, mode='w')
    
    calibrated = h5f.create_dataset(
        name=calib.__class__.__name__,
        shape=(N_events, 8, 2, 40),
        dtype=np.float32,
        compression="lzf",
        chunks=(400, 8, 2, 40),
    )


    counter = 0
    for filename in inputfiles:
        eg = inputfiles[filename]
        sample_ids = None

        for event in tqdm(
                iterable=eg,
                desc=os.path.basename(filename),
                leave=True,
                unit=' events',
                ):

            event = calib(event)

            for pixel, pixel_data in enumerate(event.data):
                for gain in pixel_data.dtype.names:
                    gain_id = {"high":0, "low":1}[gain]
                    calibrated[counter, pixel, gain_id] = event.data[pixel][gain]
            counter += 1



if __name__ == '__main__':
    arguments = docopt(
        __doc__, version='Dragon Board Time-Dependent Offset Calculation v.1.0'
    )
    print(arguments)
    extract_data(
        arguments['<inputfiles>'],
        outpath=arguments['--outpath'],
        calibpath=arguments["--calib"],
        extrapath=arguments["--extra"]
    )

