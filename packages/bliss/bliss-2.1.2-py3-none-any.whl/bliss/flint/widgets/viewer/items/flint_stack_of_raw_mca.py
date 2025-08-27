# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

from __future__ import annotations

from silx.gui.plot.items.image import ImageData

from bliss.flint.model import plot_model
from bliss.flint.model import scan_model

# FIXME: THis have to be refactored to avoid import in this direction
from bliss.flint.viewers.live_image.stages.info import ImageLayer
from bliss.flint.helper.tooltip_factory import TooltipFactory
from .flint_image_mixin import FlintImageMixIn


class FlintStackOfRawMca(ImageData, FlintImageMixIn):
    def __init__(self):
        ImageData.__init__(self)
        FlintImageMixIn.__init__(self)
        self.__mapping: list[tuple[plot_model.Item, int, bool]] = []
        self.setOrigin((-0.5, -0.5))

    def setCustomItemMapping(self, mapping: list[tuple[plot_model.Item, int, bool]]):
        self.__mapping = mapping

    def _getItemIndexFromY(self, y):
        p = 0
        for (item, size, isStack) in self.__mapping:
            if y < p + size:
                return item, y - p if isStack else None
            p += size
        return None, None, None

    def feedFlintTooltip(
        self, tooltip: TooltipFactory, index, flintModel, scan: scan_model.Scan
    ):
        if ImageLayer.MASK in self.getTags():
            return None, None
        if ImageLayer.SATURATION in self.getTags():
            return None, None
        y, x = index
        image = self.getData(copy=False)
        value = image[index]
        char = self._getColoredChar(value, flintModel)
        item, iDet = self._getItemIndexFromY(y)
        name = item.mcaChannel().name()
        slicing = f"[{iDet}]" if iDet is not None else ""

        if not tooltip.isEmpty():
            tooltip.addSeparator()
        tooltip.addQuantity("Value", value, pre=char)
        tooltip.addQuantity("Channel", x)
        tooltip.addQuantity("Name", f"{name}{slicing}")

        self.feedRawTooltip(tooltip, index)
        return x, y
