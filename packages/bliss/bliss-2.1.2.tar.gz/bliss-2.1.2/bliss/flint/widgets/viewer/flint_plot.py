# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

from __future__ import annotations
import typing

import contextlib
import logging

from silx.gui import qt
from silx.gui.plot import PlotWindow

from .viewer_events import ViewChangedEvent
from .viewer_events import MouseMovedEvent
from .viewer_configuration import ViewerConfiguration

_logger = logging.getLogger(__name__)


class _MousePressedListener(qt.QObject):
    """
    Dedicated `eventFilter` to dispatch pressevent from the plot handler.
    """

    def __init__(self, parent=None):
        qt.QObject.__init__(self, parent=parent)

    def eventFilter(self, widget, event):
        if event.type() == qt.QEvent.MouseButtonPress:
            parent = self.parent()
            parent.sigMousePressed.emit()
        return widget.eventFilter(widget, event)


class FlintPlot(PlotWindow):
    """Helper to provide few other functionalities on top of silx.

    This should be removed and merged into silx.
    """

    sigViewChanged = qt.Signal(ViewChangedEvent)

    sigMouseMoved = qt.Signal(MouseMovedEvent)

    sigMouseLeft = qt.Signal()

    sigMousePressed = qt.Signal()

    def __init__(self, parent=None, backend=None):
        self._mousePressedListener = None
        super(FlintPlot, self).__init__(parent=parent, backend=backend)
        self.sigPlotSignal.connect(self.__plotEvents)
        self.__userInteraction = False
        self.__dataMargins = 0.02, 0.02, 0.02, 0.02
        self.setDataMarginsEnabled(True)

        toolbars = self.findChildren(qt.QToolBar)
        for tb in toolbars:
            self.removeToolBar(tb)

        self._mousePressedListener = _MousePressedListener(self)

        self._backendUpdated()

    def setDefaultDataMargins(self, *margins: float):
        # "Tuple" for compatibility with python 3.8 when not used as a hint
        self.__dataMargins = typing.cast(tuple[float, float, float, float], margins)

    def setDataMarginsEnabled(self, enabled: bool):
        if enabled:
            margins = self.__dataMargins
        else:
            margins = 0, 0, 0, 0
        self.setDataMargins(*margins)

    def isDataMarginsEnabled(self) -> bool:
        margins = self.getDataMargins()
        return margins != (0, 0, 0, 0)

    def setBackend(self, backend):
        super(FlintPlot, self).setBackend(backend)
        self._backendUpdated()

    def _backendUpdated(self):
        if hasattr(self, "centralWidget"):
            self.centralWidget().installEventFilter(self)

        if self._mousePressedListener is not None:
            self.installEventFilter(self._mousePressedListener)
            self.getWidgetHandle().installEventFilter(self._mousePressedListener)

    def configuration(self) -> ViewerConfiguration:
        """Returns a global configuration of the plot"""
        config = ViewerConfiguration()

        mode = self.getInteractiveMode()["mode"]
        if mode not in ("pan", "zoom"):
            mode = None
        config.interaction_mode = mode

        # Axis
        axis = self.getXAxis()
        config.x_axis_scale = axis.getScale()
        axis = self.getYAxis()
        config.y_axis_scale = axis.getScale()
        config.y_axis_inverted = axis.isInverted()
        axis = self.getYAxis("right")
        config.y2_axis_scale = axis.getScale()
        config.y2_axis_inverted = axis.isInverted()
        config.fixed_aspect_ratio = self.isKeepDataAspectRatio()
        config.use_data_margins = self.isDataMarginsEnabled()

        # View
        config.grid_mode = self.getGraphGrid()
        config.axis_displayed = self.isAxesDisplayed()

        # Tools
        config.crosshair_enabled = self.getGraphCursor() is not None
        config.colorbar_displayed = self.getColorBarAction().isChecked()
        # FIXME: It would be good to do it
        # config.profile_widget_displayed = None
        # config.roi_widget_displayed = None
        # config.histogram_widget_displayed = None

        return config

    def setConfiguration(self, config: ViewerConfiguration):
        mode = config.interaction_mode
        if mode in ("pan", "zoom"):
            self.setInteractiveMode(mode)

        # FIXME: implement it
        # config.refresh_rate

        @contextlib.contextmanager
        def safeApply():
            try:
                yield
            except Exception:
                _logger.error(
                    "Error while applying the plot configuration", exc_info=True
                )

        # Axis
        axis = self.getXAxis()
        with safeApply():
            axis.setScale(config.x_axis_scale)
        axis = self.getYAxis()
        with safeApply():
            axis.setScale(config.y_axis_scale)
        with safeApply():
            axis.setInverted(config.y_axis_inverted)
        axis = self.getYAxis("right")
        with safeApply():
            axis.setScale(config.y2_axis_scale)
        with safeApply():
            axis.setInverted(config.y2_axis_inverted)
        with safeApply():
            self.setKeepDataAspectRatio(config.fixed_aspect_ratio)

        # View
        with safeApply():
            self.setGraphGrid(config.grid_mode)
        with safeApply():
            self.setAxesDisplayed(config.axis_displayed)
        with safeApply():
            self.setDataMarginsEnabled(config.use_data_margins)

        # Tools
        if config.crosshair_enabled:
            with safeApply():
                self.setGraphCursor(True)
        if config.colorbar_displayed:
            with safeApply():
                self.getColorBarWidget().setVisible(True)

    def graphCallback(self, ddict=None):
        """
        Override silx function to avoid to call QToolTip.showText when a curve
        is selected.
        """
        # FIXME it would be very good to remove this code and this function
        if ddict is None:
            ddict = {}
        if ddict["event"] in ["legendClicked", "curveClicked"]:
            if ddict["button"] == "left":
                self.setActiveCurve(ddict["label"])
        elif ddict["event"] == "mouseClicked" and ddict["button"] == "left":
            self.setActiveCurve(None)

    @contextlib.contextmanager
    def userInteraction(self):
        self.__userInteraction = True
        try:
            yield
        finally:
            self.__userInteraction = False

    def eventFilter(self, widget, event):
        if event.type() == qt.QEvent.Leave:
            self.__mouseLeft()
            return True
        return False

    def __mouseLeft(self):
        self.sigMouseLeft.emit()

    def __plotEvents(self, eventDict):
        if eventDict["event"] == "limitsChanged":
            event1 = ViewChangedEvent(self.__userInteraction)
            self.sigViewChanged.emit(event1)
        elif eventDict["event"] == "mouseMoved":
            event2 = MouseMovedEvent(
                eventDict["x"], eventDict["y"], eventDict["xpixel"], eventDict["ypixel"]
            )
            self.sigMouseMoved.emit(event2)

    def keyPressEvent(self, event):
        with self.userInteraction():
            super(FlintPlot, self).keyPressEvent(event)

    def onMousePress(self, xPixel, yPixel, btn):
        with self.userInteraction():
            super(FlintPlot, self).onMousePress(xPixel, yPixel, btn)

    def onMouseMove(self, xPixel, yPixel):
        with self.userInteraction():
            super(FlintPlot, self).onMouseMove(xPixel, yPixel)

    def onMouseRelease(self, xPixel, yPixel, btn):
        with self.userInteraction():
            super(FlintPlot, self).onMouseRelease(xPixel, yPixel, btn)

    def onMouseWheel(self, xPixel, yPixel, angleInDegrees):
        with self.userInteraction():
            super(FlintPlot, self).onMouseWheel(xPixel, yPixel, angleInDegrees)
