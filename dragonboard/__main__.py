'''
Usage:
    dragonviewer [<inputfile>] [options]

Options:
    -c <calibfile>   File containing the calibration constants
    -e <extrafile>   File containing the extra offset constants
    --start=<N>      First event to show
'''
import matplotlib
import matplotlib.style
matplotlib.use('Qt5Agg')
import sys
import signal
from docopt import docopt
from .plotting import DragonBrowser

from PyQt5 import QtWidgets
from PyQt5 import QtCore


def sigint_handler(*args):
    sys.stderr.write('\rReceived SIGINT, terminating\n')
    QtWidgets.QApplication.instance().quit()


def main():
    try:
        matplotlib.style.use('ggplot')
    except NameError:
        pass
    args = docopt(__doc__)
    qApp = QtWidgets.QApplication(sys.argv)
    signal.signal(signal.SIGINT, sigint_handler)

    widget = DragonBrowser(
        args['<inputfile>'],
        args['-c'],
        args['-e'],
        int(args['--start']) if args['--start'] else None,
    )
    widget.show()

    # let the QApplication process signals from the python thread
    # see http://stackoverflow.com/a/4939113/3838691
    timer = QtCore.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    sys.exit(qApp.exec_())


if __name__ == '__main__':
    main()
