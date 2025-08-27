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

_logger = logging.getLogger(__name__)


class ScatterView(DataWidget):
    """Dedicated plot to display a 2D scatter"""

    # Name of the method to add data to the plot
    METHOD = "setData"

    def _createSilxWidget(self, parent):
        widget = silx_plot.ScatterView(parent=parent)
        plot = widget.getPlotWidget()
        plot.setDataMargins(0.05, 0.05, 0.05, 0.05)
        return widget

    def silxPlot(self):
        widget = self.silxWidget()
        return widget.getPlotWidget()

    def getDataRange(self):
        plot = self.silxWidget().getPlotWidget()
        return plot.getDataRange()

    def clear(self):
        self.silxWidget().setData(None, None, None)

    def setData(
        self, x, y, value, xerror=None, yerror=None, alpha=None, resetzoom=True
    ):
        self.silxWidget().setData(
            x, y, value, xerror=xerror, yerror=yerror, alpha=alpha, copy=False
        )
        if resetzoom:
            # Else the view is not updated
            self.resetZoom()
