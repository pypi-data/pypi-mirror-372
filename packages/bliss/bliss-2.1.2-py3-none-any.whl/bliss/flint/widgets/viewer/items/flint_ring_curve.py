# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

from __future__ import annotations

from silx.gui.plot.items.curve import Curve
from bliss.flint.model import scan_model
from bliss.flint.helper.tooltip_factory import TooltipFactory


class FlintRingCurve(Curve):
    def __init__(self):
        Curve.__init__(self)
        self.__ring = None

    def setRing(self, ring):
        self.__ring = ring

    def feedFlintTooltip(
        self, tooltip: TooltipFactory, index, flintModel, scan: scan_model.Scan
    ):
        if self.__ring is None:
            return None, None

        if not tooltip.isEmpty():
            tooltip.addSeparator()
        tooltip.addQuantity("nb", self.__ring.nb, pre="Ring")
        tooltip.addQuantity("tth", self.__ring.twoTh)

        return None, None
