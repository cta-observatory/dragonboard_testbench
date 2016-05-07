'''
Usage:
    timeseries_std.py <inputfile> <fit_delta_t.py_output_file> <offset_cell_sample.py_output_file> [options]

Options:
    -p <pixel>       Pixel [default: 0]
    -g <gain>        Gain [default: low]
    -n <cores>       Cores to use [default: 1]
    -v <verbosity>   Verbosity [default: 10]
    -m <max_events>  Maximum number of Events
'''
from dragonboard import EventGenerator
from dragonboard.calibration import TimelapseCalibration
from dragonboard.calibration import TimelapseCalibrationExtraOffsets
from dragonboard.calibration import MedianTimelapseExtraOffsets
from joblib import Parallel, delayed
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from docopt import docopt

def calc_data(event):
    data = {}

    data['uncalib_mean'] = np.mean(event.data[pixel][channel])
    data['uncalib_std'] = np.std(event.data[pixel][channel])

    event_calib_1 = calib_1(event)

    data['calib_1_mean'] = np.mean(event_calib_1.data[pixel][channel])
    data['calib_1_std'] = np.std(event_calib_1.data[pixel][channel])

    event_calib_2 = calib_2(event)

    data['calib_2_mean'] = np.mean(event_calib_2.data[pixel][channel])
    data['calib_2_std'] = np.std(event_calib_2.data[pixel][channel])

    event_calib_3 = calib_3(event)

    data['calib_3_mean'] = np.mean(event_calib_3.data[pixel][channel])
    data['calib_3_std'] = np.std(event_calib_3.data[pixel][channel])

    return data


if __name__ == '__main__':
    args = docopt(
        __doc__, version='Dragon Board Time-Dependent Offset Calculation v.1.0'
    )

    pixel = int(args['-p'])
    channel = args['-g']
    
    calib_1 = TimelapseCalibration(args['<fit_delta_t.py_output_file>'])
    calib_2 = TimelapseCalibrationExtraOffsets(offsets_file=args['<offset_cell_sample.py_output_file>'],fits_file=args['<fit_delta_t.py_output_file>'])
    calib_3 = MedianTimelapseExtraOffsets(args['<offset_cell_sample.py_output_file>'])        

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
    data['calib_1_std'].plot.hist(
        bins=100, range=[0, 60], histtype='step', legend='false',
        ax=ax, label='TimelapseCalibration'
    )
    data['calib_2_std'].plot.hist(
        bins=100, range=[0, 60], histtype='step', legend='false',
        ax=ax, label='TimelapseCalibrationExtraOffsets'
    )
    data['calib_3_std'].plot.hist(
        bins=100, range=[0, 60], histtype='step', legend='false',
        ax=ax, label='MedianTimelapseExtraOffsets'
    )

    plt.title("pixel: {}, {}".format(pixel,channel))
    ax.set_xlabel('Timeseries standard deviation')
    fig.tight_layout()
    plt.show()

    # data.to_hdf(args['<outputfile>'], 'data')
