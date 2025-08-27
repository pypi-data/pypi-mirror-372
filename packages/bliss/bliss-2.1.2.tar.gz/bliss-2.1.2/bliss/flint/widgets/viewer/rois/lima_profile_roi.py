# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

from __future__ import annotations

import enum
import logging

from silx.gui.plot import items
from silx.gui.colors import rgba
from .lima_rect_roi import LimaRectRoi

_logger = logging.getLogger(__name__)


class LimaProfileRoi(LimaRectRoi):
    """Rectangle ROI used to configure Lima detector.

    It is used to compute a vertical or horizontal profile.
    """

    class Directions(enum.Enum):
        VERTICAL_REDUCTION = "vertical-reduction"
        HORIZONTAL_REDUCTION = "horizontal-reduction"

    def __init__(self, parent=None):
        super(LimaProfileRoi, self).__init__(parent=parent)
        self.__limaKind = self.Directions.VERTICAL_REDUCTION
        line = items.Shape("polylines")
        # line.setPoints([[0, 0], [0, 0]])
        line.setOverlay(True)
        line.setLineStyle(self.getLineStyle())
        line.setLineWidth(self.getLineWidth())
        line.setColor(rgba(self.getColor()))
        self.__line = line
        self.addItem(line)
        symbol = items.Marker()
        symbol.setColor(rgba(self.getColor()))
        self.addItem(symbol)
        self.__symbol = symbol
        self.__updateOverlay()
        self.sigRegionChanged.connect(self.__regionChanged)

    def _updated(self, event=None, checkVisibility=True):
        if event in [items.ItemChangedType.VISIBLE]:
            self._updateItemProperty(event, self, self.__line)
            self._updateItemProperty(event, self, self.__symbol)
        super(LimaProfileRoi, self)._updated(event, checkVisibility)

    def _updatedStyle(self, event, style):
        super(LimaProfileRoi, self)._updatedStyle(event, style)
        self.__line.setColor(style.getColor())
        self.__line.setLineStyle(style.getLineStyle())
        self.__line.setLineWidth(style.getLineWidth())
        self.__symbol.setColor(style.getColor())

    def __regionChanged(self):
        self.__updateOverlay()

    def setLimaKind(self, direction):
        if self.__limaKind == direction:
            return
        self.__limaKind = direction
        self.__updateOverlay()

    def getLimaKind(self):
        return self.__limaKind

    def setParent(self, parent):
        super(LimaProfileRoi, self).setParent(parent)
        self.__updateOverlay()

    def _getPlot(self):
        manager = self.parent()
        if manager is None:
            return None
        plot = manager.parent()
        return plot

    def _isYAxisInverted(self):
        plot = self._getPlot()
        if plot is not None:
            return plot.isYAxisInverted()
        return False

    def __updateOverlay(self):
        x, y = self.getCenter()
        w, h = self.getSize()
        w, h = w / 2, h / 2
        if self.__limaKind == self.Directions.HORIZONTAL_REDUCTION:
            points = [[x - w, y], [x + w, y]]
            symbol = "caretright"
        elif self.__limaKind == self.Directions.VERTICAL_REDUCTION:
            symbol = "caretdown"
            if self._isYAxisInverted():
                points = [[x, y - h], [x, y + h]]
            else:
                points = [[x, y + h], [x, y - h]]
        else:
            assert False
        self.__line.setPoints(points)
        self.__symbol.setSymbol(symbol)
        self.__symbol.setPosition(*points[1])

    def clone(self):
        newRoi = type(self)()
        newRoi.setGeometry(origin=self.getOrigin(), size=self.getSize())
        newRoi.setLimaKind(self.getLimaKind())
        return newRoi
