# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

"""
Implementation of a mean filter based on a sliding window.
"""
from __future__ import annotations
from typing import NamedTuple

import numpy
from numpy.lib.stride_tricks import sliding_window_view
import logging

from ..model import scan_model
from ..model import plot_model
from ..model import plot_item_model
from ..model.plot_item_model import ComputedCurveItem

_logger = logging.getLogger(__name__)


class SlidingWindowData(NamedTuple):
    xx: numpy.ndarray
    yy: numpy.ndarray
    nb_points: int


class SlidingWindowMeanItem(
    ComputedCurveItem,
    plot_model.IncrementalComputableMixIn[SlidingWindowData],
):
    """This item use the scan data to process result before displaying it."""

    NAME = "Sliding window mean"
    ICON_NAME = "flint:icons/item-func"

    DEFAULT_EXTRA_POINTS = 5
    """Extra points used on each side of the actual position"""

    def __init__(self, parent=None):
        ComputedCurveItem.__init__(self, parent=parent)
        plot_model.IncrementalComputableMixIn.__init__(self)
        self.__extra_points = self.DEFAULT_EXTRA_POINTS

    def name(self) -> str:
        nb = self.__extra_points * 2 + 1
        return f"MeanOnWindow{nb}"

    def setHalfWindowSize(self, nbPoints: int):
        """Set the number of point for the half window.

        - `0` means the mean is computed with a single point.
        - `5` means the mean is computed with 5+1+5 points
        """
        self.__extra_points = nbPoints

    def halfWindowSize(self) -> int:
        return self.__extra_points

    def __getstate__(self):
        state: dict[str, object] = {}
        state.update(plot_model.ChildItem.__getstate__(self))
        state.update(plot_item_model.CurveMixIn.__getstate__(self))
        return state

    def __setstate__(self, state):
        plot_model.ChildItem.__setstate__(self, state)
        plot_item_model.CurveMixIn.__setstate__(self, state)

    def compute(self, scan: scan_model.Scan) -> SlidingWindowData | None:
        sourceItem = self.source()
        assert sourceItem is not None

        xx = sourceItem.xArray(scan)
        yy = sourceItem.yArray(scan)
        if xx is None or yy is None:
            return None

        window_size = self.__extra_points * 2 + 1
        nb_points = min(len(xx), len(yy))
        if nb_points < window_size:
            return None

        xx, yy = xx[:nb_points], yy[:nb_points]

        xwindow = xx[self.__extra_points : -self.__extra_points]
        ywindow = sliding_window_view(yy, window_size)
        ywindow = numpy.mean(ywindow, axis=1)

        return SlidingWindowData(xwindow, ywindow, nb_points)

    def incrementalCompute(
        self, previousResult: SlidingWindowData, scan: scan_model.Scan
    ) -> SlidingWindowData:
        """Compute a data using the previous value as basis.

        The function expect extra points before and after the
        each points it can compute.
        """
        if previousResult is None:
            return self.compute(scan)

        sourceItem = self.source()
        assert sourceItem is not None
        xx = sourceItem.xArray(scan)
        yy = sourceItem.yArray(scan)
        if xx is None or yy is None:
            raise ValueError("Non empty data expected")

        nb_points = min(len(xx), len(yy))
        if nb_points <= previousResult.nb_points:
            # Obviously nothing to compute
            return previousResult

        window_size = self.__extra_points * 2 + 1
        nb_points = min(len(xx), len(yy))
        if nb_points < window_size:
            # There is still not enough data
            return SlidingWindowData(previousResult.xx, previousResult.yy, nb_points)

        # There is necessary something new to compute

        start = len(previousResult.xx) - self.__extra_points
        xx, yy = xx[:nb_points], yy[start:nb_points]

        xwindow = xx[self.__extra_points : -self.__extra_points]
        ywindow = sliding_window_view(yy, window_size)
        ywindow = numpy.mean(ywindow, axis=1)
        ywindow = numpy.append(previousResult.yy, ywindow)

        return SlidingWindowData(xwindow, ywindow, nb_points)

    def displayName(self, axisName, scan: scan_model.Scan) -> str:
        """Helper to reach the axis display name"""
        sourceItem = self.source()
        assert sourceItem is not None
        if axisName == "x":
            return sourceItem.displayName("x", scan)
        elif axisName == "y":
            return "mean(%s)" % sourceItem.displayName("y", scan)
        else:
            assert False
