# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

from __future__ import annotations

import numpy
import logging
import weakref
from silx.gui import qt
from silx.gui.plot import Plot1D
from silx.gui.plot.actions.PlotToolAction import PlotToolAction
from silx.gui.plot import items

_logger = logging.getLogger(__name__)


class FftWidget(qt.QWidget):
    """Widget displaying a histogram and some statistic indicators"""

    def __init__(self, *args, **kwargs):
        super(FftWidget, self).__init__(*args, **kwargs)

        self.__itemRef = None

        layout = qt.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.__plot = Plot1D(self)
        self.__plot.setGraphTitle("Amplitude spectrum")
        self.__plot.getXAxis().setLabel("Frequency")
        self.__plot.getYAxis().setLabel("Amplitude")
        layout.addWidget(self.__plot)

    def setItem(self, item: items.Item | None):
        """Set item from which to display histogram and statistics."""
        previous = self.getItem()
        if previous is not None:
            previous.sigItemChanged.disconnect(self.__itemChanged)

        self.__itemRef = None if item is None else weakref.ref(item, self.__itemChanged)
        if item is not None:
            item.sigItemChanged.connect(self.__itemChanged)
        self._updateFromItem()

    def getItem(self) -> items.Item | None:
        """Returns item used to display histogram and statistics."""
        return None if self.__itemRef is None else self.__itemRef()

    def __itemChanged(self, event):
        """Handle update of the item"""
        if event in (
            items.ItemChangedType.DATA,
            items.ItemChangedType.YAXIS,
            items.ItemChangedType.LINE_STYLE,
            items.ItemChangedType.LINE_WIDTH,
            items.ItemChangedType.SYMBOL,
            items.ItemChangedType.SYMBOL_SIZE,
            items.ItemChangedType.COLOR,
        ):
            self._updateFromItem()

    def _updateFromItem(self):
        curve = self.getItem()

        self.__plot.clear()
        if curve is None or not isinstance(curve, items.Curve):
            return

        x = curve.getXData()
        y = curve.getYData()
        legend = curve.getName()
        info = curve.getInfo()
        if info is None:
            info = {}

        # FAST FOURIER TRANSFORM
        fft_y = numpy.fft.fft(y)
        # amplitude spectrum
        A = numpy.abs(fft_y)

        # sampling frequency (samples per X unit)
        Fs = len(x) / (max(x) - min(x))
        # frequency array (abscissa of new curve)
        F = [k * Fs / len(x) for k in range(len(A))]

        # we need to store  the complete transform (complex data) to be
        # able to perform the reverse transform.
        info["complex fft"] = fft_y
        info["original x"] = x

        # plot the amplitude spectrum
        self.__plot.addCurve(
            F,
            A,
            legend=legend,
            info=info,
            color=curve.getColor(),
            symbol=curve.getSymbol(),
            linewidth=curve.getLineWidth(),
            linestyle=curve.getLineStyle(),
            yaxis=curve.getYAxis(),
            z=curve.getZValue(),
            resetzoom=False,
        )

        self.__plot.resetZoom()


class FftAction(PlotToolAction):
    """QAction performing a Fourier transform on all curves when checked,
    and reverse transform when unchecked.

    Arguments:
        plot: PlotWindow on which to operate
        parent: See documentation of :class:`QAction`
    """

    def __init__(self, plot, parent=None):
        PlotToolAction.__init__(
            self,
            plot,
            icon="flint:icons/math-fft",
            text="FFT",
            tooltip="Perform Fast Fourier Transform on all curves",
            parent=parent,
        )

    def _connectPlot(self, window):
        plot = self.plot
        if plot is not None:
            selection = plot.selection()
            selection.sigSelectedItemsChanged.connect(self._selectedItemsChanged)
            self._updateSelectedItem()

        PlotToolAction._connectPlot(self, window)

    def _disconnectPlot(self, window):
        plot = self.plot
        if plot is not None:
            selection = self.plot.selection()
            selection.sigSelectedItemsChanged.disconnect(self._selectedItemsChanged)

        PlotToolAction._disconnectPlot(self, window)
        self.getFftWidget().setItem(None)

    def _updateSelectedItem(self):
        """Synchronizes selected item with plot widget."""
        plot = self.plot
        if plot is not None:
            selected = plot.selection().getSelectedItems()
            # Give priority to image over scatter
            for klass in [items.Curve]:
                for item in selected:
                    if isinstance(item, klass):
                        # Found a matching item, use it
                        self.getFftWidget().setItem(item)
                        return
        self.getFftWidget().setItem(None)

    def _selectedItemsChanged(self):
        if self._isWindowInUse():
            self._updateSelectedItem()

    def getFftWidget(self):
        """Returns the widget displaying the histogram"""
        return self._getToolWindow()

    def _createToolWindow(self):
        widget = FftWidget(self.plot, qt.Qt.Window)
        widget.setWindowFlag(qt.Qt.WindowStaysOnTopHint, True)
        return widget
