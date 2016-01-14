# programm calculates statistics (mean offsets) on the fly and creates a list with all data.
# all channes and low/gain has to be implemented!

import numpy as np
import matplotlib.pyplot as plt
from dragonboard import EventGenerator # custom event generator
from dragonboard.runningstats import RunningStats # Max's method to do statistics on the fly 
from tqdm import tqdm # enable to show progress

def offset_calc(filename):
    with open(filename, "rb") as f: # open a file and call it f. "rb": read, file is binary
        generator = EventGenerator(f) #, max_events=50) #  
        next(generator) # leave the first event as it is reasonably shifted to low caps

        # 
        stats = RunningStats(shape=4096)

        # define a pixel index.
        pixelindex = 0

        # build an array with 4096 columns. calculate mean using Max's method
        for event in tqdm(generator):
            data = np.full(4096, np.nan)
            stop_cell = event.header.stop_cells[pixelindex]
            roi = event.roi
            data[:roi] = event.data["low"][pixelindex]
            stats.add(np.roll(data, stop_cell))

        np.savetxt('offsets.csv', np.column_stack([stats.mean, stats.std]), delimiter=',')

        # plot means
        plt.figure()
        plt.errorbar(
            np.arange(4096), 
            stats.mean,
            yerr=stats.std, # yerr = y-error bars
            fmt="+", # fmt means format
            markersize=3,
            capsize=0, # frame bars of error bars
        )
        # plt.xlim(0,4096)      
        plt.show()

if __name__ == '__main__':
    offset_calc('Ped444706_1.dat')