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


class SpectroPlot(BasePlot):
    # Name of the corresponding silx widget
    WIDGET = "bliss.flint.viewers.custom_spectro.viewer.SpectroPlot"

    # Available name to identify this plot
    ALIASES = ["spectroplot"]

    def set_data(self, **kwargs):
        """
        Set the data displayed in this plot.

        Arguments:
            kwargs: Name of the data associated to the new numpy array to use
        """
        self.submit("setData", **kwargs)

    def add_data(self, **kwargs):
        self.submit("addData", **kwargs)

    def clear_data(self):
        self.submit("clear")

    def refresh(self):
        self.submit("refresh")

    def set_box_min_max(self, mini, maxi):
        self.submit("setBoxMinMax", mini, maxi)
