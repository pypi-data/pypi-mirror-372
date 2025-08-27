# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

from __future__ import annotations

import logging
import numpy

from silx.gui import qt
from silx.gui import icons
from silx.gui.plot import Plot1D
from silx.gui.plot.items import axis as axis_mdl
from bliss.flint.widgets.viewer.actions.duration_action import DurationAction

_logger = logging.getLogger(__name__)


class TimeCurvePlot(qt.QWidget):
    """Curve plot which handle data following the time

    - The X is supposed to be the epoch time
    - The data can be appended
    - The user can choose the amount of time to watch
    """

    def __init__(self, parent=None):
        super(TimeCurvePlot, self).__init__(parent=parent)
        self.__data = {}
        self.__description = {}
        self.__xAxisName = "time"
        self.__plot = Plot1D(self)
        layout = qt.QVBoxLayout(self)
        layout.addWidget(self.__plot)

        self.__xduration = 60 * 2
        self.__ttl = 60 * 5

        self.__xdurationAction = DurationAction(self)
        self.__xdurationAction.setCheckable(True)
        self.__xdurationAction.setChecked(True)
        self.__xdurationAction.addDuration("1h", 60 * 60)
        self.__xdurationAction.addDuration("30m", 30 * 60)
        self.__xdurationAction.addDuration("10m", 10 * 60)
        self.__xdurationAction.addDuration("5m", 5 * 60)
        self.__xdurationAction.addDuration("2m", 2 * 60)
        self.__xdurationAction.addDuration("1m", 1 * 60)
        self.__xdurationAction.addDuration("30s", 30)
        self.__xdurationAction.setDuration(self.__xduration)
        self.__xdurationAction.valueChanged.connect(self.__xdurationChanged)

        self.__plot.setGraphXLabel("Time")
        xAxis = self.__plot.getXAxis()
        xAxis.setTickMode(axis_mdl.TickMode.TIME_SERIES)
        xAxis.setTimeZone(None)

        self.__plot.setDataMargins(
            xMinMargin=0.0, xMaxMargin=0.0, yMinMargin=0.1, yMaxMargin=0.1
        )

        # FIXME: The toolbar have to be recreated, not updated
        toolbar = self.__plot.toolBar()
        xAutoAction = self.__plot.getXAxisAutoScaleAction()
        toolbar.insertAction(xAutoAction, self.__xdurationAction)
        xAutoAction.setVisible(False)
        xLogAction = self.__plot.getXAxisLogarithmicAction()
        xLogAction.setVisible(False)

        timeToolbar = qt.QToolBar(self)

        # time to live widget
        self.__ttlAction = DurationAction(self)
        self.__ttlAction.addDuration("1h", 60 * 60)
        self.__ttlAction.addDuration("30m", 30 * 60)
        self.__ttlAction.addDuration("10m", 10 * 60)
        self.__ttlAction.addDuration("5m", 5 * 60)
        self.__ttlAction.addDuration("2m", 2 * 60)
        self.__ttlAction.addDuration("1m", 1 * 60)
        self.__ttlAction.addDuration("30s", 30)
        self.__ttlAction.setDuration(self.__ttl)
        self.__ttlAction.valueChanged.connect(self.__ttlChanged)
        ttlIcon = icons.getQIcon("flint:icons/ttl-static")
        self.__ttlButton = qt.QToolButton(self)
        self.__ttlButton.setMenu(self.__ttlAction.menu())
        self.__ttlButton.setPopupMode(qt.QToolButton.InstantPopup)
        self.__ttlButton.setIcon(ttlIcon)
        timeToolbar.addWidget(self.__ttlButton)

        self._timeToolbar = timeToolbar
        self.__plot.addToolBar(timeToolbar)

        self.clear()

    def __xdurationChanged(self, duration):
        self.setXDuration(duration)

    def xDuration(self):
        return self.__xduration

    def setXDuration(self, duration):
        self.__xdurationAction.setDuration(duration)
        self.__xduration = duration
        if self.__ttl < duration:
            self.setTtl(duration)
        self.__safeUpdatePlot()

    def ttl(self):
        return self.__ttl

    def setTtl(self, duration):
        self.__ttlAction.setDuration(duration)
        self.__ttl = duration
        self.__dropOldData()
        self.__safeUpdatePlot()

    def __ttlChanged(self, duration):
        self.setTtl(duration)

    def __dropOldData(self):
        xData = self.__data.get(self.__xAxisName)
        if xData is None:
            return
        if len(xData) == 0:
            return
        duration = xData[-1] - xData[0]
        if duration <= self.__ttl:
            return

        # FIXME: most of the time only last items with be removed
        # There is maybe no need to recompute the whole array
        distFromLastValueOfView = self.__ttl - numpy.abs(xData[-1] - self.__ttl - xData)
        index = numpy.argmax(distFromLastValueOfView)
        if index >= 1:
            index = index - 1
        if index == 0:
            # early skip
            return
        for name, data in self.__data.items():
            data = data[index:]
            self.__data[name] = data

    def getDataRange(self):
        r = self.__plot.getDataRange()
        if r is None:
            return None
        return r[0], r[1]

    def setGraphGrid(self, which):
        self.__plot.setGraphGrid(which)

    def setGraphTitle(self, title: str):
        self.__plot.setGraphTitle(title)

    def setGraphXLabel(self, label: str):
        self.__plot.setGraphXLabel(label)

    def setGraphYLabel(self, label: str, axis="left"):
        self.__plot.setGraphYLabel(label, axis=axis)

    def getPlotWidget(self):
        return self.__plot

    def clear(self):
        self.__data = {}
        self.__plot.clear()

    def __appendData(self, name, newData):
        if name in self.__data:
            data = self.__data[name]
            data = numpy.concatenate((data, newData))
        else:
            data = newData
        self.__data[name] = data

    def addTimeCurveItem(self, yName, **kwargs):
        """Update the plot description"""
        self.__description[yName] = kwargs
        self.__safeUpdatePlot()

    def setXName(self, name):
        """Update the name used as X axis"""
        self.__xAxisName = name
        self.__safeUpdatePlot()

    def setData(self, **kwargs):
        self.__data = dict(kwargs)
        self.__safeUpdatePlot()

    def appendData(self, **kwargs):
        """Update the current data with extra data"""
        for name, data in kwargs.items():
            self.__appendData(name, data)
        self.__dropOldData()
        self.__safeUpdatePlot()

    def resetZoom(self):
        if self.__xdurationAction.isChecked():
            self.__plot.resetZoom()
            xData = self.__data.get(self.__xAxisName)
            if xData is not None and len(xData) > 0:
                xmax = xData[-1]
                xmin = xmax - self.__xduration
                xAxis = self.__plot.getXAxis()
                xAxis.setLimits(xmin, xmax)

    def __safeUpdatePlot(self):
        try:
            self.__updatePlot()
        except Exception:
            _logger.critical("Error while updating the plot", exc_info=True)

    def __updatePlot(self):
        self.__plot.clear()
        xData = self.__data.get(self.__xAxisName)
        if xData is None:
            return
        for name, style in self.__description.items():
            yData = self.__data.get(name)
            if yData is None:
                continue
            if "legend" not in style:
                style["legend"] = name
            style["resetzoom"] = False
            self.__plot.addCurve(xData, yData, **style)
        self.resetZoom()
