'''
Usage:
    calibration_performance.py <inputfile> <fit_constants> <offsets> <outputfile> [options]

Options:
    -n <cores>       Cores to use [default: 1]
    -v <verbosity>   Verbosity [default: 10]
    -m <max_events>  Maximum number of Events
    --skip=<N>       Number of events to skip at start [default: 0]
    --start=<N>      First sample to consider
    --end=<N>        Last sample to consider, negative numbers count from end

extract performance information for several calibration methods:
inputfile: .dat file
fit constants: fit_delta_t.py output file
offsets: offsets_cell_sample.py output file
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


def calc_data(event, start=None, end=None):
    data = defaultdict(dict)

    sl = slice(start, end)

    for calib in calibs:
        key = calib.__class__.__name__
        event_calib = calib(event)

        for pixel in range(7):
            for channel in event.data.dtype.names:

                idx = (event.header.event_counter, pixel, channel)

                data[key + '_mean'][idx] = np.mean(event_calib.data[pixel][channel][sl])
                data[key + '_std'][idx] = np.std(event_calib.data[pixel][channel][sl])
                data[key + '_min'][idx] = np.min(event_calib.data[pixel][channel][sl])
                data[key + '_max'][idx] = np.max(event_calib.data[pixel][channel][sl])

    df = pd.DataFrame(data)
    df.index.names = 'event', 'pixel', 'channel'
    return df


if __name__ == '__main__':
    args = docopt(
        __doc__, version='Dragon Board Time-Dependent Offset Calculation v.1.0'
    )

    calibs = [
        NoCalibration(),
        TimelapseCalibration(args['<fit_constants>']),
        TimelapseCalibrationExtraOffsets(
            offsets_file=args['<offsets>'],
            fits_file=args['<fit_constants>']
        ),
        MedianTimelapseExtraOffsets(args['<offsets>']),
        MedianTimelapseCalibration(args['<fit_constants>']),
    ]

    events = EventGenerator(
        args['<inputfile>'],
        max_events=int(args['-m']) if args['-m'] else None,
    )

    for i in range(int(args['--skip'])):
        next(events)

    start = int(args['--start']) if args['--start'] else None
    end = int(args['--end']) if args['--end'] else None

    with Parallel(int(args['-n']), verbose=int(args['-v'])) as pool:

        data = pd.concat(
            pool(
                delayed(calc_data)(event, start=start, end=end)
                for event in events
            )
        )

    data.to_hdf(args['<outputfile>'], 'timeseries_full_data')
