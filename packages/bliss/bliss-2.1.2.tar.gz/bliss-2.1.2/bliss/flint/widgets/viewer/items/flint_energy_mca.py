# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

from __future__ import annotations

from numpy.polynomial.polynomial import polyval
from silx.gui.plot.items.curve import Curve
from bliss.flint.model import scan_model
from bliss.flint.helper.tooltip_factory import TooltipFactory
from .flint_item_mixin import FlintItemMixIn


class FlintEnergyMca(Curve, FlintItemMixIn):
    def __init__(self):
        Curve.__init__(self)
        FlintItemMixIn.__init__(self)
        self.__userCalibration = None
        self.__index = None

    def setCalibration(self, userCalibration):
        self.__userCalibration = userCalibration

    def energyFromIndex(self, index):
        if self.__userCalibration is None:
            return None
        return polyval(index, self.__userCalibration)

    def setItemArrayIndex(self, index: int | None):
        """Specify an index related to the array in the item"""
        self.__index = index

    def feedFlintTooltip(
        self, tooltip: TooltipFactory, index, flintModel, scan: scan_model.Scan
    ):
        value = self.getYData(copy=False)[index]
        plotItem = self.customItem()
        if plotItem is not None:
            assert plotItem.mcaChannel() is not None
            mcaName = plotItem.mcaChannel().displayName(scan)
        else:
            plotItem = None
            mcaName = "MCA"

        char = self._getColoredSymbol(flintModel, scan)
        energy = self.energyFromIndex(index)

        if not tooltip.isEmpty():
            tooltip.addSeparator()
        tooltip.addQuantity(mcaName, value, pre=char)
        tooltip.addQuantity("index", index)
        if energy is not None:
            tooltip.addQuantity(mcaName, energy, "keV", pre=char)
        return index, value
