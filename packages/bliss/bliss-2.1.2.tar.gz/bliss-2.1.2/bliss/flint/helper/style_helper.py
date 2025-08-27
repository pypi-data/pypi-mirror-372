# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

"""
Helper functions to deal with style
"""

from __future__ import annotations

import logging
from bliss.flint.model import scan_model
from bliss.flint.model import flint_model
from bliss.flint.model import plot_model
from bliss.flint.model import plot_item_model
from bliss.flint.model import style_model
from bliss.flint.helper import palettes


_logger = logging.getLogger(__name__)


class _IndexedColor(style_model.IndexedColor):
    def __init__(self, index, colorPicker: _ColorPicker):
        style_model.IndexedColor.__init__(self)
        self.__index = index
        self.__picker = colorPicker
        self.__color = None

    def color(self):
        if self.__color is None:
            maxColor = self.__picker.allocatedColors()
            if maxColor <= 6:
                palette = palettes.NORMAL_PALETTE_6
            else:
                palette = palettes.NORMAL_PALETTE_12
            self.__color = palette[self.__index % len(palette)]
        return self.__color


class _ColorPicker:
    def __init__(self):
        self.__allocated = 0

    def allocatedColors(self):
        return self.__allocated

    def pickColor(self):
        c = _IndexedColor(self.__allocated, self)
        self.__allocated += 1
        return c


class DefaultStyleStrategy(plot_model.StyleStrategy):
    def __init__(self, flintModel: flint_model.FlintState | None = None):
        super(DefaultStyleStrategy, self).__init__()
        self.__flintModel = flintModel
        self.__cached: dict[
            tuple[plot_model.Item, scan_model.Scan | None], plot_model.Style
        ] = {}
        self.__cacheInvalidated = True
        self.__scans: list = []

    def setFlintModel(self, flintModel: flint_model.FlintState):
        self.__flintModel = flintModel

    def setScans(self, scans):
        self.__scans.clear()
        self.__scans.extend(scans)
        self.invalidateStyles()

    def __getstate__(self):
        return {}

    def __setstate__(self, state):
        assert isinstance(state, dict)

    _SYMBOL_SIZE = 6.0

    _COLORMAP = "viridis"

    _COLORMAPS = ["red", "green", "blue", "gray"]

    def pickColor(self, index):
        palette = palettes.NORMAL_PALETTE_12
        return palette[index % len(palette)]

    def invalidateStyles(self):
        self.__cached = {}
        self.__cacheInvalidated = True

    def cacheStyle(
        self,
        item: plot_model.Item,
        scan: scan_model.Scan | None,
        style: plot_model.Style,
    ):
        self.__cached[item, scan] = style

    def computeItemStyleFromScatterPlot(self, plot):
        scatters = []
        for item in plot.items():
            if isinstance(item, plot_item_model.ScatterItem):
                scatters.append(item)

        if len(scatters) == 1:
            scatter = scatters[0]
            style = scatter.customStyle()
            if style is None:
                flintModel = self.__flintModel
                assert flintModel is not None
                style = flintModel.defaultScatterStyle()
            self.cacheStyle(scatter, None, style)
        else:
            baseSize = self._SYMBOL_SIZE / 3
            for i, scatter in enumerate(scatters):
                size = ((len(scatters) - 1 - i) * 2 + 2) * baseSize
                lut = self._COLORMAPS[i % len(self._COLORMAPS)]
                style = plot_model.Style(
                    symbolStyle="o", symbolSize=size, colormapLut=lut
                )
                self.cacheStyle(scatter, None, style)

    def computeItemStyleFromImagePlot(self, plot):
        images = []
        for item in plot.items():
            if isinstance(item, plot_item_model.ImageItem):
                images.append(item)

        if len(images) >= 1:
            image = images.pop(0)
            style = image.customStyle()
            if style is None:
                flintModel = self.__flintModel
                assert flintModel is not None
                style = flintModel.defaultImageStyle()
            self.cacheStyle(image, None, style)

        if len(images) == 1:
            baseSize = self._SYMBOL_SIZE
        else:
            baseSize = self._SYMBOL_SIZE / 2

        for i, scatter in enumerate(images):
            size = ((len(images) - 1 - i) * 2 + 1) * baseSize
            lut = self._COLORMAPS[i % len(self._COLORMAPS)]
            style = plot_model.Style(symbolStyle="o", symbolSize=size, colormapLut=lut)
            self.cacheStyle(scatter, None, style)

    def computeItemStyleFromCurvePlot(self, plot, scans):
        countBase = 0

        xChannel = None
        for item in plot.items():
            if xChannel is None:
                if isinstance(item, plot_item_model.CurveItem):
                    xChannel = item.xChannel()
            if isinstance(item, plot_item_model.ScanItem):
                pass
            elif isinstance(item, plot_model.ComputableMixIn):
                pass
            else:
                # That's a main item
                countBase += 1

        if len(scans) <= 1:
            if countBase <= 1:
                self.computeItemStyleFromCurvePlot_eachItemsColored(plot, scans)
            else:
                self.computeItemStyleFromCurvePlot_firstScanColored(plot, scans)
        else:
            if xChannel is not None and xChannel.name().endswith(":epoch"):
                self.computeItemStyleFromCurvePlot_eachItemsColored(plot, scans)
            elif countBase > 1:
                self.computeItemStyleFromCurvePlot_firstScanColored(plot, scans)
            else:
                self.computeItemStyleFromCurvePlot_eachScanColored(plot, scans)

    def computeItemStyleFromCurvePlot_eachItemsColored(self, plot, scans):
        """Setup the same style for each item of the plot anyway the scan"""
        colorPicker = _ColorPicker()
        for item in plot.items():
            if isinstance(item, plot_item_model.ScanItem):
                continue
            if isinstance(item, plot_model.ComputableMixIn):
                # Allocate a new color for everything
                color = colorPicker.pickColor()
                if isinstance(item, plot_item_model.CurveStatisticItem):
                    style = plot_model.Style(lineStyle=":", lineColor=color)
                else:
                    style = plot_model.Style(lineStyle="-.", lineColor=color)
            else:
                color = colorPicker.pickColor()
                style = plot_model.Style(lineStyle="-", lineColor=color)
            for scan in scans:
                self.cacheStyle(item, scan, style)

    def computeItemStyleFromCurvePlot_firstScanColored(self, plot, scans):
        colorPicker = _ColorPicker()
        for scanId, scan in enumerate(scans):
            for item in plot.items():
                if isinstance(item, plot_item_model.ScanItem):
                    continue
                if isinstance(item, plot_model.ComputableMixIn):
                    # Reuse the parent color
                    source = item.source()
                    baseStyle = self.getStyleFromItem(source, scan)
                    color = baseStyle.lineColor
                    if isinstance(item, plot_item_model.CurveStatisticItem):
                        style = plot_model.Style(lineStyle=":", lineColor=color)
                    else:
                        style = plot_model.Style(lineStyle="-.", lineColor=color)
                else:
                    if scanId == 0:
                        color = colorPicker.pickColor()
                    else:
                        # Grayed
                        color = (0x80, 0x80, 0x80)
                    style = plot_model.Style(lineStyle="-", lineColor=color)
                self.cacheStyle(item, scan, style)

    def computeItemStyleFromCurvePlot_eachScanColored(self, plot, scans):
        for scan in scans:
            scanId = scan.scanId()
            if scanId is None:
                scanId = hash(scan)
            for item in plot.items():
                if isinstance(item, plot_item_model.ScanItem):
                    continue
                if isinstance(item, plot_model.ComputableMixIn):
                    # Reuse the parent color
                    source = item.source()
                    baseStyle = self.getStyleFromItem(source, scan)
                    color = baseStyle.lineColor
                    if isinstance(item, plot_item_model.CurveStatisticItem):
                        style = plot_model.Style(lineStyle=":", lineColor=color)
                    else:
                        style = plot_model.Style(lineStyle="-.", lineColor=color)
                else:
                    color = self.pickColor(scanId)
                    style = plot_model.Style(lineStyle="-", lineColor=color)
                self.cacheStyle(item, scan, style)

    def computeItemStyleFromPlot(self):
        self.__cached = {}
        plot = self.plot()
        if isinstance(plot, plot_item_model.ScatterPlot):
            self.computeItemStyleFromScatterPlot(plot)
        elif isinstance(plot, plot_item_model.ImagePlot):
            self.computeItemStyleFromImagePlot(plot)
        else:
            scans: list[scan_model.Scan | None] = []
            if len(self.__scans) > 0:
                scans = self.__scans
            else:
                assert plot is not None
                for item in plot.items():
                    if isinstance(item, plot_item_model.ScanItem):
                        scans.append(item.scan())
                if scans == []:
                    scans.append(None)

            self.computeItemStyleFromCurvePlot(plot, scans)

    def getStyleFromItem(
        self, item: plot_model.Item, scan: scan_model.Scan | None = None
    ) -> plot_model.Style:
        if self.__cacheInvalidated:
            self.__cacheInvalidated = False
            self.computeItemStyleFromPlot()
        return self.__cached[item, scan]
