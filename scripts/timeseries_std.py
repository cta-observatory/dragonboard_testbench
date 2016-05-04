'''
Usage:
    timeseries_std.py <inputfile> <outputfile> [options]

Options:
    -p <pixel>       Pixel [default: 0]
    -c <channel>     Channel [default: low]
    -n <cores>       Cores to use [default: 1]
    -v <verbosity>   Verbosity [default: 10]
    -m <max_events>  Maximum number of Events
'''
from dragonboard import EventGenerator
from dragonboard.calibration import TimelapseCalibration
from joblib import Parallel, delayed
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from docopt import docopt


def calc_data(event):
    data = {}

    data['uncalib_mean'] = np.mean(event.data[pixel][channel])
    data['uncalib_std'] = np.std(event.data[pixel][channel])
    data['uncalib_min'] = np.min(event.data[pixel][channel])
    data['uncalib_max'] = np.max(event.data[pixel][channel])

    event_calib = calib(event)

    data['calib_mean'] = np.mean(event_calib.data[pixel][channel])
    data['calib_std'] = np.std(event_calib.data[pixel][channel])
    data['calib_min'] = np.min(event_calib.data[pixel][channel])
    data['calib_max'] = np.max(event_calib.data[pixel][channel])

    return data


if __name__ == '__main__':
    args = docopt(__doc__)

    pixel = int(args['-p'])
    channel = args['-c']

    calib = TimelapseCalibration('./calib_constants.hdf5')
    events = EventGenerator(
        args['<inputfile>'],
        max_events=int(args['-m']) if args['-m'] else None,
    )

    with Parallel(int(args['-n']), verbose=int(args['-v'])) as pool:

        data = pd.DataFrame(
            pool(delayed(calc_data)(event) for event in events)
        )

    plt.style.use('ggplot')
    fig, ax = plt.subplots()

    data['uncalib_std'].plot.hist(
        bins=100, range=[0, 60], histtype='step', legend='false',
        ax=ax, label='Uncalibrated'
    )
    data['calib_std'].plot.hist(
        bins=100, range=[0, 60], histtype='step', legend='false',
        ax=ax, label='Calibrated'
    )

    ax.set_xlabel('Timeseries standard deviation')
    fig.tight_layout()
    plt.show()

    data.to_hdf(args['<outputfile>'], 'data')
