# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

from __future__ import annotations
from typing import NamedTuple

import numpy
import logging

from silx.gui import plot as silx_plot
from bliss.flint.widgets.viewer.data_widget import DataWidget


_logger = logging.getLogger(__name__)


class Plot1D(DataWidget):
    """Generic plot to display 1D data"""

    # Name of the method to add data to the plot
    METHOD = "addCurve"

    class CurveItem(NamedTuple):
        xdata: str
        ydata: str
        style: dict[str, object]

    def __init__(self, parent=None):
        DataWidget.__init__(self, parent=parent)
        self.__items = {}
        self.__autoUpdatePlot = True
        self.__raiseOnException = False

    def setRaiseOnException(self, raises):
        """To simplify remote debug"""
        self.__raiseOnException = raises

    def _createSilxWidget(self, parent):
        widget = silx_plot.Plot1D(parent=parent)
        widget.setDataMargins(0.05, 0.05, 0.05, 0.05)
        widget.setActiveCurveStyle(linewidth=2, symbol=".")
        return widget

    def setAutoUpdatePlot(self, update="bool"):
        """Set to true to enable or disable update of plot for each changes of
        the data or items"""
        self.__autoUpdatePlot = update

    def clearItems(self):
        """Remove the item definitions"""
        self.__items.clear()
        self.__updatePlotIfNeeded()

    def removeItem(self, legend: str):
        """Remove a specific item by name"""
        del self.__items[legend]
        self.__updatePlotIfNeeded()

    def getItem(self, legend: str):
        item = self.__items[legend]
        return item._asdict()

    def itemExists(self, legend: str):
        """True if a specific item exists."""
        return legend in self.__items

    def addCurve(self, *args, **kwargs):
        """
        For compatibility with silx 2. Silx 2 returns a non serializable object.
        """
        plot = self.silxPlot()
        item = plot.addCurve(*args, **kwargs)
        return item.getName()

    def addCurveItem(
        self,
        xdata: str,
        ydata: str,
        legend: str | None = None,
        color: str | None = None,
        **kwargs,
    ):
        """Define an item which have to be displayed with the specified data
        name
        """
        if legend is None:
            legend = ydata + " -> " + xdata
        if color is not None:
            if isinstance(color, str):
                if color.startswith("color"):
                    # FIXME: This could be removed in the future: silx > 1.1 will implement it
                    icolor = int(color[5:])
                    colorList = self.silxWidget().colorList
                    color = colorList[icolor % len(colorList)]
            kwargs["color"] = color
        self.__items[legend] = self.CurveItem(xdata, ydata, kwargs)
        self.__updatePlotIfNeeded()

    def setData(self, **kwargs):
        dataDict = self.dataDict()
        for k, v in kwargs.items():
            dataDict[k] = v
        self.__updatePlotIfNeeded()

    def appendData(self, **kwargs):
        dataDict = self.dataDict()
        for k, v in kwargs.items():
            d = dataDict.get(k, None)
            if d is None:
                d = v
            else:
                d = numpy.concatenate((d, v))
            dataDict[k] = d
        self.__updatePlotIfNeeded()

    def clear(self):
        super(Plot1D, self).clear()
        self.__updatePlotIfNeeded()

    def updatePlot(self, resetzoom: bool = True):
        try:
            self.__updatePlot()
        except Exception:
            _logger.error("Error while updating the plot", exc_info=True)
            if self.__raiseOnException:
                raise
        if resetzoom:
            self.resetZoom()

    def __updatePlotIfNeeded(self):
        if self.__autoUpdatePlot:
            self.updatePlot(resetzoom=True)

    def __updatePlot(self):
        plot = self.silxPlot()
        unusedCurves = set([c.getLegend() for c in plot.getAllCurves()])

        dataDict = self.dataDict()
        for legend, item in self.__items.items():
            unusedCurves.discard(legend)
            xData = dataDict.get(item.xdata)
            yData = dataDict.get(item.ydata)
            if xData is None or yData is None:
                continue
            if len(yData) != len(xData):
                size = min(len(yData), len(xData))
                xData = xData[0:size]
                yData = yData[0:size]
            if len(yData) == 0:
                continue

            style = {**item.style}
            prevItem = plot.getCurve(legend)
            if prevItem is not None:
                # Sounds like it is mandatory for silx 2.0
                # replace=True does not work with default style
                plot.removeCurve(legend)
                if "color" not in style:
                    # Restore the previous color
                    style["color"] = prevItem.getColor()

            plot.addCurve(xData, yData, legend=legend, **style, resetzoom=False)

        for legend in unusedCurves:
            plot.removeCurve(legend)

    def getXAxisScale(self):
        plot = self.silxPlot()
        return "log" if plot.isXAxisLogarithmic() else "linear"

    def setXAxisScale(self, scale):
        assert scale in ["log", "linear"]
        plot = self.silxPlot()
        plot.setXAxisLogarithmic(scale == "log")

    def getYAxisScale(self):
        plot = self.silxPlot()
        return "log" if plot.isYAxisLogarithmic() else "linear"

    def setYAxisScale(self, scale):
        assert scale in ["log", "linear"]
        plot = self.silxPlot()
        plot.setYAxisLogarithmic(scale == "log")
