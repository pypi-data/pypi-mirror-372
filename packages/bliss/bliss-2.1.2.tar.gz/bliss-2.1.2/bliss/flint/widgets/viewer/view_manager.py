# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

from __future__ import annotations

import logging

from silx.gui import qt
from silx.gui import icons
from silx.gui.plot import _utils as plot_utils


_logger = logging.getLogger(__name__)


class ViewManager(qt.QObject):

    sigZoomMode = qt.Signal(bool)

    def __init__(self, plot):
        super(ViewManager, self).__init__(parent=plot)
        self.__plot = plot
        self.__plot.sigViewChanged.connect(self.__viewChanged)
        self.__inUserView: bool = False
        self.__resetOnStart = True
        self.__resetOnClear = True
        self.__xduration = None

    def setResetWhenScanStarts(self, reset: bool):
        self.__resetOnStart = reset

    def setResetWhenPlotCleared(self, reset: bool):
        self.__resetOnClear = reset

    def setXDuration(self, duration):
        if self.__xduration == duration:
            return
        self.__xduration = duration
        self.__updateView()

    def __setUserViewMode(self, userMode):
        if self.__inUserView == userMode:
            return
        self.__inUserView = userMode
        self.sigZoomMode.emit(userMode)

    def __viewChanged(self, event):
        if event.userInteraction:
            self.__setUserViewMode(True)

    def scanStarted(self):
        if self.__resetOnStart:
            self.__setUserViewMode(False)
            # Remove from the plot location which should not have anymore meaning
            self.__plot.getLimitsHistory().clear()

    def resetZoom(self):
        self.__updateView()
        self.__setUserViewMode(False)

    def widgetResized(self):
        if not self.__inUserView:
            self.__updateView()

    def plotUpdated(self):
        if not self.__inUserView:
            self.__updateView()

    def plotCleared(self):
        if self.__resetOnClear:
            self.__updateView()
            self.__setUserViewMode(False)

    def __updateView(self):
        if self.__xduration is None:
            self.__plot.resetZoom()
        else:
            ranges = self.__plot.getDataRange()
            if ranges is None:
                self.__plot.resetZoom()
            else:
                dataMargins = self.__plot.getDataMargins()
                xrange, yrange, yrange2 = ranges
                if xrange is None:
                    self.__plot.resetZoom()
                    return
                else:
                    xmax = xrange[1]
                    xmin = xmax - self.__xduration
                newLimits = list(
                    plot_utils.addMarginsToLimits(
                        dataMargins,
                        self.__plot.getXAxis()._isLogarithmic(),
                        self.__plot.getYAxis()._isLogarithmic(),
                        xmin,
                        xmax,
                        yrange[0] if yrange else None,
                        yrange[1] if yrange else None,
                        yrange2[0] if yrange2 else None,
                        yrange2[1] if yrange2 else None,
                    )
                )
                self.__plot.setLimits(*newLimits)

    def createResetZoomAction(self, parent: qt.QWidget) -> qt.QAction:
        resetZoom = qt.QAction(parent)
        resetZoom.triggered.connect(self.resetZoom)
        resetZoom.setText("Reset zoom")
        resetZoom.setToolTip("Back to the auto-zoom")
        resetZoom.setIcon(icons.getQIcon("flint:icons/zoom-auto"))
        resetZoom.setEnabled(self.__inUserView)

        def updateResetZoomAction(isUserMode):
            resetZoom.setEnabled(isUserMode)

        self.sigZoomMode.connect(updateResetZoomAction)

        return resetZoom
