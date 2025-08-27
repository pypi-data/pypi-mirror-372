# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.
"""
Provides plot helper class to deal with flint proxy.
"""

from __future__ import annotations

import numpy
import contextlib
import logging

from bliss.flint.client.data_plot import DataPlot


_logger = logging.getLogger(__name__)


class Plot3D(DataPlot):

    # Name of the corresponding silx widget
    WIDGET = "bliss.flint.viewers.custom_plot3d.viewer.Plot3D"

    # Available name to identify this plot
    ALIASES = ["3d", "plot3d"]

    def add_scatter_item(
        self,
        x: str,
        y: str,
        z: str,
        v: str,
        legend: str | None = None,
        symbol: str = ",",
        symbol_size=None,
        lut=None,
        vmin=None,
        vmax=None,
    ):
        """
        Create a scatter item in the plot.
        """
        self.submit(
            "addScatterItem",
            x,
            y,
            z,
            v,
            legend=legend,
            symbol=symbol,
            symbolSize=symbol_size,
            lut=lut,
            vmin=vmin,
            vmax=vmax,
        )

    def add_mesh_item(
        self,
        vertices: str,
        faces: str,
        legend: str | None = None,
        color: numpy.ndarray | None = None,
    ):
        """
        Create a mesh item in the plot.
        """
        self.submit(
            "addMeshItem", vertices=vertices, faces=faces, legend=legend, color=color
        )

    def clear_items(self):
        """Remove all the items described in this plot

        If no transaction was open, it will update the plot and refresh the plot
        view.
        """
        self.submit("clearItems")

    def reset_zoom(self):
        """Reset the zoom of the camera."""
        self.submit("resetZoom")

    def remove_item(self, legend: str):
        """Remove a specific item.

        If no transaction was open, it will update the plot and refresh the plot
        view.
        """
        self.submit("removeItem", legend)

    def set_data(self, **kwargs):
        """Set data named from keys with associated values.

        If no transaction was open, it will update the plot and refresh the plot
        view.
        """
        self.submit("setData", **kwargs)

    @contextlib.contextmanager
    def transaction(self, resetzoom=True):
        """Context manager to handle a set of changes and a single refresh of
        the plot. This is needed cause the action are done on the plot
        asynchronously"""
        self.submit("setAutoUpdatePlot", False)
        try:
            yield
        finally:
            self.submit("setAutoUpdatePlot", True)
            self.submit("updatePlot", resetzoom=resetzoom)
