# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

from __future__ import annotations
from typing import NamedTuple

import numpy
import logging

from bliss.flint.widgets.viewer.data_widget import DataWidget


_logger = logging.getLogger(__name__)


class Plot3D(DataWidget):
    """Dedicated plot to display a 3D scatter"""

    # Name of the method to add data to the plot
    METHOD = "setData"

    class ScatterItem(NamedTuple):
        xdata: str
        ydata: str
        zdata: str
        vdata: str

        @property
        def channelNames(self):
            return {self.xdata, self.ydata, self.zdata, self.vdata}

    class MeshItem(NamedTuple):
        vertices: str
        faces: str
        color: numpy.ndarray

        @property
        def channelNames(self):
            return {self.vertices, self.faces}

    def __init__(self, parent=None):
        DataWidget.__init__(self, parent=parent)
        self.__items = {}
        self.__plotItems = {}
        self.__autoUpdatePlot = True
        self.__raiseOnException = False
        self.__firstRendering = True

    def setAutoUpdatePlot(self, update="bool"):
        """Set to true to enable or disable update of plot for each changes of
        the data or items"""
        self.__autoUpdatePlot = update

    def addScatterItem(
        self,
        xdata: str,
        ydata: str,
        zdata: str,
        vdata: str,
        legend: str | None = None,
        symbol: str = ",",
        symbolSize: float | None = None,
        lut=None,
        vmin=None,
        vmax=None,
    ):
        """Define an item which have to be displayed with the specified data
        name
        """
        if legend is None:
            legend = f"{xdata},{ydata},{zdata} -> {vdata}"
        self.__items[legend] = self.ScatterItem(xdata, ydata, zdata, vdata)

        widget = self.silxPlot()
        sceneWidget = widget.getSceneWidget()
        if legend in self.__plotItems:
            i = self.__plotItems[legend]
            sceneWidget.removeItem(i)

        from silx.gui.plot3d import items

        item = items.Scatter3D()
        item.setSymbol(symbol)
        item.setSymbolSize(symbolSize)
        colormap = item.getColormap()
        if lut is not None:
            colormap.setName(lut)
        if vmin is not None:
            colormap.setVMin(vmin)
        if vmax is not None:
            colormap.setVMax(vmax)
        sceneWidget.addItem(item)
        self.__plotItems[legend] = item
        self.__updatePlotIfNeeded()

    def addMeshItem(
        self,
        vertices: str,
        faces: str,
        legend: str | None = None,
        color=None,
    ):
        """Define an item which have to be displayed with the specified data
        name
        """
        if legend is None:
            legend = f"{vertices} x {faces}"
        self.__items[legend] = self.MeshItem(vertices, faces, color)

        widget = self.silxPlot()
        sceneWidget = widget.getSceneWidget()
        if legend in self.__plotItems:
            i = self.__plotItems[legend]
            sceneWidget.removeItem(i)

        from silx.gui.plot3d import items

        item = items.Mesh()
        sceneWidget.addItem(item)
        self.__plotItems[legend] = item
        self.__updatePlotIfNeeded()

    def clearItems(self):
        for name in self.__plotItems.keys():
            self.removeItem(name)

    def removeItem(self, legend: str):
        """Remove a specific item by name"""
        i = self.__plotItems.pop(legend)
        widget = self.silxPlot()
        sceneWidget = widget.getSceneWidget()
        sceneWidget.removeItem(i)

    def _createSilxWidget(self, parent):
        from silx.gui.plot3d.SceneWindow import SceneWindow

        widget = SceneWindow(parent=parent)
        return widget

    def getDataRange(self):
        widget = self.silxPlot()
        sceneWidget = widget.getSceneWidget()
        bounds = sceneWidget.viewport.scene.bounds(transformed=True)
        return bounds

    def clear(self):
        super(Plot3D, self).clear()
        self.__updatePlot()

    def setData(self, **kwargs):
        dataDict = self.dataDict()
        for k, v in kwargs.items():
            dataDict[k] = v
        self.__updatePlotIfNeeded(updatedChannels=kwargs.keys())

    def resetZoom(self):
        widget = self.silxPlot()
        sceneWidget = widget.getSceneWidget()
        sceneWidget.resetZoom()

    def __updatePlotIfNeeded(self, updatedChannels=None):
        if self.__autoUpdatePlot:
            self.updatePlot(resetzoom=False, updatedChannels=updatedChannels)

    def updatePlot(self, resetzoom: bool = True, updatedChannels=None):
        try:
            self.__updatePlot(updatedChannels=updatedChannels)
        except Exception:
            _logger.error("Error while updating the plot", exc_info=True)
            if self.__raiseOnException:
                raise
        if resetzoom or self.__firstRendering:
            self.__firstRendering = False
            self.resetZoom()

    def __iterItemsUsingChannels(self, channelNames):
        channelNames = set(channelNames)
        for legend, item in self.__items.items():
            if len(item.channelNames.intersection(channelNames)) != 0:
                yield legend, item

    def __getClampedData(self, *args):
        dataDict = self.dataDict()
        data = [dataDict.get(n) for n in args]
        if True in [d is None for d in data]:
            return [None] * len(args)
        smallest = min([len(d) for d in data])
        data = [d[0:smallest] for d in data]
        return data

    def __getData(self, *args):
        dataDict = self.dataDict()
        data = [dataDict.get(n) for n in args]
        if True in [d is None for d in data]:
            return [None] * len(args)
        return data

    def __updatePlot(self, updatedChannels=None):
        if updatedChannels is None:
            updatedItems = self.__items.items()
        else:
            updatedItems = self.__iterItemsUsingChannels(updatedChannels)

        for legend, item in updatedItems:
            try:
                if isinstance(item, self.ScatterItem):
                    xData, yData, zData, vData = self.__getClampedData(
                        item.xdata, item.ydata, item.zdata, item.vdata
                    )
                    if xData is None:
                        continue
                    pitem = self.__plotItems[legend]
                    pitem.setData(xData, yData, zData, vData, copy=False)
                elif isinstance(item, self.MeshItem):
                    vertices, faces = self.__getData(item.vertices, item.faces)
                    if vertices is None:
                        continue
                    pitem = self.__plotItems[legend]
                    faces = numpy.array(faces)
                    if faces.dtype.kind != "u":
                        faces = numpy.array(faces, dtype=numpy.uint32)
                    pitem.setData(position=vertices, indices=faces, color=item.color)
            except Exception:
                _logger.error("Error while updating the item %s", legend, exc_info=True)
