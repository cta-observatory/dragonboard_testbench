'''
Usage:
    timeseries_std.py <inputfile> <fit_delta_t.py_output_file> <offset_cell_sample.py_output_file> <outputfile> [options]

Options:
    -n <cores>       Cores to use [default: 1]
    -v <verbosity>   Verbosity [default: 10]
    -m <max_events>  Maximum number of Events
    --skip=<N>       Number of events to skip at start [default: 0]
    --start=<N>      First sample to consider
    --end=<N>        Last sample to consider, negative numbers count from end
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

<<<<<<< HEAD
                data[key + '_mean'][idx] = np.mean(event_calib.data[pixel][channel])
                data[key + '_std'][idx] = np.std(event_calib.data[pixel][channel])
                data[key + '_min'][idx] = np.min(event_calib.data[pixel][channel])
                data[key + '_max'][idx] = np.max(event_calib.data[pixel][channel])

    return pd.DataFrame(data)
=======
                data[key + '_mean'][idx] = np.mean(event_calib.data[pixel][channel][sl])
                data[key + '_std'][idx] = np.std(event_calib.data[pixel][channel][sl])
                data[key + '_min'][idx] = np.min(event_calib.data[pixel][channel][sl])
                data[key + '_max'][idx] = np.max(event_calib.data[pixel][channel][sl])

    df = pd.DataFrame(data)
    df.index.names = 'event', 'pixel', 'channel'
    return df
>>>>>>> d77d4bf55ac190daa50db5a7c428335911d2fb80


if __name__ == '__main__':
    args = docopt(
        __doc__, version='Dragon Board Time-Dependent Offset Calculation v.1.0'
    )

<<<<<<< HEAD
    pixel = int(args['-p'])
    channel = args['-g']

=======
>>>>>>> d77d4bf55ac190daa50db5a7c428335911d2fb80
    calibs = [
        NoCalibration(),
        TimelapseCalibration(args['<fit_delta_t.py_output_file>']),
        TimelapseCalibrationExtraOffsets(
            offsets_file=args['<offset_cell_sample.py_output_file>'],
            fits_file=args['<fit_delta_t.py_output_file>']
        ),
        MedianTimelapseExtraOffsets(args['<offset_cell_sample.py_output_file>']),
<<<<<<< HEAD
        MedianTimelapseCalibration(args['<fit_delta_t.py_output_file>'])
    ]
=======
        MedianTimelapseCalibration(args['<fit_delta_t.py_output_file>']),
    ]

>>>>>>> d77d4bf55ac190daa50db5a7c428335911d2fb80
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

<<<<<<< HEAD
    plt.style.use('ggplot')
    fig, ax = plt.subplots()

    data['uncalib_std'].plot.hist(
        bins=100, range=[0, 60], histtype='step', legend='false',
        ax=ax, label='Uncalibrated', color="red"
    )
    data['calib_1_std'].plot.hist(
        bins=100, range=[0, 60], histtype='step', legend='false',
        ax=ax, label='TimelapseCalibration', color="blue"
    )
    data['calib_2_std'].plot.hist(
        bins=100, range=[0, 60], histtype='step', legend='false',
        ax=ax, label='TimelapseCalibrationExtraOffsets', color="green"
    )
    data['calib_3_std'].plot.hist(
        bins=100, range=[0, 60], histtype='step', legend='false',
        ax=ax, label='MedianTimelapseExtraOffsets', color="black"
    )
    data['calib_4_std'].plot.hist(
        bins=100, range=[0, 60], histtype='step', legend='false',
        ax=ax, label='MedianTimelapseCalibration', color="orange"
    )

    plt.title("pixel: {}, {}".format(pixel,channel))
    ax.set_xlabel('Timeseries standard deviation')
    fig.tight_layout()
    plt.show()

    data.to_hdf(args['<outputfile>'], 'timeseries_full_data')
=======
    data.to_hdf(args['<outputfile>'], 'timeseries_full_data')
>>>>>>> d77d4bf55ac190daa50db5a7c428335911d2fb80
