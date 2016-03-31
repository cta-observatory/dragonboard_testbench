"""
##################################################
*          Dragon board readout software         *
* calculate offset constants from pedestal files *
##################################################

annotations:

- inputdirectory is the path to the directory of your pedestal files


Usage:
  offset_calculation.py <inputdirectory> [options]
  offset_calculation.py (-h | --help)
  offset_calculation.py --version

Options:
  -h --help     Show this screen.
  --version     Show version.
  --outpath N   Outputfile path [default: calibration_constants.pickle]

"""

import numpy as np
import matplotlib.pyplot as plt
from dragonboard import EventGenerator
from dragonboard.runningstats import RunningStats
import dragonboard
from tqdm import tqdm
import glob
import os
from docopt import docopt
import sys
import pickle

def timelapse_calc(inputdirectory):
    """ calculate time lapse dependency for a given capacitor """

    glob_expression = os.path.join(inputdirectory, '*.dat')
    for filename in sorted(glob.glob(glob_expression)):
        try:
    # inputdirectory += "Ped_Rand1kHz_No1_IP90.dat"

            times = []
            events = []
            capno = 1337
            for event in tqdm(
                    iterable=dragonboard.EventGenerator(filename),
                    desc=os.path.basename(filename),
                    leave=True,
                    unit=" events"):
                # print(event.header.counter_133MHz / 133e6)
                times.append(event.header.counter_133MHz / 133e6)
                for pixelindex in range(dragonboard.io.num_channels):
                    for gaintype in dragonboard.io.gaintypes:
                        # print(event.header.stop_cells[gaintype][pixelindex])
                        stop_cell = event.header.stop_cells[gaintype][pixelindex]
                        if stop_cell <= capno <= (stop_cell + event.roi):
                            # print(event)
                            rolled_event = np.roll(event,stop_cell)
                            events.append(rolled_event[0])
                            print(rolled_event[0])

                            # stats = calibration_constants[(pixelindex, gaintype)]

                            # data = np.full(dragonboard.io.max_roi, np.nan)
                            # stop_cell = event.header.stop_cells[gaintype][pixelindex]
                            # data[:event.roi] = event.data[gaintype][pixelindex]

                            # stats.add(np.roll(data, stop_cell))
                

            # times = np.array(times)
            # delta_t_in_ms = np.diff(times)*1e3
            # print(delta_t_in_ms.mean())

            # plt.hist(delta_t_in_ms, bins=100, histtype="step")
            # plt.xlabel("time between consecutive events / ms")
            # plt.title(os.path.basename(filename))
            # plt.figure()
        except Exception as e:
            print(e)
    # calibration_constants = {}
    # for pixelindex in range(dragonboard.io.num_channels):
    #     for gaintype in dragonboard.io.gaintypes:
    #         calibration_constants[(pixelindex, gaintype)] = RunningStats(shape=dragonboard.io.max_roi)

    # glob_expression = os.path.join(inputdirectory, '*.dat')
    # for filename in sorted(glob.glob(glob_expression)):
    #     try:
    #         for event in tqdm(
    #                 iterable=EventGenerator(filename),
    #                 desc=os.path.basename(filename),
    #                 leave=True,
    #                 unit="events"):
    #             for pixelindex in range(dragonboard.io.num_channels):
    #                 for gaintype in dragonboard.io.gaintypes:
    #                     stats = calibration_constants[(pixelindex, gaintype)]

    #                     data = np.full(dragonboard.io.max_roi, np.nan)
    #                     stop_cell = event.header.stop_cells[gaintype][pixelindex]
    #                     data[:event.roi] = event.data[gaintype][pixelindex]

    #                     stats.add(np.roll(data, stop_cell))
    #     except Exception as e:
    #         print(e)

    # return calibration_constants


if __name__ == '__main__':
    arguments = docopt(__doc__, version='Dragon Board Offset Calculation v.1.1')

    if not glob.glob(os.path.join(arguments["<inputdirectory>"], '*.dat')):
        sys.exit("Error: no files found to perform time-lapse calculation")

    timelapse_calc(arguments["<inputdirectory>"])
    # calibration_constants = offset_calc(arguments["<inputdirectory>"])
    # pickle.dump(calibration_constants, open(arguments["--outpath"], 'wb'))
    plt.show()