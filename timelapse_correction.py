"""
#######################################################
*          Dragon board readout software              *
* calculate time-lapse dependence from pedestal files *
#######################################################

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
from scipy.optimize import curve_fit

def f(x, a, m, b):
    return a*x**m + b

def timelapse_calc(inputdirectory):
    """ calculate time lapse dependence for a given capacitor """

    glob_expression = os.path.join(inputdirectory, '*.dat')
    for filename in sorted(glob.glob(glob_expression)):
        try:
            cell_id = 2399
            gaintype = "low"
            pixelindex = 0

            time = []
            adc_counts = []
            rel_pos_in_roi = []

            for event in tqdm(
                    iterable=dragonboard.EventGenerator(filename),
                    desc=os.path.basename(filename),
                    leave=True,
                    unit=" events"):
                stop_cell = event.header.stop_cells[gaintype][pixelindex]
                if stop_cell <= cell_id < (stop_cell + event.roi):
                    sample_id = cell_id - stop_cell
                    if 0 < sample_id <= 40:
                        time.append(event.header.counter_133MHz)
                        adc_counts.append(int(event[2][pixelindex][gaintype][sample_id]))
                        rel_pos_in_roi.append(100 / event.roi * sample_id)
        except Exception as e:
            print(e)

    time_since_last_readout = np.diff(time) / 133e4
    parameters, covariance = curve_fit(f, time_since_last_readout, adc_counts[1:], maxfev=10000, p0=[1,-1,1])
    x_plot = np.linspace(np.amin(time_since_last_readout, axis=None, out=None, keepdims=False), np.amax(time_since_last_readout, axis=None, out=None, keepdims=False))
    print(parameters)
    
    plot = plt.scatter(time_since_last_readout, adc_counts[1:], c=rel_pos_in_roi[1:], cmap="rainbow", vmin=0, vmax=100)
    plt.plot(x_plot, f(x_plot, *parameters), "r-", label="Fit: f(x) = {} * x^{} + {}".format(round(parameters[0],2),round(parameters[1],2),round(parameters[2],2)), linewidth=3)
    plt.xlabel("time between consecutive events / ms")
    plt.ylabel("ADC counts")
    plt.xscale("log")
    plt.title("Time dependence: cell_id {} @ {} {} ({})\n".format(cell_id, pixelindex, gaintype, os.path.basename(filename)))
    colorbar = plt.colorbar(plot)
    colorbar.set_label("relative position of sample_id in roi / %")
    plt.legend(loc="best")

if __name__ == '__main__':
    arguments = docopt(__doc__, version='Dragon Board Time-Dependent Offset Calculation v.1.0')

    if not glob.glob(os.path.join(arguments["<inputdirectory>"], '*.dat')):
        sys.exit("Error: no file(s) found to perform time-lapse calculation")

    timelapse_calc(arguments["<inputdirectory>"])
    plt.show()