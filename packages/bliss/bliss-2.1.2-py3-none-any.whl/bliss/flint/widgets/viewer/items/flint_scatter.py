# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

from __future__ import annotations

from silx.gui.plot.items.scatter import Scatter
from bliss.flint.model import scan_model
from bliss.flint.helper.tooltip_factory import TooltipFactory

from .flint_item_mixin import FlintItemMixIn


class FlintScatter(Scatter, FlintItemMixIn):
    def __init__(self):
        Scatter.__init__(self)
        FlintItemMixIn.__init__(self)
        self.__indexes = None

    def setRealIndexes(self, indexes):
        """Specify a scatter following the axis and values, which hold the real
        index from the real data."""
        self.__indexes = indexes

    def feedFlintTooltip(
        self, tooltip: TooltipFactory, index, flintModel, scan: scan_model.Scan
    ):
        # Drop other picked indexes
        x = self.getXData(copy=False)[index]
        y = self.getYData(copy=False)[index]
        value = self.getValueData(copy=False)[index]
        if self.__indexes is not None:
            index = self.__indexes[index]

        plotItem = self.customItem()
        if plotItem is not None:
            assert (
                plotItem.xChannel() is not None
                and plotItem.yChannel() is not None
                and plotItem.valueChannel() is not None
            )
            xName = plotItem.xChannel().displayName(scan)
            yName = plotItem.yChannel().displayName(scan)
            vName = plotItem.valueChannel().displayName(scan)
        else:
            xName = "X"
            yName = "Y"
            vName = "Value"

        char = self._getColoredChar(value, flintModel)

        if not tooltip.isEmpty():
            tooltip.addSeparator()
        tooltip.addQuantity(vName, value, pre=char)
        tooltip.addQuantity(yName, y)
        tooltip.addQuantity(xName, x)
        tooltip.addQuantity("index", index)
        return x, y
