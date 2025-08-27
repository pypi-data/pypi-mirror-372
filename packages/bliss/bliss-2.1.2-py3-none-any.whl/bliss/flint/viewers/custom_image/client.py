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


class ImageView(DataPlot):

    # Name of the corresponding silx widget
    WIDGET = "bliss.flint.viewers.custom_image.viewer.ImageView"

    # Available name to identify this plot
    ALIASES = ["image", "imageview", "histogramimage"]

    def _init(self):
        # Make it public
        self.set_colormap = self._set_colormap

    def _init_plot(self):
        super(ImageView, self)._init_plot()
        self.submit("setKeepDataAspectRatio", True)
        self.submit("setDisplayedIntensityHistogram", True)

    @property
    def yaxis_direction(self) -> str:
        """Direction of the y-axis.

        One of "up", "down"
        """
        return self.submit("getYaxisDirection")

    @yaxis_direction.setter
    def yaxis_direction(self, direction: str):
        self.submit("setYaxisDirection", direction)

    def set_data(self, data, **kwargs):
        if "origin" in kwargs:
            if kwargs["origin"] is None:
                # Enforce the silx default
                del kwargs["origin"]
        if "scale" in kwargs:
            if kwargs["scale"] is None:
                # Enforce the silx default
                del kwargs["scale"]
        self.submit("setImage", data, **kwargs)

    @property
    def side_histogram_displayed(self) -> bool:
        return self.submit("isSideHistogramDisplayed")

    @side_histogram_displayed.setter
    def side_histogram_displayed(self, displayed: bool):
        self.submit("setSideHistogramDisplayed", displayed)
