# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

from __future__ import annotations

import logging
from silx.gui import qt
from silx.gui.utils.matplotlib import FigureCanvasQTAgg
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d.art3d import Poly3DCollection


_logger = logging.getLogger(__name__)


class SpectroPlot(qt.QWidget):
    def __init__(self, parent=None):
        super(SpectroPlot, self).__init__(parent=parent)
        self.__data = {}
        self._box_min_max = None

        fig = Figure()
        self._ax = fig.add_subplot(111, projection="3d")
        self._ax.grid(False)
        self._ax.view_init(elev=21.0, azim=-85)
        self._ax.set_box_aspect(aspect=(1, 1, 1))

        self.__plot = FigureCanvasQTAgg(fig)
        self.__plot.setParent(self)

        layout = qt.QVBoxLayout(self)
        layout.addWidget(self.__plot)

    def setGraphTitle(self, title: str):
        self.__plot.setGraphTitle(title)

    def getPlotWidget(self):
        return self.__plot

    def clear(self):
        self.__data = {}
        self._ax.clear()

    def refresh(self):
        self.__safeUpdatePlot()

    def setData(self, **kwargs):
        self.__data = kwargs
        self.__safeUpdatePlot()

    def addData(self, **kwargs):
        for k in kwargs:
            if self.__data.get(k) is None:
                self.__data[k] = kwargs[k]
            else:
                self.__data[k].extend(kwargs[k])

    def setBoxMinMax(self, mini, maxi):
        self._box_min_max = (mini, maxi)
        self._ax.set_xlim([mini[0], maxi[0]])
        self._ax.set_ylim([mini[1], maxi[1]])
        self._ax.set_zlim([mini[2], maxi[2]])

    def __safeUpdatePlot(self):
        try:
            self.__updatePlot()
        except Exception:
            _logger.critical("Error while updating the plot", exc_info=True)

    def __updatePlot(self):

        # === store current magnification and view params
        xlm = self._ax.get_xlim3d()
        ylm = self._ax.get_ylim3d()
        zlm = self._ax.get_zlim3d()
        # axx=self._ax.get_axes()
        # azm=axx.azim
        # ele=axx.elev

        # === clear draw
        self._ax.cla()

        # === restore plot info and view
        self._ax.grid(False)
        self._ax.set_xlabel("X")
        self._ax.set_ylabel("Y")
        self._ax.set_zlabel("Z")

        # self._ax.view_init(elev=ele, azim=azm) #Reproduce view
        self._ax.set_xlim3d(xlm[0], xlm[1])  # Reproduce magnification
        self._ax.set_ylim3d(ylm[0], ylm[1])  # ...
        self._ax.set_zlim3d(zlm[0], zlm[1])  # ...

        # === perform the different kind of plots

        # ax.quiver(x, y, z, u, v, w, length=0.1, normalize=True)
        for args, kwargs in self.__data.get("quivers", []):
            self._ax.quiver(*args, **kwargs)

        # ax.plot(x, y, zs=0, zdir='z', label='curve in (x, y)')
        for args, kwargs in self.__data.get("plots", []):
            self._ax.plot(*args, **kwargs)

        # ax.scatter(xs, ys, zs, marker=m)
        for args, kwargs in self.__data.get("scatters", []):
            self._ax.scatter(*args, **kwargs)

        # ax.plot_trisurf(x, y, z, linewidth=0.2, antialiased=True)
        for args, kwargs in self.__data.get("surfaces", []):
            # self._ax.plot_surface(*args, **kwargs)
            self._ax.plot_trisurf(*args, **kwargs)

        # ax.add_collection3d(Poly3DCollection([verts], alpha=0.5, facecolor='orange'))
        for args, kwargs in self.__data.get("polygons", []):
            self._ax.add_collection3d(Poly3DCollection(*args, **kwargs))

        # === render
        self.__plot.draw()
