# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

from __future__ import annotations

import numpy
import logging
from silx.gui import qt
from .base_stage import BaseStage


_logger = logging.getLogger(__name__)


class IsoContourStage(BaseStage):
    def __init__(self, parent: qt.QObject | None = None):
        BaseStage.__init__(self, parent=parent)
        self.__value = 20
        self.__isocontour = None

    def setValue(self, value):
        """Set the actual value"""
        self.__value = value
        self.configUpdated.emit()

    def value(self):
        """Returns the value used to filter the image"""
        return self.__value

    def isValid(self):
        return True

    def isoContours(self):
        return self.__isocontour

    def correction(self, image: numpy.ndarray, mask: numpy.ndarray | None):
        self._resetApplyedCorrections()
        try:
            from silx.image.marchingsquares import MarchingSquaresMergeImpl

            algo = MarchingSquaresMergeImpl(image, mask)
            polygons = algo.find_contours(self.__value)
            self.__isocontour = polygons
        except Exception:
            _logger.error("Error while computing isocontour", exc_info=True)
            self.__isocontour = None

        return None
