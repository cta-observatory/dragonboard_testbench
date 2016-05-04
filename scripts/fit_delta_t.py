'''
Usage:
    fit_delta_t.py <inputfile> <outputfile> [options]

Options:
    -n <n>, --n-jobs=<n>     How many threads to use [default: 1]
    -v <v>, --verbosity=<v>  Verbosity of joblib [default: 5]
'''
import pandas as pd
from scipy.optimize import curve_fit
from joblib import Parallel, delayed
import numpy as np
import logging
import os
import sys
from docopt import docopt

logging.basicConfig(level=logging.INFO)


def f(x, a, b, c):
    return a * x ** b + c


def fit(df, cell, plot=False):
    df = df[(5 <= df['sample']) & (df['sample'] < 35)]

    p0 = [
        1.3,
        -0.38,
        df.adc_counts[df.delta_t > 0.05].mean(),
    ]

    try:
        (a, b, c), cov = curve_fit(
            f,
            df['delta_t'],
            df['adc_counts'],
            p0=p0,
        )
    except RuntimeError:
        logging.error('Could not fit cell {}'.format(cell))
        return np.full(4, np.nan)

    ndf = len(df.index) - 3
    residuals = df['adc_counts'] - f(df['delta_t'], a, b, c)
    chisquare = np.sum(residuals**2) / ndf

    return a, b, c, chisquare


if __name__ == '__main__':
    args = docopt(__doc__)

    pool = Parallel(int(args['--n-jobs']), verbose=int(args['--verbosity']))
    ids = np.arange(4096)

    if os.path.isfile(args['<outputfile>']):
        answer = input('Outputfile exists, overwrite? (y / [n]): ')
        if not answer.lower().startswith('y'):
            sys.exit()

    with pd.HDFStore(args['<outputfile>'], 'w') as store:
        for pixel in range(8):
            for channel in ('low', 'high'):
                logging.info('%s  %s', pixel, channel)
                data = pd.read_hdf(
                    args['<inputfile>'],
                    'pixel_{}_{}'.format(pixel, channel)
                )

                by_cell = data.groupby('cell')
                result = pd.DataFrame(
                    pool(delayed(fit)(df, name) for name, df in by_cell),
                    columns=['a', 'b', 'c', 'chisq_ndf']
                )
                result['pixel'] = pixel
                result['channel'] = channel
                result['cell'] = ids

                store.append('data', result, min_itemsize={'channel': 4})
