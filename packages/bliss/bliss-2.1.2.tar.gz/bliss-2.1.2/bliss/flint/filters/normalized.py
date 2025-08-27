# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

"""
Implementation of a normalization of the data using a monitor channel
"""
from __future__ import annotations

import numpy
import logging

from ..model import scan_model
from ..model import plot_model
from ..model import plot_item_model
from ..model.plot_item_model import getHashableSource

_logger = logging.getLogger(__name__)


class NormalizedCurveItem(plot_model.ChildItem, plot_item_model.CurveMixIn):
    """Curve based on a source item, normalized by a side channel."""

    NAME = "Normalized function"
    ICON_NAME = "flint:icons/item-func"

    def __init__(self, parent=None):
        plot_model.ChildItem.__init__(self, parent)
        plot_item_model.CurveMixIn.__init__(self)
        self.__monitor: plot_model.ChannelRef | None = None

    def __getstate__(self):
        state: dict[str, object] = {}
        state.update(plot_model.ChildItem.__getstate__(self))
        state.update(plot_item_model.CurveMixIn.__getstate__(self))
        monitor = self.__monitor
        if monitor is not None:
            state["monitor"] = monitor.name()
        return state

    def __setstate__(self, state):
        plot_model.ChildItem.__setstate__(self, state)
        plot_item_model.CurveMixIn.__setstate__(self, state)
        monitorName = state.get("monitor")
        if monitorName is not None:
            channel = plot_model.ChannelRef(None, monitorName)
            self.setMonitorChannel(channel)

    def name(self) -> str:
        monitor = self.__monitor
        if monitor is None:
            return "Normalized"
        else:
            return "Normalized by %s" % monitor.name()

    def inputData(self):
        return getHashableSource(self.source()) + getHashableSource(self.__monitor)

    def isValid(self):
        return self.source() is not None and self.__monitor is not None

    def getScanValidation(self, scan: scan_model.Scan) -> str | None:
        """
        Returns None if everything is fine, else a message to explain the problem.
        """
        xx = self.xArray(scan)
        yy = self.yArray(scan)
        monitor = self.__monitor
        if monitor is not None:
            if monitor.array(scan) is None:
                return "No data for the monitor"
        if xx is None and yy is None:
            return "No data available for X and Y data"
        elif xx is None:
            return "No data available for X data"
        elif yy is None:
            return "No data available for Y data"
        elif xx.ndim != 1:
            return "Dimension of X data do not match"
        elif yy.ndim != 1:
            return "Dimension of Y data do not match"
        elif len(xx) != len(yy):
            return "Size of X and Y data do not match"
        # It's fine
        return None

    def monitorChannel(self) -> plot_model.ChannelRef | None:
        return self.__monitor

    def setMonitorChannel(self, channel: plot_model.ChannelRef | None):
        self.__monitor = channel
        self._emitValueChanged(plot_model.ChangeEventType.Y_CHANNEL)

    def xData(self, scan: scan_model.Scan) -> scan_model.Data | None:
        source = self.source()
        assert source is not None
        return source.xData(scan)

    def yData(self, scan: scan_model.Scan) -> scan_model.Data | None:
        source = self.source()
        assert source is not None
        data = source.yArray(scan)
        if data is None:
            return None
        monitorChannel = self.monitorChannel()
        if monitorChannel is None:
            return None
        monitor = monitorChannel.array(scan)
        if data is None or monitor is None:
            return None
        # FIXME: Could be cached
        with numpy.errstate(all="ignore"):
            yy = data / monitor
        return scan_model.Data(None, yy)

    def setSource(self, source: plot_model.Item):
        previousSource = self.source()
        if previousSource is not None:
            previousSource.valueChanged.disconnect(self.__sourceChanged)
        plot_model.ChildItem.setSource(self, source)
        if source is not None:
            source.valueChanged.connect(self.__sourceChanged)
            self.__sourceChanged(plot_model.ChangeEventType.X_CHANNEL)
            self.__sourceChanged(plot_model.ChangeEventType.Y_CHANNEL)

    def __sourceChanged(self, eventType):
        if eventType == plot_model.ChangeEventType.Y_CHANNEL:
            self._emitValueChanged(plot_model.ChangeEventType.Y_CHANNEL)
        if eventType == plot_model.ChangeEventType.X_CHANNEL:
            self._emitValueChanged(plot_model.ChangeEventType.X_CHANNEL)

    def isAvailableInScan(self, scan: scan_model.Scan) -> bool:
        """Returns true if this item is available in this scan.

        This only imply that the data source is available.
        """
        if not plot_model.ChildItem.isAvailableInScan(self, scan):
            return False
        monitor = self.monitorChannel()
        if monitor is not None:
            if monitor.channel(scan) is None:
                return False
        return True

    def displayName(self, axisName, scan: scan_model.Scan) -> str:
        """Helper to reach the axis display name"""
        sourceItem = self.source()
        assert sourceItem is not None
        monitor = self.__monitor
        if axisName == "x":
            return sourceItem.displayName("x", scan)
        elif axisName == "y":
            if monitor is None:
                return "norm %s" % (sourceItem.displayName("y", scan))
            else:
                monitorName = monitor.displayName(scan)
                return "norm %s by %s" % (
                    sourceItem.displayName("y", scan),
                    monitorName,
                )
        else:
            assert False
