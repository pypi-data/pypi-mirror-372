# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

"""
Implementation of a derivative filter.
"""
from __future__ import annotations
from typing import NamedTuple

import numpy
import logging

from ..model import scan_model
from ..model import plot_model
from ..model import plot_item_model
from ..model.plot_item_model import ComputedCurveItem
from ..utils import mathutils

_logger = logging.getLogger(__name__)


class DerivativeData(NamedTuple):
    xx: numpy.ndarray
    yy: numpy.ndarray
    nb_points: int


class DerivativeItem(
    ComputedCurveItem,
    plot_model.IncrementalComputableMixIn[DerivativeData],
):
    """This item use the scan data to process result before displaying it."""

    NAME = "Derivative function"
    ICON_NAME = "flint:icons/item-func"

    EXTRA_POINTS = 5
    """Extra points needed before and after a single point to compute a result"""

    def __init__(self, parent=None):
        ComputedCurveItem.__init__(self, parent=parent)
        plot_model.IncrementalComputableMixIn.__init__(self)

    def name(self) -> str:
        return "Derivative"

    def __getstate__(self):
        state: dict[str, object] = {}
        state.update(plot_model.ChildItem.__getstate__(self))
        state.update(plot_item_model.CurveMixIn.__getstate__(self))
        return state

    def __setstate__(self, state):
        plot_model.ChildItem.__setstate__(self, state)
        plot_item_model.CurveMixIn.__setstate__(self, state)

    def compute(self, scan: scan_model.Scan) -> DerivativeData | None:
        sourceItem = self.source()
        assert sourceItem is not None

        xx = sourceItem.xArray(scan)
        yy = sourceItem.yArray(scan)
        if xx is None or yy is None:
            return None

        if len(xx) < self.EXTRA_POINTS * 2 + 1:
            return DerivativeData(numpy.array([]), numpy.array([]), 0)

        try:
            derived = mathutils.derivate(xx, yy)
        except Exception as e:
            _logger.debug("Error while computing derivative", exc_info=True)
            result = DerivativeData(numpy.array([]), numpy.array([]), 0)
            raise plot_model.ComputeError(
                "Error while creating derivative.\n" + str(e), result=result
            )

        return DerivativeData(derived[0], derived[1], len(xx))

    def incrementalCompute(
        self, previousResult: DerivativeData, scan: scan_model.Scan
    ) -> DerivativeData:
        """Compute a data using the previous value as basis

        The derivative function expect 5 extra points before and after the
        points it can compute.

        The last computed point have to be recomputed.

        This code is deeply coupled with the implementation of the derivative
        function.
        """
        sourceItem = self.source()
        assert sourceItem is not None

        xx = sourceItem.xArray(scan)
        yy = sourceItem.yArray(scan)
        if xx is None or yy is None:
            raise ValueError("Non empty data expected")

        nb = previousResult.nb_points
        if nb == len(xx):
            # obviously nothing to compute
            return previousResult
        nextNb = len(xx)

        # The last point have to be recomputed
        LAST = 1

        if len(xx) <= 2 * self.EXTRA_POINTS + LAST:
            return DerivativeData(numpy.array([]), numpy.array([]), nextNb)

        if len(previousResult.xx) == 0:
            # If there is no previous point, there is no need to compute it
            LAST = 0

        xx = xx[nb - 2 * self.EXTRA_POINTS - LAST :]
        yy = yy[nb - 2 * self.EXTRA_POINTS - LAST :]

        derived = mathutils.derivate(xx, yy)

        xx = numpy.append(previousResult.xx[:-1], derived[0])
        yy = numpy.append(previousResult.yy[:-1], derived[1])

        result = DerivativeData(xx, yy, nextNb)
        return result

    def displayName(self, axisName, scan: scan_model.Scan) -> str:
        """Helper to reach the axis display name"""
        sourceItem = self.source()
        assert sourceItem is not None

        if axisName == "x":
            return sourceItem.displayName("x", scan)
        elif axisName == "y":
            return "d(%s)" % sourceItem.displayName("y", scan)
        else:
            assert False
