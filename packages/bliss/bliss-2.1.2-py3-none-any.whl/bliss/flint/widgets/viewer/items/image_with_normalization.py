# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

import numpy
from silx.gui.plot.items.scatter import Scatter


class ImageWithNormalization(Scatter):
    """
    Image item with normalized axis implemented with a `Scatter`.
    """

    def __init__(self):
        Scatter.__init__(self)
        self.setVisualization(self.Visualization.IRREGULAR_GRID)

    def setData(self, image, xAxis, yAxis, copy=True):
        x = numpy.asarray(xAxis)
        y = numpy.asarray(yAxis)
        value = numpy.asarray(image)
        assert x.ndim == 1
        assert y.ndim == 1
        assert value.ndim == 2
        assert (y.shape[0], x.shape[0]) == value.shape

        ax = numpy.broadcast_to(x, value.shape)
        ay = numpy.broadcast_to(y.reshape(-1, 1), value.shape)
        Scatter.setData(self, ax.flatten(), ay.flatten(), value.flatten(), copy=copy)

        self.setVisualizationParameter(
            self.VisualizationParameter.GRID_SHAPE,
            image.shape,
        )
        self.setVisualizationParameter(
            self.VisualizationParameter.GRID_BOUNDS,
            ((x[0], y[0]), (x[-1], y[-1])),
        )
        self.setVisualizationParameter(
            self.VisualizationParameter.GRID_MAJOR_ORDER, "row"
        )
