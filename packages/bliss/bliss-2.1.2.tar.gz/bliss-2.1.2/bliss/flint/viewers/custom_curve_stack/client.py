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


class CurveStack(BasePlot):
    # Name of the corresponding silx widget
    WIDGET = "bliss.flint.viewers.custom_curve_stack.viewer.CurveStack"

    # Available name to identify this plot
    ALIASES = ["curvestack"]

    def set_data(self, curves, x=None, reset_zoom=None):
        """
        Set the data displayed in this plot.

        Arguments:
            curves: The data of the curves (first dim is curve index, second dim
                    is the x index)
            x: Mapping of the real X axis values to use
            reset_zoom: If True force reset zoom, else the user selection is
                        applied
        """
        self.submit("setData", data=curves, x=x, resetZoom=reset_zoom)

    def clear_data(self):
        self.submit("clear")
