from __future__ import division, print_function, absolute_import
import numpy as np
from PyQt5 import QtCore, QtWidgets, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT
from matplotlib.figure import Figure
from collections import defaultdict
from functools import partial
from matplotlib.colors import ColorConverter
import os
import sys

from .io import EventGenerator
from .calibration import TimelapseCalibration, TimelapseCalibrationExtraOffsets

color_converter = ColorConverter()


class NavigationToolbar(NavigationToolbar2QT):
    toolitems = [t for t in NavigationToolbar2QT.toolitems if
                 t[0] in ('Home', 'Pan', 'Zoom', 'Subplots', 'Save', None)]


def mpl2rgb(color):
    return tuple(int(c * 255) for c in color_converter.to_rgb(color))


class FigureCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        FigureCanvasQTAgg.__init__(self, self.fig)

        self.setParent(parent)
        FigureCanvas.setSizePolicy(
            self,
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding,
        )
        FigureCanvas.updateGeometry(self)


class DragonBrowser(QtWidgets.QMainWindow):
    def __init__(self, filename=None, calibfile=None, extra_offset_file=None, start=None, **kwargs):
        QtWidgets.QMainWindow.__init__(self, **kwargs)

        self.setWindowTitle('DragonBrowser')

        if filename is None:
            filename, _ = QtWidgets.QFileDialog.getOpenFileName(
                self, 'Open file', os.environ['HOME']
            )
        self.filename = filename

        if not self.filename:
            sys.exit()

        if extra_offset_file is not None:
            self.calib = TimelapseCalibrationExtraOffsets(calibfile, extra_offset_file)
        elif calibfile is not None:
            self.calib = TimelapseCalibration(calibfile)
        else:
            self.calib = lambda x: x

        self.generator = EventGenerator(self.filename)

        if start is not None:
            for i in range(start):
                next(self.generator)

        self.dragon_event = self.calib(next(self.generator))
        self.gains = self.dragon_event.data.dtype.names
        self.n_channels = self.dragon_event.data.shape[0]
        self.init_gui()

    def init_gui(self):
        self.canvas = FigureCanvas(self, 12.8, 7.2)
        self.setCentralWidget(self.canvas)
        self.fig = self.canvas.fig

        self.axs = {'high': self.fig.add_subplot(2, 1, 2)}
        self.axs['low'] = self.fig.add_subplot(2, 1, 1, sharex=self.axs['high'])
        self.axs['low'].set_title('Low Gain Channel')
        self.axs['high'].set_title('High Gain Channel')
        self.axs['high'].set_xlim(-0.5, self.dragon_event.roi)

        self.navbar = NavigationToolbar(self.canvas, self)
        self.toolbar = self.addToolBar('Test')
        self.toolbar.addWidget(self.navbar)

        bottom_frame = QtWidgets.QFrame()
        layout = QtWidgets.QHBoxLayout(bottom_frame)
        self.text = QtWidgets.QLineEdit(bottom_frame)
        self.text.setReadOnly(True)
        self.text.setFocusPolicy(QtCore.Qt.NoFocus)
        layout.addWidget(self.text)

        self.plots = defaultdict(dict)
        for channel in range(self.n_channels):
            for gain in self.gains:
                plot, = self.axs[gain].plot(
                    [], [], '.:', ms=10, mew=1, label='Ch{}'.format(channel)
                )
                plot.set_visible(False)
                self.plots[gain][channel] = plot

            button = QtWidgets.QPushButton(bottom_frame)
            button.setStyleSheet('background-color: rgb({}, {}, {});'.format(
                *mpl2rgb(plot.get_color())
            ))
            button.clicked.connect(partial(
                self.changeColor, channel=channel, button=button)
            )
            button.setFocusPolicy(QtCore.Qt.NoFocus)
            layout.addWidget(button)

            cb = QtWidgets.QCheckBox(str(channel), bottom_frame)
            cb.setFocusPolicy(QtCore.Qt.NoFocus)
            cb.stateChanged.connect(
                partial(self.toggle_channel, channel=channel)
            )
            if channel != 7:
                cb.toggle()
            layout.addWidget(cb)

        cb = QtWidgets.QCheckBox('Rescale', bottom_frame)
        cb.setFocusPolicy(QtCore.Qt.NoFocus)
        cb.toggle()
        layout.addWidget(cb)
        self.rescale_box = cb

        cb = QtWidgets.QCheckBox('Show Cell ID', bottom_frame)
        cb.setFocusPolicy(QtCore.Qt.NoFocus)
        cb.stateChanged.connect(self.update)
        layout.addWidget(cb)
        self.cb_physical = cb

        button = QtWidgets.QPushButton(bottom_frame)
        button.clicked.connect(self.next_event)
        button.setFocusPolicy(QtCore.Qt.NoFocus)
        button.setText('Next Event')
        layout.addWidget(button)

        self.statusBar().insertWidget(0, bottom_frame)
        for ax in self.axs.values():
            ax.set_ylabel('ADC Counts')
        self.axs['high'].set_xlabel('Time Slice')

        self.fig.tight_layout()
        self.update()

    def changeColor(self, channel, button):
        diag = QtWidgets.QColorDialog(self)
        color = diag.getColor().name()
        button.setStyleSheet('background-color: {}'.format(color))

        for gain in self.gains:
            self.plots[gain][channel].set_color(color)
        self.canvas.draw()

    def toggle_channel(self, channel):
        for gain in self.gains:
            plot = self.plots[gain][channel]
            plot.set_visible(not plot.get_visible())
        self.canvas.draw()

    def update(self):
        event = self.dragon_event

        for gain in self.gains:
            for channel in range(event.data.shape[0]):
                stop_cell = event.header.stop_cells[channel][gain]
                x = np.arange(event.roi)
                if self.cb_physical.isChecked():
                    x = (x + stop_cell) % 4096
                self.plots[gain][channel].set_data(x, event.data[gain][channel])

        for ax in self.axs.values():
            ax.relim()
            if self.rescale_box.isChecked():
                ax.autoscale(enable=True)
            ax.autoscale_view()

        if self.cb_physical.isChecked():
            self.axs['high'].set_xlabel('Cell ID')
        else:
            self.axs['high'].set_xlabel('Sample ID')
            self.axs['high'].set_xlim(-0.5, event.roi)

        self.fig.canvas.draw()
        self.text.setText('Event: {}'.format(
            self.dragon_event.header.event_counter
        ))

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Right:
            self.next_event()

    def next_event(self):
        try:
            self.dragon_event = self.calib(next(self.generator))
        except StopIteration:
            pass
        else:
            self.update()

    def closeEvent(self, event):
        event.accept()
        QtCore.QCoreApplication.instance().quit()
