'''
Usage:
    plot_all_fit_results.py <inputfile> [options]

Options:
    --outdir P             path where to store output [default: timelapse_fit_results/png]
'''
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from docopt import docopt
import os
from dragonboard.calibration import read_calib_constants

if __name__ == '__main__':
    args = docopt(__doc__)
    outdir = args["--outdir"]
    os.makedirs(outdir, exist_ok=True)

    calib_constants = read_calib_constants(args["<inputfile>"])
    basename = os.path.basename(args["<inputfile>"])
    for pixel in range(7):
        for gain in ["low", "high"]:

            df = calib_constants.loc[pixel, gain]

            fig, axes = plt.subplots(2,2, figsize=(12, 9), sharex=True)
            
            for i, (name, limits) in enumerate([
                ("a", (0, 10)),
                ("b", (-1, 0)),
                ("c", (100, 400)),
                ("chisq_ndf", (0, 40)),
            ]):
                ax = axes.flatten()[i]
                ax.plot(df[name], '.')
                ax.set_ylabel(name)
                ax.grid()
                ax.set_xlabel("cells")
                ax.set_ylim(*limits)

            plt.suptitle("fit results channel {} {}\n based on: {}".format(
                pixel, gain, basename))

            outpath = os.path.join(outdir, '{}_{}_{}.png'.format(
                pixel, gain, basename)
            )
            plt.savefig(outpath)
            plt.close("all")
