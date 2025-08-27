# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.
"""
Provides plot helper class to deal with flint proxy.
"""

from bliss.flint.viewers.live_image.client import LiveImagePlot
from bliss.flint.viewers.live_scatter.client import LiveScatterPlot
from bliss.flint.viewers.live_curve.client import LiveCurvePlot
from bliss.flint.viewers.live_mca.client import LiveMcaPlot
from bliss.flint.viewers.live_onedim.client import LiveOneDimPlot

from bliss.flint.viewers.custom_time_curve.client import TimeCurvePlot
from bliss.flint.viewers.custom_spectro.client import SpectroPlot

from bliss.flint.viewers.custom_curve_stack.client import CurveStack
from bliss.flint.viewers.custom_image_stack.client import StackView
from bliss.flint.viewers.custom_image.client import ImageView
from bliss.flint.viewers.custom_scatter.client import ScatterView
from bliss.flint.viewers.custom_scatter3d.client import ScatterView3D

from bliss.flint.viewers.custom_plot1d.client import Plot1D
from bliss.flint.viewers.custom_plot2d.client import Plot2D
from bliss.flint.viewers.custom_plot3d.client import Plot3D

from bliss.flint.viewers.custom_grid_container.client import GridContainer

# Used by external code to create custom plots
from bliss.flint.client.base_plot import BasePlot  # noqa


CUSTOM_CLASSES = [
    Plot1D,
    Plot2D,
    Plot3D,
    ScatterView,
    ScatterView3D,
    ImageView,
    StackView,
    CurveStack,
    TimeCurvePlot,
    SpectroPlot,
    GridContainer,
]

LIVE_CLASSES = [
    LiveCurvePlot,
    LiveImagePlot,
    LiveScatterPlot,
    LiveMcaPlot,
    LiveOneDimPlot,
]

# For compatibility
CurvePlot = Plot1D
ImagePlot = Plot2D
ScatterPlot = ScatterView
HistogramImagePlot = ImageView
ImageStackPlot = StackView
