'''
Usage:
    plot_all_fit_results.py <inputfile> [options]

Options:
    -p, --plot              Show plots while fitting
'''
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from docopt import docopt
import os

if __name__ == '__main__':
    args = docopt(__doc__)

    inputfile = args["<inputfile>"]
    basename = inputfile.split("_")[-1][:-5]
    with pd.HDFStore(inputfile) as st:
        for pixel in range(7):
            for gain in ["low", "high"]:
                df = st["{}/{}".format(pixel, gain)]

                fig, axes = plt.subplots(2,2, figsize=(16, 12), sharex=True)
                df["a"].plot(ax=axes[0,0])
                df["b"].plot(ax=axes[0,1])
                df["c"].plot(ax=axes[1,0])
                df["chisq_ndf"].plot(ax=axes[1,1])
                axes[0,0].set_ylabel("a")
                axes[0,0].grid()
                axes[0,0].set_xlabel("cells")

                axes[0,1].set_ylabel("b")
                axes[0,1].grid()
                axes[0,1].set_xlabel("cells")

                axes[1,0].set_ylabel("c")
                axes[1,0].grid()
                axes[1,0].set_xlabel("cells")

                axes[1,1].set_ylabel("chisq_ndf")
                axes[1,1].grid()
                axes[1,1].set_xlabel("cells")


                plt.suptitle("fit results channel {} {}\n based on: {}".format(
                    pixel, gain, basename))
            
                plt.savefig('fit_results_png/{}_{}_{}.png'.format(pixel, gain, basename))
