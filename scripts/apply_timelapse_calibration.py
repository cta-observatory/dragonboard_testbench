"""
Usage:
    apply_timelapse_calibration.py <inputfile> <fit_constants> <outputfile> [options]

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
"""
from dragonboard import EventGenerator
from dragonboard.calibration import TimelapseCalibration
from joblib import Parallel, delayed
import pandas as pd
from docopt import docopt
from collections import defaultdict
import joblib

def calc_data(event, start, end):
    """Calibrate data"""
    data = defaultdict(dict)

    sl = slice(start, end)

    for calib in calibs:
        key = calib.__class__.__name__
        event_calib = calib(event)

        for pixel in range(7):
            for channel in event.data.dtype.names:

                idx = (event.header.event_counter, pixel, channel)
                data[key][idx] = event_calib.data[pixel][channel][sl]

    return data


if __name__ == '__main__':
    args = docopt(
        __doc__, version='Dragon Board Timelapse Calibration v.1.0'
    )

    calibs = [TimelapseCalibration(args['<fit_constants>'])]

    events = EventGenerator(
        args['<inputfile>'],
        max_events=int(args['-m']) if args['-m'] else None,
    )

    for i in range(int(args['--skip'])):
        next(events)

    start = int(args['--start']) if args['--start'] else None
    end = int(args['--end']) if args['--end'] else None

    with Parallel(int(args['-n']), verbose=int(args['-v'])) as pool:

        data = []
        data.append(
            pool(
                delayed(calc_data)(event, start=start, end=end)
                for event in events
            )
        )

    # print(data)
    joblib.dump(data, args['<outputfile>'] + 'TimelapseCalibration.pickle')

    data = joblib.load(args['<outputfile>'] + 'TimelapseCalibration.pickle')
    print(data[0][0]["TimelapseCalibration"][(1, 6, "high")])
    # print(data[0][1]["TimelapseCalibration"][(2, 6, "high")])
