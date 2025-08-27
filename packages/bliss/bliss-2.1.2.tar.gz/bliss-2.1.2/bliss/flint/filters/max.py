# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

"""
Implementation of a max filter.
"""
from __future__ import annotations
from typing import NamedTuple

import numpy
import logging

from ..model import scan_model
from ..model import plot_model
from ..model.plot_item_model import CurveStatisticItem

_logger = logging.getLogger(__name__)


class MaxData(NamedTuple):
    max_index: int
    max_location_y: float
    max_location_x: float
    min_y_value: float
    nb_points: int


class MaxCurveItem(CurveStatisticItem, plot_model.IncrementalComputableMixIn[MaxData]):
    """Statistic identifying the maximum location of a curve."""

    NAME = "Max marker"
    ICON_NAME = "flint:icons/item-stats"

    def name(self) -> str:
        return "Max"

    def isResultValid(self, result):
        return result is not None

    def compute(self, scan: scan_model.Scan) -> MaxData | None:
        sourceItem = self.source()
        assert sourceItem is not None

        xx = sourceItem.xArray(scan)
        yy = sourceItem.yArray(scan)
        if xx is None or yy is None:
            return None

        max_index = numpy.argmax(yy)
        min_y_value = numpy.min(yy)
        max_location_x, max_location_y = xx[max_index], yy[max_index]

        result = MaxData(
            int(max_index), max_location_y, max_location_x, min_y_value, len(xx)
        )
        return result

    def incrementalCompute(
        self, previousResult: MaxData, scan: scan_model.Scan
    ) -> MaxData:
        sourceItem = self.source()
        assert sourceItem is not None

        xx = sourceItem.xArray(scan)
        yy = sourceItem.yArray(scan)
        if xx is None or yy is None:
            raise ValueError("Non empty data is expected")

        nb = previousResult.nb_points
        if nb == len(xx):
            # obviously nothing to compute
            return previousResult

        xx = xx[nb:]
        yy = yy[nb:]

        max_index = numpy.argmax(yy)
        min_y_value = numpy.min(yy)
        max_location_x, max_location_y = xx[max_index], yy[max_index]
        max_index = max_index + nb

        if previousResult.min_y_value < min_y_value:
            min_y_value = previousResult.min_y_value

        if previousResult.max_location_y > max_location_y:
            # Update and return the previous result
            return MaxData(
                previousResult.max_index,
                previousResult.max_location_y,
                previousResult.max_location_x,
                min_y_value,
                nb + len(xx),
            )

        # Update and new return the previous result
        result = MaxData(
            int(max_index), max_location_y, max_location_x, min_y_value, nb + len(xx)
        )
        return result
