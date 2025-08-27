# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

from __future__ import annotations

import logging
import weakref

from silx.gui import qt
from silx.gui import icons
from silx.gui import utils as qtutils

from bliss.flint.model import flint_model
from bliss.flint.model import plot_model
from bliss.flint.model import plot_item_model
from bliss.flint.model import scan_model
from bliss.flint.helper import model_helper, scan_history
from bliss.flint.scan_info_parser.plots import create_plot_model
from bliss.flint.helper.style_helper import DefaultStyleStrategy
from bliss.flint.widgets.plot_model_edited import PlotModelEditAction
from bliss.flint.utils import qmodelutils
from bliss.flint.utils import qt_backport
from bliss.flint.widgets import delegates
from bliss.flint.widgets import _property_tree_helper
from bliss.flint.widgets import interfaces


_logger = logging.getLogger(__name__)


class _DataItem(_property_tree_helper.ScanRowItem):

    XAxisIndexRole = 1

    def __init__(self):
        super(_DataItem, self).__init__()
        qt.QStandardItem.__init__(self)
        self.__xaxis = delegates.HookedStandardItem("")
        self.__used = delegates.HookedStandardItem("")
        self.__displayed = delegates.HookedStandardItem("")
        self.__style = qt.QStandardItem("")
        self.__error = qt.QStandardItem("")
        self.__xAxisSelected = False
        self.__role = None
        self.__device = None

        self.__plotModel: plot_model.Plot | None = None
        self.__plotItem: plot_model.Item | None = None
        self.__channel: scan_model.Channel | None = None
        self.__treeView: qt.QTreeView | None = None
        self.__flintModel: flint_model.FlintState | None = None

        self.setOtherRowItems(
            self.__xaxis, self.__used, self.__displayed, self.__style, self.__error
        )

    def __hash__(self):
        return hash(id(self))

    def channel(self) -> scan_model.Channel | None:
        return self.__channel

    def setEnvironment(
        self, treeView: qt.QTreeView, flintState: flint_model.FlintState
    ):
        self.__treeView = treeView
        self.__flintModel = flintState

    def setPlotModel(self, plotModel: plot_model.Plot):
        self.__plotModel = plotModel

    def plotModel(self) -> plot_model.Plot | None:
        return self.__plotModel

    def styleItem(self) -> qt.QStandardItem:
        return self.__style

    def updateError(self):
        assert self.__flintModel is not None
        scan = self.__flintModel.currentScan()
        if scan is None or self.__plotItem is None:
            # No message to reach
            self.__error.setText(None)
            self.__error.setIcon(qt.QIcon())
            return
        result = self.__plotItem.getErrorMessage(scan)
        if result is None:
            # Ths item is valid
            self.__error.setText(None)
            self.__error.setIcon(qt.QIcon())
            return

        self.__error.setText(result)
        icon = icons.getQIcon("flint:icons/warning")
        self.__error.setIcon(icon)

    def __usedChanged(self, item: qt.QStandardItem):
        assert self.__plotModel is not None
        plotModel = self.__plotModel
        if self.__plotItem is not None:
            # There is a plot item already
            model_helper.removeItemAndKeepAxes(plotModel, self.__plotItem)
            plotModel.tagUserEditTime()
        else:
            assert self.__channel is not None
            _curve, _wasUpdated = model_helper.createCurveItem(
                plotModel, self.__channel, "left", allowIndexed=True
            )
            plotModel.tagUserEditTime()

    def __visibilityViewChanged(self, item: qt.QStandardItem):
        if self.__plotItem is not None:
            state = item.data(delegates.VisibilityRole)
            self.__plotItem.setVisible(state == qt.Qt.Checked)

    def setSelectedXAxis(self):
        if self.__xAxisSelected:
            return
        self.__xAxisSelected = True

        old = self.__xaxis.modelUpdated
        self.__xaxis.modelUpdated = None
        try:
            self.__xaxis.setData(qt.Qt.Checked, role=delegates.RadioRole)
        finally:
            self.__xaxis.modelUpdated = old
        # It have to be closed to be refreshed. Sounds like a bug.
        assert self.__treeView is not None
        self.__treeView.closePersistentEditor(self.__xaxis.index())
        self.__treeView.openPersistentEditor(self.__xaxis.index())

    def __xAxisChanged(self, item: qt.QStandardItem):
        assert self.__plotModel is not None
        plotModel = self.__plotModel

        if self.__channel is not None:
            topMaster = self.__channel.device().topMaster()
            scan = topMaster.scan()
            xChannelName = self.__channel.name()
            model_helper.updateXAxis(
                plotModel, scan, topMaster, xChannelName=xChannelName
            )
            plotModel.tagUserEditTime()
        elif self.__role == self.XAxisIndexRole:
            assert self.__device is not None
            topMaster = self.__device.topMaster()
            scan = topMaster.scan()
            model_helper.updateXAxis(plotModel, scan, topMaster, xIndex=True)
            plotModel.tagUserEditTime()
        else:
            assert False

    def setDevice(self, device: scan_model.Device):
        self.setDeviceLookAndFeel(device)
        self.__updateXAxisStyle(True, None)
        self.__used.setCheckable(False)
        self.__used.setData(None, role=delegates.CheckRole)

    def __rootRow(self) -> int:
        item = self
        while item is not None:
            parent = item.parent()
            if parent is None:
                break
            item = parent
        return item.row()

    def __updateXAxisStyle(self, setAxisValue: bool, radioValue=None):
        # FIXME: avoid hard coded style
        cellColors = [qt.QColor(0xE8, 0xE8, 0xE8), qt.QColor(0xF5, 0xF5, 0xF5)]
        old = self.__xaxis.modelUpdated
        self.__xaxis.modelUpdated = None
        if setAxisValue:
            self.__xaxis.setData(radioValue, role=delegates.RadioRole)
        i = self.__rootRow()
        self.__xaxis.setBackground(cellColors[i % 2])
        self.__xaxis.modelUpdated = old

    def setRole(self, role, device=None):
        assert self.__plotModel is not None
        self.__role = role
        if role == self.XAxisIndexRole:
            assert device is not None
            self.__device = device
            items = self.__plotModel.items()
            if len(items) > 0:
                item = items[0]
                checked = isinstance(item.xChannel(), plot_model.XIndexChannelRef)
            else:
                checked = True
            self.setText("index")
            self.setToolTip("Use data index as axis")
            qtchecked = qt.Qt.Checked if checked else qt.Qt.Unchecked
            self.__updateXAxisStyle(True, qtchecked)
            self.__xaxis.modelUpdated = weakref.WeakMethod(self.__xAxisChanged)
            assert self.__treeView is not None
            self.__treeView.openPersistentEditor(self.__xaxis.index())
            icon = icons.getQIcon("flint:icons/item-index")
            self.setIcon(icon)
        else:
            assert False, f"Role '{role}' is unknown"

    def setChannel(self, channel: scan_model.Channel):
        assert self.__treeView is not None
        self.__channel = channel
        self.setChannelLookAndFeel(channel)
        self.__updateXAxisStyle(True, qt.Qt.Unchecked)
        self.__xaxis.modelUpdated = weakref.WeakMethod(self.__xAxisChanged)
        self.__used.modelUpdated = None
        self.__used.setData(qt.Qt.Unchecked, role=delegates.CheckRole)
        self.__used.modelUpdated = weakref.WeakMethod(self.__usedChanged)

        self.__treeView.openPersistentEditor(self.__xaxis.index())
        self.__treeView.openPersistentEditor(self.__used.index())

    def data(self, role=qt.Qt.DisplayRole):
        if role == qt.Qt.ToolTipRole:
            return self.toolTip()
        return _property_tree_helper.ScanRowItem.data(self, role)

    def toolTip(self):
        if self.__role == self.XAxisIndexRole:
            return "Use data index as x-axis"
        elif self.__channel is not None:
            data = self.__channel.data()
            if data is not None:
                array = data.array()
            else:
                array = None
            if array is None:
                shape = "No data"
            elif array is tuple():
                shape = "Scalar"
            else:
                shape = " × ".join([str(s) for s in array.shape])
            name = self.__channel.name()
            return f"""<html><ul>
            <li><b>Channel name:</b> {name}</li>
            <li><b>Data shape:</b> {shape}</li>
            </ul></html>"""

        return None

    def plotItem(self) -> plot_model.Item | None:
        return self.__plotItem

    def setPlotItem(self, plotItem: plot_model.Item):
        self.__plotItem = plotItem

        self.__style.setData(plotItem, role=delegates.PlotItemRole)

        self.__used.modelUpdated = None
        self.__used.setData(qt.Qt.Checked, role=delegates.CheckRole)
        self.__used.modelUpdated = weakref.WeakMethod(self.__usedChanged)

        if plotItem is not None:
            isVisible = plotItem.isVisible()
            state = qt.Qt.Checked if isVisible else qt.Qt.Unchecked
            self.__displayed.setData(state, role=delegates.VisibilityRole)
            self.__displayed.modelUpdated = weakref.WeakMethod(
                self.__visibilityViewChanged
            )
        else:
            self.__displayed.setData(None, role=delegates.VisibilityRole)
            self.__displayed.modelUpdated = None

        if self.__channel is None:
            self.setPlotItemLookAndFeel(plotItem)

        if isinstance(plotItem, plot_item_model.CurveItem):
            self.__xaxis.modelUpdated = weakref.WeakMethod(self.__xAxisChanged)
            useXAxis = True
        elif isinstance(plotItem, plot_item_model.CurveMixIn):
            # self.__updateXAxisStyle(False, None)
            useXAxis = False
            self.__updateXAxisStyle(False)
        elif isinstance(plotItem, plot_item_model.CurveStatisticItem):
            useXAxis = False
            self.__updateXAxisStyle(False)

        assert self.__treeView is not None
        # FIXME: It have to be converted into delegate
        if useXAxis:
            self.__treeView.openPersistentEditor(self.__xaxis.index())
        # FIXME: close/open is needed, sometime the item is not updated
        if self.__treeView.isPersistentEditorOpen(self.__used.index()):
            self.__treeView.closePersistentEditor(self.__used.index())
        self.__treeView.openPersistentEditor(self.__used.index())
        self.__treeView.openPersistentEditor(self.__displayed.index())
        widget = delegates.StylePropertyWidget(self.__treeView)
        widget.setPlotItem(self.__plotItem)
        widget.setFlintModel(self.__flintModel)
        self.__treeView.setIndexWidget(self.__style.index(), widget)

        self.updateError()


class OneDimPlotPropertyWidget(qt.QWidget, interfaces.HasPlotModel, interfaces.HasScan):

    NameColumn = 0
    XAxisColumn = 1
    UsedColumn = 2
    VisibleColumn = 3
    StyleColumn = 4

    plotItemSelected = qt.Signal(object)

    def __init__(self, parent=None):
        super(OneDimPlotPropertyWidget, self).__init__(parent=parent)
        self.__scan: scan_model.Scan | None = None
        self.__flintModel: flint_model.FlintState | None = None
        self.__plotModel: plot_model.Plot | None = None
        self.__tree = qt_backport.QTreeView(self)
        self.__tree.setEditTriggers(qt.QAbstractItemView.NoEditTriggers)
        self.__tree.setUniformRowHeights(True)

        self.__structureInvalidated: bool = False
        self.__xAxisInvalidated: bool = False
        self.__xAxisDelegate = delegates.RadioPropertyItemDelegate(self)
        self.__usedDelegate = delegates.CheckBoxItemDelegate(self)
        self.__visibilityDelegate = delegates.VisibilityPropertyItemDelegate(self)

        model = qt.QStandardItemModel(self)
        self.__tree.setModel(model)
        selectionModel = self.__tree.selectionModel()
        selectionModel.currentChanged.connect(self.__selectionChanged)

        self.__scan = None
        self.__focusWidget = None

        toolBar = self.__createToolBar()

        self.setAutoFillBackground(True)
        self.__tree.setFrameShape(qt.QFrame.NoFrame)
        line = qt.QFrame(self)
        line.setFrameShape(qt.QFrame.HLine)
        line.setFrameShadow(qt.QFrame.Sunken)

        layout = qt.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(toolBar)
        layout.addWidget(line)
        layout.addWidget(self.__tree)

    def __removeAllItems(self):
        plotModel = self.__plotModel
        if plotModel is None:
            return
        with plotModel.transaction():
            items = list(plotModel.items())
            for item in items:
                try:
                    plotModel.removeItem(item)
                except IndexError:
                    # Item was maybe already removed
                    pass
        plotModel.tagRawEdit()

    def __resetPlotWithOriginalPlot(self):
        assert self.__focusWidget is not None
        assert self.__flintModel is not None
        widget = self.__focusWidget
        scan = widget.scan()
        if scan is None:
            return
        plots = create_plot_model(scan.scanInfo(), scan)
        manager = self.__flintModel.mainManager()
        plots = manager.getCompatiblePlots(widget, plots)
        if len(plots) == 0:
            _logger.warning("No curve plot to display")
            qt.QMessageBox.warning(
                None, "Warning", "There was no curve plot in this scan"
            )
            return
        plotModel = plots[0]
        previousPlotModel = self.__plotModel

        # Reuse only available values
        if isinstance(previousPlotModel, plot_item_model.CurvePlot):
            model_helper.removeNotAvailableChannels(previousPlotModel, plotModel, scan)
            model_helper.copyItemsFromChannelNames(
                previousPlotModel, plotModel, scan=None
            )
        if plotModel.styleStrategy() is None:
            plotModel.setStyleStrategy(DefaultStyleStrategy(self.__flintModel))
        widget.setPlotModel(plotModel)

    def __createToolBar(self):
        toolBar = qt.QToolBar(self)
        toolBar.setMovable(False)

        toolBar.addWidget(qt.QLabel("Selection:", toolBar))

        self.__plotModelEditAction = PlotModelEditAction(toolBar)
        self.__plotModelEditAction.setText("Lock/unlock displayed selection")
        toolBar.addAction(self.__plotModelEditAction)

        action = qt.QAction(self)
        icon = icons.getQIcon("flint:icons/reset-to-plotselect")
        action.setIcon(icon)
        action.setText("Reset with plotselect")
        action.setToolTip(
            "Reset displayed curves using the original plot definition (including plotselect)"
        )
        action.triggered.connect(self.__resetPlotWithOriginalPlot)
        toolBar.addAction(action)

        action = qt.QAction(self)
        icon = icons.getQIcon("flint:icons/remove-all-items")
        action.setIcon(icon)
        action.setText("Clear displayed selection")
        action.setToolTip("Clean up the all displayed elements from the plot")
        action.triggered.connect(self.__removeAllItems)
        toolBar.addAction(action)

        toolBar.addSeparator()

        action = qt.QAction(self)
        icon = icons.getQIcon("flint:icons/scan-history")
        action.setIcon(icon)
        action.setToolTip(
            "Load a previous scan stored in Redis (about 24 hour of history)"
        )
        action.triggered.connect(self.__requestLoadScanFromHistory)
        toolBar.addAction(action)

        return toolBar

    def __requestLoadScanFromHistory(self):
        assert self.__flintModel is not None
        from bliss.flint.dialog.scan_history_dialog import ScanHistoryDialog

        sessionName = self.__flintModel.blissSessionName()

        dialog = ScanHistoryDialog(self)
        dialog.setFlintModel(self.__flintModel)
        dialog.setSessionName(sessionName)
        result = dialog.exec_()
        if result:
            selection = dialog.selectedScanNodeNames()
            widget = self.__focusWidget
            if widget is None:
                _logger.error("No curve widget connected")
                return

            if len(selection) == 0:
                _logger.error("No selection")
                return

            nodeName = selection[0]
            try:
                self.__loadScanFromHistory(nodeName)
            except Exception:
                _logger.error("Error while loading scan from history", exc_info=True)
                qt.QMessageBox.critical(
                    None,
                    "Error",
                    "An error occurred while a scan was loading from the history",
                )

    def __loadScanFromHistory(self, nodeName: str):
        scan = scan_history.create_scan(nodeName, self.__flintModel.dataProvider())
        widget = self.__focusWidget
        if widget is not None:
            plots = create_plot_model(scan.scanInfo(), scan)
            plots = [p for p in plots if isinstance(p, plot_item_model.CurvePlot)]
            if len(plots) == 0:
                _logger.warning("No curve plot to display")
                qt.QMessageBox.warning(
                    None, "Warning", "There was no curve plot in the selected scan"
                )
                return
            plotModel = plots[0]
            previousWidgetPlot = self.__plotModel

            # Reuse only available values
            if isinstance(previousWidgetPlot, plot_item_model.CurvePlot):
                model_helper.removeNotAvailableChannels(
                    previousWidgetPlot, plotModel, scan
                )
                widget.setScan(scan)
            if previousWidgetPlot is None or previousWidgetPlot.isEmpty():
                if plotModel.styleStrategy() is None:
                    plotModel.setStyleStrategy(DefaultStyleStrategy(self.__flintModel))
                widget.setPlotModel(plotModel)

    def __findItemFromPlotItem(
        self, requestedItem: plot_model.Item
    ) -> _DataItem | None:
        """Returns a silx plot item from a flint plot item."""
        if requestedItem is None:
            return None
        model = self.__tree.model()
        for index in qmodelutils.iterAllItems(model):
            item = model.itemFromIndex(index)
            if isinstance(item, _DataItem):
                plotItem = item.plotItem()
                if plotItem is requestedItem:
                    return item
        return None

    def __selectionChangedFromPlot(self, current: plot_model.Item):
        self.selectPlotItem(current)

    def selectPlotItem(self, select: plot_model.Item | None):
        selectionModel = self.__tree.selectionModel()
        if select is None:
            # Break reentrant signals
            selectionModel.setCurrentIndex(
                qt.QModelIndex(), qt.QItemSelectionModel.Clear
            )
            return
        if select is self.selectedPlotItem():
            # Break reentrant signals
            return
        item = self.__findItemFromPlotItem(select)
        flags = qt.QItemSelectionModel.Rows | qt.QItemSelectionModel.ClearAndSelect
        if item is None:
            index = qt.QModelIndex()
        else:
            index = item.index()
        selectionModel = self.__tree.selectionModel()
        selectionModel.setCurrentIndex(index, flags)

    def __selectionChanged(self, current: qt.QModelIndex, previous: qt.QModelIndex):
        model = self.__tree.model()
        index = model.index(current.row(), 0, current.parent())
        item = model.itemFromIndex(index)
        if isinstance(item, _DataItem):
            plotItem = item.plotItem()
        else:
            plotItem = None
        self.plotItemSelected.emit(plotItem)

    def selectedPlotItem(self) -> plot_model.Item | None:
        """Returns the current selected plot item, if one"""
        selectionModel = self.__tree.selectionModel()
        indices = selectionModel.selectedRows()
        index = indices[0] if len(indices) > 0 else qt.QModelIndex()
        if not index.isValid():
            return None
        model = self.__tree.model()
        index = model.index(index.row(), 0, index.parent())
        item = model.itemFromIndex(index)
        if isinstance(item, _DataItem):
            plotItem = item.plotItem()
            return plotItem
        return None

    def setFlintModel(self, flintModel: flint_model.FlintState | None):
        self.__flintModel = flintModel

    def focusWidget(self):
        return self.__focusWidget

    def setFocusWidget(self, widget):
        if self.__focusWidget is not None:
            widget.plotModelUpdated.disconnect(self.__plotModelUpdated)
            widget.scanModelUpdated.disconnect(self.__currentScanChanged)
        self.__focusWidget = widget
        if self.__focusWidget is not None:
            widget.plotModelUpdated.connect(self.__plotModelUpdated)
            widget.scanModelUpdated.connect(self.__currentScanChanged)
            plotModel = widget.plotModel()
            scanModel = widget.scan()
        else:
            plotModel = None
            scanModel = None
        self.__plotModelUpdated(plotModel)
        self.__currentScanChanged(scanModel)

    def __plotModelUpdated(self, plotModel):
        self.setPlotModel(plotModel)

    def setPlotModel(self, plotModel: plot_model.Plot):
        if self.__plotModel is not None:
            self.__plotModel.structureChanged.disconnect(self.__structureChanged)
            self.__plotModel.itemValueChanged.disconnect(self.__itemValueChanged)
            self.__plotModel.transactionFinished.disconnect(self.__transactionFinished)
        self.__plotModel = plotModel
        if self.__plotModel is not None:
            self.__plotModel.structureChanged.connect(self.__structureChanged)
            self.__plotModel.itemValueChanged.connect(self.__itemValueChanged)
            self.__plotModel.transactionFinished.connect(self.__transactionFinished)
        self.__plotModelEditAction.setPlotModel(plotModel)
        self.__updateTree()

    def __currentScanChanged(self, scan: scan_model.Scan | None):
        self.__setScan(scan)

    def __structureChanged(self):
        assert self.__plotModel is not None
        if self.__plotModel.isInTransaction():
            self.__structureInvalidated = True
        else:
            self.__updateTree()

    def __itemValueChanged(
        self, item: plot_model.Item, eventType: plot_model.ChangeEventType
    ):
        assert self.__plotModel is not None
        if eventType == plot_model.ChangeEventType.X_CHANNEL:
            if self.__plotModel.isInTransaction():
                self.__xAxisInvalidated = True
            else:
                self.__updateTree()
        elif eventType == plot_model.ChangeEventType.Y_CHANNEL:
            if self.__plotModel.isInTransaction():
                self.__xAxisInvalidated = True
            else:
                self.__updateTree()

    def __transactionFinished(self):
        updateTree = self.__xAxisInvalidated or self.__structureInvalidated
        if updateTree:
            self.__xAxisInvalidated = False
            self.__structureInvalidated = False
            self.__updateTree()

    def plotModel(self) -> plot_model.Plot | None:
        return self.__plotModel

    def __setScan(self, scan: scan_model.Scan | None):
        if self.__scan is scan:
            return
        if self.__scan is not None:
            self.__scan.scanDataUpdated[object].disconnect(self.__scanDataUpdated)
        self.__scan = scan
        if self.__scan is not None:
            self.__scan.scanDataUpdated[object].connect(self.__scanDataUpdated)
        self.__updateTree()

    def scan(self) -> scan_model.Scan | None:
        return self.__scan

    def __scanDataUpdated(self, event: scan_model.ScanDataUpdateEvent):
        model = self.__tree.model()
        flags = qt.Qt.MatchWildcard | qt.Qt.MatchRecursive
        items = model.findItems("*", flags)
        channels = set(event.iterUpdatedChannels())
        # FIXME: This loop could be optimized
        for item in items:
            if isinstance(item, _DataItem):
                if item.channel() in channels:
                    item.updateError()

    def __genScanTree(
        self,
        model: qt.QStandardItemModel,
        scan: scan_model.Scan,
        channelFilter: scan_model.ChannelType,
    ) -> dict[str, _DataItem]:
        """Feed the provided model with a tree of scan concepts (devices,
        channels).

        Returns a map from channel name to Qt items (`_DataItem`)
        """
        assert self.__tree is not None
        assert self.__flintModel is not None
        assert self.__plotModel is not None
        scanTree = {}
        channelItems: dict[str, _DataItem] = {}

        devices: list[qt.QStandardItem] = []
        channelsPerDevices: dict[qt.QStandardItem, int] = {}

        name = self.__plotModel.deviceName()
        if name is not None:
            try:
                deviceRoot = scan.getDeviceByName(name, oneOf=True)
            except Exception as e:
                deviceRoot = None
                if ":" in name:
                    deviceRoot = scan.findDeviceByName(name.split(":", 1)[0])
                if deviceRoot is None:
                    _logger.error("Error while reaching device name", exc_info=e)
        else:
            deviceRoot = None

        for device in scan.devices():
            if deviceRoot and (
                device is not deviceRoot or not device.isChildOf(deviceRoot)
            ):
                continue

            item = _DataItem()
            item.setEnvironment(self.__tree, self.__flintModel)
            scanTree[device] = item

            master = device.master()
            if master is None:
                # Root device
                parent = model
            else:
                itemMaster = scanTree.get(master, None)
                if itemMaster is None:
                    parent = model
                    _logger.warning("Device list is not well ordered")
                else:
                    parent = itemMaster

            parent.appendRow(item.rowItems())
            # It have to be done when model index are initialized
            item.setDevice(device)
            devices.append(item)

            channels = []
            for channel in device.channels():
                if channel.type() != channelFilter:
                    continue
                channels.append(channel)

            if device.master() is None:
                indexItem = _DataItem()
                indexItem.setEnvironment(self.__tree, self.__flintModel)
                indexItem.setPlotModel(self.__plotModel)
                item.appendRow(indexItem.rowItems())
                # It have to be done when model index are initialized
                indexItem.setRole(_DataItem.XAxisIndexRole, device=device)

            for channel in channels:
                channelItem = _DataItem()
                channelItem.setEnvironment(self.__tree, self.__flintModel)
                item.appendRow(channelItem.rowItems())
                # It have to be done when model index are initialized
                channelItem.setChannel(channel)
                channelItem.setPlotModel(self.__plotModel)
                channelItems[channel.name()] = channelItem

            # Update channel use
            parent = item
            channelsPerDevices[parent] = 0
            while parent is not None:
                if parent in channelsPerDevices:
                    channelsPerDevices[parent] += len(channels)
                parent = parent.parent()
                if parent is None:
                    break

        # Clean up unused devices
        for device in reversed(devices):
            if device not in channelsPerDevices:
                continue
            if channelsPerDevices[device] > 0:
                continue
            parent = device.parent()
            if parent is None:
                parent = model
            parent.removeRows(device.row(), 1)

        return channelItems

    def __updateTree(self):
        assert self.__flintModel is not None
        collapsed = _property_tree_helper.getPathFromCollapsedNodes(self.__tree)
        selectedItem = self.selectedPlotItem()
        scrollx = self.__tree.horizontalScrollBar().value()
        scrolly = self.__tree.verticalScrollBar().value()

        model = self.__tree.model()
        model.clear()

        if self.__plotModel is None:
            model.setHorizontalHeaderLabels([""])
            foo = qt.QStandardItem("")
            model.appendRow(foo)
            return

        model.setHorizontalHeaderLabels(
            ["Name", "X", "Y", "Displayed", "Style", "Message"]
        )
        self.__tree.setItemDelegateForColumn(self.XAxisColumn, self.__xAxisDelegate)
        self.__tree.setItemDelegateForColumn(self.UsedColumn, self.__usedDelegate)
        self.__tree.setItemDelegateForColumn(
            self.VisibleColumn, self.__visibilityDelegate
        )
        self.__tree.setStyleSheet("QTreeView:item {padding: 0px 8px;}")
        header = self.__tree.header()
        header.setStyleSheet("QHeaderView { qproperty-defaultAlignment: AlignCenter; }")
        header.setSectionResizeMode(self.NameColumn, qt.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(self.XAxisColumn, qt.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(self.UsedColumn, qt.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(self.VisibleColumn, qt.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(self.StyleColumn, qt.QHeaderView.ResizeToContents)
        header.setMinimumSectionSize(10)
        header.moveSection(self.StyleColumn, self.VisibleColumn)

        sourceTree: dict[plot_model.Item, qt.QStandardItem] = {}
        scan = self.__scan
        if scan is not None:
            channelItems = self.__genScanTree(
                model, scan, scan_model.ChannelType.VECTOR
            )
        else:
            channelItems = {}

        itemWithoutLocation = qt.QStandardItem("Not linked to this scan")
        itemWithoutMaster = qt.QStandardItem("Not linked to a master")
        model.appendRow(itemWithoutLocation)
        model.appendRow(itemWithoutMaster)

        assert self.__plotModel is not None
        xChannelPerMasters = model_helper.getMostUsedXChannelPerMasters(
            scan, self.__plotModel
        )

        for plotItem in self.__plotModel.items():
            parentChannel = None

            if isinstance(plotItem, plot_item_model.ScanItem):
                continue
            if isinstance(plotItem, plot_item_model.AxisPositionMarker):
                continue

            if isinstance(plotItem, (plot_model.ComputableMixIn, plot_model.ChildItem)):
                source = plotItem.source()
                if source is None:
                    parent = itemWithoutLocation
                else:
                    itemSource = sourceTree.get(source, None)
                    if itemSource is None:
                        parent = itemWithoutMaster
                        _logger.warning("Item list is not well ordered")
                    else:
                        parent = itemSource
            else:
                if scan is None:
                    parent = itemWithoutLocation
                else:
                    if isinstance(plotItem, plot_item_model.CurveItem):
                        xChannel = plotItem.xChannel()
                        if xChannel is None or isinstance(
                            xChannel, plot_model.XIndexChannelRef
                        ):
                            yChannel = plotItem.yChannel()
                            if yChannel is not None:
                                yChannelName = yChannel.name()
                                parentChannel = channelItems.get(yChannelName, None)
                                if parentChannel is None:
                                    parent = itemWithoutLocation
                            else:
                                # X-axis only
                                continue
                        else:
                            topMaster = model_helper.getConsistentTopMaster(
                                scan, plotItem
                            )
                            xChannelName = xChannel.name()
                            if (
                                topMaster is not None
                                and xChannelPerMasters[topMaster] == xChannelName
                            ):
                                # The x-channel is what it is expected then we can link the y-channel
                                yChannel = plotItem.yChannel()
                                if yChannel is not None:
                                    yChannelName = yChannel.name()
                                    parentChannel = channelItems.get(yChannelName, None)
                                    if parentChannel is None:
                                        parent = itemWithoutLocation
                                xAxisItem = channelItems[xChannelName]
                                xAxisItem.setSelectedXAxis()
                                if yChannel is None:
                                    # This item must not be displayed
                                    continue
                            else:
                                parent = itemWithoutLocation

            if parentChannel is not None:
                parentChannel.setPlotItem(plotItem)
                sourceTree[plotItem] = parentChannel
            else:
                item = _DataItem()
                item.setEnvironment(self.__tree, self.__flintModel)
                parent.appendRow(item.rowItems())
                # It have to be done when model index are initialized
                item.setPlotItem(plotItem)
                sourceTree[plotItem] = item

        if itemWithoutLocation.rowCount() == 0:
            model.removeRows(itemWithoutLocation.row(), 1)
        if itemWithoutMaster.rowCount() == 0:
            model.removeRows(itemWithoutMaster.row(), 1)

        self.__tree.expandAll()
        _property_tree_helper.collapseNodesFromPaths(self.__tree, collapsed)
        self.__tree.horizontalScrollBar().setValue(scrollx)
        self.__tree.verticalScrollBar().setValue(scrolly)

        with qtutils.blockSignals(self):
            self.selectPlotItem(selectedItem)
