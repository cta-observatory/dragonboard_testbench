'''
Usage:
    plot_chisq.py <inputfile> <outputfile>
'''

from docopt import docopt
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np

plt.style.use('ggplot')


if __name__ == '__main__':

    args = docopt(__doc__)
    data = pd.read_hdf(args['<inputfile>'])

    data = data.query('pixel != 7').copy()
    max_chisq = data.chisq_ndf.max()

    with PdfPages(args['<outputfile>']) as pdf:

        for (channel, pixel), df in data.groupby(['channel', 'pixel']):
            fig = plt.figure()
            ax = fig.add_subplot(1, 1, 1)

            ax.plot(np.arange(4096), df.chisq_ndf, linewidth=0.5)
            ax.set_title('Pixel: {}, Channel: {}'.format(pixel, channel))

            ax.set_xlabel('cell id')
            ax.set_ylabel('$\chi^2 / \mathrm{n.d.f.}$')

            ax.set_xticks(np.arange(0, 4097, 1024))
            ax.set_xticks(np.arange(0, 4097, 128), minor=True)

            ax.set_xlim(-5, 4100)
            ax.set_ylim(0, 80)

            fig.tight_layout()
            pdf.savefig(fig)
