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


class SaturationStage(BaseStage):
    def __init__(self, parent: qt.QObject | None = None):
        BaseStage.__init__(self, parent=parent)
        self.__mask = None
        self.__value = None

    def setValue(self, value):
        if self.__value == value:
            return
        self.__value = value
        self.configUpdated.emit()

    def value(self):
        return self.__value

    def saturationMask(self):
        """Returns the mask used to filter the image"""
        return self.__mask

    def correction(self, image: numpy.ndarray):
        self._resetApplyedCorrections()
        if self.__value is None:
            self.__mask = None
            return
        self.__mask = image > self.__value
        return None
