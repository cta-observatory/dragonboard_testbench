'''
Usage:
    timeseries_std.py <inputfile> <calc_method_1> <calc_method_2> [options]

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
import dragonboard as db
from tqdm import tqdm
import os

# timeseries_std.py <inputfile> <calc_method_1> <calc_method_2> <calc_method_3> <outputfile> [options]

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
    gain = args['-g']
    filename = args["<inputfile>"]
    # df = pd.read_hdf(args["<calc_method_3>"], key="pixel_{}_{}".format(pixel, gain))
    # print(df)

    calib = TimelapseCalibration(args['<calc_method_1>'])
    calib_extra = TimelapseCalibrationExtraOffsets(offsets_file=args['<calc_method_2>'],fits_file=args['<calc_method_1>'])
    # calib_median = MedianTimelapseExtraOffsets(args['<calc_method_2>'])

    # cell,sample,a,b,c,chisq_ndf,pixel,channel
    # df = pd.read_hdf(args["<calc_method_2>"])
    # for index, row in tqdm(df.iterrows()):    
    #     print(row["a"])
    # cell = 1234
    # channel = gain
    # sample = 12
    # print(df.loc[cell])
    # for sample in range(40):
    # a, b, c = df.loc[(df["cell"] == cell) & (df["sample"] == sample) & (df["channel"] == gain) & (df["pixel"] == pixel)].values.T[2:5]

    # print(df.loc[(df["cell"] == cell) & (df["sample"] == sample) & (df["channel"] == gain) & (df["pixel"] == pixel)].values.T[2:5])

    # index = 0
    # time = []
    # time.append(0)
    # calib = []

    # for event in tqdm(
    #     iterable=EventGenerator(filename, max_events=1),
    #     desc=os.path.basename(filename),
    #     leave=True,
    #     unit=" events"
    #     ):
    #     index += 1
    #     time.append(event.header.counter_133MHz / 133e4)
    #     dt = time[index] - time[index-1]
    #     cell = event.header.stop_cells[gain][pixel]
    #     calib_event = []
    #     for sample in tqdm(range(40)):
    #         raw_adc = event.data[gain][pixel][sample]
    #         a, b, c = df.loc[(df["cell"] == cell) & (df["sample"] == sample) & (df["channel"] == gain) & (df["pixel"] == pixel)].values.T[2:5]
    #         offset = a*dt**b+c
    #         adc = raw_adc - float(offset)
    #         calib_event.append(int(adc))
    #     calib.append(calib_event)
    
    # print(calib[0])
    # plt.plot(calib[0])
    # plt.show()
    
    # events = EventGenerator(
    #     args['<inputfile>'],
    #     max_events=int(args['-m']) if args['-m'] else None,
    # )

    # with Parallel(int(args['-n']), verbose=int(args['-v'])) as pool:

    #     data = pd.DataFrame(
    #         pool(delayed(calc_data)(event) for event in events)
    #     )

    # plt.style.use('ggplot')
    # fig, ax = plt.subplots()

    # data['uncalib_std'].plot.hist(
    #     bins=100, range=[0, 60], histtype='step', legend='false',
    #     ax=ax, label='Uncalibrated'
    # )
    # data['calib_1_std'].plot.hist(
    #     bins=100, range=[0, 60], histtype='step', legend='false',
    #     ax=ax, label='Calibrated_M1'
    # )
    # data['calib_2_std'].plot.hist(
    #     bins=100, range=[0, 60], histtype='step', legend='false',
    #     ax=ax, label='Calibrated_M2'
    # )
    # data['calib_3_std'].plot.hist(
    #     bins=100, range=[0, 60], histtype='step', legend='false',
    #     ax=ax, label='Calibrated_M3'
    # )

    # ax.set_xlabel('Timeseries standard deviation')
    # fig.tight_layout()
    # plt.show()

    # data.to_hdf(args['<outputfile>'], 'data')
