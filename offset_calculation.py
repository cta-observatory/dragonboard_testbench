"""
##########################################################
* calculate offset constants and RMS from pedestal files *
##########################################################

annotations:

- filedirectory is the path to the directory of your pedestal files
- outputdirectory is the directory where the calibration constants are written to


Usage:
  offset_calculation.py <filedirectory> <outputdirectory>
  offset_calculation.py (-h | --help)
  offset_calculation.py --version

Options:
  -h --help     Show this screen.
  --version     Show version.

"""

import numpy as np
import matplotlib.pyplot as plt
from dragonboard import EventGenerator # custom event generator
from dragonboard.runningstats import RunningStats # Max's method to do statistics on the fly 
from tqdm import tqdm # enable to show progress
import glob # enable to search for files in directories
import os
from docopt import docopt # write your own menu! furthermore control terminal input parameters


def offset_calc(filedirectory, outputdirectory, pixelindex, gaintype):
    """ calculate mean offset & RMS for every capacitor and plot the data. the data is saved as .csv files.
        The .csv files are named offsets_channel<pixelindex>_<gaintype>-gain. 
        this FORMAT MUST NOT BE CHANGED
    """

    stats = RunningStats(shape=4096) # initialize stats array on which calculations are carried out

    for filename in glob.glob(os.path.join(filedirectory, 'Ped*.dat')): # search for all .dat's in the current directory

        with open(filename, "rb") as f: # open a file and call it f. "rb": read, file is binary

            max_events = 1000 # 1000 at all
            generator = EventGenerator(f, max_events=max_events) 
            next(generator) # leave the first event as it is reasonably shifted to low caps
            
            # give out pixelindex (= channel) and gaintype during calculation to maintain overview of progress
            print("reading file: %s, channel %s, %s gain" % (filename, pixelindex, gaintype))

            # calculate mean using Max's method
            for event in tqdm(generator, total=max_events):
                data = np.full(4096, np.nan)
                stop_cell = event.header.stop_cells[pixelindex]
                #print(stop_cell) 
                roi = event.roi
                data[:roi] = event.data[gaintype][pixelindex]

                # assert correct stop cell. Assumed for the if-structure: stop cells(sc) are arranged in array [(channel0_sc_low, channel0_sc_high), ..., (channel7_sc_low), channel7_sc_high)]
                if gaintype == "low":
                    stop_cell_array_pos = 0
                else:
                    stop_cell_array_pos = 1

                # data is added throughout the array starting at stop cell
                stats.add(np.roll(data, stop_cell[stop_cell_array_pos])) # that [...] is insane. how was it before?



    # save means and RMS's of data as .csv in declared directory
    np.savetxt(
        '{}offsets_channel{}_{}-gain.csv'.format(outputdirectory, pixelindex, gaintype), 
        np.column_stack([stats.mean, stats.std]), delimiter=','
    )

    # plot means with RMS
    plt.title("channel %s, %s gain" %(pixelindex, gaintype))
    plt.errorbar(
        np.arange(4096),
        stats.mean,
        yerr=stats.std, # yerr = y-error bars
        fmt="+", # fmt means format
        markersize=3,
        capsize=1, # frame bars of error bars
    )
    plt.xlim(0,4096)
    plt.figure()

# def scan_file_amount(filedirectory):
#     for filename in glob.glob(os.path.join(filedirectory, 'Ped*.dat')):
#         list(filename)
#     print("found {} files to perform calibration" % (list(filename))

if __name__ == '__main__':

    # docopt arguments
    arguments = docopt(__doc__, version='YEAH!')
    filedirectory = arguments["<filedirectory>"]
    outputdirectory = arguments["<outputdirectory>"]

    # calculation
    for pixelindex in range(1): # max range = number of channels
        for gaintype in ["low", "high"]:
            offset_calc(filedirectory, outputdirectory, pixelindex, gaintype)

    plt.show()