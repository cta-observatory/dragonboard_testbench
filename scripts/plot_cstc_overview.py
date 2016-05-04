'''
Usage:
  plot_cstc_overview.py <cstcfiles>... [options]

  --outdir PATH     output directory [default: ./timelapse_data/cstc_overview]
'''

from docopt import docopt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import pandas as pd
from mpl_toolkits.axes_grid1 import make_axes_locatable

import os


def main(cstcfile, args):
    st = pd.HDFStore(cstcfile)
    keys = st.keys()[:-2]  # ignore channel 7

    name, ext = os.path.splitext(cstcfile)

    with PdfPages(name + '.pdf') as pdf:
        fig, axes = plt.subplots(1, 2, figsize=(12, 6))
        for i, n in enumerate(keys):
            df = st[n]

            m = df.groupby(['cell', 'sample']).mean()
            s = df.groupby(['cell', 'sample']).std()

            m2d = m['adc_counts'].values.reshape(-1, 40)
            s2d = s['adc_counts'].values.reshape(-1, 40)

            plots = {
                'mean': {
                    'data': m2d,
                    'ax_id': 0,
                    'vmax': 15,
                    'vmin': -15,
                    'cmap': 'RdBu_r',

                },
                'std_dev': {
                    'data': s2d,
                    'ax_id': 1,
                    'vmax': 30,
                    'vmin': 0,
                    'cmap': 'viridis',
                },
            }
            for plot_name, plot in plots.items():
                ax = axes[plot['ax_id']]
                ax.cla()
                im = ax.imshow(
                    plot['data'],
                    cmap=plot['cmap'],
                    aspect='auto',
                    interpolation='nearest',
                    vmin=plot['vmin'],
                    vmax=plot['vmax'],
                )
                divider = make_axes_locatable(ax)
                cax = divider.append_axes('right', size='5%', pad=0.05)
                cb = fig.colorbar(im, cax=cax)
                cb.set_label(plot_name + ' adc count')
                ax.set_xlabel('sample')
                ax.set_ylabel('cell')
                ax.set_title(n)

            fig.tight_layout()
            pdf.savefig(fig)


if __name__ == '__main__':
    args = docopt(__doc__)
    print(args)

    args['--outdir'] = os.path.abspath(args['--outdir'])
    os.makedirs(args['--outdir'], exist_ok=True)

    for cstcfile in args['<cstcfiles>']:
        main(cstcfile, args)
