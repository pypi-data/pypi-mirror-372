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

from bliss.flint.client.data_plot import DataPlot


_logger = logging.getLogger(__name__)


class ScatterView3D(DataPlot):

    # Name of the corresponding silx widget
    WIDGET = "bliss.flint.viewers.custom_scatter3d.viewer.ScatterView3D"

    # Available name to identify this plot
    ALIASES = ["scatter3d"]

    def _init(self):
        # Make it public
        self.set_colormap = self._set_colormap

    def set_marker(self, symbol):
        """
        Set the kind of marker to use for scatters.

        Attributes:
            symbol: One of '.', ',', 'o'.
        """
        self.submit("setMarker", symbol)

    def set_data(self, x, y, z, value):
        if x is None or y is None or z is None or value is None:
            self.clear_data()
        else:
            self.submit("setData", x, y, z, value)
