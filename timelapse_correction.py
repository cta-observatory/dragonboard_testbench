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
            # times_with_events = {}
            capno = 1337

            time = []
            adc_counts = []
            timeerror = 0
            adcerror = 0

            for event in tqdm(
                    iterable=dragonboard.EventGenerator(filename),
                    desc=os.path.basename(filename),
                    leave=True,
                    unit=" events"):
                stop_cell = event.header.stop_cells["low"][0]
                if stop_cell <= capno <= (stop_cell + event.roi):
                        # times_with_events[event.header.counter_133MHz / 133e6] = event[2][0][0][capno - stop_cell]
                    try:
                        t = event.header.counter_133MHz / 133e6
                    except:
                        timeerror += 1
                    try:
                        adc = int(event[2][0][0][capno - stop_cell])
                    except:
                        adcerror += 1
                    if isinstance( t, float ) and isinstance( adc, int ) == True:
                            time.append(t)
                            adc_counts.append(adc)
            # times = np.array(times)
            # delta_t_in_ms = np.diff(times)*1e3
            # print(delta_t_in_ms.mean())

            # plt.hist(delta_t_in_ms, bins=100, histtype="step")
            # plt.xlabel("time between consecutive events / ms")
            # plt.title(os.path.basename(filename))
            # plt.figure()
        except Exception as e:
            print(e)

    print(timeerror)
    print(adcerror)

    print(len(time))
    print(len(adc_counts))

if __name__ == '__main__':
    arguments = docopt(__doc__, version='Dragon Board Offset Calculation v.1.1')

    if not glob.glob(os.path.join(arguments["<inputdirectory>"], '*.dat')):
        sys.exit("Error: no files found to perform time-lapse calculation")

    timelapse_calc(arguments["<inputdirectory>"])
    plt.show()