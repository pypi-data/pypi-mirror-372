# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

from __future__ import annotations

import numpy
from numpy.polynomial.polynomial import polyval
import logging
import enum

from silx.gui import qt
from silx.gui import icons
from silx.gui import colors

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
from bliss.flint.widgets.viewer.items.flint_raw_mca import FlintRawMca
from bliss.flint.widgets.viewer.items.flint_stack_of_raw_mca import FlintStackOfRawMca
from bliss.flint.widgets.viewer.items.flint_energy_mca import FlintEnergyMca
from bliss.flint.widgets.viewer.actions import export_action
from bliss.flint.widgets.viewer.actions import plot_action
from bliss.flint.widgets.viewer.actions import mca_user_calibration_action
from bliss.flint.widgets.viewer.actions import style_action
from bliss.flint.widgets import interfaces

from .viewer_api import McaPlotWidgetApi


_logger = logging.getLogger(__name__)


class DisplayMode(enum.Enum):
    SPECTRUM = 0
    IMAGE = 1


class XAxisMode(enum.Enum):
    CHANNEL = 0
    """Displays the channels bins"""

    ENERGY_USER_CALIBRATION = 1
    """Displays the energy from a polynomial user calibration"""

    ENERGY_FROM_METADATA = 2
    """Displays the energy from a channel metadata"""


class _DisplayModeAction(qt.QAction):
    valueChanged = qt.Signal(DisplayMode)

    def __init__(self, parent=None):
        super(_DisplayModeAction, self).__init__(parent)
        self.__value: DisplayMode | None = None
        self.__values: dict[DisplayMode, tuple[str, qt.QIcon]] = {
            DisplayMode.SPECTRUM: (
                "As spectrum",
                icons.getQIcon("flint:icons/channel-spectrum"),
            ),
            DisplayMode.IMAGE: (
                "As an image",
                icons.getQIcon("flint:icons/channel-spectrum-d-c"),
            ),
        }

        self.__menu = qt.QMenu(parent)
        self.__menu.aboutToShow.connect(self.__menuAboutToShow)
        self.setMenu(self.__menu)
        self.setValue(DisplayMode.SPECTRUM)

    def __menuAboutToShow(self):
        menu = self.sender()
        menu.clear()
        currentValue = self.__value
        currentWasFound = False
        group = qt.QActionGroup(menu)
        group.setExclusive(True)
        for value, (label, icon) in self.__values.items():
            action = qt.QAction()
            action.setText(label)
            action.setData(value)
            action.setIcon(icon)
            action.setCheckable(True)
            if currentValue == value:
                action.setChecked(True)
                currentWasFound = True
            group.addAction(action)
            menu.addAction(action)
        if currentValue is not None and not currentWasFound:
            menu.addSeparator()
            action = qt.QAction()
            action.setText(self.__values.get(currentValue, currentValue))
            action.setData(currentValue)
            action.setCheckable(True)
            action.setChecked(True)
            currentWasFound = True
            group.addAction(action)
            menu.addAction(action)

        group.triggered.connect(self.__actionSelected)

    def __actionSelected(self, action):
        v = action.data()
        self.setValue(v)

    def setValue(self, value: DisplayMode):
        if self.__value is value:
            return
        self.__value = value
        self.__updateLookAndFeel()
        self.valueChanged.emit(value)

    def value(self) -> DisplayMode:
        """Return the selected value"""
        return self.__value

    def __updateLookAndFeel(self):
        value = self.__value
        label, icon = self.__values.get(value, (None, None))
        if icon is None:
            icon = qt.QIcon()
        if label is None:
            label = value
        self.setIcon(icon)
        self.setText(label)


class McaPlotWidget(
    ViewerDock,
    interfaces.HasPlotModel,
    interfaces.HasScan,
    interfaces.HasDeviceName,
):
    DEFAULT_DATA_MARGINS = 0.02, 0.02, 0.1, 0.1

    sigXAxisMode = qt.Signal(XAxisMode)

    def __init__(self, parent=None):
        super(McaPlotWidget, self).__init__(parent=parent)
        self.__scan: scan_model.Scan | None = None
        self.__flintModel: flint_model.FlintState | None = None
        self.__plotModel: plot_model.Plot | None = None
        self.__deviceName: str | None = None
        self.__api = McaPlotWidgetApi(self)

        self.__colormap = colors.Colormap("viridis")
        """Each detector have a dedicated widget and a dedicated colormap"""

        self.__items: dict[plot_model.Item, list[tuple[str, str]]] = {}

        self.__plotWasUpdated: bool = False
        self.__plot = flint_plot.FlintPlot(parent=self)
        self.__plot.sigMousePressed.connect(self.__onPlotPressed)
        self.__plot.setActiveCurveStyle(linewidth=2)
        self.__plot.setDefaultDataMargins(*self.DEFAULT_DATA_MARGINS)

        self.__userCalibration = None
        self.__xAxisMode = XAxisMode.CHANNEL

        self.__initializeModeWhenDataIsReceived = False

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
        self.__tooltipManager.setFilter([FlintRawMca, FlintStackOfRawMca])

        self.__syncAxisTitle = signalutils.InvalidatableSignal(self)
        self.__syncAxisTitle.triggered.connect(self.__updateAxesLabel)

        self.__plot.addItem(self.__tooltipManager.marker())

        self.widgetActivated.connect(self.__activated)

    def plotApi(self):
        """Expose dedicated API to BLISS"""
        return self.__api

    def deviceName(self):
        return self.__deviceName

    def setDeviceName(self, name):
        self.__deviceName = name
        self.__syncAxisTitle.trigger()

    def getRefreshManager(self) -> refresh_manager.RefreshManager:
        return self.__refreshManager

    def userCalibration(self) -> tuple[float, float, float] | None:
        return self.__userCalibration

    def setUserCalibration(self, calibration: tuple[float, float, float] | None):
        if self.__userCalibration == calibration:
            return
        self.__userCalibration = calibration
        if self.__userCalibration is not None:
            self.__xAxisMode = XAxisMode.ENERGY_USER_CALIBRATION
        else:
            self.__xAxisMode = XAxisMode.CHANNEL
        self.sigXAxisMode.emit(self.__xAxisMode)

        self.__updateAxesLabel()
        self.__redrawAll()

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
        toolBar.addAction(plot_action.CustomAxisAction(self.__plot, self, kind="mca"))
        toolBar.addSeparator()

        # View

        self.__displayModeAction = _DisplayModeAction(self)
        self.__displayModeAction.setCheckable(True)
        self.__displayModeAction.setChecked(False)
        self.__displayModeAction.setEnabled(True)
        self.__displayModeAction.valueChanged.connect(self.__displayModeChanged)
        toolBar.addAction(self.__displayModeAction)

        action = mca_user_calibration_action.McaUserCalibrationAction(self)
        toolBar.addAction(action)

        toolBar.addSeparator()

        # Tools

        action = style_action.FlintSharedColormapAction(self.__plot, self)
        action.setInitColormapWidgetCallback(self.__initColormapWidget)
        toolBar.addAction(action)
        self.__contrastAction = action

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

    def __activated(self):
        self.__initColormapWidget()

    def __initColormapWidget(self):
        flintModel = self.flintModel()
        if flintModel is None:
            return
        if self.__displayModeAction.value() != DisplayMode.IMAGE:
            return
        live = flintModel.liveWindow()
        colormapWidget = live.acquireColormapWidget(self)
        if colormapWidget is not None:
            for item in self.__plot.getItems():
                if isinstance(item, FlintStackOfRawMca):
                    colormapWidget.setItem(item)
                    break
            else:
                colormapWidget.setColormap(self.__colormap)

    def _silxPlot(self):
        """Returns the silx plot associated to this view.

        It is provided without any warranty.
        """
        return self.__plot

    def __onPlotPressed(self):
        self.widgetActivated.emit(self)

    def createPropertyWidget(self, parent: qt.QWidget):
        from .property import McaPlotPropertyWidget

        propertyWidget = McaPlotPropertyWidget(parent)
        propertyWidget.setFlintModel(self.__flintModel)
        propertyWidget.setFocusWidget(self)
        return propertyWidget

    def flintModel(self) -> flint_model.FlintState | None:
        return self.__flintModel

    def setFlintModel(self, flintModel: flint_model.FlintState | None):
        self.__flintModel = flintModel
        self.__exportAction.setFlintModel(flintModel)
        self.__contrastAction.setFlintModel(flintModel)

    def setPlotModel(self, plotModel: plot_model.Plot):
        if self.__plotModel is not None:
            self.__plotModel.structureChanged.disconnect(
                self.__aggregator.callbackTo(self.__structureChanged)
            )
            self.__plotModel.itemValueChanged.disconnect(
                self.__aggregator.callbackTo(self.__itemValueChanged)
            )
            self.__plotModel.valueChanged.disconnect(
                self.__aggregator.callbackTo(self.__valueChanged)
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
            self.__plotModel.valueChanged.connect(
                self.__aggregator.callbackTo(self.__valueChanged)
            )
            self.__plotModel.transactionFinished.connect(
                self.__aggregator.callbackTo(self.__transactionFinished)
            )
        self.plotModelUpdated.emit(plotModel)
        self.__redrawAll()
        self.__syncAxisTitle.trigger()

    def plotModel(self) -> plot_model.Plot:
        return self.__plotModel

    def __structureChanged(self):
        self.__redrawAll()
        self.__syncAxisTitle.trigger()

    def __transactionFinished(self):
        if self.__plotWasUpdated:
            self.__plotWasUpdated = False
            self.__view.plotUpdated()
        self.__syncAxisTitle.validate()

    def __displayModeChanged(self):
        displayMode = self.__displayModeAction.value()
        self.__contrastAction.setVisible(displayMode == DisplayMode.IMAGE)
        self.__updateAxesLabel()
        self.__redrawAll()

    def __itemValueChanged(
        self, item: plot_model.Item, eventType: plot_model.ChangeEventType
    ):
        assert self.__plotModel is not None
        inTransaction = self.__plotModel.isInTransaction()
        if eventType == plot_model.ChangeEventType.VISIBILITY:
            self.__redrawAll()
            self.__syncAxisTitle.triggerIf(not inTransaction)
        elif eventType == plot_model.ChangeEventType.MCA_CHANNEL:
            self.__redrawAll()
            self.__syncAxisTitle.triggerIf(not inTransaction)

    def __valueChanged(self, eventType: plot_model.ChangeEventType):
        assert self.__plotModel is not None
        inTransaction = self.__plotModel.isInTransaction()
        if eventType == plot_model.ChangeEventType.MCA_X_AXIS:
            self.__redrawAll()
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
                if isinstance(item, plot_item_model.McaItem):
                    labels.append(item.mcaChannel().displayName(scan))
            label = " + ".join(sorted(set(labels)))
        self.__plot.getYAxis().setLabel(label)

        xLabel = ""
        if self.__plotModel is not None:
            xLabel = "Channel index"
            if self.__displayModeAction.value() != DisplayMode.IMAGE:
                if self.__userCalibration is not None:
                    xLabel = "Energy (keV)"
                elif self.__plotModel.xAxisInEnergy():
                    device = self.__device()
                    if device is not None:
                        userCalibration = device.metadata().mca_user_calibration
                        if userCalibration is not None:
                            xLabel = "Energy (keV)"
        self.__plot.getXAxis().setLabel(xLabel)

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
                self.__updateTitle(self.__scan)
        self.scanModelUpdated.emit(scan)
        self.__syncAxisTitle.trigger()
        self.__redrawAll()

    def __scanStarted(self):
        assert self.__scan is not None
        self.__updateTitle(self.__scan)
        self.__initializeModeWhenDataIsReceived = True
        self.viewerEvent.emit(
            viewer_events.ScanViewerEvent(
                viewer_events.ViewerEventType.SCAN_STARTED, self.__scan
            )
        )

    def __updateTitle(self, scan: scan_model.Scan):
        title = scan_info_helper.get_full_title(scan)
        self.__plot.setGraphTitle(title)

    def __scanFinished(self):
        assert self.__scan is not None
        self.__refreshManager.scanFinished()
        self.viewerEvent.emit(
            viewer_events.ScanViewerEvent(
                viewer_events.ViewerEventType.SCAN_FINISHED, self.__scan
            )
        )

    def __scanDataUpdated(self, event: scan_model.ScanDataUpdateEvent):
        plotModel = self.__plotModel
        if plotModel is None:
            return

        if self.__initializeModeWhenDataIsReceived:
            self.__initializeModeWhenDataIsReceived = False
            if not self.__displayModeAction.isChecked():
                self.__autoSelectDisplayMode()

        self.__redrawAll()

    def __autoSelectDisplayMode(self):
        plotModel = self.__plotModel
        if plotModel is None:
            return

        modes = set()
        for item in plotModel.items():
            if not item.isValid():
                continue
            if not isinstance(item, plot_item_model.McaItem):
                continue
            if not item.isVisible():
                continue
            scan = self.__scan
            if not item.isValidInScan(scan):
                continue
            mcaChannelRef = item.mcaChannel()
            if mcaChannelRef is None:
                continue
            # Channels from channel ref
            mcaChannel = mcaChannelRef.channel(scan)
            if mcaChannel is None:
                continue

            if mcaChannel.type() == scan_model.ChannelType.SPECTRUM:
                modes.add(DisplayMode.SPECTRUM)
            elif mcaChannel.type() == scan_model.ChannelType.SPECTRUM_D_C:
                array = mcaChannel.array()
                if array is None:
                    continue
                else:
                    d = array.shape[0]
                    if d > 4:
                        modes.add(DisplayMode.IMAGE)
                    else:
                        modes.add(DisplayMode.SPECTRUM)

        if DisplayMode.IMAGE in modes:
            mode = DisplayMode.IMAGE
        elif DisplayMode.SPECTRUM in modes:
            mode = DisplayMode.SPECTRUM
        else:
            # status quo
            return
        self.__displayModeAction.setValue(mode)

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
        if self.__plotModel is None:
            return
        if self.__scan is None:
            return
        plotModel = self.__plotModel
        if plotModel is None:
            return

        displayMode = self.__displayModeAction.value()
        if displayMode == DisplayMode.SPECTRUM:
            self.__renderAsSpectrums()
        elif displayMode == DisplayMode.IMAGE:
            self.__renderAsImage()
        else:
            raise ValueError(f"Unsupported display mode {displayMode}")

    def __renderAsImage(self):
        assert self.__plotModel is not None
        plotModel = self.__plotModel
        scan = self.__scan
        updateZoomNow = not plotModel.isInTransaction()

        legend = "as_image"
        _wasUpdated = self.__cleanItem(legend)  # noqa: F841

        def getValidArraysFromItems(
            items: plot_model.Item,
        ) -> list[tuple[plot_item_model.McaItem, numpy.ndarray, bool]]:
            arrays = []
            for item in items:
                if not isinstance(item, plot_item_model.McaItem):
                    continue
                mcaChannelRef = item.mcaChannel()
                if mcaChannelRef is None:
                    continue
                mcaChannel = mcaChannelRef.channel(scan)
                if mcaChannel is None:
                    continue
                array = mcaChannel.array()
                if array is None:
                    continue
                # Normalize SPECTRUM / SPECTRUM_D_C
                if len(array.shape) == 1:
                    array = numpy.array(array)
                    array.shape = 1, -1
                    isStack = False
                else:
                    isStack = True
                arrays.append((mcaChannel.name(), item, array, isStack))
            arrays = sorted(arrays)
            result = [d[1:] for d in arrays]
            return result

        arrays = getValidArraysFromItems(plotModel.items())

        shape = [0, 0]
        for _item, array, _isStack in arrays:
            shape[0] += array.shape[0]
            shape[1] = max(shape[1], array.shape[1])

        data = numpy.full(shape, numpy.nan)

        pos = 0
        for item, array, _isStack in arrays:
            if not item.isVisible():
                continue
            if not item.isValidInScan(scan):
                continue

            data[pos : pos + array.shape[0], 0 : array.shape[1]] = array
            pos += array.shape[0]

        plot = self.__plot
        plotItems: list[tuple[str, str]] = []

        mcaItem = FlintStackOfRawMca()
        mcaItem.setData(data, copy=False)
        mapping = [(i, a.shape[0], s) for i, a, s in arrays]
        mcaItem.setCustomItemMapping(mapping)
        mcaItem.setName(legend)
        plot.addItem(mcaItem)

        plotItems.append((legend, "image"))
        self.__items[None] = plotItems
        self.__updatePlotZoom(updateZoomNow)

    def __renderAsSpectrums(self):
        plotModel = self.__plotModel
        assert plotModel is not None
        for item in plotModel.items():
            self.__updateItem(item)

    def __device(self) -> scan_model.Device | None:
        # FIXME: This have to be cached
        if self.__scan is None:
            return None
        for device in self.__scan.devices():
            if device.type() not in [
                scan_model.DeviceType.MCA,
                scan_model.DeviceType.MOSCA,
            ]:
                continue
            if device.name() == self.deviceName():
                return device
                break
        return None

    def getNormalization(self) -> numpy.ndarray | None:
        """Returns the channel to energy normalization"""
        if self.__plotModel is None:
            return None
        if self.__scan is None:
            return None
        userCalibration = self.__userCalibration
        if userCalibration is None:
            device = self.__device()
            if device is not None:
                # MCA device based calibration
                if self.__plotModel.xAxisInEnergy():
                    userCalibration = device.metadata().mca_user_calibration
        if not userCalibration:
            return None
        for item in self.__plotModel.items():
            if not item.isValid():
                continue
            if not isinstance(item, plot_item_model.McaItem):
                continue
            if not item.isVisible():
                continue
            if not item.isValidInScan(self.__scan):
                continue
            break
        else:
            return None

        mcaChannelRef = item.mcaChannel()
        if mcaChannelRef is None:
            return None

        # Channels from channel ref
        mcaChannel = mcaChannelRef.channel(self.__scan)
        if mcaChannel is None:
            return None

        array = mcaChannel.array()

        return polyval(numpy.arange(len(array)), userCalibration)

    def __updateItem(self, item: plot_model.Item):
        if self.__plotModel is None:
            return
        if self.__scan is None:
            return
        if not item.isValid():
            return
        if not isinstance(item, plot_item_model.McaItem):
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

        mcaChannelRef = item.mcaChannel()
        if mcaChannelRef is None:
            if wasUpdated:
                self.__updatePlotZoom(updateZoomNow)
            return

        # Channels from channel ref
        mcaChannel = mcaChannelRef.channel(scan)
        if mcaChannel is None:
            return

        array = mcaChannel.array()
        if array is None:
            if wasUpdated:
                self.__updatePlotZoom(updateZoomNow)
            return

        # Widget based calibration
        userCalibration = self.__userCalibration
        if userCalibration is None:
            device = self.__device()
            if device is not None:
                # MCA device based calibration
                if self.__plotModel.xAxisInEnergy():
                    userCalibration = device.metadata().mca_user_calibration

        if mcaChannel.type() == scan_model.ChannelType.SPECTRUM:
            legend = mcaChannel.name()
            style = item.getStyle(self.__scan)

            if userCalibration:
                energy = polyval(numpy.arange(len(array)), userCalibration)
                mcaItem = FlintEnergyMca()
                mcaItem.setData(energy, array, copy=False)
                mcaItem.setColor(style.lineColor)
                mcaItem.setSymbol("")
                mcaItem.setLineStyle("-")
                mcaItem.setCalibration(userCalibration)
                plotItems.append((legend, "curve"))
            else:
                edges = numpy.arange(len(array) + 1) - 0.5
                mcaItem = FlintRawMca()
                mcaItem.setData(array, edges, copy=False)
                mcaItem.setColor(style.lineColor)
                mcaItem.setCalibration(userCalibration)
                plotItems.append((legend, "histogram"))

            mcaItem.setName(legend)
            mcaItem.setCustomItem(item)
            plot.addItem(mcaItem)

            plotItems.append((legend, "histogram"))

        elif mcaChannel.type() == scan_model.ChannelType.SPECTRUM_D_C:
            style = item.getStyle(self.__scan)

            if userCalibration:
                energy = polyval(numpy.arange(array.shape[1]), userCalibration)
                for iDet, arrayDet in enumerate(array):
                    legend = f"{mcaChannel.name()}_image_{iDet}"
                    mcaItem = FlintEnergyMca()
                    mcaItem.setData(energy, arrayDet, copy=False)
                    mcaItem.setItemArrayIndex(iDet)
                    mcaItem.setColor(style.lineColor)
                    mcaItem.setName(legend)
                    mcaItem.setSymbol("")
                    mcaItem.setLineStyle("-")
                    mcaItem.setCalibration(userCalibration)
                    mcaItem.setCustomItem(item)
                    plot.addItem(mcaItem)
                    plotItems.append((legend, "curve"))
            else:
                edges = numpy.arange(array.shape[1] + 1) - 0.5
                for iDet, arrayDet in enumerate(array):
                    legend = f"{mcaChannel.name()}_histo_{iDet}"
                    mcaItem = FlintRawMca()
                    mcaItem.setData(arrayDet, edges, copy=False)
                    mcaItem.setItemArrayIndex(iDet)
                    mcaItem.setColor(style.lineColor)
                    mcaItem.setName(legend)
                    mcaItem.setCustomItem(item)
                    plot.addItem(mcaItem)
                    plotItems.append((legend, "histogram"))

        self.__items[item] = plotItems
        self.__updatePlotZoom(updateZoomNow)

    def __updatePlotZoom(self, updateZoomNow):
        if updateZoomNow:
            self.__view.plotUpdated()
        else:
            self.__plotWasUpdated = True
