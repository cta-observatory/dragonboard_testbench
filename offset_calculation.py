# programm calculates statistics (mean offsets) on the fly and creates a list with all data.

import numpy as np
import matplotlib.pyplot as plt
from dragonboard import EventGenerator # custom event generator
from dragonboard.runningstats import RunningStats # Max's method to do statistics on the fly 
from tqdm import tqdm # enable to show progress
import glob # enable to search for files in directories
import os

# calculate mean offset & RMS for every capacitor and plot the data.
def offset_calc(filename, pixelindex, gaintype):
    with open(filename, "rb") as f: # open a file and call it f. "rb": read, file is binary
        max_events = 10 # 1000 at all
        generator = EventGenerator(f, max_events=max_events) #, max_events=50) #  
        next(generator) # leave the first event as it is reasonably shifted to low caps
        
        # initialize stats array on which calculations are carried out
        stats = RunningStats(shape=4096)
   
        # give out pixelindex (= channel) and gaintype during calculation to maintain overview of progress
        print("channel %s, %s gain" % (pixelindex, gaintype))

        # calculate mean using Max's method
        for event in tqdm(generator, total=max_events):
        #for event in generator:
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
            # do actual calculation. data is added throughout the array starting at stop cell
            stats.add(np.roll(data, stop_cell[stop_cell_array_pos])) # that [1] is insane. how was it before? (FORMER VERSION!)
            
            # # assert a folder "offsets" where to save .csv's
            # if not os.path.exists("offsets"):
            #     os.makedirs("offsets")
            # # save data as .csv
            # #np.savetxt("/offsets",'offsets_{}_channel{}_{}-gain.csv'.format(filename, pixelindex, gaintype), np.column_stack([stats.mean, stats.std]), delimiter=',')       
            np.savetxt('offsets_{}_channel{}_{}-gain.csv'.format(filename, pixelindex, gaintype), np.column_stack([stats.mean, stats.std]), delimiter=',')

        # plot means with RMS
        plt.title("file: %s, channel %s, %s gain" %(filename, pixelindex, gaintype))
        plt.errorbar(
            np.arange(4096), 
            stats.mean,
            yerr=stats.std, # yerr = y-error bars
            fmt="+", # fmt means format
            markersize=3,
            capsize=1, # frame bars of error bars
        )
        plt.figure()
        # plt.xlim(0,4096)


if __name__ == '__main__':
    #path = "/home/mario/Programs/IP192.168.1.1/Pedestal/" # starts from current directory
    #for filename in glob.glob(os.path.join(path, '*.dat')):  
    for filename in glob.glob('*.dat'): # search for all .dat's in the current directory
        print("reading file: %s" % (filename))
        for pixelindex in range(1):
            offset_calc(filename, pixelindex, "low")
            offset_calc(filename, pixelindex, "high")
    plt.show()