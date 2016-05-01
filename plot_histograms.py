'''
plot histograms from cstc.h5 files

Usage:
  data_histo_datas.py <datafile> [options]
  data_histo_datas.py (-h | --help)
  data_histo_datas.py --version

Options:
  -h --help     Show this screen.
  --version     Show version.

'''

from tqdm import tqdm
import os
from docopt import docopt
# from collections import defaultdict
import numpy as np
# from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
np.set_printoptions(threshold=np.nan)
import glob
import pandas as pd
import time
import sys

def k(key):
    """ conversion method to ensure more intuitive data treatment """
    if key == "adc_counts":
        return 0
    if key == "cell":
        return 1
    if key == "delta_t":
        return 2
    if key == "sample":
        return 3
    else:
        sys.exit("Error: DataFrame only contains the keys: adc_counts, cell, delta_t, sample")

if __name__ == '__main__':
    arguments = docopt(
        __doc__, version='Dragon Board Time-Dependent Offset Calculation v.1.0'
    )
    datafile = arguments['<datafile>']

    pixel = 0
    gain = "low"

    df = pd.read_hdf(datafile, key="pixel_{}_{}".format(pixel, gain))
    
    num_bins = 201
    data = []
    for index, row in tqdm(df.iterrows()):
        if 5 <= row[k("sample")] <= 35:
            data.append(row[k("adc_counts")])
        if (index+1) % 100000 == 0:
            break

    plt.hist(data, num_bins, facecolor='blue')
    plt.show()