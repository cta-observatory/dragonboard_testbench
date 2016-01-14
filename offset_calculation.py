# 1 pedestal_file öffnen
# plotten?
# mittelwerte berechnen

import numpy as np
import matplotlib.pyplot as plt
from dragonboard import EventGenerator


def offset_calc(filename):
    with open(filename, "rb") as f:
        generator = EventGenerator(f, max_events=20)
        #event = next(generator)
        # plt.plot(event.data["low"][0])
        # plt.show()

        # declare events which is a list of all generator events
        events = list(generator)

        # read out list length
        numberofevents = len(events)

        # initialize an array full of nans. length = number of caps, width = number of events
        pedestalvalues = np.full((numberofevents, 4096), np.nan)

        #
        pixelindex = 0

        # build an array with numberofevents rows and 4096 columns. each event is then implemented into a big matrix
        for i in range(numberofevents):
            stopcell = events[i].header.stop_cells[pixelindex]
            roi = events[i].roi
            pedestalvalues[i][stopcell:stopcell + roi] = events[i].data["low"][pixelindex]

        # calculate and plot means
        plt.figure()
        plt.errorbar(
            np.arange(4096), 
            np.nanmean(pedestalvalues, axis=0),
            yerr=np.nanstd(pedestalvalues, axis=0),
            fmt="+",
            markersize=3,
            capsize=0,
        )
        plt.xlim(0,4096)      
        plt.show()

if __name__ == '__main__':
    offset_calc('Ped444706_1.dat')
