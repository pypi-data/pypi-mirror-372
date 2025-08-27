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

from bliss.flint.model import flint_model
from bliss.flint.model import plot_model
from bliss.flint.model import plot_item_model
from bliss.flint.model import scan_model
from bliss.flint.widgets import delegates
from bliss.flint.widgets import _property_tree_helper
from bliss.flint.widgets import interfaces


_logger = logging.getLogger(__name__)


class _DataItem(_property_tree_helper.ScanRowItem):
    def __init__(self):
        super(_DataItem, self).__init__()
        self.__used = delegates.HookedStandardItem("")
        self.__displayed = delegates.HookedStandardItem("")
        self.__style = qt.QStandardItem("")

        self.__plotModel: plot_model.Plot | None = None
        self.__plotItem: plot_model.Item | None = None
        self.__channel: scan_model.Channel | None = None
        self.__treeView: qt.QTreeView | None = None
        self.__flintModel: flint_model.FlintState | None = None

        self.setOtherRowItems(self.__used, self.__displayed, self.__style)

    def __hash__(self):
        return hash(id(self))

    def setEnvironment(
        self, treeView: qt.QTreeView, flintState: flint_model.FlintState
    ):
        self.__treeView = treeView
        self.__flintModel = flintState

    def setPlotModel(self, plotModel: plot_model.Plot):
        self.__plotModel = plotModel

    def __usedChanged(self, item: qt.QStandardItem):
        if self.__plotItem is not None:
            # There is a plot item already
            assert self.__plotModel is not None
            self.__plotModel.removeItem(self.__plotItem)
        else:
            assert self.__channel is not None
            assert self.__plotModel is not None
            plot = self.__plotModel

            channelName = self.__channel.name()
            newItem = plot_item_model.McaItem(plot)
            newItem.setMcaChannel(plot_model.ChannelRef(plot, channelName))
            plot.addItem(newItem)

            self.__plotItem = newItem

    def __visibilityViewChanged(self, item: qt.QStandardItem):
        if self.__plotItem is not None:
            state = item.data(delegates.VisibilityRole)
            self.__plotItem.setVisible(state == qt.Qt.Checked)

    def setDevice(self, device: scan_model.Device):
        self.setDeviceLookAndFeel(device)
        self.__used.setCheckable(False)

    def setChannel(self, channel: scan_model.Channel):
        self.__channel = channel
        self.setChannelLookAndFeel(channel)
        self.__used.modelUpdated = None
        self.__used.setCheckable(True)
        self.__used.modelUpdated = weakref.WeakMethod(self.__usedChanged)

    def setPlotItem(self, plotItem):
        self.__plotItem = plotItem

        self.__used.modelUpdated = None
        self.__used.setData(plotItem, role=delegates.PlotItemRole)
        self.__used.setCheckState(qt.Qt.Checked)
        self.__used.modelUpdated = weakref.WeakMethod(self.__usedChanged)

        self.__style.setData(plotItem, role=delegates.PlotItemRole)

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

        # FIXME: It have to be converted into delegate
        assert self.__treeView is not None
        self.__treeView.openPersistentEditor(self.__displayed.index())
        widget = delegates.StylePropertyWidget(self.__treeView)
        widget.setPlotItem(self.__plotItem)
        widget.setFlintModel(self.__flintModel)
        self.__treeView.setIndexWidget(self.__style.index(), widget)


class McaPlotPropertyWidget(qt.QWidget, interfaces.HasPlotModel):

    NameColumn = 0
    UseColumn = 1
    VisibleColumn = 2
    StyleColumn = 3

    def __init__(self, parent=None):
        super(McaPlotPropertyWidget, self).__init__(parent=parent)
        self.__scan: scan_model.Scan | None = None
        self.__flintModel: flint_model.FlintState | None = None
        self.__plotModel: plot_model.Plot | None = None

        self.__tree = qt.QTreeView(self)
        self.__tree.setEditTriggers(qt.QAbstractItemView.NoEditTriggers)
        self.__tree.setUniformRowHeights(True)

        self.__visibilityDelegate = delegates.VisibilityPropertyItemDelegate(self)

        model = qt.QStandardItemModel(self)
        self.__tree.setModel(model)

        self.__focusWidget = None

        self.__tree.setFrameShape(qt.QFrame.NoFrame)
        layout = qt.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.__tree)

    def setFlintModel(self, flintModel: flint_model.FlintState):
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
        self.__plotModel = plotModel
        if self.__plotModel is not None:
            self.__plotModel.structureChanged.connect(self.__structureChanged)
            self.__plotModel.itemValueChanged.connect(self.__itemValueChanged)
        self.__updateTree()

    def __currentScanChanged(self, scanModel):
        self.__setScan(scanModel)

    def __structureChanged(self):
        self.__updateTree()

    def __itemValueChanged(
        self, item: plot_model.Item, eventType: plot_model.ChangeEventType
    ):
        pass

    def plotModel(self) -> plot_model.Plot | None:
        return self.__plotModel

    def __setScan(self, scan):
        self.__scan = scan
        self.__updateTree()

    def __genScanTree(
        self,
        model: qt.QStandardItemModel,
        scan: scan_model.Scan,
    ) -> dict[str, _DataItem]:
        assert self.__tree is not None
        assert self.__flintModel is not None
        assert self.__plotModel is not None
        scanTree: dict[scan_model.Device, _DataItem] = {}
        channelItems: dict[str, _DataItem] = {}

        devices: list[qt.QStandardItem] = []
        channelsPerDevices: dict[qt.QStandardItem, int] = {}

        for device in scan.devices():
            if (
                device.master() is not None
                and device.master().type() == scan_model.DeviceType.MCA
                and device.type() == scan_model.DeviceType.VIRTUAL_MCA_DETECTOR
            ):
                # hide this node
                # hide_device = True
                # FIXME: This is often buggy so let's fallback to False
                hide_device = False
            else:
                hide_device = False

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

            if not hide_device:
                item = _DataItem()
                item.setEnvironment(self.__tree, self.__flintModel)
                scanTree[device] = item
                parent.appendRow(item.rowItems())
                # It have to be done when model index are initialized
                item.setDevice(device)
                devices.append(item)
            else:
                # Feed the content to the parent
                item = parent

            channels = []
            if device.type() in [
                scan_model.DeviceType.LIMA,
                scan_model.DeviceType.MCA,
                scan_model.DeviceType.MOSCA,
                scan_model.DeviceType.VIRTUAL_MCA_DETECTOR,
            ]:
                for channel in device.channels():
                    if channel.type() not in set(
                        [
                            scan_model.ChannelType.SPECTRUM,
                            scan_model.ChannelType.SPECTRUM_D_C,
                        ]
                    ):
                        continue
                    channels.append(channel)

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
        # FIXME: expanded/collapsed items have to be restored

        model = self.__tree.model()
        model.clear()

        if self.__plotModel is None:
            model.setHorizontalHeaderLabels([""])
            foo = qt.QStandardItem("")
            model.appendRow(foo)
            return

        model.setHorizontalHeaderLabels(
            ["Name", "Use", "Displayed", "Style", "Message"]
        )
        self.__tree.setItemDelegateForColumn(
            self.VisibleColumn, self.__visibilityDelegate
        )
        header = self.__tree.header()
        header.setSectionResizeMode(self.NameColumn, qt.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(self.UseColumn, qt.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(self.VisibleColumn, qt.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(self.StyleColumn, qt.QHeaderView.ResizeToContents)

        scan = self.__scan
        if scan is not None:
            channelItems = self.__genScanTree(
                model,
                scan,
            )
        else:
            channelItems = {}

        itemWithoutLocation = qt.QStandardItem("Not linked to this scan")
        model.appendRow(itemWithoutLocation)

        for plotItem in self.__plotModel.items():
            if not isinstance(plotItem, plot_item_model.McaItem):
                continue

            mcaChannel = plotItem.mcaChannel()
            if mcaChannel is None:
                continue

            mcaChannelName = mcaChannel.name()
            if mcaChannelName in channelItems:
                channelItem = channelItems[mcaChannelName]
                channelItem.setPlotItem(plotItem)
            else:
                item = _DataItem()
                item.setEnvironment(self.__tree, self.__flintModel)
                itemWithoutLocation.appendRow(item.rowItems())
                # It have to be done when model index are initialized
                item.setPlotItem(plotItem)

        if itemWithoutLocation.rowCount() == 0:
            model.removeRows(itemWithoutLocation.row(), 1)

        self.__tree.expandAll()
