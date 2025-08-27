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


class StackView(DataPlot):

    # Name of the corresponding silx widget
    WIDGET = "bliss.flint.viewers.custom_image_stack.viewer.StackImageView"

    # Available name to identify this plot
    ALIASES = ["stack", "imagestack", "stackview"]

    def _init(self):
        # Make it public
        self.set_colormap = self._set_colormap

    def set_data(self, data, **kwargs):
        self.submit("setStack", data, **kwargs)
