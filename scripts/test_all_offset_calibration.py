'''
Usage:
    test_all_offset_calibration.py <inputfile> <calibfile>[options]

Options:
    -p, --plot              Show plots while fitting
    -n <n>, --n-jobs=<n>    How many threads to use [default: 1]
'''
import pandas as pd
from scipy.optimize import curve_fit
from joblib import Parallel, delayed
import numpy as np
import matplotlib.pyplot as plt
import logging
from docopt import docopt
import os

fig = None
x = np.logspace(-4, 0, 250)


def f(x, a, b, c):
    return a * x ** b + c


def test(df, cell, fit_results):
    df = df[df["sample"] < 38]

    fr = fit_results.iloc[cell]
    offset = f(
        x=df.delta_t,
        a=fr.a,
        b=fr.b,
        c=fr.c,
        )

    calibrated = df.adc_counts - offset

    m = calibrated.mean()
    s = calibrated.std()
    n = len(calibrated)
    return m, s, n


if __name__ == '__main__':
    args = docopt(__doc__)

    input_number = int(os.path.basename(args["<inputfile>"]).split(".")[0][-1])
    calib_number = int(os.path.basename(args["<calibfile>"]).split(".")[0][-1])

    with pd.HDFStore(args["<calibfile>"]) as st:

        for pixel in range(7):
            for gain in ["low", "high"]:

                data = pd.read_hdf(args['<inputfile>'], 'pixel_{}_{}'.format(pixel, gain))

                by_cell = data.groupby('cell')

                fit_results = st['{}/{}'.format(pixel, gain)]

                with Parallel(int(args['--n-jobs']), verbose=5) as pool:
                    result = pd.DataFrame(
                        pool(delayed(test)(df, name, fit_results) for name, df in by_cell),
                        columns=['mean', 'std', 'N']
                    )

                result.to_hdf(
                    'test_results_in{}_calib{}.hdf5'.format(input_number, calib_number),
                    '{}/{}'.format(pixel, gain)
                )
