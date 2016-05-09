'''
Usage:
    timeseries_std.py <inputfile> <fit_delta_t.py_output_file> <offset_cell_sample.py_output_file> <outputfile> [options]

Options:
    -p <pixel>       Pixel [default: 0]
    -g <gain>        Gain [default: low]
    -n <cores>       Cores to use [default: 1]
    -v <verbosity>   Verbosity [default: 10]
    -m <max_events>  Maximum number of Events
    --skip=<N>       Number of events to skip at start [default: 0]
'''
from dragonboard import EventGenerator
from dragonboard.calibration import TimelapseCalibration
from dragonboard.calibration import TimelapseCalibrationExtraOffsets
from dragonboard.calibration import MedianTimelapseExtraOffsets
from dragonboard.calibration import MedianTimelapseCalibration
from dragonboard.calibration import NoCalibration
from joblib import Parallel, delayed
import numpy as np
import pandas as pd
from docopt import docopt
from collections import defaultdict


def calc_data(event):
    data = defaultdict(dict)

    for calib in calibs:
        key = calib.__class__.__name__
        event_calib = calib(event)

        for pixel in range(7):
            for channel in event.data.dtype.names:

                idx = (event.header.event_counter, pixel, channel)

                data[key + '_mean'][idx] = np.mean(event_calib.data[pixel][channel])
                data[key + '_std'][idx] = np.std(event_calib.data[pixel][channel])
                data[key + '_min'][idx] = np.min(event_calib.data[pixel][channel])
                data[key + '_max'][idx] = np.max(event_calib.data[pixel][channel])

    return pd.DataFrame(data)


if __name__ == '__main__':
    args = docopt(
        __doc__, version='Dragon Board Time-Dependent Offset Calculation v.1.0'
    )

    pixel = int(args['-p'])
    channel = args['-g']

    calibs = [
        NoCalibration(),
        TimelapseCalibration(args['<fit_delta_t.py_output_file>']),
        TimelapseCalibrationExtraOffsets(
            offsets_file=args['<offset_cell_sample.py_output_file>'],
            fits_file=args['<fit_delta_t.py_output_file>']
        ),
        MedianTimelapseExtraOffsets(args['<offset_cell_sample.py_output_file>']),
        MedianTimelapseCalibration(args['<fit_delta_t.py_output_file>']),
    ]

    events = EventGenerator(
        args['<inputfile>'],
        max_events=int(args['-m']) if args['-m'] else None,
    )

    for i in range(int(args['--skip'])):
        next(events)

    with Parallel(int(args['-n']), verbose=int(args['-v'])) as pool:

        data = pd.concat(
            pool(delayed(calc_data)(event) for event in events)
        )

    data.to_hdf(args['<outputfile>'], 'timeseries_full_data')
