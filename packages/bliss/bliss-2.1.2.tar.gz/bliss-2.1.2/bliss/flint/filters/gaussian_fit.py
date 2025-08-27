# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

"""
Implementation of a gaussian fit filter.
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


class GaussianFitData(NamedTuple):
    xx: numpy.ndarray
    yy: numpy.ndarray
    fit: mathutils.GaussianFitResult | None


class GaussianFitItem(ComputedCurveItem, plot_model.ComputableMixIn[GaussianFitData]):
    """This item use the scan data to process result before displaying it."""

    NAME = "Gaussian fit"
    ICON_NAME = "flint:icons/item-func"

    def __getstate__(self):
        state: dict[str, object] = {}
        state.update(plot_model.ChildItem.__getstate__(self))
        state.update(plot_item_model.CurveMixIn.__getstate__(self))
        return state

    def __setstate__(self, state):
        plot_model.ChildItem.__setstate__(self, state)
        plot_item_model.CurveMixIn.__setstate__(self, state)

    def compute(self, scan: scan_model.Scan) -> GaussianFitData | None:
        sourceItem = self.source()
        assert sourceItem is not None

        xx = sourceItem.xArray(scan)
        yy = sourceItem.yArray(scan)
        if xx is None or yy is None:
            return None

        if len(xx) < 4:
            return GaussianFitData(numpy.array([]), numpy.array([]), None)

        try:
            fit = mathutils.fit_gaussian(xx, yy)
        except Exception as e:
            _logger.debug("Error while computing gaussian fit", exc_info=True)
            result = GaussianFitData(numpy.array([]), numpy.array([]), None)
            raise plot_model.ComputeError(
                "Error while creating gaussian fit.\n" + str(e), result=result
            )

        yy = fit.transform(xx)
        return GaussianFitData(xx, yy, fit)

    def name(self) -> str:
        return "Gaussian"

    def displayName(self, axisName, scan: scan_model.Scan) -> str:
        """Helper to reach the axis display name"""
        sourceItem = self.source()
        assert sourceItem is not None

        if axisName == "x":
            return sourceItem.displayName("x", scan)
        elif axisName == "y":
            return "gaussian(%s)" % sourceItem.displayName("y", scan)
        else:
            assert False
