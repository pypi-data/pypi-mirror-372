# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

from __future__ import annotations

import logging

from silx.gui import qt
from bliss.flint.widgets.extended_dock_widget import ExtendedDockWidget
from .refresh_manager import RefreshManager
from .. import interfaces


_logger = logging.getLogger(__name__)


class ViewerDock(ExtendedDockWidget):

    widgetActivated = qt.Signal(object)

    plotModelUpdated = qt.Signal(object)
    """Emitted when the plot model displayed by the plot was changed"""

    scanModelUpdated = qt.Signal(object)
    """Emitted when the scan model displayed by the plot was changed"""

    viewerEvent = qt.Signal(object)
    """Event related to the displayed scan life cycle"""

    DEFAULT_DATA_MARGINS = 0.02, 0.02, 0.02, 0.02

    def configuration(self):
        plot = self._silxPlot()
        config = plot.configuration()

        if hasattr(self, "getRefreshManager"):
            refreshManager: RefreshManager = self.getRefreshManager()
            if refreshManager is not None:
                rate = refreshManager.refreshMode()
                config.refresh_mode = rate

        if isinstance(self, interfaces.HasDeviceName):
            deviceName = self.deviceName()
            config.device_name = deviceName

        return config

    def setConfiguration(self, config):
        plot = self._silxPlot()
        if hasattr(self, "getRefreshManager"):
            refreshManager: RefreshManager = self.getRefreshManager()
            if refreshManager is not None:
                rate = config.refresh_mode
                refreshManager.setRefreshMode(rate)
        if isinstance(self, interfaces.HasDeviceName):
            deviceName = config.device_name
            if deviceName is not None:
                self.setDeviceName(deviceName)
            else:
                # FIXME: backward compatibility with BLISS <= 1.7
                # This is stored in the Redis db and mostly never updated
                # So it is not so easy to remove
                deviceName = self.windowTitle().split(" ", 1)[0]
            self.setDeviceName(deviceName)

        plot.setConfiguration(config)

    def event(self, event: qt.QEvent) -> bool:
        if event.type() == qt.QEvent.MouseButtonPress:
            self.widgetActivated.emit(self)
        return ExtendedDockWidget.event(self, event)
