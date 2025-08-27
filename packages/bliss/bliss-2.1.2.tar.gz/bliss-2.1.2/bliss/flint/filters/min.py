# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

"""
Implementation of a min filter.
"""
from __future__ import annotations
from typing import NamedTuple

import numpy
import logging

from ..model import scan_model
from ..model import plot_model
from ..model.plot_item_model import CurveStatisticItem

_logger = logging.getLogger(__name__)


class MinData(NamedTuple):
    min_index: int
    min_location_y: float
    min_location_x: float
    max_y_value: float
    nb_points: int


class MinCurveItem(CurveStatisticItem, plot_model.IncrementalComputableMixIn[MinData]):
    """Statistic identifying the minimum location of a curve."""

    NAME = "Min marker"
    ICON_NAME = "flint:icons/item-stats"

    def name(self) -> str:
        return "Min"

    def isResultValid(self, result):
        return result is not None

    def compute(self, scan: scan_model.Scan) -> MinData | None:
        sourceItem = self.source()
        assert sourceItem is not None

        xx = sourceItem.xArray(scan)
        yy = sourceItem.yArray(scan)
        if xx is None or yy is None:
            return None

        min_index = numpy.argmin(yy)
        max_y_value = numpy.max(yy)
        min_location_x, min_location_y = xx[min_index], yy[min_index]

        result = MinData(
            int(min_index), min_location_y, min_location_x, max_y_value, len(xx)
        )
        return result

    def incrementalCompute(
        self, previousResult: MinData, scan: scan_model.Scan
    ) -> MinData:
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

        min_index = numpy.argmin(yy)
        max_y_value = numpy.max(yy)
        min_location_x, min_location_y = xx[min_index], yy[min_index]
        min_index = min_index + nb

        if previousResult.max_y_value < max_y_value:
            max_y_value = previousResult.max_y_value

        if previousResult.min_location_y < min_location_y:
            # Update and return the previous result
            return MinData(
                previousResult.min_index,
                previousResult.min_location_y,
                previousResult.min_location_x,
                max_y_value,
                nb + len(xx),
            )

        # Update and new return the previous result
        result = MinData(
            int(min_index), min_location_y, min_location_x, max_y_value, nb + len(xx)
        )
        return result
