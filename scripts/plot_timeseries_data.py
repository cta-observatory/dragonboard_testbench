'''
Plot mean and std for the files produced by scripts/timeseries_full.py
Save in a multipage pdf for each pixel / channel

Usage:
    plot_timeseries_data.py <inputfile> <outputfile>
'''
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages
from cycler import cycler
from docopt import docopt


if __name__ == '__main__':
    args = docopt(__doc__)

    plt.style.use('ggplot')
    plt.rcParams['axes.prop_cycle'] = cycler(
        color=["#DA573A", "#7A79D7", "#75C236", "#D252B9"]
    )

    df = pd.read_hdf(args['<inputfile>'])
    df.index.names = ('event', 'pixel', 'channel')
    df.reset_index(inplace=True)

    fig, (ax1, ax2) = plt.subplots(2, 1)

    with PdfPages(args['<outputfile>']) as pdf:

        for pixel in range(7):
            for channel in ('low', 'high'):

                ax1.cla()
                ax2.cla()
                ax1.set_title('{} {}'.format(pixel, channel))

                data = df.query('pixel == @pixel & channel == @channel')

                for key in filter(lambda x: '_std' in x, df.columns):

                    ax1.hist(
                        data[key].values,
                        bins=200,
                        range=(0, 40),
                        histtype='step',
                        label=key.split('_')[0],
                    )

                ax1.set_xlabel('Standard deviation of time series / adc counts')
                ax1.legend(loc='best')

                for key in filter(lambda x: '_mean' in x and 'NoCalibration' not in x, df.columns):

                    ax2.hist(
                        data[key].values,
                        bins=200,
                        range=(-20, 20),
                        histtype='step',
                        label=key.split('_')[0],
                    )

                ax2.legend(loc='best')
                ax2.set_xlabel('Mean of time series / adc counts')

                fig.tight_layout()
                pdf.savefig(fig)
