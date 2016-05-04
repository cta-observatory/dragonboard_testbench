"""
Usage:
  plot_cstc_overview.py <cstcfiles>... [options]

  --outdir PATH     output directory [default: ./timelapse_data/cstc_overview]
"""

from docopt import docopt
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from mpl_toolkits.axes_grid1 import make_axes_locatable

import os


def main(cstcfile, args):
    st = pd.HDFStore(cstcfile)
    keys = st.keys()[:-2] # ignore channel 7
    N = len(keys)
    fig, axes = plt.subplots(N,2, figsize=(12, 6*N))
    for i,n in enumerate(keys):
        df = st[n]
        
        m = df.groupby(["cell", "sample"]).mean()
        s = df.groupby(["cell", "sample"]).std()
        
        m2d = m["adc_counts"].values.reshape(-1, 40)
        s2d = s["adc_counts"].values.reshape(-1, 40)

        plots = {
            "mean":{
                "data":m2d,
                "ax_id":0,
                "vmax":20,
                "vmin":-5,
            },
            "std_dev":{
                "data":s2d,
                "ax_id":1,
                "vmax":30,
                "vmin":0,
            },
        }
        cax_labels = ["mean", "std dev"]
        v_limits = []
        for plot_name in plots:
            plot=plots[plot_name]
            ax = axes[i, plot["ax_id"]]
            im = ax.imshow(
                plot["data"], 
                cmap="viridis", 
                aspect="auto", 
                interpolation="nearest",
                vmin=plot["vmin"],
                vmax=plot["vmax"],
            )
            divider = make_axes_locatable(ax)
            cax = divider.append_axes("right", size="5%", pad=0.05)
            plt.colorbar(im, cax=cax)
            ax.set_xlabel("sample")
            ax.set_ylabel("cell")
            ax.set_title(n)
            cax.set_ylabel(plot_name+" adc count")
    
    outpath = os.path.join(
        args["--outdir"],
        os.path.basename(cstcfile)+".png"
        )
    plt.savefig(outpath)


if __name__ == "__main__":
    args = docopt(__doc__)
    print(args)

    args["--outdir"] = os.path.abspath(args["--outdir"])
    os.makedirs(args["--outdir"], exist_ok=True)
    
    for cstcfile in args["<cstcfiles>"]:
        main(cstcfile, args)