# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

from __future__ import annotations

import numpy
import logging

from silx.gui import plot as silx_plot
from silx.gui.plot import items
from silx.gui.colors import Colormap
from bliss.flint.widgets.viewer.data_widget import DataWidget
from bliss.flint.widgets.viewer.items.image_with_normalization import (
    ImageWithNormalization,
)


_logger = logging.getLogger(__name__)


class Plot2D(DataWidget):
    """Generic plot to display 2D data"""

    # Name of the method to add data to the plot
    METHOD = "addImage"

    def __init__(self, parent=None):
        DataWidget.__init__(self, parent=parent)
        self.__items = {}

    def _createSilxWidget(self, parent):
        widget = silx_plot.Plot2D(parent=parent)
        widget.setDataMargins(0.05, 0.05, 0.05, 0.05)
        return widget

    def clear(self):
        super(Plot2D, self).clear()
        self.__items.clear()

    def clearItems(self):
        """Remove the item definitions"""
        self.__items.clear()
        widget = self.silxWidget()
        widget.clear()

    def removeItem(self, legend: str):
        """Remove a specific item by name"""
        previous = self.__items.pop(legend, None)
        widget = self.silxWidget()
        if isinstance(previous, items.Item):
            widget.removeItem(previous)

    def itemExists(self, legend: str):
        """True if a specific item exists."""
        return legend in self.__items

    def resetZoom(self):
        widget = self.silxPlot()
        widget.resetZoom()

    def getYaxisDirection(self) -> str:
        """Returns the direction of the y-axis.

        Returns:
            One of "up", "down"
        """
        inverted = self.silxWidget().getYAxis().isInverted()
        return "down" if inverted else "up"

    def setYaxisDirection(self, direction: str):
        """Specify the direction of the y-axis.

        By default the direction is up, which mean the 0 is on bottom, and
        positive values are above.

        Argument:
            direction: One of "up", "down"
        """
        assert direction in ("up", "down")
        inverted = direction == "down"
        self.silxWidget().getYAxis().setInverted(inverted)

    def setDisplayedIntensityHistogram(self, show):
        self.getIntensityHistogramAction().setVisible(show)

    def _getColormap(self, colormap: str | dict | None) -> Colormap | None:
        if colormap is None:
            return None
        if isinstance(colormap, str):
            c = self.__items.get(colormap)
            if c is None:
                raise ValueError(f"Colormap '{colormap}' does not exist")
            if not isinstance(c, Colormap):
                raise ValueError(f"Item '{colormap}' is not a colormap")
            return c

        return Colormap._fromDict(colormap)

    def _addItem(self, legend: str, item: items.Item, resetzoom=True):
        previous = self.__items.pop(legend, None)
        widget = self.silxWidget()
        if previous is not None:
            widget.removeItem(previous)
        item.setName(legend)
        widget.addItem(item)
        self.__items[legend] = item
        if resetzoom:
            widget.resetZoom()

    def addColormap(
        self,
        name: str,
        lut: str | None = None,
        vmin: float | str | None = None,
        vmax: float | str | None = None,
        normalization: str | None = None,
        gammaNormalization: float | None = None,
        autoscale: bool | None = None,
        autoscaleMode: str | None = None,
    ):
        """
        Add a named colormap
        """
        colormap = self.__items.get(name, None)
        if colormap is not None:
            if not isinstance(colormap, Colormap):
                raise TypeError(f"Name '{name}' already exists and is not a colormap")
        else:
            colormap = Colormap()
            self.__items[name] = colormap

        if lut is not None:
            colormap.setName(lut)
        if vmin is not None:
            if vmin == "auto":
                vmin = None
            colormap.setVMin(vmin)
        if vmax is not None:
            if vmax == "auto":
                vmax = None
            colormap.setVMax(vmax)
        if normalization is not None:
            colormap.setNormalization(normalization)
        if gammaNormalization is not None:
            colormap.setGammaNormalizationParameter(gammaNormalization)
            colormap.setNormalization("gamma")
        if autoscale is not None:
            if autoscale:
                colormap.setVRange(None, None)
        if autoscaleMode is not None:
            colormap.setAutoscaleMode(autoscaleMode)

    def addImage(
        self,
        image: numpy.ndarray,
        origin: tuple[float, float] | None = None,
        scale: tuple[float, float] | None = None,
        colormap: str | dict | None = None,
        legend: str = "image",
        resetzoom: bool = True,
    ):
        image = numpy.asarray(image)
        if image.ndim == 3:
            item = items.ImageRgba()
        else:
            item = items.ImageData()
            colormap = self._getColormap(colormap)
            if colormap is not None:
                item.setColormap(colormap)
        if origin is not None:
            item.setOrigin(origin)
        if scale is not None:
            item.setScale(scale)
        item.setData(image, copy=False)
        self._addItem(legend, item, resetzoom=resetzoom)

    def addScatter(
        self,
        x: numpy.ndarray,
        y: numpy.ndarray,
        value: numpy.ndarray,
        colormap=None,
        legend="scatter",
        resetzoom=True,
    ):
        item = items.Scatter()
        item.setData(x, y, value, copy=False)
        colormap = self._getColormap(colormap)
        if colormap is not None:
            item.setColormap(colormap)
        self._addItem(legend, item, resetzoom=resetzoom)

    def addImageWithNormalization(
        self,
        image: numpy.ndarray,
        xAxis: numpy.ndarray,
        yAxis: numpy.ndarray,
        legend="image",
        colormap=None,
        resetzoom=True,
    ):
        item = ImageWithNormalization()
        item.setData(image, xAxis=xAxis, yAxis=yAxis, copy=False)
        colormap = self._getColormap(colormap)
        if colormap is not None:
            item.setColormap(colormap)
        self._addItem(legend, item, resetzoom=resetzoom)
