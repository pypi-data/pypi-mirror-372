# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

from __future__ import annotations

import logging
import weakref
import typing

from silx.gui.plot.items import roi as roi_items
from bliss.flint.widgets.viewer import viewer_events


_logger = logging.getLogger(__name__)


class ImagePlotWidgetApi:
    def __init__(self, parent):
        from .viewer import ImagePlotWidget

        self._parent: ImagePlotWidget = parent
        self._parent.viewerEvent.connect(self.__viewerEvent)
        self._markers: weakref.WeakValueDictionary = weakref.WeakValueDictionary()
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

    def updateMarker(
        self,
        uniqueName: str,
        position: tuple[float, float] | None = None,
        text: str | None = None,
        editable: bool | None = None,
        kind: str | None = None,
    ):
        """
        Create or update a marker into the image.

        Arguments:
            uniqueName: Unique name identifying this marker
            position: X and Y position in the image, else None to remove the marker
            text: Text to display with the marker
            editable: If true, the marker can be moved with the mouse
            kind: Shape of the ROI. One of `point`, `cross`, `vline`, `hline`
        """
        item = self._markers.get(uniqueName, None)
        manager = self._parent.markerAction().getRoiManager()
        wasNotThere = item is None
        if item is None:
            if kind in (None, "point", "."):
                item = roi_items.PointROI(manager)
            elif kind in ("cross", "+"):
                item = roi_items.CrossROI(manager)
            elif kind in ("vline", "|"):
                item = roi_items.VerticalLineROI(manager)
            elif kind in ("hline", "-"):
                item = roi_items.HorizontalLineROI(manager)
            else:
                raise ValueError(f"Expected one of '.-+|', found {kind}")

        if position is not None:
            item.setPosition(position)
        if editable is not None:
            item.setEditable(editable)
        if text is not None:
            item.setName(text)

        if wasNotThere:
            manager.addRoi(item)
            self._markers[uniqueName] = item

    def removeMarker(self, uniqueName: str):
        """
        Remove a marker already existing.

        If the marker is not there, no feedback is returned.

        Arguments:
            uniqueName: Unique name identifying this marker
        """
        item = self._markers.pop(uniqueName, None)
        manager = self._parent.markerAction().getRoiManager()
        if item is not None:
            manager.removeRoi(item)
            item.deleteLater()

    def markerPosition(self, uniqueName: str) -> tuple[float, float] | None:
        """
        Create or update a marker into the image.

        Arguments:
            unique_name: Unique name identifying this marker

        Returns:
            The position of the marker, else None if the marker does not exist
        """
        item = self._markers.get(uniqueName, None)
        if item is None:
            return None
        return item.getPosition()
