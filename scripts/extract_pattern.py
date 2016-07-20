'''
Calculate the remaining offset in the first ten slices
after TimeLapseCalibration.

Usage:
    extract_pattern <cstc_file> <outputfile>
'''
import pandas as pd
from tqdm import tqdm
from docopt import docopt


if __name__ == '__main__':
    args = docopt(__doc__)

    with pd.HDFStore(args['<outputfile>'], 'w') as store:
        with tqdm(total=14) as pbar:
            for pixel in range(7):
                for channel in ('low', 'high'):

                    df = pd.read_hdf(
                        args['<cstc_file>'],
                        'pixel_{}_{}'.format(pixel, channel)
                    )
                    df = df[df['sample'] <= 10]

                    mean = df.groupby(['cell', 'sample'])['adc_counts'].mean()

                    store.append('pixel_{}_{}'.format(pixel, channel), mean)
                    pbar.update(1)
