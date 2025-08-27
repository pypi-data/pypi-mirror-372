# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

from __future__ import annotations

import numpy
import logging

from bliss.flint.widgets.viewer.data_widget import DataWidget


_logger = logging.getLogger(__name__)


class ScatterView3D(DataWidget):
    """Dedicated plot to display a 3D scatter"""

    # Name of the method to add data to the plot
    METHOD = "setData"

    def _createSilxWidget(self, parent):
        from silx.gui.plot3d.SceneWindow import SceneWindow
        from silx.gui.plot3d import items

        widget = SceneWindow(parent=parent)
        sceneWidget = widget.getSceneWidget()
        item = items.Scatter3D()
        item.setSymbol(",")
        sceneWidget.addItem(item)

        # FIXME: that's small hack to store the item
        widget._item = item
        widget._first_render = True
        return widget

    def silxItem(self):
        widget = self.silxPlot()
        return widget._item

    def getDataRange(self):
        widget = self.silxPlot()
        sceneWidget = widget.getSceneWidget()
        bounds = sceneWidget.viewport.scene.bounds(transformed=True)
        return bounds

    def clear(self):
        item = self.silxItem()
        item.setData([numpy.nan], [numpy.nan], [numpy.nan], [numpy.nan])

    def setMarker(self, symbol):
        item = self.silxItem()
        item.setSymbol(symbol)

    def getColormap(self):
        item = self.silxItem()
        return item.getColormap()

    def setData(self, x, y, z, value):
        item = self.silxItem()
        item.setData(x, y, z, value, copy=False)
        widget = self.silxPlot()
        if widget._first_render:
            widget._first_render = False
            widget.getSceneWidget().resetZoom()
