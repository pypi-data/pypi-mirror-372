# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.
"""
Provides plot helper class to deal with flint proxy.
"""

import logging

from bliss.flint.client.base_plot import BasePlot


_logger = logging.getLogger(__name__)


class TimeCurvePlot(BasePlot):
    # Name of the corresponding silx widget
    WIDGET = "bliss.flint.viewers.custom_time_curve.viewer.TimeCurvePlot"

    # Available name to identify this plot
    ALIASES = ["timecurveplot"]

    def select_x_axis(self, name: str):
        """
        Select the x-axis to use

        Arguments:
            name: Name of the data to use as x-axis
        """
        self.submit("setXName", name)

    @property
    def xaxis_duration(self):
        return self.submit("xDuration")

    @xaxis_duration.setter
    def xaxis_duration(self, second: int):
        """
        Select the x-axis duration in second

        Arguments:
            second: Amount of seconds displayed in the x-axis
        """
        self.submit("setXDuration", second)

    def select_x_duration(self, second: int):
        """
        Select the x-axis duration in second

        Arguments:
            second: Amount of seconds displayed in the x-axis
        """
        self.xaxis_duration = second

    @property
    def ttl(self):
        return self.submit("ttl")

    @ttl.setter
    def ttl(self, second: int):
        """
        Set the time to live of the data.

        After this period of time, a received data is not anymore displayable
        in Flint.

        Arguments:
            second: Amount of seconds a data will live
        """
        self.submit("setTtl", second)

    def add_time_curve_item(self, yname, **kwargs):
        """
        Select a dedicated data to be displayed against the time.

        Arguments:
            name: Name of the data to use as y-axis
            kwargs: Associated style (see `addCurve` from silx plot)
        """
        self.submit("addTimeCurveItem", yname, **kwargs)

    def set_data(self, **kwargs):
        """
        Set the data displayed in this plot.

        Arguments:
            kwargs: Name of the data associated to the new numpy array to use
        """
        self.submit("setData", **kwargs)

    def append_data(self, **kwargs):
        """
        Append the data displayed in this plot.

        Arguments:
            kwargs: Name of the data associated to the numpy array to append
        """
        self.submit("appendData", **kwargs)

    def clear_data(self):
        self.submit("clear")
