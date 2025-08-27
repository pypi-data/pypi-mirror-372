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


class Plot1D(DataPlot):

    # Name of the corresponding silx widget
    WIDGET = "bliss.flint.viewers.custom_plot1d.viewer.Plot1D"

    # Available name to identify this plot
    ALIASES = ["curve", "plot1d"]

    def update_axis_marker(
        self, unique_name: str, channel_name, position: float, text: str
    ):
        """
        Display a vertical marker for a specific x-axis channel name.

        Arguments:
            unique_name: Unique name identifying this marker
            channel_name: X-axis name in which the marker have to be displayed (for example `axis:foo`)
                          The marker will only be displayed if the actual plot's x-axis is this channel
            position: Position of this marker in the `channel_name` axis
            text: Text to display with the marker
        """
        self._flint.update_axis_marker(
            self._plot_id, unique_name, channel_name, position, text
        )

    def add_curve(self, x, y, **kwargs):
        """
        Create a curve in this plot.
        """
        if x is None:
            x = numpy.arange(len(y))
        if y is None:
            raise ValueError("A y value is expected. None found.")
        self.submit("addCurve", x, y, **kwargs)

    @property
    def xscale(self):
        """
        Scale of the x-axis of this plot.

        The value is one of "linear", "log"
        """
        return self.submit("getXAxisScale")

    @xscale.setter
    def xscale(self, scale):
        self.submit("setXAxisScale", scale)

    @property
    def yscale(self):
        """
        Scale of the y-axis of this plot.

        The value is one of "linear", "log"
        """
        return self.submit("getYAxisScale")

    @yscale.setter
    def yscale(self, scale):
        self.submit("setYAxisScale", scale)

    def set_xaxis_scale(self, value):
        """
        Set the X-axis scale of this plot.

        Deprecated in BLISS 1.10. prefer using `xscale` property

        Argument:
            value: One of "linear" or "log"
        """
        self.xscale = value

    def set_yaxis_scale(self, value):
        """
        Set the Y-axis scale of this plot.

        Deprecated in BLISS 1.10. prefer using `xscale` property

        Argument:
            value: One of "linear" or "log"
        """
        self.yscale = value

    def clear_items(self):
        """Remove all the items described in this plot

        If no transaction was open, it will update the plot and refresh the plot
        view.
        """
        self.submit("clearItems")

    def add_curve_item(
        self, xname: str, yname: str, legend: str | None = None, **kwargs
    ):
        """Define a specific curve item

        If no transaction was open, it will update the plot and refresh the plot
        view.
        """
        self.submit("addCurveItem", xname, yname, legend=legend, **kwargs)

    def get_item(self, legend: str) -> dict:
        """Get the description of an item"""
        return self.submit("getItem", legend=legend)

    def remove_item(self, legend: str):
        """Remove a specific item.

        If no transaction was open, it will update the plot and refresh the plot
        view.
        """
        self.submit("removeItem", legend)

    def item_exists(self, legend: str):
        """True if a specific item exists."""
        return self.submit("itemExists", legend)

    def set_data(self, **kwargs):
        """Set data named from keys with associated values.

        If no transaction was open, it will update the plot and refresh the plot
        view.
        """
        self.submit("setData", **kwargs)

    def append_data(self, **kwargs):
        """Append data named from keys with associated values.

        If no transaction was open, it will update the plot and refresh the plot
        view.
        """
        self.submit("appendData", **kwargs)

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

    def select_points_to_remove(
        self, legend: str, data_names: list[str] | None = None
    ) -> bool:
        """Start a user selection to remove points from the UI.

        The interaction can be stoped from the UI or by a ctrl-c

        The result can be retrieved with the `get_data(name_of_the_data)`.

        Arguments:
            legend: The name of the curve item in which points have to be removed
            data_names: An optional list of data name which also have to be updated
        """
        desc = self.get_item(legend)
        x_name, y_name = desc["xdata"], desc["ydata"]
        style = desc["style"]
        self.add_curve_item(
            x_name, y_name, legend=legend, linestyle="-", symbol="o", linewidth=2
        )
        previous_data = {x_name: self.get_data(x_name), y_name: self.get_data(y_name)}
        if data_names is not None:
            for n in data_names:
                previous_data[n] = self.get_data(n)
        try:
            while True:
                res = self.select_shape("rectangle", valid=True, cancel=True)
                if res is False:
                    raise KeyboardInterrupt()
                if res is True:
                    break
                rect = res
                assert len(rect) == 2
                range_x = sorted([rect[0][0], rect[1][0]])
                range_y = sorted([rect[0][1], rect[1][1]])
                # mask on everything outside the rect
                x = self.get_data(x_name)
                y = self.get_data(y_name)
                i = numpy.logical_or(
                    numpy.logical_or(x < range_x[0], x > range_x[1]),
                    numpy.logical_or(y < range_y[0], y > range_y[1]),
                )
                data = {x_name: x[i], y_name: y[i]}
                if data_names is not None:
                    for n in data_names:
                        data[n] = self.get_data(n)[i]
                self.set_data(**data)
        except KeyboardInterrupt:
            self.set_data(**previous_data)
            return False
        finally:
            self.add_curve_item(x_name, y_name, legend=legend, **style)
        return True
