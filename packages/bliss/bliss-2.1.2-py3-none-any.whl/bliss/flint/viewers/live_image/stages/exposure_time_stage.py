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
from .info import ImageCorrections
from .base_stage import BaseStage


_logger = logging.getLogger(__name__)


class ExposureTimeStage(BaseStage):
    def __init__(self, parent: qt.QObject | None = None):
        BaseStage.__init__(self, parent=parent)

    def correction(self, array: numpy.ndarray, exposureTime: float | None):
        self._resetApplyedCorrections()
        if exposureTime is not None:
            array = array / exposureTime
            self._setApplyedCorrections([ImageCorrections.EXPOTIME_CORRECTION])
        return array
