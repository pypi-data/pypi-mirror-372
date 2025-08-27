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
from silx.gui.plot.items.shape import BoundingRect

from bliss.flint.model import scan_model
from bliss.flint.model import flint_model
from bliss.flint.model import plot_model
from bliss.flint.model import plot_item_model
from bliss.flint.helper import scan_info_helper
from bliss.flint.utils import signalutils
from bliss.flint.widgets.viewer.viewer_dock import ViewerDock
from bliss.flint.widgets.viewer import flint_plot
from bliss.flint.widgets.viewer import viewer_events
from bliss.flint.widgets.viewer import viewer_theme
from bliss.flint.widgets.viewer import view_manager
from bliss.flint.widgets.viewer import refresh_manager
from bliss.flint.widgets.viewer import tooltip_item_manager
from bliss.flint.widgets.viewer.items.flint_curve import FlintCurve
from bliss.flint.widgets.viewer.actions import export_action
from bliss.flint.widgets.viewer.actions import plot_action
from bliss.flint.widgets import interfaces
from .viewer_api import OneDimPlotWidgetApi


_logger = logging.getLogger(__name__)


class _Title:
    def __init__(self, plot):
        self.__plot = plot

        self.__hasPreviousImage: bool = False
        """Remember that there was an image before this scan, to avoid to
        override the title at startup and waiting for the first image"""
        self.__lastSubTitle = None
        """Remembers the last subtitle in case it have to be reuse when
        displaying the data from the previous scan"""

    def itemUpdated(self, scan, item: plot_model.Item):
        self.__updateAll(scan, item)

    def scanRemoved(self, scan):
        """Removed scan, just before using another scan"""
        if scan is not None:
            self.__updateTitle("From previous scan")
            self.__hasPreviousImage = True
        else:
            self.__hasPreviousImage = False

    def scanStarted(self, scan):
        if not self.__hasPreviousImage:
            self.__updateAll(scan)

    def scanFinished(self, scan):
        title = scan_info_helper.get_full_title(scan)
        if scan.state() == scan_model.ScanState.FINISHED:
            title += " (finished)"
        self.__updateTitle(title)

    def __formatItemTitle(self, scan: scan_model.Scan, item=None):
        if item is None:
            return None
        channel = item.yChannel()
        if channel is None:
            return None

        frameInfo = ""
        displayName = channel.displayName(scan)
        data = channel.data(scan)
        if data is not None:

            if data.frameId() is not None:
                frameInfo = f", id={data.frameId()}"
        return f"{displayName}{frameInfo}"

    def __updateTitle(self, title):
        subtitle = None
        if self.__lastSubTitle is not None:
            subtitle = self.__lastSubTitle
        if subtitle is not None:
            title = f"{title}\n{subtitle}"
        self.__plot.setGraphTitle(title)

    def __updateAll(self, scan: scan_model.Scan, item: plot_model.Item | None = None):
        title = scan_info_helper.get_full_title(scan)
        subtitle = None
        itemTitle = self.__formatItemTitle(scan, item)
        self.__lastSubTitle = itemTitle
        if itemTitle is not None:
            subtitle = f"{itemTitle}"
        if subtitle is not None:
            title = f"{title}\n{subtitle}"
        self.__plot.setGraphTitle(title)


class OneDimDataPlotWidget(
    ViewerDock,
    interfaces.HasPlotModel,
    interfaces.HasScan,
    interfaces.HasDeviceName,
):

    DEFAULT_DATA_MARGINS = 0.02, 0.02, 0.1, 0.1

    def __init__(self, parent=None):
        super(OneDimDataPlotWidget, self).__init__(parent=parent)
        self.__scan: scan_model.Scan | None = None
        self.__flintModel: flint_model.FlintState | None = None
        self.__plotModel: plot_model.Plot | None = None
        self.__deviceName: str | None = None
        self.__api = OneDimPlotWidgetApi(self)

        self.__items: dict[plot_model.Item, list[tuple[str, str]]] = {}

        self.__plotWasUpdated: bool = False
        self.__plot = flint_plot.FlintPlot(parent=self)
        self.__plot.sigMousePressed.connect(self.__onPlotPressed)
        self.__plot.setActiveCurveStyle(linewidth=2, symbol=".")
        self.__plot.setDefaultDataMargins(*self.DEFAULT_DATA_MARGINS)

        self.__title = _Title(self.__plot)

        self.setFocusPolicy(qt.Qt.StrongFocus)
        self.__view = view_manager.ViewManager(self.__plot)
        self.__theme = viewer_theme.ViewerTheme(self)

        self.__aggregator = viewer_events.PlotEventAggregator(self)
        self.__refreshManager = refresh_manager.RefreshManager(self)
        self.__refreshManager.setAggregator(self.__aggregator)

        toolBar = self.__createToolBar()

        # Try to improve the look and feel
        # FIXME: THis should be done with stylesheet
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

        self.__bounding = BoundingRect()
        self.__bounding.setName("bound")

        self.__plot.addItem(self.__bounding)
        self.__plot.addItem(self.__tooltipManager.marker())

    def plotApi(self):
        """Expose dedicated API to BLISS"""
        return self.__api

    def deviceName(self):
        return self.__deviceName

    def setDeviceName(self, name):
        self.__deviceName = name

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
        action = self.__plot.getCurvesRoiDockWidget().toggleViewAction()
        action.setToolTip(action.toolTip() + " (not yet implemented)")
        action.setEnabled(False)
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

    def __onPlotPressed(self):
        self.widgetActivated.emit(self)

    def createPropertyWidget(self, parent: qt.QWidget):
        from .property import OneDimPlotPropertyWidget

        propertyWidget = OneDimPlotPropertyWidget(parent)
        propertyWidget.setFlintModel(self.__flintModel)
        propertyWidget.setFocusWidget(self)
        return propertyWidget

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
        self.__plotModel = plotModel
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
        self.__redrawAll()
        self.__syncAxisTitle.trigger()

    def plotModel(self) -> plot_model.Plot | None:
        return self.__plotModel

    def __structureChanged(self):
        self.__redrawAll()
        self.__syncAxisTitle.trigger()

    def __transactionFinished(self):
        if self.__plotWasUpdated:
            self.__plotWasUpdated = False
            self.__view.plotUpdated()
        self.__syncAxisTitle.validate()

    def __itemValueChanged(
        self, item: plot_model.Item, eventType: plot_model.ChangeEventType
    ):
        assert self.__plotModel is not None
        inTransaction = self.__plotModel.isInTransaction()
        if eventType == plot_model.ChangeEventType.VISIBILITY:
            self.__updateItem(item)
            self.__syncAxisTitle.triggerIf(not inTransaction)
        elif eventType == plot_model.ChangeEventType.X_CHANNEL:
            self.__updateItem(item)
            self.__syncAxisTitle.triggerIf(not inTransaction)
        elif eventType == plot_model.ChangeEventType.Y_CHANNEL:
            self.__updateItem(item)
            self.__syncAxisTitle.triggerIf(not inTransaction)

    def __updateAxesLabel(self):
        scan = self.__scan
        plot = self.__plotModel
        if plot is None:
            label = ""
        else:
            labels = []
            for item in plot.items():
                if not item.isValid():
                    continue
                if not item.isVisible():
                    continue
                if isinstance(item, plot_item_model.CurveItem):
                    labels.append(item.yChannel().displayName(scan))
            label = " + ".join(sorted(set(labels)))
        self.__plot.getYAxis().setLabel(label)

    def scan(self) -> scan_model.Scan | None:
        return self.__scan

    def setScan(self, scan: scan_model.Scan | None = None):
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
        self.__title.scanRemoved(self.__scan)
        self.__scan = scan
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
                self.__title.scanStarted(self.__scan)
        self.scanModelUpdated.emit(scan)
        self.__redrawAll()

    def __scanStarted(self):
        self.__title.scanStarted(self.__scan)
        self.viewerEvent.emit(
            viewer_events.ScanViewerEvent(
                viewer_events.ViewerEventType.SCAN_STARTED, self.__scan
            )
        )

    def __scanFinished(self):
        self.__refreshManager.scanFinished()
        self.__title.scanFinished(self.__scan)
        self.viewerEvent.emit(
            viewer_events.ScanViewerEvent(
                viewer_events.ViewerEventType.SCAN_FINISHED, self.__scan
            )
        )

    def __scanDataUpdated(self, event: scan_model.ScanDataUpdateEvent):
        plotModel = self.__plotModel
        if plotModel is None:
            return
        for item in plotModel.items():
            if isinstance(item, plot_item_model.CurveItem):
                channelName = item.yChannel().name()
                if event.isUpdatedChannelName(channelName):
                    self.__updateItem(item)

    def __cleanAll(self):
        for _item, itemKeys in self.__items.items():
            for key in itemKeys:
                self.__plot.remove(*key)
        self.__view.plotCleared()

    def __cleanItem(self, item: plot_model.Item) -> bool:
        itemKeys = self.__items.pop(item, [])
        if len(itemKeys) == 0:
            return False
        for key in itemKeys:
            self.__plot.remove(*key)
        return True

    def __redrawAll(self):
        self.__cleanAll()
        plotModel = self.__plotModel
        if plotModel is None:
            return

        for item in plotModel.items():
            self.__updateItem(item)

    def __updateItem(self, item: plot_model.Item):
        if self.__plotModel is None:
            return
        if self.__scan is None:
            return
        if not item.isValid():
            return
        if not isinstance(item, plot_item_model.CurveItem):
            return

        scan = self.__scan
        plot = self.__plot
        plotItems: list[tuple[str, str]] = []

        updateZoomNow = not self.__plotModel.isInTransaction()

        wasUpdated = self.__cleanItem(item)

        if not item.isVisible():
            if wasUpdated:
                self.__updatePlotZoom(updateZoomNow)
            return

        if not item.isValidInScan(scan):
            if wasUpdated:
                self.__updatePlotZoom(updateZoomNow)
            return

        xData = item.xData(scan)
        yData = item.yData(scan)
        if xData is None or yData is None:
            if wasUpdated:
                self.__updatePlotZoom(updateZoomNow)
            return

        self.__title.itemUpdated(scan, item)

        x = xData.array()
        y = yData.array()
        if x is None or y is None:
            if wasUpdated:
                self.__updatePlotZoom(updateZoomNow)
            return

        legend = item.displayName("y", scan)
        style = item.getStyle(self.__scan)

        curveItem = FlintCurve()
        curveItem.setData(x, y, copy=False)
        curveItem.setName(legend)
        curveItem.setLineStyle(style.lineStyle)
        if len(x) == 1:
            curveItem.setSymbol(".")
        else:
            curveItem.setSymbol("")
        curveItem.setColor(style.lineColor)
        curveItem.setCustomItem(item)
        plot.addItem(curveItem)

        plotItems.append((legend, "curve"))

        self.__items[item] = plotItems
        self.__updatePlotZoom(updateZoomNow)

    def __updatePlotZoom(self, updateZoomNow):
        if updateZoomNow:
            self.__view.plotUpdated()
        else:
            self.__plotWasUpdated = True
