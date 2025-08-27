# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

from __future__ import annotations

from silx.gui.plot.items.image import ImageData
from bliss.flint.model import scan_model

# FIXME: THis have to be refactored to avoid import in this direction
from bliss.flint.viewers.live_image.stages.info import ImageLayer
from bliss.flint.helper.tooltip_factory import TooltipFactory
from .flint_image_mixin import FlintImageMixIn


class FlintImage(ImageData, FlintImageMixIn):
    def __init__(self):
        ImageData.__init__(self)
        FlintImageMixIn.__init__(self)

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
        unit = self.getUnit()

        xName = "Col/X"
        yName = "Row/Y"

        if not tooltip.isEmpty():
            tooltip.addSeparator()
        tooltip.addQuantity("Value", value, unit, pre=char)
        tooltip.addQuantity(xName, x)
        tooltip.addQuantity(yName, y)

        self.feedFlintCorrectionTooltip(tooltip)
        self.feedRawTooltip(tooltip, index)
        return x + 0.5, y + 0.5
