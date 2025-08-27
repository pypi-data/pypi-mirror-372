# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

from __future__ import annotations

from silx.gui.plot.items.curve import Curve
from bliss.flint.model import plot_item_model
from bliss.flint.filters.gaussian_fit import GaussianFitItem
from bliss.flint.model import scan_model
from bliss.flint.helper.tooltip_factory import TooltipFactory
from .flint_item_mixin import FlintItemMixIn


class FlintCurve(Curve, FlintItemMixIn):
    def __init__(self):
        Curve.__init__(self)
        FlintItemMixIn.__init__(self)

    def feedFlintTooltip(
        self, tooltip: TooltipFactory, index, flintModel, scan: scan_model.Scan
    ):
        xx = self.getXData(copy=False)
        yy = self.getYData(copy=False)
        xValue = xx[index]
        yValue = yy[index]

        plotItem = self.customItem()
        if isinstance(plotItem, plot_item_model.CurveMixIn):
            xName = plotItem.displayName("x", scan)
            yName = plotItem.displayName("y", scan)
        else:
            plotItem = None
            xName = "X"
            yName = "Y"

        char = self._getColoredSymbol(flintModel, None)

        if not tooltip.isEmpty():
            tooltip.addSeparator()
        tooltip.addQuantity(yName, yValue, pre=char)
        tooltip.addQuantity(xName, xValue)
        tooltip.addQuantity("index", index)

        if isinstance(plotItem, GaussianFitItem):
            result = plotItem.reachResult(scan)
            if result is not None:
                tooltip.addQuantity("FWHM", result.fit.fwhm)
                tooltip.addQuantity("std dev (σ)", result.fit.std)
                tooltip.addQuantity("position (μ)", result.fit.pos_x)

        return xValue, yValue
