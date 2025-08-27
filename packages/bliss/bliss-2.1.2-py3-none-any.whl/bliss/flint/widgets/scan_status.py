# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

from __future__ import annotations
import typing

import time
import logging

from silx.gui import qt

from bliss.flint.model import scan_model
from bliss.flint.model import flint_model
from bliss.flint.widgets.extended_dock_widget import ExtendedDockWidget
from bliss.flint.widgets.stacked_progress_bar import StackedProgressBar
from bliss.flint.utils import stringutils
from bliss.flint.helper import scan_info_helper
from bliss.flint.helper import scan_progress

from . import interfaces


_logger = logging.getLogger(__name__)


DefaultColor = qt.QColor("#3B71CA")
RetryColor = qt.QColor("#E4A11B")
FailedColor = qt.QColor("#DC4C64")
UserAbortColor = qt.QColor("#9FA6B2")


class _SingleScanStatus(qt.QWidget):

    VALUE_FOR_SCAN_OF_SEQUENCE = 10

    def __init__(self, parent: qt.QWidget = None):
        super(_SingleScanStatus, self).__init__(parent=parent)

        self.__scanTitle = qt.QLabel(self)
        self.__process = StackedProgressBar(self)
        self.__childProcess = qt.QProgressBar(self)
        self.__childProcess.setVisible(False)
        self.__subHolder = qt.QWidget(self)
        self.__subHolder.setVisible(False)

        self.__subLayout = qt.QVBoxLayout(self.__subHolder)
        self.__subLayout.setContentsMargins(0, 0, 0, 0)

        self.__subWidget: _SingleScanStatus | None = None
        self.__scan: scan_model.Scan | None = None
        self.__start: float | None = None
        self.__end: float | None = None
        self.__childScan: scan_model.Scan | None = None
        self.__childStart: float | None = None
        self.__childEnd: float | None = None
        self.__scanCount: int | None = None

        layout = qt.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.__scanTitle)
        layout.addWidget(self.__process)
        layout.addWidget(self.__subHolder)

        self.__timer = qt.QTimer(self)
        self.__timer.setInterval(1000)
        self.__timer.timeout.connect(self.__updatePeriodically)

        self._updateWhenNoScan()

    def scan(self) -> scan_model.Scan | None:
        return self.__scan

    def setScan(self, scan: scan_model.Scan | None = None):
        if self.__scan is scan:
            return
        if self.__scan is not None:
            self.__scan.scanStarted.disconnect(self.__scanStarted)
            self.__scan.scanFinished.disconnect(self.__scanFinished)
            if isinstance(self.__scan, scan_model.ScanGroup):
                self.__scan.subScanAdded.disconnect(self.__subScanAdded)
        self.__scan = scan
        if self.__scan is not None:
            self.__scan.scanStarted.connect(self.__scanStarted)
            self.__scan.scanFinished.connect(self.__scanFinished)
            if isinstance(self.__scan, scan_model.ScanGroup):
                self.__scan.subScanAdded.connect(self.__subScanAdded)
        self.__updateByState()

    def __scanStarted(self):
        self._updateWhenStarted()

    def __scanFinished(self):
        self._updateWhenFinished()

    def __updateByState(self):
        scan = self.__scan
        if scan is None:
            self.__updateNoScan()
        else:
            self.__parseScanInfo()
            if scan.state() == scan_model.ScanState.INITIALIZED:
                self._updateWhenInitialized()
            elif scan.state() == scan_model.ScanState.PROCESSING:
                self._updateWhenStarted()
            elif scan.state() == scan_model.ScanState.FINISHED:
                self._updateWhenFinished()

    def __parseScanInfo(self):
        scan = self.__scan
        childScan = self.__childScan
        assert scan is not None
        title = scan_info_helper.get_full_title(scan)
        info = scan.scanInfo()

        if childScan is not None:
            childTitle = scan_info_helper.get_full_title(childScan)
            title = f"{title} - {childTitle}"
        self.setToolTip(title)

        self.__scanCount = info.get("sequence_info", {}).get("scan_count", None)

        self.__childEnd = None

        self.__scanTitle.setText(title)

        self.__end = None

    def __updatePeriodically(self):
        self.updateRemaining()

    def updateRemaining(self):
        scan = self.__scan
        if self.__end is not None:
            now = time.time()
            remaining = self.__end - now
            if remaining < 0:
                remaining = 0
            remaining = stringutils.human_readable_duration(seconds=round(remaining))
            # self.__widget.remainingTime.setText(f"Remaining time: {remaining}")
        percent = scan_progress.get_scan_progress_percent(scan)
        if percent is not None:
            self.__process.setProgressItem(
                "progress", color=DefaultColor, value=int(percent * 100)
            )

    def setActiveChildScan(self, scan: scan_model.Scan | None = None):
        layout = self.__subHolder.layout()
        if self.__subWidget is not None:
            w = self.__subWidget
            w.deleteLater()
            layout.removeWidget(w)
            self.__subWidget = None
        if scan is not None:
            widget = _SingleScanStatus(self)
            widget.setScan(scan)
            self.__subHolder.setVisible(True)
            self.__subWidget = widget
            layout.addWidget(self.__subWidget)
        else:
            self.__subHolder.setVisible(False)

    def __subScanAdded(self, scan: scan_model.Scan):
        group: scan_model.ScanGroup = typing.cast(scan_model.ScanGroup, self.__scan)

        if self.__scanCount is None:
            nb = len(group.subScans())
            self.__process.setRange(0, nb * self.VALUE_FOR_SCAN_OF_SEQUENCE)

        if len(group.subScans()) >= 2:
            previousScan = group.subScans()[-2]
            previousInfo = previousScan.scanInfo()
            previousIndex = previousInfo.get(
                "index_in_sequence", len(group.subScans()) - 2
            )
            toolTip, color = self._getFinalTooltip(previousScan)
            self.__process.setProgressItem(
                f"s{previousIndex}",
                color=color,
                striped=False,
                animated=False,
                toolTip=toolTip,
            )

        info = scan.scanInfo()
        index = info.get("index_in_sequence", len(group.subScans()) - 1)
        title = scan_info_helper.get_full_title(scan)
        retry_nb = info.get("retry_nb", 0)
        if retry_nb == 0:
            color = DefaultColor
        else:
            color = RetryColor
            title += f"{title} (retried)"
        self.__process.setProgressItem(
            f"s{index}",
            color=color,
            value=self.VALUE_FOR_SCAN_OF_SEQUENCE,
            striped=True,
            animated=True,
            toolTip=title,
        )

        self.setActiveChildScan(scan)

    def _updateWhenNoScan(self):
        self.__scanTitle.setText("No scan available")
        self.__process.setVisible(False)

    def _updateWhenInitialized(self):
        self.__process.setVisible(False)

    def _updateWhenStarted(self):
        self.__start = time.time()

        scan = self.__scan
        self.__process.clear()
        if isinstance(scan, scan_model.ScanGroup):
            group: scan_model.ScanGroup = scan
            self.__process.setSpacing(1)
            self.__process.setSpacingCollapsible(False)
            if self.__scanCount is not None:
                self.__process.setRange(
                    0, self.__scanCount * self.VALUE_FOR_SCAN_OF_SEQUENCE
                )
            else:
                nb = max(len(group.subScans()), 1)
                self.__process.setRange(0, nb)
            self.__process.setProgressItem(
                "s0",
                color=DefaultColor,
                value=self.VALUE_FOR_SCAN_OF_SEQUENCE,
                striped=True,
                animated=True,
            )
        else:
            self.__process.setProgressItem(
                "progress", color=DefaultColor, value=0, striped=True, animated=True
            )
            self.__process.setRange(0, 100)
            self.__timer.start()

        self.__process.setVisible(True)
        self.updateRemaining()

    def _getFinalTooltip(self, scan: scan_model.Scan) -> tuple[str, qt.QColor]:
        if isinstance(scan, scan_model.ScanGroup):
            name = "Sequence"
        else:
            name = "Scan"

        info = scan.scanInfo()
        scan_nb = info.get("scan_nb", None)
        if scan_nb is not None:
            scan_ref = f"{name} #{scan_nb}"
        else:
            scan_ref = f"{name}"

        endReason = scan.endReason()
        if endReason == scan_model.ScanEndReason.SUCCESS:
            color = DefaultColor
            toolTip = f"{scan_ref} successfully terminated"
        elif endReason == scan_model.ScanEndReason.FAILURE:
            color = FailedColor
            toolTip = f"{scan_ref} have failed"
        elif endReason == scan_model.ScanEndReason.DELETION:
            color = FailedColor
            toolTip = f"{scan_ref} deleted by BLISS"
        elif endReason == scan_model.ScanEndReason.USER_ABORT:
            color = UserAbortColor
            toolTip = f"{scan_ref} aborted by the user"
        else:
            color = FailedColor
            toolTip = f"{scan_ref} status unknown"
        return toolTip, color

    def _updateWhenFinished(self):
        self.__start = None
        self.__end = None
        self.__timer.stop()

        scan = self.__scan
        assert scan is not None
        toolTip, color = self._getFinalTooltip(scan)

        if isinstance(scan, scan_model.ScanGroup):
            group: scan_model.ScanGroup = scan
            for i, s in enumerate(group.subScans()):
                index = s.scanInfo().get("index_in_sequence", i)
                self.__process.setProgressItem(
                    f"s{index}", striped=False, animated=False
                )
            self.__process.setMaximum(self.__process.maximum() + 1)
            self.__process.setProgressItem(
                "sequence",
                color=color,
                value=1,
                striped=False,
                animated=False,
                toolTip=toolTip,
            )
        else:
            self.updateRemaining()
            self.__process.setProgressItem(
                "progress", color=color, striped=False, animated=False, toolTip=toolTip
            )

        self.__process.setVisible(True)
        self.setActiveChildScan(None)


class _OtherScansStatus(qt.QLabel):
    def __init__(self, parent=None):
        qt.QLabel.__init__(self, parent=parent)
        self.setAlignment(qt.Qt.AlignCenter)
        self.setVisible(False)
        self.__scans = []

    def addScan(self, scan):
        self.__scans.append(scan)
        self.__updateDisplay()

    def removeScan(self, scan):
        try:
            self.__scans.remove(scan)
        except Exception:
            pass
        else:
            self.__updateDisplay()

    def popScan(self):
        if len(self.__scans) == 0:
            return None
        scan = self.__scans.pop(0)
        self.__updateDisplay()
        return scan

    def __updateDisplay(self):
        self.setVisible(len(self.__scans) != 0)
        if len(self.__scans) == 0:
            pass
        elif len(self.__scans) == 1:
            self.setText("plus another scan...")
        else:
            self.setText(f"plus {len(self.__scans)} other scans...")


class ScanStatus(ExtendedDockWidget, interfaces.HasScan):
    def __init__(self, parent=None):
        super(ScanStatus, self).__init__(parent=parent)

        self.__widget = qt.QWidget(self)
        _ = qt.QVBoxLayout(self.__widget)

        self.__scanWidgets: list[_SingleScanStatus] = []
        self.__otherScans = _OtherScansStatus(parent=self)

        # Try to improve the look and feel
        # FIXME: This should be done with stylesheet
        frame = qt.QFrame(self)
        frame.setFrameShape(qt.QFrame.StyledPanel)
        layout = qt.QVBoxLayout(frame)
        layout.addWidget(self.__widget)
        layout.addStretch(1)
        layout.addWidget(self.__otherScans)
        layout.setContentsMargins(0, 0, 0, 0)
        widget = qt.QFrame(self)
        layout = qt.QVBoxLayout(widget)
        layout.addWidget(frame)
        layout.setContentsMargins(0, 1, 0, 0)
        self.setWidget(widget)

        widget.setSizePolicy(qt.QSizePolicy.Preferred, qt.QSizePolicy.Preferred)

        self.__flintModel: flint_model.FlintState | None = None

        holder = _SingleScanStatus(self)
        self.__addScanWidget(holder)

    def setFlintModel(self, flintModel: flint_model.FlintState | None = None):
        if self.__flintModel is not None:
            self.__flintModel.aliveScanAdded.disconnect(self.__aliveScanAdded)
            self.__flintModel.aliveScanRemoved.disconnect(self.__aliveScanRemoved)
            self.__flintModel.currentScanChanged.disconnect(self.__currentScanChanged)
        self.__flintModel = flintModel
        if self.__flintModel is not None:
            self.__flintModel.aliveScanAdded.connect(self.__aliveScanAdded)
            self.__flintModel.aliveScanRemoved.connect(self.__aliveScanRemoved)
            self.__flintModel.currentScanChanged.connect(self.__currentScanChanged)

    def __getWidgetByScan(self, scan):
        for w in self.__scanWidgets:
            if w.scan() is scan:
                return w
        return None

    def __addScanWidget(self, widget):
        layout = self.__widget.layout()

        # Clear dead widgets
        safeList = list(self.__scanWidgets)
        for otherWidget in safeList:
            scan = otherWidget.scan()
            if scan is None or scan.state() == scan_model.ScanState.FINISHED:
                self.__scanWidgets.remove(otherWidget)
                otherWidget.deleteLater()

        layout.addWidget(widget)
        self.__scanWidgets.append(widget)
        self.updateGeometry()

    def __updateWidgets(self):
        for widget in self.__scanWidgets:
            widget.updateRemaining()

    def __removeWidgetFromScan(self, scan):
        assert self.__flintModel is not None
        if len(self.__scanWidgets) == 1:
            # Do not remove the last scan widget
            return

        if self.__flintModel.currentScan() is scan:
            # Do not remove the current scan widget
            # Right now it is the one displayed by the other widgets
            return

        widgets = [w for w in self.__scanWidgets if w.scan() is scan]
        if len(widgets) == 0:
            # No widget for this scan
            return

        assert len(widgets) == 1
        widget = widgets[0]

        self.__scanWidgets.remove(widget)
        widget.deleteLater()

        scan = self.__otherScans.popScan()
        if scan:
            self.__feedWidgetFromScan(scan)

    def __feedWidgetFromScan(self, scan):
        if scan.group() is not None:
            return
        if len(self.__scanWidgets) < 2:
            widget = _SingleScanStatus(self)
            widget.setScan(scan)
            self.__addScanWidget(widget)
        else:
            self.__otherScans.addScan(scan)

    def __aliveScanAdded(self, scan):
        self.__feedWidgetFromScan(scan)

    def __aliveScanRemoved(self, scan):
        self.__removeWidgetFromScan(scan)
        self.__otherScans.removeScan(scan)

    def __currentScanChanged(self):
        # TODO: The current scan could be highlighted
        pass
