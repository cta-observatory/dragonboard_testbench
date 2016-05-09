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
<<<<<<< HEAD
from dragonboard.calibration import MedianTimelapseCalibration
=======
from dragonboard.calibration import NoCalibration
>>>>>>> e3819ed300dac4e3a62dbc08e0890d6558036c54
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

<<<<<<< HEAD
    event_calib_4 = calib_4(event)

    data['calib_4_mean'] = np.mean(event_calib_4.data[pixel][channel])
    data['calib_4_std'] = np.std(event_calib_4.data[pixel][channel])
    data['calib_4'] = np.min(event.data[pixel][channel])
    data['calib_4'] = np.max(event.data[pixel][channel])

    return data
=======
    return pd.DataFrame(data)
>>>>>>> e3819ed300dac4e3a62dbc08e0890d6558036c54


if __name__ == '__main__':
    args = docopt(
        __doc__, version='Dragon Board Time-Dependent Offset Calculation v.1.0'
    )

    pixel = int(args['-p'])
    channel = args['-g']
<<<<<<< HEAD
    
    calib_1 = TimelapseCalibration(args['<fit_delta_t.py_output_file>'])
    calib_2 = TimelapseCalibrationExtraOffsets(offsets_file=args['<offset_cell_sample.py_output_file>'],fits_file=args['<fit_delta_t.py_output_file>'])
    calib_3 = MedianTimelapseExtraOffsets(args['<offset_cell_sample.py_output_file>']) 
    calib_4 = MedianTimelapseCalibration(args['<fit_delta_t.py_output_file>'])       
=======

    calibs = [
        NoCalibration(),
        TimelapseCalibration(args['<fit_delta_t.py_output_file>']),
        TimelapseCalibrationExtraOffsets(
            offsets_file=args['<offset_cell_sample.py_output_file>'],
            fits_file=args['<fit_delta_t.py_output_file>']
        ),
        MedianTimelapseExtraOffsets(args['<offset_cell_sample.py_output_file>'])
    ]
>>>>>>> e3819ed300dac4e3a62dbc08e0890d6558036c54

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
>>>>>>> e3819ed300dac4e3a62dbc08e0890d6558036c54
