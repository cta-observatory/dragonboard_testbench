""" Plot Dragon Board Raw

Show drag data interactively. Just click on the plotting canvas to
see the next event.


Usage:
  crosstalk_study.py <folder>  
  crosstalk_study.py (-h | --help)
  crosstalk_study.py --version

Options:
  -h --help     Show this screen.
  --version     Show version.

"""

import numpy as np
import os
from dragonboard import EventGenerator
from dragonboard.io import get_roi,guess_event_size,num_channels,num_gains,max_roi
from docopt import docopt
import matplotlib.pyplot as plt
import pprint

def calculatedIntegral(data,posMax,intWindow=3):
    slices = np.arange(posMax-intWindow,posMax+intWindow+1)
    print posMax
    print slices
    integral = 0
    for sl in slices:
        integral += data[sl]
    return integral

def find_max_amplitude(data,min,max):
    pos = np.argmax(data[min:max])+min
    maxAmplitude = data[pos-min]
    return pos,maxAmplitude

def estimateBaseline(data,min=0,max=20):
    baseline = np.mean(data[min:max])
    return baseline

def main():
    arguments = docopt(__doc__, version='Dragon Data Browser 0.1alpha')
    leftWindow=20
    rightWindow=20
    folder = arguments["<folder>"]

    fig_matrix = dict()
    ax_matrix = dict()
    fig_matrix["low"],ax_matrix["low"] = plt.subplots(1,1,figsize=(20,20))
    fig_matrix["high"],ax_matrix["high"] = plt.subplots(1,1,figsize=(20,20))

    fig_averaged = dict()
    axes_averaged = dict()
    fig_averaged["low"], axes_averaged["low"] = plt.subplots(8,8,figsize=(20,20))
    fig_averaged["high"], axes_averaged["high"] = plt.subplots(8,8,figsize=(20,20))

    for gainChannel in ["high","low"]:
        if gainChannel == "high":
            fileChar = "L"
        elif gainChannel == "low":
            fileChar = "H"
        crosstalkRatio = np.zeros((num_channels,num_channels))

        for pulsePixel in range(num_channels-1):
            filepath = os.path.join(folder,"CtCh{}{}.dat".format(pulsePixel,fileChar))
            print filepath
            with open(filepath, "rb") as f:
                averagedShiftedData = np.zeros((num_channels,rightWindow+leftWindow))
                generator = EventGenerator(f)
                num_events = 0

                for event in generator:
                    num_events += 1
                    pulsePos, pulseMax = find_max_amplitude(event.data[gainChannel][pulsePixel],20,75)
                    xvalues = np.arange(pulsePos - leftWindow,pulsePos+rightWindow)

                    for pix in range(num_channels):
                        data = event.data[gainChannel][pix]
                        averagedShiftedData[pix][:] += data[xvalues]
                for pix in range(num_channels):
                    averagedShiftedData[pix] /= num_events
                    baseline = estimateBaseline(averagedShiftedData[pix],0,13)
                    averagedShiftedData[pix] -= baseline

                xvalues = np.arange(-leftWindow,rightWindow)
                pos,maxAmplitudeReference = find_max_amplitude(averagedShiftedData[pulsePixel],0,40)

                fig_averaged[gainChannel].suptitle("{} gain".format(gainChannel))
                for pix in range(num_channels):
                    pos, crosstalkRatio[pulsePixel][pix] = find_max_amplitude(averagedShiftedData[pix],0,40)
                    crosstalkRatio[pulsePixel][pix] /= maxAmplitudeReference
                    crosstalkRatio[pulsePixel][pix] *= 100.0
                    # print("Crosstalk ratio pixel: {} = {}".format(pix,crosstalkRatio[pix]))
                    axes_averaged[gainChannel][pulsePixel][pix].plot(xvalues,averagedShiftedData[pix],label='Pixel: {}'.format(pix))
                    axes_averaged[gainChannel][pulsePixel][pix].set_ylim(-70,70)
                    axes_averaged[gainChannel][pulsePixel][pix].set_title("{} gain, pulse: {}, pix: {}".format(gainChannel,pulsePixel,pix))

                # plt.legend()
                # plt.show()
        pprint.pprint(crosstalkRatio)
        matshowPlot = ax_matrix[gainChannel].matshow(crosstalkRatio,cmap='hot',vmax=5)
        plt.colorbar(matshowPlot,ax = ax_matrix[gainChannel],label="crosstalk / %")
        ax_matrix[gainChannel].set_ylabel("pixel with injected pulse")
        ax_matrix[gainChannel].set_xlabel("crosstalk pixel")
        ax_matrix[gainChannel].set_title("Crosstalk for {} channel".format(gainChannel))
        # fig_matrix[gainChannel].show()
    plt.show()


if __name__ == '__main__':
    main()
