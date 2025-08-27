# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

"""
Implementation of a negative filter
"""
from __future__ import annotations
from typing import NamedTuple

import numpy
import logging

from ..model import scan_model
from ..model import plot_model
from ..model import plot_item_model
from ..model.plot_item_model import ComputedCurveItem

_logger = logging.getLogger(__name__)


class NegativeData(NamedTuple):
    xx: numpy.ndarray
    yy: numpy.ndarray
    nb_points: int


class NegativeItem(
    ComputedCurveItem, plot_model.IncrementalComputableMixIn[NegativeData]
):
    """This item use a curve item to negative it."""

    NAME = "Negative function"
    ICON_NAME = "flint:icons/item-func"

    def __init__(self, parent=None):
        ComputedCurveItem.__init__(self, parent=parent)
        plot_model.IncrementalComputableMixIn.__init__(self)

    def name(self) -> str:
        return "Negative"

    def __getstate__(self):
        state: dict[str, object] = {}
        state.update(plot_model.ChildItem.__getstate__(self))
        state.update(plot_item_model.CurveMixIn.__getstate__(self))
        return state

    def __setstate__(self, state):
        plot_model.ChildItem.__setstate__(self, state)
        plot_item_model.CurveMixIn.__setstate__(self, state)

    def compute(self, scan: scan_model.Scan) -> NegativeData | None:
        sourceItem = self.source()
        assert sourceItem is not None

        xx = sourceItem.xArray(scan)
        yy = sourceItem.yArray(scan)
        if xx is None or yy is None:
            return None

        size = min(len(xx), len(yy))
        return NegativeData(xx[0:size], -yy[0:size], size)

    def incrementalCompute(
        self, previousResult: NegativeData, scan: scan_model.Scan
    ) -> NegativeData:
        """Compute a data using the previous value as basis"""
        sourceItem = self.source()
        assert sourceItem is not None

        xx = sourceItem.xArray(scan)
        yy = sourceItem.yArray(scan)
        if xx is None or yy is None:
            raise ValueError("Non empty data expected")

        nb = previousResult.nb_points
        if nb == len(xx) or nb == len(yy):
            # obviously nothing to compute
            return previousResult

        xx = xx[nb:]
        yy = yy[nb:]

        nbInc = min(len(xx), len(yy))

        xx = numpy.append(previousResult.xx, xx[: nbInc + 1])
        yy = numpy.append(previousResult.yy, -yy[: nbInc + 1])

        result = NegativeData(xx, yy, nb + nbInc)
        return result

    def displayName(self, axisName, scan: scan_model.Scan) -> str:
        """Helper to reach the axis display name"""
        sourceItem = self.source()
        assert sourceItem is not None

        if axisName == "x":
            return sourceItem.displayName("x", scan)
        elif axisName == "y":
            return "neg(%s)" % sourceItem.displayName("y", scan)
        else:
            assert False
