# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

from __future__ import annotations

import logging

from silx.gui import plot as silx_plot
from bliss.flint.widgets.viewer.data_widget import DataWidget
from bliss.flint.widgets.viewer.image_tooltip import ImageTooltip


_logger = logging.getLogger(__name__)


class ImageView(DataWidget):
    """Dedicated plot to display an image"""

    # Name of the method to add data to the plot
    METHOD = "setImage"

    class _PatchedImageView(silx_plot.ImageView):
        def isSideHistogramDisplayed(self):
            """True if the side histograms are displayed"""
            # FIXME: This have to be fixed in silx <= 1.1
            return self._histoHPlot.isVisibleTo(self)

    def _createSilxWidget(self, parent):
        widget = self._PatchedImageView(parent=parent)
        widget.setDataMargins(0.05, 0.05, 0.05, 0.05)
        widget.valueChanged.connect(self._updateTooltip)
        self._tooltip = ImageTooltip()
        return widget

    def getYaxisDirection(self) -> str:
        """Returns the direction of the y-axis.

        Returns:
            One of "up", "down"
        """
        inverted = self.silxWidget().getYAxis().isInverted()
        return "down" if inverted else "up"

    def setYaxisDirection(self, direction: str):
        """Specify the direction of the y-axis.

        By default the direction is up, which mean the 0 is on bottom, and
        positive values are above.

        Argument:
            direction: One of "up", "down"
        """
        assert direction in ("up", "down")
        inverted = direction == "down"
        self.silxWidget().getYAxis().setInverted(inverted)

    def setDisplayedIntensityHistogram(self, show):
        self.getIntensityHistogramAction().setVisible(show)

    def _updateTooltip(self, row, column, value):
        """Update status bar with coordinates/value from plots."""
        widget = self.silxPlot()
        self._tooltip.showUnderMouse(widget, row, column, value)
