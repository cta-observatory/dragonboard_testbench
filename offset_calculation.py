# programm calculates statistics (mean offsets) on the fly and creates a list with all data.

import numpy as np
import matplotlib.pyplot as plt
from dragonboard import EventGenerator # custom event generator
from dragonboard.runningstats import RunningStats # Max's method to do statistics on the fly 
from tqdm import tqdm # enable to show progress
import glob # enable to search for files in directories
import os


def offset_calc(pixelindex, gaintype):
    """ calculate mean offset & RMS for every capacitor and plot the data. the data is saved as .csv files in
        a subdirectory ("offsets" by default). the .csv files are named offsets_channel<pixelindex>_<gaintype>-gain. 
        this format MUST NOT BE CHANGED """

    stats = RunningStats(shape=4096) # initialize stats array on which calculations are carried out

    for filename in glob.glob('Ped*.dat'): # search for all .dat's in the current directory

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




def save_data_to(output_folder_name): # written while seen from the current executing directory
    """ creates an output folder "output_folder_name" if not existent. save all generated data to this folder """

    # assert a folder "output_folder_name" where to save .csv's
    if not os.path.exists(output_folder_name):
        os.makedirs(output_folder_name)

    # declare an output directory to save the processed data
    output_directory = os.getcwd() + "/" + output_folder_name + "/" # creates a/path/to/your/files/output_folder_name
    #print(output_directory)

    return output_directory




def apply_offset_calibration(filename, pixelindex, gaintype):
    """ applies the offset calibration for a given filename, pixelindex and gaintype. returns calibrated_data.
        apply_offset_calibration reads the calibration constants from .csv files in its subdirectory ("offsets" by default) """

    offset_directory = os.getcwd() + "/offsets/" + "offsets_channel" + str(pixelindex) + "_" + gaintype + "-gain.csv" # assumed e.g. "offsets_channel0_low-gain.csv"
    offset, rms = np.loadtxt(offset_directory, delimiter=",", usecols=(0, 1), unpack=True) # read every column of the .csv as each an array offset and rms. method's options are important!
    # give out pixelindex (= channel) and gaintype during calculation to maintain overview of progress        
    print("calibrating file: %s, channel %s, %s gain" % (filename, pixelindex, gaintype))    
    #print(filename)
    #print(offset)
    #print(rms)

    with open(filename, "rb") as f: # open a file and call it f. "rb": read, file is binary

        max_events = 100 # number of max_events depends on input file
        generator = EventGenerator(f, max_events=max_events)
        #print(generator)

        # switch to the max_events-1'th event to apply the offset calibration
        for event_number in tqdm(range(max_events-1),total=max_events):  # try/catch might be good in case of excess
            next(generator) # go to next event. crashes if exceeding max_events

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

        #print(event)

        # data is subtracted throughout the array starting at stop cell
        calibrated_data = np.subtract(np.roll(data, stop_cell[stop_cell_array_pos]), offset) # that [...] is insane. how was it before?

    # plot of raw data
    plt.xlabel('time slice / DRS4 cell')
    plt.ylabel('ADC counts')
    plt.axis([60,180,-100,350]) # ([xmin, xmax, ymin, ymax]), before any figure() or show() command!
    plt.title("%s, channel %s, %s gain" %(filename, pixelindex, gaintype))
    plt.step(np.roll(data, stop_cell[stop_cell_array_pos]), ":",label="raw data")
    plt.legend()
    plt.figure()

    # plot of raw and calibrated data
    plt.xlabel('time slice / DRS4 cell')
    plt.ylabel('ADC counts')
    plt.axis([60,180,-100,350]) # ([xmin, xmax, ymin, ymax]), before any figure() or show() command!
    plt.title("%s, channel %s, %s gain" %(filename, pixelindex, gaintype))
    plt.step(np.roll(data, stop_cell[stop_cell_array_pos]), ":",label="raw data")
    plt.step(calibrated_data, "r:",label="calibrated data")
    plt.legend()    
    plt.figure()

    return calibrated_data

    # # plot calibrated data
    # plt.title("raw data: %s, channel %s, %s gain" %(filename, pixelindex, gaintype))
    # plt.errorbar(
    #     np.arange(4096),
    #     np.roll(data, stop_cell[stop_cell_array_pos]),
    #     yerr=rms, # yerr = y-error bars
    #     fmt="o:", # fmt means format
    #     markersize=3,
    #     capsize=1, # frame bars of error bars
    # )
    # #plt.axis([60,180,-100,350]) # ([xmin, xmax, ymin, ymax]), before any figure() or show() command!
    # plt.figure()
    

    # # plot calibrated data
    # plt.title("calibrated data: %s, channel %s, %s gain" %(filename, pixelindex, gaintype))
    # plt.errorbar(
    #     np.arange(4096),
    #     calibrated_data,
    #     yerr=rms, # yerr = y-error bars
    #     fmt="ro:", # fmt means format
    #     markersize=3,
    #     capsize=1, # frame bars of error bars
    # )
    # #plt.axis([60,180,-100,350])



if __name__ == '__main__':
    # for pixelindex in range(8): # max range = number of channels
    #     for gaintype in ["low", "high"]:
    #         offset_calc(pixelindex, gaintype)

    #apply_offset_calibration("Ped444442_1.dat", 0, "low")
    #apply_offset_calibration("Ped444442_67.dat", 0, "low")
    apply_offset_calibration("TPGain40.dat", 1, "low")
    #print(apply_offset_calibration("TPGain40.dat", 1, "low")
    #apply_offset_calibration("CtCh0L.dat", 0, "low")

    plt.show()