# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

from __future__ import annotations
from typing import NamedTuple

import enum
import logging

from bliss.flint.model import scan_model
from bliss.flint.utils import signalutils


_logger = logging.getLogger(__name__)


class ViewChangedEvent(NamedTuple):
    userInteraction: bool


class MouseMovedEvent(NamedTuple):
    xData: float
    yData: float
    xPixel: int
    yPixel: int


class PlotEventAggregator(signalutils.EventAggregator):
    def reduce(self, eventStack: list) -> tuple[list, list]:
        """Override the method to reduce plot refresh by
        removing duplication events.
        """
        result: list = []
        # Reduce specific channel events
        lastSpecificChannel: set[object] = set([])
        for event in reversed(eventStack):
            if len(event.args) == 0:
                result.insert(0, event)
                continue
            e = event.args[0]
            if not isinstance(e, scan_model.ScanDataUpdateEvent):
                result.insert(0, event)
                continue

            channel = e.selectedChannel()
            if channel is not None:
                if channel in lastSpecificChannel:
                    continue
                else:
                    lastSpecificChannel.add(channel)
            result.insert(0, event)
        return result, []


class ScalarEventAggregator(signalutils.EventAggregator):
    def reduce(self, eventStack: list) -> tuple[list, list]:
        """Override the method to reduce plot refresh by
        removing duplication events.
        """
        result: list = []
        # Reduce specific channel events
        fullDevices: set = set()
        fullAggregation: set = set()
        currentAggregation: set = set()
        currentScan = None
        currentCallback = None

        def flush():
            nonlocal currentAggregation, currentScan, currentCallback
            if len(currentAggregation) == 0:
                return
            e = scan_model.ScanDataUpdateEvent(
                currentScan, channels=list(currentAggregation)
            )
            result.insert(0, signalutils.Event(currentCallback, [e], {}))
            currentAggregation = set()
            currentScan = None
            currentCallback = None

        for event in reversed(eventStack):
            if len(event.args) == 0:
                result.insert(0, event)
                continue
            e = event.args[0]
            if not isinstance(e, scan_model.ScanDataUpdateEvent):
                result.insert(0, event)
                continue

            if event.kwargs != {}:
                result.insert(0, event)
                continue

            channels = e.selectedChannels()
            device = e.selectedDevice()
            if channels is not None:
                if fullAggregation.issuperset(channels):
                    continue
                if currentCallback is None or currentCallback is event.callback:
                    currentCallback = event.callback
                    currentScan = e.scan()
                    fullAggregation.update(channels)
                    currentAggregation.update(channels)
                else:
                    flush()
                    result.insert(0, event)
            elif device is not None:
                if device in fullDevices:
                    continue
                fullDevices.add(device)
                result.insert(0, event)
            else:
                flush()
                result.insert(0, event)
        flush()
        return result, []


class ViewerEventType(enum.Enum):
    SCAN_STARTED = 0
    """The UI starts to update the plot"""
    SCAN_FINISHED = 1
    """The UI have finished to update the plot"""


class ViewerEvent(NamedTuple):
    type: ViewerEventType


class ScanViewerEvent(NamedTuple):
    type: ViewerEventType
    scan: scan_model.Scan
