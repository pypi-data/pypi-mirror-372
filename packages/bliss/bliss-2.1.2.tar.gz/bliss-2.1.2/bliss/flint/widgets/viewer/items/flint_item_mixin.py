# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

from __future__ import annotations

import numpy
from bliss.flint.model import plot_model
from bliss.flint.model import scan_model
from bliss.flint.helper.tooltip_factory import TooltipFactory
from silx.gui.plot.items.image import ColormapMixIn


class FlintItemMixIn:
    def __init__(self):
        self.__plotItem = None
        self.__scan = None

    def customItem(self) -> plot_model.Item | None:
        return self.__plotItem

    def setCustomItem(self, item: plot_model.Item):
        self.__plotItem = item

    def setScan(self, scan):
        self.__scan = scan

    def scan(self):
        return self.__scan

    def feedFlintTooltip(
        self, tooltip: TooltipFactory, index, flintModel, scan: scan_model.Scan
    ) -> tuple[int | None, int | None]:
        return None, None

    def _getColoredChar(self, value, flintModel, color=None):
        if color is not None:
            cssColor = f"#{color[0]:02X}{color[1]:02X}{color[2]:02X}"
        else:
            if isinstance(self, ColormapMixIn):
                colormap = self.getColormap()
                data = numpy.array([float(value)])
                color = colormap.applyToData(data, reference=self)
                cssColor = f"#{color[0,0]:02X}{color[0,1]:02X}{color[0,2]:02X}"
            else:
                cssColor = "#000000"

        if flintModel is not None and flintModel.getDate() == "0214":
            char = "\u2665"
        else:
            char = "■"
        return f"""<font color="{cssColor}">{char}</font>"""

    def _getColoredSymbol(self, flintModel, scan: scan_model.Scan | None):
        """Returns a colored HTML char according to the expected plot item style"""
        if scan is None:
            scan = self.__scan
        plotItem = self.customItem()
        if plotItem is not None:
            style = plotItem.getStyle(scan)
            color = style.lineColor
            cssColor = f"#{color[0]:02X}{color[1]:02X}{color[2]:02X}"
        else:
            cssColor = "#000000"

        if flintModel is not None and flintModel.getDate() == "0214":
            char = "\u2665"
        else:
            char = "⬤"
        return f"""<font color="{cssColor}">{char}</font>"""
