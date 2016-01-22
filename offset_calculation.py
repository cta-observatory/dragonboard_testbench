# programm calculates statistics (mean offsets) on the fly and creates a list with all data.

import numpy as np
import matplotlib.pyplot as plt
from dragonboard import EventGenerator # custom event generator
from dragonboard.runningstats import RunningStats # Max's method to do statistics on the fly 
from tqdm import tqdm # enable to show progress
import glob # enable to search for files in directories
import os

# calculate mean offset & RMS for every capacitor and plot the data.
def offset_calc(pixelindex, gaintype):

    # initialize stats array on which calculations are carried out
    stats = RunningStats(shape=4096)

    for filename in glob.glob('*.dat'): # search for all .dat's in the current directory

        with open(filename, "rb") as f: # open a file and call it f. "rb": read, file is binary

            max_events = 10 # 1000 at all
            generator = EventGenerator(f, max_events=max_events) #, max_events=50) #  
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
        '{}offsets_channel{}_{}-gain.csv'.format(save_data_to("offsets"), pixelindex, gaintype), 
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
    plt.figure()
    # plt.xlim(0,4096)

# create an output folder if not existent. save all generated data to this folder.
def save_data_to(output_folder_name): # written while seen from the current executing directory

    # assert a folder "output_folder_name" where to save .csv's
    if not os.path.exists(output_folder_name):
        os.makedirs(output_folder_name)

    # declare an output directory to save the processed data
    output_directory = os.getcwd() + "/" + output_folder_name + "/" # creates a/path/to/your/files/output_folder_name
    #print(output_directory)

    return output_directory




def offset_apply(csv_filename):
    offset, rms = np.loadtxt(csv_filename, delimiter=",", usecols=(0, 1), unpack=True) # read every column of the .csv as each an array offset and rms. method's options are important!
    #print(filename)
    #print(offset)
    #print(rms)
    # initialize stats array on which calculations are carried out
    stats = RunningStats(shape=4096)

    #for filename in glob.glob('*.dat'): # search for all .dat's in the current directory
    for filename in glob.glob('Ped444442_1.dat'): # search for all .dat's in the current directory

        with open(filename, "rb") as f: # open a file and call it f. "rb": read, file is binary

            max_events = 1 # 1000 at all
            generator = EventGenerator(f, max_events=max_events) #, max_events=50) #  
            #next(generator) # leave the first event as it is reasonably shifted to low caps
            
            # give out pixelindex (= channel) and gaintype during calculation to maintain overview of progress
            print("calibrating file: %s, channel %s, %s gain" % (filename, pixelindex, gaintype))

            # calculate mean using Max's method
            for event in tqdm(generator, total=max_events):
                #print(event)
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

                # data is subtracted throughout the array starting at stop cell
                calibrated_data = np.subtract(np.roll(data, stop_cell[stop_cell_array_pos]), offset) # that [...] is insane. how was it before?

                # plot calibrated data
                plt.title("uncalibrated data: channel %s, %s gain" %(pixelindex, gaintype))
                plt.errorbar(
                    np.arange(4096),
                    np.roll(data, stop_cell[stop_cell_array_pos]),
                    yerr=rms, # yerr = y-error bars
                    fmt="+", # fmt means format
                    markersize=3,
                    capsize=1, # frame bars of error bars
                )
                plt.figure()

                # plot calibrated data
                plt.title("calibrated data: channel %s, %s gain" %(pixelindex, gaintype))
                plt.errorbar(
                    np.arange(4096),
                    calibrated_data,
                    yerr=rms, # yerr = y-error bars
                    fmt="+", # fmt means format
                    markersize=3,
                    capsize=1, # frame bars of error bars
                )



if __name__ == '__main__':
    # for pixelindex in range(1): # max range = number of channels
    #     for gaintype in ["low"]: #, "high"]:
    #         offset_calc(pixelindex, gaintype)

    for pixelindex in range(1): # max range = number of channels
        for gaintype in ["low"]: #, "high"]:
            #offset_calc(pixelindex, gaintype)
            for csv_filename in glob.glob('*.csv'):
                offset_apply(csv_filename)

    plt.show()