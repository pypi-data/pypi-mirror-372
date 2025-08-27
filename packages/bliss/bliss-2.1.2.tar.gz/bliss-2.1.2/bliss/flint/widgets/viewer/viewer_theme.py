# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

from __future__ import annotations

from silx.gui import qt
from silx.gui.plot import PlotWidget as SilxPlotWidget
from .viewer_dock import ViewerDock
from . import viewer_events


INSIDE_LIVE_COLOR = "#FFFFFF"
OUTSIDE_LIVE_COLOR = "#bdd4e5"
INSIDE_OFFLINE_COLOR = "#FFFFFF"
OUTSIDE_OFFLINE_COLOR = "#efefef"


class ViewerTheme(qt.QObject):
    def __init__(self, flintViewer: ViewerDock):
        super(ViewerTheme, self).__init__(parent=flintViewer)
        flintViewer.viewerEvent.connect(self.__events)
        silxPlot = flintViewer._silxPlot()
        self.scanTerminated(silxPlot)

    def __events(self, event: viewer_events.ViewerEvent):
        viewer: ViewerDock = self.sender()
        if event.type == viewer_events.ViewerEventType.SCAN_STARTED:
            silxPlot = viewer._silxPlot()
            self.scanProcessing(silxPlot)
        elif event.type == viewer_events.ViewerEventType.SCAN_FINISHED:
            silxPlot = viewer._silxPlot()
            self.scanTerminated(silxPlot)

    def scanProcessing(self, silxPlot: SilxPlotWidget):
        silxPlot.setDataBackgroundColor(INSIDE_LIVE_COLOR)
        silxPlot.setBackgroundColor(OUTSIDE_LIVE_COLOR)

    def scanTerminated(self, silxPlot: SilxPlotWidget):
        silxPlot.setDataBackgroundColor(INSIDE_OFFLINE_COLOR)
        silxPlot.setBackgroundColor(OUTSIDE_OFFLINE_COLOR)
