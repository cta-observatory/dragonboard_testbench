'''
Usage:
  calc_timelapse_constants <outputfile> <inputfiles> ... [options]

Options:
  --max_events N    integer; maximum events to be used from a file. default is all.
  --skip_begin N    integer; number of start-samples to be skipped for fitting [default: 5]
  --skip_end N      integer; number of end-samples to be skipped for fitting [default: 5]
  --do_channel8     fit also channel 8 values
'''

import os
import sys
import psutil
import logging
from tqdm import tqdm
from docopt import docopt

from joblib import Parallel, delayed

import numpy as np

import pandas as pd

import scipy.sparse
from scipy.sparse import lil_matrix, coo_matrix
from scipy.optimize import curve_fit

import dragonboard as dr

logging.basicConfig(level=logging.DEBUG)


from array import array

def f(x, a, b, c):
    return a * x ** b + c


def fit(adc, delta_t, cell):
    a0 = 1.3
    b0 = -0.38
    c0 = 0

    if not len(adc):
        return a0, b0, c0, np.nan

    big_time = np.percentile(delta_t, 75)
    p0 = [
        1.3,
        -0.38,
        adc[delta_t >= big_time].mean(),
    ]
    try:
        (a, b, c), cov = curve_fit(
            f,
            delta_t,
            adc,
            p0=p0,
        )
    except (RuntimeError, TypeError):
        logging.error('Could not fit cell {}'.format(cell))
        return p0[0], p0[1], p0[2], np.nan

    ndf = len(adc) - 3
    residuals = adc - f(delta_t, a, b, c)
    chisquare = np.sum(residuals**2) / ndf

    return a, b, c, chisquare

def main():
    args = docopt(__doc__)
    args["--max_events"] = None if args["--max_events"] is None else int(args["--max_events"])
    args["--skip_begin"] = int(args["--skip_begin"])
    args["--skip_end"] = int(args["--skip_end"])
    args["--do_channel8"] = bool(args["--do_channel8"])
    print(args['<outputfile>'])
    if os.path.isfile(args['<outputfile>']):
        answer = input('Outputfile {} exists. Do you want to overwrite? y/[n] '.format(args['<outputfile>']))
        if not answer.lower().startswith('y'):
            sys.exit()


    store = pd.HDFStore(args['<outputfile>'], 'w')



    adc = {}
    delta_t = {}
    for pixel in range(8 if args["--do_channel8"] else 7):
        for gain in ["high", "low"]:
            adc[pixel, gain] = [array('H') for i in range(4096)]
            delta_t[pixel, gain] = [array('f') for i in range(4096)]
    if not args["--do_channel8"]:
        # We need to put nans for channel 8 into the output file, since the
        # rest of the system expects this data to be there ... even if it its nan.
        result = pd.DataFrame( np.full((4096, 4), np.nan),
            columns=['a', 'b', 'c', 'chisq_ndf']
        )
        result['pixel'] = 7
        result['channel'] = "high"
        result['cell'] = np.arange(4096)
        store.append('data', result, min_itemsize={'channel': 4})

        result['channel'] = "low"
        store.append('data', result, min_itemsize={'channel': 4})

    print("reading raw file(s) into memory:")
    for eg in [dr.EventGenerator(filename, max_events=args["--max_events"]) for filename in args["<inputfiles>"]]:
        sample_ids = np.arange(eg.roi)

        for event in tqdm(
                iterable=eg,
                desc=os.path.basename(eg.path),
                leave=True,
                unit=' events',
                ):

            for pixel, gain in sorted(adc.keys()):
                sc = event.header.stop_cells[pixel][gain]
                skip_slice = slice(args["--skip_begin"], -args["--skip_end"])
                cell_ids = dr.sample2cell(sample_ids, sc)[skip_slice]
                data = event.data[pixel][gain][skip_slice]
                delta_ts = event.time_since_last_readout[pixel][gain][skip_slice]
                for i, cid in enumerate(cell_ids):
                    delta_t[pixel, gain][cid].append(delta_ts[i])
                    adc[pixel, gain][cid].append(data[i])

    for key in sorted(adc.keys()):
        # adc and delta_t have the same keys
        for i in tqdm(range(4096), desc=str(key)):
            adc[key][i] = np.array(adc[key][i], dtype=adc[key][i].typecode)
            delta_t[key][i] = np.array(delta_t[key][i], dtype=delta_t[key][i].typecode)

            adc[key][i] = adc[key][i][~np.isnan(delta_t[key][i])]
            delta_t[key][i] = delta_t[key][i][~np.isnan(delta_t[key][i])]


    print("fitting")
    pool = Parallel(max(psutil.cpu_count()-1, 1))
    for key in tqdm(iterable=sorted(adc.keys()), leave=True):
        result = pd.DataFrame(
            pool(delayed(fit)(adc[key][i], delta_t[key][i], i) for i in range(4096)),
            columns=['a', 'b', 'c', 'chisq_ndf']
        )
        pixel, channel = key
        result['pixel'] = pixel
        result['channel'] = channel
        result['cell'] = np.arange(4096)

        store.append('data', result, min_itemsize={'channel': 4})

if __name__ == '__main__':
    main()
