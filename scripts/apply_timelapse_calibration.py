"""
Usage:
    apply_timelapse_calibration.py <inputfile> <fit_constants> <outputfile> [options]

Options:
    -n <cores>       Cores to use [default: 1]
    -v <verbosity>   Verbosity [default: 10]
    -m <max_events>  Maximum number of Events

apply TimelapseCalibration for given .dat file(s):
inputfile: .dat file
fit constants: fit_delta_t.py output file
"""
from dragonboard import EventGenerator
from dragonboard.calibration import TimelapseCalibration
from joblib import Parallel, delayed
from docopt import docopt
import joblib
import os

def calc_data(event):
    """Calibrate data"""
    return calib(event)


if __name__ == '__main__':
    args = docopt(
        __doc__, version='Dragon Board Timelapse Calibration v.1.0'
    )

    calib = TimelapseCalibration(args['<fit_constants>'])

    events = EventGenerator(
        args['<inputfile>'],
        max_events=int(args['-m']) if args['-m'] else None,
    )

    with Parallel(int(args['-n']), verbose=int(args['-v'])) as pool:

        data = list(
            pool(
                delayed(calc_data)(event) for event in events
            )
        )

    joblib.dump(data, args['<outputfile>'] + '{}_calib.pickle'.format(os.path.basename(args['<inputfile>'])), compress=5)
