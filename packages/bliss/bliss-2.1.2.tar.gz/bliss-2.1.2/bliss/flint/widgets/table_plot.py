# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

from __future__ import annotations

import numbers
import datetime
import logging

from silx.gui import qt
from silx.gui import icons

from bliss.flint.model import scan_model
from bliss.flint.model import flint_model
from bliss.flint.helper import scan_info_helper
from bliss.flint.helper import scan_history
from bliss.flint.widgets.extended_dock_widget import ExtendedDockWidget
from bliss.flint.widgets.viewer import refresh_manager
from bliss.flint.widgets.viewer import viewer_events
from . import interfaces


_logger = logging.getLogger(__name__)


class CenteringFloatingPointDot(qt.QStyledItemDelegate):
    def displayText(self, value, locale):
        if isinstance(value, numbers.Number):
            return str(value)
        return str(value)

    def paint(
        self,
        painter: qt.QPainter,
        option: qt.QStyleOptionViewItem,
        index: qt.QModelIndex,
    ):
        value = index.data(qt.Qt.DisplayRole)
        if not isinstance(value, numbers.Number):
            return super(CenteringFloatingPointDot, self).paint(painter, option, index)

        text = option.text
        if text is None or text == "":
            text = self.displayText(value, option.locale)
            option.text = text
        if "." not in text:
            return super(CenteringFloatingPointDot, self).paint(painter, option, index)

        elements = text.split(".")
        fontMetrics = option.fontMetrics
        prefix = fontMetrics.width(elements[0])
        option.text = text
        width = option.rect.width()
        padding = width // 2 - prefix
        if padding > 0 and padding < width:
            option.rect.setLeft(option.rect.left() + padding)
        return super(CenteringFloatingPointDot, self).paint(painter, option, index)

    def sizeHint(self, option: qt.QStyleOptionViewItem, index: qt.QModelIndex):
        value = index.data(qt.Qt.SizeHintRole)
        if value is not None:
            return value
        value = index.data(qt.Qt.DisplayRole)
        if not isinstance(value, numbers.Number):
            return super(CenteringFloatingPointDot, self).sizeHint(option, index)

        text = option.text
        if text is None or text == "":
            text = self.displayText(value, option.locale)
            option.text = text
        if "." not in text:
            return super(CenteringFloatingPointDot, self).sizeHint(option, index)

        elements = text.split(".")
        fontMetrics = option.fontMetrics
        prefix = fontMetrics.width(elements[0])
        dot = fontMetrics.width(".")
        suffix = fontMetrics.width(elements[1])

        option.text = ""
        base = super(CenteringFloatingPointDot, self).sizeHint(option, index)
        option.text = text

        half = max(prefix, suffix)
        size = qt.QSize(half * 2 + dot + base.width(), base.height())
        return size


class Formatter:
    def __init__(self):
        self.__integrationTime: float = 0
        self.__integrationMode: bool = False

    def setIntegrationTime(self, integrationTime: float):
        self.__integrationTime = integrationTime

    def setIntegrationMode(self, integrationMode: bool):
        self.__integrationMode = integrationMode

    def __getLastValueFromChannel(self, channel: scan_model.Channel):
        data = channel.data()
        if data is None:
            return None
        array = data.array()
        if array is None:
            return None
        if len(array) <= 0:
            return None
        return array[-1]

    def __formatEpoch(self, channel: scan_model.Channel):
        try:
            value = self.__getLastValueFromChannel(channel)
            dt = datetime.datetime.fromtimestamp(value)
            text = dt.isoformat(sep=" ")
            icon = qt.QIcon()
        except Exception as e:
            text = e.args[0]
            icon = icons.getQIcon("flint:icons/warning")

        unit = channel.unit()
        if unit == "s":
            unit = ""
        return text, icon, unit

    def __formatElapsedTime(self, channel: scan_model.Channel):
        try:
            value = self.__getLastValueFromChannel(channel)
            text = value
            icon = qt.QIcon()
        except Exception as e:
            text = e.args[0]
            icon = icons.getQIcon("flint:icons/warning")
        unit = channel.unit()
        return text, icon, unit

    def __formatAxis(self, channel: scan_model.Channel):
        try:
            value = self.__getLastValueFromChannel(channel)
            text = value
            icon = qt.QIcon()
        except Exception as e:
            text = e.args[0]
            icon = icons.getQIcon("flint:icons/warning")
        unit = channel.unit()
        return text, icon, unit

    def __formatIntegratedValue(self, channel: scan_model.Channel):
        try:
            value = self.__getLastValueFromChannel(channel)
            text: str
            if isinstance(value, (numbers.Real, numbers.Integral)):
                if self.__integrationMode:
                    text = str(value / self.__integrationTime)
                else:
                    text = str(value)
            elif value is None:
                text = "∅"
            else:
                text = str(value)
            icon = qt.QIcon()
        except Exception as e:
            text = e.args[0]
            icon = icons.getQIcon("flint:icons/warning")

        unit = channel.unit()
        if unit is None:
            unit = ""
        if self.__integrationMode:
            if unit == "s":
                # Obvious case
                # FIXME: It would be better to use pint
                unit = ""
            else:
                unit = f"{unit}/s"
        return text, icon, unit

    def format(self, channel: scan_model.Channel):
        name = channel.name()
        if channel.unit() == "s":
            if name.endswith(":elapsed_time"):
                return self.__formatElapsedTime(channel)
            if name.endswith(":epoch"):
                return self.__formatEpoch(channel)
        if "axis:" in name:
            return self.__formatAxis(channel)
        return self.__formatIntegratedValue(channel)


class TablePlotWidget(ExtendedDockWidget, interfaces.HasPlotModel, interfaces.HasScan):

    widgetActivated = qt.Signal(object)

    scanModelUpdated = qt.Signal(object)
    """Emitted when the scan model displayed by the plot was changed"""

    def __init__(self, parent=None):
        super(TablePlotWidget, self).__init__(parent=parent)

        self.__scan: scan_model.Scan | None = None
        self.__flintModel: flint_model.FlintState | None = None

        self.__aggregator = viewer_events.ScalarEventAggregator(self)
        self.__refreshManager = refresh_manager.RefreshManager(self)
        self.__refreshManager.setAggregator(self.__aggregator)
        self.__refreshManager.setRefreshMode(100)

        mainWidget = qt.QFrame(self)
        mainWidget.setFrameShape(qt.QFrame.StyledPanel)
        mainWidget.setAutoFillBackground(True)

        self.__table = qt.QTableView(mainWidget)
        model = qt.QStandardItemModel(self.__table)
        self.__table.setModel(model)
        self.__table.setFrameShape(qt.QFrame.NoFrame)
        delegate = CenteringFloatingPointDot(self.__table)
        self.__table.setItemDelegate(delegate)

        self.__title = qt.QLabel(mainWidget)
        self.__title.setAlignment(qt.Qt.AlignHCenter)
        self.__title.setTextInteractionFlags(qt.Qt.TextSelectableByMouse)
        self.__title.setStyleSheet("QLabel {font-size: 14px;}")

        toolbar = self.__createToolBar()

        line = qt.QFrame(self)
        line.setFrameShape(qt.QFrame.HLine)
        line.setFrameShadow(qt.QFrame.Sunken)

        layout = qt.QVBoxLayout(mainWidget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(toolbar)
        layout.addWidget(line)
        layout.addWidget(self.__title)
        layout.addWidget(self.__table)

        # Try to improve the look and feel
        # FIXME: THis should be done with stylesheet
        widget = qt.QFrame(self)
        layout = qt.QVBoxLayout(widget)
        layout.addWidget(mainWidget)
        layout.setContentsMargins(0, 1, 0, 0)
        self.setWidget(widget)

    def __createToolBar(self):
        toolBar = qt.QToolBar(self)
        toolBar.setMovable(False)

        action = qt.QAction(self)
        icon = icons.getQIcon("flint:icons/scan-history")
        action.setIcon(icon)
        action.setToolTip(
            "Load a previous scan stored in Redis (about 24 hour of history)"
        )
        action.triggered.connect(self.__requestLoadScanFromHistory)
        toolBar.addAction(action)

        toolBar.addSeparator()

        action = qt.QAction()
        action.setText("Integration")
        action.setToolTip("Divide the values by the integration time")
        action.setCheckable(True)
        icon = icons.getQIcon("flint:icons/mode-integration")
        action.setIcon(icon)
        action.toggled.connect(self.__displayModeChanged)
        toolBar.addAction(action)
        self.__integrationMode = action

        return toolBar

    def setPlotModel(self, model):
        pass

    def plotModel(self):
        return None

    def __displayModeChanged(self):
        self.__updateData()

    def __requestLoadScanFromHistory(self):
        from bliss.flint.dialog.scan_history_dialog import ScanHistoryDialog

        assert self.__flintModel is not None
        sessionName = self.__flintModel.blissSessionName()

        dialog = ScanHistoryDialog(self)
        dialog.setFlintModel(self.__flintModel)
        # Only display ct-like scans
        dialog.setCategoryFilter(point=True, nscan=False, mesh=False, others=False)
        dialog.setSessionName(sessionName)
        result = dialog.exec_()
        if result:
            selection = dialog.selectedScanNodeNames()
            if len(selection) == 0:
                _logger.error("No selection")
                return

            nodeName = selection[0]
            try:
                scan = scan_history.create_scan(nodeName)
            except Exception:
                _logger.error("Error while loading scan from history", exc_info=True)
                qt.QMessageBox.critical(
                    None,
                    "Error",
                    "An error occurred while a scan was loading from the history",
                )
            else:
                self.setScan(scan)

    def createPropertyWidget(self, parent: qt.QWidget):
        propertyWidget = qt.QWidget(parent)
        return propertyWidget

    def flintModel(self) -> flint_model.FlintState | None:
        return self.__flintModel

    def setFlintModel(self, flintModel: flint_model.FlintState | None):
        self.__flintModel = flintModel

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
        self.__scan = scan
        # As the scan was updated, clear the previous cached events
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
        self.scanModelUpdated.emit(scan)

        self.__redrawAll()

    def __clear(self):
        model = self.__table.model()
        model.clear()

    def __scanStarted(self):
        self.__updateFields()
        self.__updateTitle()

    def __updateTitle(self):
        scan = self.__scan
        title = scan_info_helper.get_full_title(scan)
        self.__title.setText(title)

    def __scanFinished(self):
        self.__updateData()

    def __scanDataUpdated(self, event: scan_model.ScanDataUpdateEvent):
        self.__updateData()

    def __redrawAll(self):
        self.__updateTitle()
        self.__updateFields()
        self.__updateData()

    def __updateFields(self):
        model = self.__table.model()
        model.clear()
        model.setHorizontalHeaderLabels(["Channel", "Name", "Value", "Unit"])

        header = self.__table.verticalHeader()
        header.setVisible(False)

        header = self.__table.horizontalHeader()
        header.setSectionResizeMode(0, qt.QHeaderView.Fixed)
        header.setSectionResizeMode(1, qt.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, qt.QHeaderView.Stretch)
        header.setSectionResizeMode(3, qt.QHeaderView.ResizeToContents)
        header.setSectionHidden(0, True)

        scan = self.__scan
        if scan is None:
            return

        for device in scan.devices():
            for channel in device.channels():
                if channel.type() != scan_model.ChannelType.COUNTER:
                    continue

                channelName = channel.name()
                name = channel.displayName()
                unit = channel.unit()
                if unit is None:
                    unit = ""
                value = "..."

                data = [channelName, name, value, unit]
                items = []
                for d in data:
                    i = qt.QStandardItem(d)
                    i.setEditable(False)
                    items.append(i)
                model.appendRow(items)

    def __updateData(self):
        scan = self.__scan
        if scan is None:
            return

        formatter = Formatter()
        formatter.setIntegrationTime(scan.scanInfo().get("count_time", 1))
        formatter.setIntegrationMode(self.__integrationMode.isChecked())

        model = self.__table.model()
        for i in range(model.rowCount()):
            channelItem = model.item(i, 0)
            # nameItem = model.item(i, 1)
            valueItem = model.item(i, 2)
            unitItem = model.item(i, 3)
            channel = scan.getChannelByName(channelItem.text())
            text, icon, unit = formatter.format(channel)
            valueItem.setData(text, role=qt.Qt.DisplayRole)
            valueItem.setIcon(icon)
            unitItem.setText(unit)
