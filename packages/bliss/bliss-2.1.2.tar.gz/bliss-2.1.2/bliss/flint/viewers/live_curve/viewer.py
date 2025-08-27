# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

from __future__ import annotations
from typing import cast
from collections.abc import Sequence

import numpy
import logging
import time
import gevent

from silx.gui import qt
from silx.gui import icons
from silx.gui import utils as qtutils
from silx.gui.plot.items.shape import XAxisExtent
from silx.gui.plot.items import Curve
from silx.gui.plot.items import axis as axis_mdl
from silx.gui.plot.actions import fit

from bliss.flint.model import scan_model
from bliss.flint.model import flint_model
from bliss.flint.model import plot_model
from bliss.flint.model import plot_item_model
from bliss.flint.filters.min import MinCurveItem
from bliss.flint.filters.max import MaxCurveItem
from bliss.flint.helper import scan_info_helper
from bliss.flint.helper import model_helper
from bliss.flint.utils import signalutils
from bliss.scanning import scan_math
from bliss.flint.widgets.viewer.viewer_dock import ViewerDock
from bliss.flint.widgets.viewer import flint_plot
from bliss.flint.widgets.viewer import viewer_events
from bliss.flint.widgets.viewer import viewer_theme
from bliss.flint.widgets.viewer import view_manager
from bliss.flint.widgets.viewer import refresh_manager
from bliss.flint.widgets.viewer import tooltip_item_manager
from bliss.flint.widgets.viewer.items.flint_curve import FlintCurve
from bliss.flint.widgets.viewer.actions import marker_action
from bliss.flint.widgets.viewer.actions import plot_action
from bliss.flint.widgets.viewer.actions import export_action
from bliss.flint.widgets.viewer.actions import fft_action
from bliss.flint.widgets.viewer.actions import duration_action
from bliss.flint.widgets import interfaces
from .viewer_api import CurvePlotWidgetApi

_logger = logging.getLogger(__name__)


class SpecMode(qt.QObject):
    stateChanged = qt.Signal(bool)
    """Emitted when the enability changed"""

    titleChanged = qt.Signal()
    """Emitted when the title change"""

    MIN_REFRESH_PERIOD = 1.0

    def __init__(self, parent: qt.QObject = None):
        super(SpecMode, self).__init__(parent=parent)
        self.__enabled = False
        self.__lastTitle = ""
        self.__lastCall: float = 0
        self.__greenlet: gevent.Greenlet | None = None
        self.__next: tuple[
            numpy.ndarray | None, numpy.ndarray | None, scan_model.Channel | None
        ] | None = None

    def lastTitle(self) -> str:
        return self.__lastTitle

    def clear(self):
        self.__lastTitle = ""

    def isEnabled(self) -> bool:
        return self.__enabled

    def setEnabled(self, enabled: bool):
        if self.__enabled == enabled:
            return
        self.__enabled = enabled
        self.stateChanged.emit(enabled)

    def createAction(self):
        action = qt.QAction(self)
        action.setText("Spec-like statistics")
        action.setToolTip("Enable/disable Spec-like statistics for boomers")
        action.setCheckable(True)
        icon = icons.getQIcon("flint:icons/spec")
        action.setIcon(icon)
        self.stateChanged.connect(action.setChecked)
        action.toggled.connect(self.setEnabled)
        return action

    def __selectedData(
        self, plot: flint_plot.FlintPlot, scan: scan_model.Scan | None
    ) -> tuple[numpy.ndarray | None, numpy.ndarray | None, scan_model.Channel | None]:
        curve = plot.getActiveCurve()
        if curve is None:
            curves = plot.getAllCurves()
            curves = [c for c in curves if isinstance(c, FlintCurve)]
            if len(curves) != 1:
                return None, None, None
            curve = curves[0]
        x = curve.getXData()
        y = curve.getYData()
        if isinstance(curve, FlintCurve):
            item = curve.customItem()
        else:
            item = None
        if item is not None and scan is not None:
            ref = item.xChannel()
            if isinstance(ref, plot_model.XIndexChannelRef):
                xChannel = None
            else:
                xChannel = ref.channel(scan)
        else:
            xChannel = None
        return x, y, xChannel

    def initPlot(self, plot: flint_plot.FlintPlot):
        if self.__enabled:
            pass

    def __geventException(self, greenlet):
        """Process gevent exception"""
        try:
            greenlet.get()
        except Exception:
            _logger.error(
                "Error while computing cen/peak/com (greenlet %s)",
                greenlet.name,
                exc_info=True,
            )
        self.__greenlet = None

    def requestUpdateTitle(
        self,
        plot: flint_plot.FlintPlot,
        scan: scan_model.Scan | None,
        force: bool = False,
    ):
        t = time.time()
        if not force:
            if t - self.__lastCall < self.MIN_REFRESH_PERIOD:
                return

        self.__lastCall = t
        data = self.__selectedData(plot, scan)
        if self.__greenlet is None:
            self.__greenlet = gevent.spawn(self.__processData, data)
            self.__greenlet.link_exception(self.__geventException)
        else:
            self.__next = data

    def __processData(
        self,
        data: tuple[
            numpy.ndarray | None, numpy.ndarray | None, scan_model.Channel | None
        ],
    ):
        title = self.__computeTitle(data)
        self.__emitTitle(title)
        while self.__next is not None:
            data, self.__next = self.__next, None
            title = self.__computeTitle(data)
            self.__emitTitle(title)
        self.__greenlet = None

    def __emitTitle(self, title: str | None):
        if title is None:
            title = ""
        self.__lastTitle = title
        self.titleChanged.emit()

    def __computeTitle(
        self,
        data: tuple[
            numpy.ndarray | None, numpy.ndarray | None, scan_model.Channel | None
        ],
    ) -> str | None:
        x, y, channel = data
        if x is None or y is None:
            return None
        # FIXME: It would be good to cache this statistics
        peak = scan_math.peak2(x, y)
        gevent.sleep()  # release the greenlet
        cen = scan_math.cen(x, y)
        gevent.sleep()  # release the greenlet
        com = scan_math.com(x, y)
        gevent.sleep()  # release the greenlet
        # Formatter don't like int
        peak = float(peak[0]), float(peak[1])
        cen = float(cen[0]), float(cen[1])
        com = float(com)
        if channel is None or channel.metadata().decimals is None:
            return f"Peak: {peak[0]:.3} ({peak[1]:.3})  Cen: {cen[0]:.3} (FWHM: {cen[1]:.3})  COM: {com:.3}"
        else:
            d = channel.metadata().decimals
            return f"Peak: {peak[0]:.{d}f} ({peak[1]:.3})  Cen: {cen[0]:.{d}f} (FWHM: {cen[1]:.{d}f})  COM: {com:.{d}f}"


class CurvePlotWidget(ViewerDock, interfaces.HasPlotModel, interfaces.HasScan):
    plotItemSelected = qt.Signal(object)
    """Emitted when a flint plot item was selected by the plot"""

    scanSelected = qt.Signal(object)
    """Emitted when a flint plot item was selected by the plot"""

    scanListUpdated = qt.Signal(object)
    """Emitted when the list of scans is changed"""

    DEFAULT_XDURATION = 2 * 60

    DEFAULT_DATA_MARGINS = 0.02, 0.02, 0.1, 0.1

    def __init__(self, parent=None):
        super(CurvePlotWidget, self).__init__(parent=parent)
        self.__maxStoredScans = 3
        self.__storePreviousScans = False
        self.__flintModel: flint_model.FlintState | None = None
        self.__plotModel: plot_model.Plot | None = None
        self.__api = CurvePlotWidgetApi(self)
        self.__scanItems: list[plot_item_model.ScanItem] = []
        self.__title: str = ""

        self.__selectionLock = qtutils.LockReentrant()

        self.__specMode = SpecMode(self)
        self.__specMode.stateChanged.connect(self.__specModeChanged)
        self.__specMode.titleChanged.connect(self.__updatePlotTitle)

        self.__items: dict[
            plot_model.Item, dict[scan_model.Scan, list[tuple[str, str]]]
        ] = {}

        self.__plotWasUpdated: bool = False
        self.__plot = flint_plot.FlintPlot(parent=self)
        self.__plot.sigMousePressed.connect(self.__onPlotPressed)

        self.__plot.setActiveCurveStyle(linewidth=2, symbol=".")
        self.__plot.setDefaultDataMargins(*self.DEFAULT_DATA_MARGINS)

        self.setFocusPolicy(qt.Qt.StrongFocus)
        self.__plot.selection().sigCurrentItemChanged.connect(self.__selectionChanged)
        self.__view = view_manager.ViewManager(self.__plot)
        self.__theme = viewer_theme.ViewerTheme(self)
        self.__selectedPlotItem = None
        self.__selectedScan: scan_model.Scan | None = None

        self.__aggregator = viewer_events.ScalarEventAggregator(self)
        self.__refreshManager = refresh_manager.RefreshManager(self)
        self.__refreshManager.setAggregator(self.__aggregator)

        toolBar = self.__createToolBar()

        # Try to improve the look and feel
        # FIXME: This should be done with stylesheet
        line = qt.QFrame(self)
        line.setFrameShape(qt.QFrame.HLine)
        line.setFrameShadow(qt.QFrame.Sunken)

        frame = qt.QFrame(self)
        frame.setFrameShape(qt.QFrame.StyledPanel)
        frame.setAutoFillBackground(True)
        layout = qt.QVBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(toolBar)
        layout.addWidget(line)
        layout.addWidget(self.__plot)
        widget = qt.QFrame(self)
        layout = qt.QVBoxLayout(widget)
        layout.addWidget(frame)
        layout.setContentsMargins(0, 1, 0, 0)
        self.setWidget(widget)

        self.__tooltipManager = tooltip_item_manager.TooltipItemManager(
            self, self.__plot
        )
        self.__tooltipManager.setFilter(FlintCurve)

        self.__syncAxisTitle = signalutils.InvalidatableSignal(self)
        self.__syncAxisTitle.triggered.connect(self.__updateAxesLabel)
        self.__syncAxisItems = signalutils.InvalidatableSignal(self)
        self.__syncAxisItems.triggered.connect(self.__updateAxesItems)

        self.__boundingY1 = XAxisExtent()
        self.__boundingY1.setName("bound-y1")
        self.__boundingY1.setVisible(False)
        self.__boundingY2 = XAxisExtent()
        self.__boundingY2.setName("bound-y2")
        self.__boundingY2.setVisible(False)

        self.__plot.addItem(self.__boundingY1)
        self.__plot.addItem(self.__boundingY2)
        self.__plot.addItem(self.__tooltipManager.marker())

    def configuration(self):
        config = super(CurvePlotWidget, self).configuration()
        config.spec_mode = self.__specMode.isEnabled()
        config.x_duration = self.__xdurationAction.duration()
        config.x_duration_enabled = self.__xdurationAction.isChecked()
        config.previous_scans_displayed = self.__storePreviousScans
        config.previous_scans_stack_size = self.__maxStoredScans
        return config

    def setConfiguration(self, config):
        if config.spec_mode:
            self.__specMode.setEnabled(True)
        if config.x_duration is not None:
            self.__xdurationAction.setDuration(config.x_duration)
        if config.x_duration_enabled is not None:
            self.__xdurationAction.setChecked(config.x_duration_enabled)
        if config.previous_scans_displayed is not None:
            self.setPreviousScanStored(config.previous_scans_displayed)
        if config.previous_scans_stack_size is not None:
            self.setMaxStoredScans(config.previous_scans_stack_size)
        super(CurvePlotWidget, self).setConfiguration(config)

    def __specModeChanged(self, enabled):
        if enabled:
            self.__specMode.requestUpdateTitle(self.__plot, self.__scan, force=True)
        self.__updateTitle(self.__scan)

    def getRefreshManager(self) -> refresh_manager.RefreshManager:
        return self.__refreshManager

    def __createToolBar(self):
        toolBar = qt.QToolBar(self)
        toolBar.setMovable(False)

        from silx.gui.plot.actions import mode
        from silx.gui.plot.actions import control
        from silx.gui.widgets.MultiModeAction import MultiModeAction

        modeAction = MultiModeAction(self)
        modeAction.addAction(mode.ZoomModeAction(self.__plot, self))
        modeAction.addAction(mode.PanModeAction(self.__plot, self))
        toolBar.addAction(modeAction)

        resetZoom = self.__view.createResetZoomAction(parent=self)
        toolBar.addAction(resetZoom)

        self.__xdurationAction = duration_action.DurationAction(self)
        self.__xdurationAction.setCheckable(True)
        self.__xdurationAction.setChecked(False)
        self.__xdurationAction.setEnabled(False)
        self.__xdurationAction.addDuration("1h", 60 * 60)
        self.__xdurationAction.addDuration("30m", 30 * 60)
        self.__xdurationAction.addDuration("10m", 10 * 60)
        self.__xdurationAction.addDuration("5m", 5 * 60)
        self.__xdurationAction.addDuration("2m", 2 * 60)
        self.__xdurationAction.addDuration("1m", 1 * 60)
        self.__xdurationAction.addDuration("30s", 30)
        self.__xdurationAction.setDuration(self.DEFAULT_XDURATION)
        self.__xdurationAction.valueChanged.connect(self.__xdurationChanged)
        self.__xdurationAction.toggled.connect(self.__xdurationCheckChanged)
        toolBar.addAction(self.__xdurationAction)
        toolBar.addSeparator()

        # Axis
        action = self.__refreshManager.createRefreshAction(self)
        toolBar.addAction(action)
        toolBar.addAction(plot_action.CustomAxisAction(self.__plot, self, kind="curve"))
        toolBar.addSeparator()

        # Tools

        action = control.CrosshairAction(self.__plot, parent=self)
        action.setIcon(icons.getQIcon("flint:icons/crosshair"))
        toolBar.addAction(action)

        action = marker_action.MarkerAction(plot=self.__plot, parent=self, kind="curve")
        self.__markerAction = action
        toolBar.addAction(action)

        action = self.__plot.getCurvesRoiDockWidget().toggleViewAction()
        toolBar.addAction(action)

        action = self.__specMode.createAction()
        toolBar.addAction(action)

        action = fit.FitAction(plot=self.__plot, parent=self)
        action.setFittedItemUpdatedFromActiveCurve(True)
        action.setXRangeUpdatedOnZoom(True)
        toolBar.addAction(action)

        action = fft_action.FftAction(plot=self.__plot, parent=self)
        toolBar.addAction(action)

        toolBar.addSeparator()

        # Export

        self.__exportAction = export_action.ExportAction(self.__plot, self)
        toolBar.addAction(self.__exportAction)

        return toolBar

    def logbookAction(self):
        """Expose a logbook action if one"""
        return self.__exportAction.logbookAction()

    def _silxPlot(self):
        """Returns the silx plot associated to this view.

        It is provided without any warranty.
        """
        return self.__plot

    def plotApi(self):
        """Expose dedicated API to BLISS"""
        return self.__api

    def __onPlotPressed(self):
        self.widgetActivated.emit(self)

    def createPropertyWidget(self, parent: qt.QWidget):
        from .property import CurvePlotPropertyWidget

        propertyWidget = CurvePlotPropertyWidget(parent)
        propertyWidget.setFlintModel(self.__flintModel)
        propertyWidget.setFocusWidget(self)
        return propertyWidget

    def __findItemFromPlot(
        self, requestedItem: plot_model.Item, requestedScan: scan_model.Scan
    ):
        """Returns a silx plot item from a flint plot item and scan."""
        if requestedItem is None:
            return None
        alternative = None
        for item in self.__plot.getItems():
            if isinstance(item, FlintCurve):
                if item.customItem() is not requestedItem:
                    continue
                if item.scan() is not requestedScan:
                    if item.scan() is self.__scan:
                        alternative = item
                    continue
                return item
        return alternative

    def selectedPlotItem(self) -> plot_model.Item | None:
        """Returns the current selected plot item, if one"""
        return self.__selectedPlotItem

    def selectedScan(self) -> scan_model.Scan | None:
        """Returns the current selected scan, if one"""
        return self.__selectedScan

    def __selectionChanged(self, previous, current):
        """Callback executed when the selection from the plot was changed"""
        if self.__selectionLock.locked():
            return

        if isinstance(current, FlintCurve):
            selected = current.customItem()
            scanSelected = current.scan()
        else:
            selected = None
            scanSelected = None
        self.__selectedPlotItem = selected
        self.plotItemSelected.emit(selected)
        self.scanSelected.emit(scanSelected)
        if self.__specMode.isEnabled():
            self.__specMode.requestUpdateTitle(self.__plot, self.__scan, force=True)
            self.__updateTitle(self.__scan)

    def selectScan(self, select: scan_model.Scan):
        wasUpdated = self.__selectedScan is not select
        self.__selectedScan = select
        if wasUpdated:
            self.scanSelected.emit(select)
        self.__updatePlotWithSelectedCurve()

    def __xdurationChanged(self, duration):
        self.__updateXDuration()

    def __xdurationCheckChanged(self):
        self.__updateXDuration()

    def xDuration(self):
        if not self.__xdurationAction.isChecked():
            return None
        return self.__xdurationAction.duration()

    def __updateXDuration(self):
        if not self.__xdurationAction.isEnabled():
            d = None
        else:
            d = self.xDuration()
        self.__view.setXDuration(d)

    def setXDuration(self, duration):
        if self.xDuration() == duration:
            return
        with qtutils.blockSignals(self.__xdurationAction):
            if duration is None:
                self.__xdurationAction.setChecked(False)
            else:
                self.__xdurationAction.setChecked(True)
                self.__xdurationAction.setDuration(duration)
        self.__updateXDuration()

    def selectPlotItem(self, select: plot_model.Item | None, force=False):
        """Select a flint plot item"""
        if not force:
            if self.__selectedPlotItem is select:
                return
            if select is self.selectedPlotItem():
                # Break reentrant signals
                return
        wasUpdated = self.__selectedPlotItem is not select
        self.__selectedPlotItem = select
        self.__updatePlotWithSelectedCurve()
        if wasUpdated:
            self.plotItemSelected.emit(select)
            if self.__specMode.isEnabled():
                self.__specMode.requestUpdateTitle(self.__plot, self.__scan, force=True)

    def __updatePlotWithSelectedCurve(self):
        item = self.__findItemFromPlot(self.__selectedPlotItem, self.__selectedScan)
        # FIXME: We should not use the legend
        if item is None:
            legend = None
        else:
            legend = item.getLegend()
        with self.__selectionLock:
            self.__plot.setActiveCurve(legend)

    def flintModel(self) -> flint_model.FlintState | None:
        return self.__flintModel

    def setFlintModel(self, flintModel: flint_model.FlintState | None):
        self.__flintModel = flintModel
        self.__exportAction.setFlintModel(flintModel)

    def setPlotModel(self, plotModel: plot_model.Plot):
        if self.__plotModel is not None:
            self.__plotModel.structureChanged.disconnect(
                self.__aggregator.callbackTo(self.__structureChanged)
            )
            self.__plotModel.itemValueChanged.disconnect(
                self.__aggregator.callbackTo(self.__itemValueChanged)
            )
            self.__plotModel.transactionFinished.disconnect(
                self.__aggregator.callbackTo(self.__transactionFinished)
            )
        previousModel = self.__plotModel
        self.__plotModel = plotModel
        self.__syncStyleStrategy()
        if self.__plotModel is not None:
            self.__plotModel.structureChanged.connect(
                self.__aggregator.callbackTo(self.__structureChanged)
            )
            self.__plotModel.itemValueChanged.connect(
                self.__aggregator.callbackTo(self.__itemValueChanged)
            )
            self.__plotModel.transactionFinished.connect(
                self.__aggregator.callbackTo(self.__transactionFinished)
            )
        self.plotModelUpdated.emit(plotModel)
        self.__reselectPlotItem(previousModel, plotModel)
        self.__redrawAllScans()
        self.__syncAxisTitle.trigger()

    def __reselectPlotItem(self, previousModel, plotModel):
        """Update the plot item selection from the previous plot model to the
        new plot model"""
        if previousModel is None or plotModel is None:
            return
        selectedItem = self.__selectedPlotItem
        self.__selectedPlotItem = None
        if selectedItem is None:
            return
        try:
            expectedLabel = selectedItem.displayName("y", scan=None)
        except AttributeError:
            # FIXME: The selected item could not have Y channel.
            # This way to restore the selected item is dumb
            pass
        else:
            for item in plotModel.items():
                if isinstance(item, plot_item_model.CurveMixIn):
                    if item.isValid():
                        label = item.displayName("y", scan=None)
                        if label == expectedLabel:
                            self.selectPlotItem(item)
                            return
        self.selectPlotItem(None)

    def plotModel(self) -> plot_model.Plot | None:
        return self.__plotModel

    def __structureChanged(self):
        self.__redrawAllScans()
        self.__syncAxisTitle.trigger()

    def __transactionFinished(self):
        if self.__plotWasUpdated:
            self.__plotWasUpdated = False
            self.__view.plotUpdated()
        self.__syncAxisTitle.trigger()
        self.__syncAxisItems.trigger()

    def __itemValueChanged(
        self, item: plot_model.Item, eventType: plot_model.ChangeEventType
    ):
        assert self.__plotModel is not None
        inTransaction = self.__plotModel.isInTransaction()
        if item not in self.__plotModel:
            # Item could already be removed from the plot
            # FIXME: Such event have to be cleaned up by the event aggregator
            return
        if eventType == plot_model.ChangeEventType.VISIBILITY:
            self.__updateItem(item)
            self.__syncAxisTitle.triggerIf(not inTransaction)
        elif eventType == plot_model.ChangeEventType.YAXIS:
            self.__updateItem(item)
            self.__syncAxisTitle.triggerIf(not inTransaction)
        elif eventType == plot_model.ChangeEventType.X_CHANNEL:
            self.__updateItem(item)
            self.__syncAxisTitle.triggerIf(not inTransaction)
            self.__syncAxisItems.triggerIf(not inTransaction)
        elif eventType == plot_model.ChangeEventType.Y_CHANNEL:
            self.__updateItem(item)
            self.__syncAxisTitle.triggerIf(not inTransaction)

    def __updateAxesLabel(self):
        scan = self.__scan
        plot = self.__plotModel
        xAxis = None
        if plot is None:
            xLabel = ""
            y1Label = ""
            y2Label = ""
        else:
            xLabels = []
            y1Labels = []
            y2Labels = []
            for item in plot.items():
                if not item.isValid():
                    continue
                if not item.isVisible():
                    continue

                if isinstance(item, plot_item_model.CurveItem):
                    xChannel = item.xChannel()
                    if xChannel is not None:
                        if not isinstance(xChannel, plot_model.XIndexChannelRef):
                            xAxis = xChannel.channel(scan)
                        xLabels.append(xChannel.displayName(scan))
                    yChannel = item.yChannel()
                    if yChannel is not None:
                        if item.yAxis() == "left":
                            y1Labels.append(yChannel.displayName(scan))
                        elif item.yAxis() == "right":
                            y2Labels.append(yChannel.displayName(scan))
                        else:
                            assert False
                    else:
                        pass
            xLabel = " + ".join(sorted(set(xLabels)))
            y1Label = " + ".join(sorted(set(y1Labels)))
            y2Label = " + ".join(sorted(set(y2Labels)))
        self.__plot.getXAxis().setLabel(xLabel)
        self.__plot.getYAxis(axis="left").setLabel(y1Label)
        self.__plot.getYAxis(axis="right").setLabel(y2Label)

        axis = self.__plot.getXAxis()
        if xAxis is not None:
            if xAxis.unit() == "s":
                # FIXME: There is no metadata for time and duration
                if "elapse" in xAxis.name():
                    # NOTE: There is no plot axis for duration
                    # the elapse time will be displayed in 1970
                    # the UTC force to display 0 at 0
                    axis.setTickMode(axis_mdl.TickMode.TIME_SERIES)
                    axis.setTimeZone("UTC")
                else:
                    axis.setTickMode(axis_mdl.TickMode.TIME_SERIES)
                    axis.setTimeZone(None)  # Use the local timezone
                self.__xdurationAction.setEnabled(True)
                self.__updateXDuration()
            else:
                axis.setTickMode(axis_mdl.TickMode.DEFAULT)
                self.__xdurationAction.setEnabled(False)
                self.__updateXDuration()
        else:
            axis.setTickMode(axis_mdl.TickMode.DEFAULT)
            self.__xdurationAction.setEnabled(False)
            self.__updateXDuration()

    def __updateAxesItems(self):
        """Update items which have relation with the X axis"""
        self.__curveAxesUpdated()
        scan = self.__scan
        if scan is None:
            return
        if self.__specMode.isEnabled():
            self.__specMode.requestUpdateTitle(self.__plot, self.__scan, force=True)
            self.__updateTitle(scan)
        plotModel = self.__plotModel
        if plotModel is None:
            return
        for item in plotModel.items():
            # FIXME: Use a better abstract concept for that
            if isinstance(item, plot_item_model.AxisPositionMarker):
                self.__updatePlotItem(item, scan)
        self.__view.resetZoom()

    def __reachRangeForYAxis(self, plot, scan, yAxis) -> tuple[float, float] | None:
        xAxis: set[scan_model.Channel | None] = set([])
        for item in plot.items():
            if isinstance(item, plot_item_model.CurveItem):
                if item.yAxis() != yAxis:
                    continue
                xChannel = item.xChannel()
                if xChannel is not None:
                    if not isinstance(xChannel, plot_model.XIndexChannelRef):
                        xAxis.add(xChannel.channel(scan))
        xAxis.discard(None)
        if len(xAxis) == 0:
            return None

        def getRange(axis: Sequence[scan_model.Channel]):
            vv: set[float | None] = set()
            for a in axis:
                metadata = a.metadata()
                v = set([metadata.start, metadata.stop, metadata.min, metadata.max])
                vv.update(v)

            vv.discard(None)
            vvv = cast(set[float], vv)  # The None was discaded

            if len(vvv) == 0:
                return None, None
            return min(vvv), max(vvv)

        xRange = getRange(list(xAxis))
        if xRange[0] is None:
            return None
        return xRange[0], xRange[1]

    def __curveAxesUpdated(self):
        scan = self.__scan
        plot = self.__plotModel
        if plot is None or scan is None:
            return

        result_l = self.__reachRangeForYAxis(plot, scan, "left")
        if result_l is None:
            self.__boundingY1.setVisible(False)
        else:
            xMin, xMax = result_l
            self.__boundingY1.setRange(xMin, xMax)
            self.__boundingY1.setVisible(True)

        result_r = self.__reachRangeForYAxis(plot, scan, "right")
        if result_r is None:
            self.__boundingY2.setVisible(False)
        else:
            xMin, xMax = result_r
            self.__boundingY2.setRange(xMin, xMax)
            self.__boundingY2.setVisible(True)

    def scanList(self):
        return [i.scan() for i in self.__scanItems]

    def scanItemList(self):
        return list(self.__scanItems)

    def removeScan(self, scan):
        if scan is None:
            return
        if scan is self.__scan:
            _logger.warning("Removing the current scan is not available")
            return
        scanItems = [i for i in self.__scanItems if i.scan() is scan]
        if len(scanItems) == 0:
            return
        scanItem = scanItems[0]
        self.__scanItems.remove(scanItem)
        self.__syncStyleStrategy()
        scanItem.deleteLater()
        self.scanListUpdated.emit(self.scanList())
        self.__redrawAllScans()

    def insertScan(self, scan):
        if scan is None:
            return
        if scan is self.__scan:
            _logger.warning("Removing the current scan is not available")
            return
        scanItem = plot_item_model.ScanItem(self, scan)
        scanItem.valueChanged.connect(self.__scanItemUpdated)
        self.__scanItems.append(scanItem)
        self.__scanItems = list(
            reversed(sorted(self.__scanItems, key=lambda i: i.scan().startTime()))
        )
        self.__syncStyleStrategy()
        self.scanListUpdated.emit(self.scanList())
        self.__redrawAllScans()

    def setMaxStoredScans(self, maxScans: int):
        # FIXME: Must emit event
        self.__maxStoredScans = maxScans

    def maxStoredScans(self) -> int:
        return self.__maxStoredScans

    def setPreviousScanStored(self, storeScans: bool):
        # FIXME: Must emit event
        self.__storePreviousScans = storeScans
        self.__syncStyleStrategy()

    def isPreviousScanStored(self) -> bool:
        return self.__storePreviousScans

    @property
    def __scan(self):
        scans = self.scanList()
        if len(scans) == 0:
            return None
        else:
            return scans[0]

    def scan(self) -> scan_model.Scan | None:
        return self.__scan

    def setScan(self, scan: scan_model.Scan | None):
        if self.__scan is scan:
            return
        if self.__scan is not None:
            self.__scan.scanDataUpdated[object].disconnect(
                self.__aggregator.callbackTo(self.__scanDataUpdated)
            )
            self.__scan.scanStarted.disconnect(
                self.__aggregator.callbackTo(self.__scanStarted)
            )
            self.__scan.scanFinished.disconnect(
                self.__aggregator.callbackTo(self.__scanFinished)
            )
        if self.__storePreviousScans:
            if scan is not None:
                item = plot_item_model.ScanItem(self, scan)
                item.valueChanged.connect(self.__scanItemUpdated)
                self.__scanItems.insert(0, item)
            while len(self.__scanItems) > self.__maxStoredScans:
                i = self.__scanItems.pop(-1)
                i.deleteLater()
        else:
            if scan is not None:
                while len(self.__scanItems):
                    i = self.__scanItems.pop(-1)
                    i.deleteLater()
                item = plot_item_model.ScanItem(self, scan)
                item.valueChanged.connect(self.__scanItemUpdated)
                self.__scanItems.append(item)
        self.__syncStyleStrategy()
        self.scanListUpdated.emit(self.scanList())
        self.__selectedScan = self.__scan
        self.scanSelected.emit(self.__scan)
        if self.__scan is not None:
            self.__scan.scanDataUpdated[object].connect(
                self.__aggregator.callbackTo(self.__scanDataUpdated)
            )
            self.__scan.scanStarted.connect(
                self.__aggregator.callbackTo(self.__scanStarted)
            )
            self.__scan.scanFinished.connect(
                self.__aggregator.callbackTo(self.__scanFinished)
            )
            if self.__scan.state() != scan_model.ScanState.INITIALIZED:
                self.__updateTitle(self.__scan)
        self.scanModelUpdated.emit(scan)
        if scan is not None and self.__specMode.isEnabled():
            self.__specMode.requestUpdateTitle(self.__plot, self.__scan, force=True)
        self.__updateTitle(scan)
        self.__redrawAllScans()
        self.__syncAxisTitle.trigger()

    def __scanItemUpdated(self):
        scanItem = self.sender()
        scan = scanItem.scan()
        if self.__specMode.isEnabled():
            self.__specMode.requestUpdateTitle(self.__plot, self.__scan)
        self.__redrawScan(scan)

    def __syncStyleStrategy(self):
        if self.__plotModel is not None:
            styleStrategy = self.__plotModel.styleStrategy()
            if styleStrategy is not None:
                if self.__storePreviousScans:
                    styleStrategy.setScans(self.scanList())
                else:
                    styleStrategy.setScans([])

    def __cleanScanIfNeeded(self, scan):
        plotModel = self.__plotModel
        if plotModel is None:
            self.__cleanScan(scan)
            return
        for item in plotModel.items():
            if isinstance(item, plot_item_model.ScanItem):
                if item.scan() is scan:
                    return
        self.__cleanScan(scan)

    def __scanStarted(self):
        self.__specMode.clear()
        self.__markerAction.clear()
        self.__updateTitle(self.__scan)
        self.__curveAxesUpdated()
        self.viewerEvent.emit(
            viewer_events.ScanViewerEvent(
                viewer_events.ViewerEventType.SCAN_STARTED, self.__scan
            )
        )

    def __scanFinished(self):
        self.__refreshManager.scanFinished()
        self.viewerEvent.emit(
            viewer_events.ScanViewerEvent(
                viewer_events.ViewerEventType.SCAN_FINISHED, self.__scan
            )
        )
        self.__specMode.requestUpdateTitle(self.__plot, self.__scan, force=True)
        self.__updateTitle(self.__scan)

    def __updateTitle(self, scan: scan_model.Scan | None):
        if scan is None:
            self.__title = "No scan"
        else:
            self.__title = scan_info_helper.get_full_title(scan)
        self.__updatePlotTitle()

    def __updatePlotTitle(
        self,
    ):
        if self.__specMode.isEnabled():
            state = self.__specMode.lastTitle()
        else:
            state = ""
        if state != "":
            title = f"{self.__title}\n{state}"
        else:
            title = self.__title
        self.__plot.setGraphTitle(title)

    def __scanDataUpdated(self, event: scan_model.ScanDataUpdateEvent):
        scan = self.__scan
        if scan is None:
            return
        plotModel = self.__plotModel
        if plotModel is None:
            return
        for item in plotModel.items():
            if isinstance(item, plot_item_model.CurveItem):
                if item.isValid():
                    xName = item.xChannel().name() if item.xChannel() else ""
                    yName = item.yChannel().name() if item.yChannel() else ""
                    if event.isUpdatedChannelName(xName) or event.isUpdatedChannelName(
                        yName
                    ):
                        self.__updatePlotItem(item, scan)
            elif isinstance(item, plot_model.ChildItem):
                if item.isValid():
                    sources = item.inputData()
                    for source in sources:
                        if source is not None:
                            if event.isUpdatedChannelName(source):
                                self.__updatePlotItem(item, scan)
                                break
        if self.__specMode.isEnabled():
            self.__specMode.requestUpdateTitle(self.__plot, self.__scan)
            self.__updateTitle(scan)

    def __redrawCurrentScan(self):
        currentScan = self.__scan
        if currentScan is None:
            return
        self.__redrawScan(currentScan)

    def __redrawAllScans(self):
        with qtutils.blockSignals(self.__plot):
            self.__cleanAllItems()
            if self.__plotModel is None:
                return

        with qtutils.blockSignals(self):
            scanItems = []
            plotModel = self.__plotModel
            for item in plotModel.items():
                if isinstance(item, plot_item_model.ScanItem):
                    scanItems.append(item)

            if len(scanItems) > 0:
                for scan in scanItems:
                    self.__redrawScan(scan.scan())
            else:
                for item in self.__scanItems:
                    self.__redrawScan(item.scan())

    def __cleanScan(self, scan: scan_model.Scan):
        items = self.__items.pop(scan, {})
        for _item, itemKeys in items.items():
            for key in itemKeys:
                self.__plot.remove(*key)
        for curve in self.__plot.getAllCurves():
            legend = curve.getName()
            if legend.startswith("Fit "):
                # Guess it's a fit from silx
                self.__plot.removeCurve(legend)
        self.__view.plotCleared()

    def __cleanAllItems(self):
        for _scan, items in self.__items.items():
            for _item, itemKeys in items.items():
                for key in itemKeys:
                    self.__plot.remove(*key)
        self.__items.clear()

    def __cleanScanItem(self, item: plot_model.Item, scan: scan_model.Scan) -> bool:
        itemKeys = self.__items.get(scan, {}).pop(item, [])
        if len(itemKeys) == 0:
            return False
        for key in itemKeys:
            self.__plot.remove(*key)
        return True

    def __redrawScan(self, scan: scan_model.Scan):
        assert scan is not None

        with qtutils.blockSignals(self.__plot):
            self.__cleanScan(scan)

        scanItem = [i for i in self.__scanItems if i.scan() is scan]
        if len(scanItem) > 0 and not scanItem[0].isVisible():
            return

        with qtutils.blockSignals(self):
            plotModel = self.__plotModel
            if plotModel is None:
                return

            for item in plotModel.items():
                self.__updatePlotItem(item, scan)

    def __updateItem(self, item: plot_model.Item):
        if self.__plotModel is None:
            return

        selectedPlotItem = self.selectedPlotItem()
        if item is selectedPlotItem:
            reselect = item
        else:
            reselect = None

        with qtutils.blockSignals(self):
            scanItems = []
            plotModel = self.__plotModel
            for scanItem in plotModel.items():
                if isinstance(scanItem, plot_item_model.ScanItem):
                    scanItems.append(scanItem)

            if len(scanItems) > 0:
                for scan in scanItems:
                    self.__updatePlotItem(item, scan.scan())
            else:
                for scanItem in self.__scanItems:
                    self.__updatePlotItem(item, scanItem.scan())

            if reselect is not None:
                self.selectPlotItem(reselect)

    def __updatePlotItem(self, item: plot_model.Item, scan: scan_model.Scan):
        if not item.isValid():
            return
        if isinstance(item, plot_item_model.ScanItem):
            return
        assert self.__plotModel is not None

        plot = self.__plot
        plotItems: list[tuple[str, str]] = []

        updateZoomNow = not self.__plotModel.isInTransaction()

        with qtutils.blockSignals(self.__plot):
            wasUpdated = self.__cleanScanItem(item, scan)

        if not item.isVisible():
            if wasUpdated:
                self.__updatePlotZoom(updateZoomNow)
            return

        if not item.isValidInScan(scan):
            if wasUpdated:
                self.__updatePlotZoom(updateZoomNow)
            return

        if isinstance(item, plot_item_model.CurveMixIn):
            if isinstance(item, plot_item_model.CurveItem):
                x = item.xChannel()
                if x is None:
                    xName = "none"
                else:
                    xName = x.name()
                y = item.yChannel()
                # FIXME: remove legend, use item mapping
                legend = f"{scan.scanId()}/{xName}/{y.name()}"
            else:
                legend = str(item) + "/" + str(scan)
            xx = item.xArray(scan)
            yy = item.yArray(scan)
            if xx is None or yy is None:
                # FIXME: the item legend have to be removed
                return

            style = item.getStyle(scan)
            curveItem = FlintCurve()
            curveItem.setCustomItem(item)
            curveItem.setScan(scan)
            curveItem.setData(x=xx, y=yy, copy=False)
            curveItem.setName(legend)
            curveItem.setLineStyle(style.lineStyle)
            curveItem.setColor(style.lineColor)
            curveItem.setSymbol("")
            curveItem.setYAxis(item.yAxis())
            plot.addItem(curveItem)
            plotItems.append((legend, "curve"))

        elif isinstance(item, plot_item_model.CurveStatisticItem):
            if isinstance(item, MaxCurveItem):
                legend = str(item) + "/" + str(scan)
                result = item.reachResult(scan)
                if item.isResultValid(result):
                    style = item.getStyle(scan)
                    height = result.max_location_y - result.min_y_value
                    xx = numpy.array([result.max_location_x, result.max_location_x])
                    text_location_y = result.max_location_y + height * 0.1
                    yy = numpy.array([result.max_location_y, text_location_y])

                    curveItem = Curve()
                    curveItem.setData(x=xx, y=yy, copy=False)
                    curveItem.setName(legend)
                    curveItem._setSelectable(False)
                    curveItem.setLineStyle(style.lineStyle)
                    curveItem.setColor(style.lineColor)
                    curveItem.setSymbol("")
                    curveItem.setYAxis(item.yAxis())
                    plot.addItem(curveItem)
                    plotItems.append((legend, "curve"))
                    key = plot.addMarker(
                        legend=legend + "_text",
                        x=result.max_location_x,
                        y=text_location_y,
                        symbol=",",
                        text="max",
                        color=style.lineColor,
                        yaxis=item.yAxis(),
                    )
                    plotItems.append((key, "marker"))
                    key = plot.addMarker(
                        legend=legend + "_pos",
                        x=result.max_location_x,
                        y=result.max_location_y,
                        symbol="x",
                        text="",
                        color=style.lineColor,
                        yaxis=item.yAxis(),
                    )
                    plotItems.append((key, "marker"))
            elif isinstance(item, MinCurveItem):
                legend = str(item) + "/" + str(scan)
                result = item.reachResult(scan)
                if item.isResultValid(result):
                    style = item.getStyle(scan)
                    height = result.max_y_value - result.min_location_y
                    xx = numpy.array([result.min_location_x, result.min_location_x])
                    text_location_y = result.min_location_y - height * 0.1
                    yy = numpy.array([result.min_location_y, text_location_y])

                    curveItem = Curve()
                    curveItem.setData(x=xx, y=yy, copy=False)
                    curveItem.setName(legend)
                    curveItem._setSelectable(False)
                    curveItem.setLineStyle(style.lineStyle)
                    curveItem.setColor(style.lineColor)
                    curveItem.setSymbol("")
                    curveItem.setYAxis(item.yAxis())
                    plot.addItem(curveItem)
                    plotItems.append((legend, "curve"))
                    key = plot.addMarker(
                        legend=legend + "_text",
                        x=result.min_location_x,
                        y=text_location_y,
                        symbol=",",
                        text="min",
                        color=style.lineColor,
                        yaxis=item.yAxis(),
                    )
                    plotItems.append((key, "marker"))
                    key = plot.addMarker(
                        legend=legend + "_pos",
                        x=result.min_location_x,
                        y=result.min_location_y,
                        symbol="x",
                        text="",
                        color=style.lineColor,
                        yaxis=item.yAxis(),
                    )
                    plotItems.append((key, "marker"))

        elif isinstance(item, plot_item_model.AxisPositionMarker):
            if item.isValid():
                model = self.__plotModel
                if model_helper.isChannelUsedAsAxes(
                    model, item.motorChannel().channel(scan)
                ):
                    legend = str(item) + "/" + str(scan)
                    key = plot.addXMarker(
                        legend=legend + "_text",
                        x=item.position(),
                        text=item.text(),
                        color="black",
                    )
                    plotItems.append((key, "marker"))

        if scan not in self.__items:
            self.__items[scan] = {}
        self.__items[scan][item] = plotItems

        if self.selectedPlotItem() is item:
            self.selectPlotItem(item, True)

        self.__updatePlotZoom(updateZoomNow)

    def __updatePlotZoom(self, updateZoomNow):
        if updateZoomNow:
            self.__view.plotUpdated()
        else:
            self.__plotWasUpdated = True

    def getXAxisScale(self):
        """Used as remote API"""
        plot = self._silxPlot()
        return "log" if plot.isXAxisLogarithmic() else "linear"

    def setXAxisScale(self, scale):
        """Used as remote API"""
        assert scale in ["log", "linear"]
        plot = self._silxPlot()
        plot.setXAxisLogarithmic(scale == "log")

    def getYAxisScale(self):
        """Used as remote API"""
        plot = self._silxPlot()
        return "log" if plot.isYAxisLogarithmic() else "linear"

    def setYAxisScale(self, scale):
        """Used as remote API"""
        assert scale in ["log", "linear"]
        plot = self._silxPlot()
        plot.setYAxisLogarithmic(scale == "log")
