# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

from __future__ import annotations

import logging
import typing
from bliss.flint.widgets.viewer import viewer_events

if typing.TYPE_CHECKING:
    from .viewer import McaPlotWidget

_logger = logging.getLogger(__name__)


class OneDimPlotWidgetApi:
    def __init__(self, parent):
        self._parent: McaPlotWidget = parent
        self._parent.viewerEvent.connect(self.__viewerEvent)
        self.__terminatedScans = []

    def __viewerEvent(self, event: viewer_events.ViewerEvent):
        if event.type == viewer_events.ViewerEventType.SCAN_FINISHED:
            e = typing.cast(viewer_events.ScanViewerEvent, event)
            unique = e.scan.scanUniqueId()
            self.__appendTerminated(unique)

    def __appendTerminated(self, uniqueScanId: str):
        self.__terminatedScans.append(uniqueScanId)
        while len(self.__terminatedScans) > 10:
            self.__terminatedScans.pop(0)

    def scanWasTerminated(self, nodeName: str):
        return nodeName in self.__terminatedScans
