# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

from __future__ import annotations

import logging
import numpy
import silx.gui.plot.items.roi as silx_rois

_logger = logging.getLogger(__name__)


class LimaRectRoi(silx_rois.RectangleROI):
    """Rectangle ROI used to configure Lima detector.

    It is used to count sum, avg, min, max
    """

    def __init__(self, parent=None):
        silx_rois.RectangleROI.__init__(self, parent=parent)
        self.sigEditingFinished.connect(self.__normalizeGeometry)
        self.__sizeLabel = self.addLabelHandle()

    def setFirstShapePoints(self, points):
        # Normalize the ROI position to the pixel
        points = points.astype(int)
        silx_rois.RectangleROI.setFirstShapePoints(self, points)

    def _updateGeometry(self, origin=None, size=None, center=None):
        silx_rois.RectangleROI._updateGeometry(
            self, origin=origin, size=size, center=center
        )
        self.__updateSizeLabel()

    def __normalizeGeometry(self):
        # Normalize the ROI position to the pixel
        pixelcenter = numpy.array([0.5, 0.5])
        pos1 = self.getOrigin()
        pos2 = (pos1 + self.getSize() + pixelcenter).astype(int)
        pos1 = (pos1 + pixelcenter).astype(int)
        size = pos2 - pos1
        self.setGeometry(origin=pos1, size=size)

    def __updateSizeLabel(self):
        size = self.getSize().astype(int)
        pos = self.getOrigin().astype(int)
        self.__sizeLabel.setText(f"{size[0]}x{size[1]}")
        self.__sizeLabel.setPosition(*(pos + size * 0.5))

    def clone(self):
        newRoi = type(self)()
        newRoi.setGeometry(origin=self.getOrigin(), size=self.getSize())
        return newRoi
