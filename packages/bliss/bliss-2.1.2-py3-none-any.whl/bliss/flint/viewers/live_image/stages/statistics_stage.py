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
from silx.math.combo import min_max
from .base_stage import BaseStage


_logger = logging.getLogger(__name__)


class StatisticsStage(BaseStage):
    def __init__(self, parent: qt.QObject | None = None):
        BaseStage.__init__(self, parent=parent)
        self.__minimum = None
        self.__maximum = None
        self.__nanmean = None
        self.__nanstd = None

    def setEnabled(self, enabled: bool):
        super().setEnabled(enabled)
        if not self.isEnabled():
            self.clear()

    def clear(self):
        self.__minimum = None
        self.__maximum = None
        self.__nanmean = None
        self.__nanstd = None
        self.sinkResultUpdated.emit()

    def correction(self, array: numpy.ndarray):
        self._resetApplyedCorrections()

        result = min_max(array, min_positive=True, finite=True)
        self.__minimum = result.minimum
        self.__maximum = result.maximum
        # result.min_positive)
        # result.argmin
        # result.argmin_positive
        # result.argmax
        self.__nanmean = numpy.nanmean(array)
        self.__nanstd = numpy.nanstd(array)

        self.sinkResultUpdated.emit()

    def minimum(self):
        return self.__minimum

    def maximum(self):
        return self.__maximum

    def nanmean(self):
        return self.__nanmean

    def nanstd(self):
        return self.__nanstd
