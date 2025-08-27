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


class StackImageView(DataWidget):
    """Dedicated plot to display a stack of images"""

    # Name of the method to add data to the plot
    METHOD = "setStack"

    def _createSilxWidget(self, parent):
        stack = silx_plot.StackView(parent=parent)
        stack.valueChanged.connect(self._updateTooltip)
        self._tooltip = ImageTooltip()
        return stack

    def _updateTooltip(self, row, column, value):
        """Update status bar with coordinates/value from plots."""
        widget = self.silxPlot()
        if value is None:
            self._tooltip.hide()
        else:
            self._tooltip.showUnderMouse(widget, row, column, value)

    def getDataRange(self):
        plot = self.silxWidget().getPlotWidget()
        return plot.getDataRange()
