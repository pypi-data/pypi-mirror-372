# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

from __future__ import annotations
from typing import Any

import numpy
import logging
import numbers

from silx.gui import qt
from bliss.flint.helper.tooltip_factory import TooltipFactory

_logger = logging.getLogger(__name__)


class ImageTooltip:
    def _formatPixelValue(self, value) -> tuple[str, Any]:
        if isinstance(value, (numbers.Integral, numbers.Real)):
            return "Value", value
        try:
            if isinstance(value, numpy.ndarray):
                if len(value) == 4:
                    return "RGBA", "%.3g, %.3g, %.3g, %.3g" % (
                        value[0],
                        value[1],
                        value[2],
                        value[3],
                    )
                elif len(value) == 3:
                    return "RGB", "%.3g, %.3g, %.3g" % (
                        value[0],
                        value[1],
                        value[2],
                    )
        except Exception:
            _logger.error("Error while formatting pixel value", exc_info=True)
        return "Value", str(value)

    def hide(self):
        qt.QToolTip.hideText()

    def showUnderMouse(self, widget: qt.QWidget, row: float, column: float, value: Any):
        """
        Called to update the tooltip ovre the plot.

        Arguments:
            widget: Widget to use to display the tooltip
            row: Integer as float value of the row (always 1.0 2.0).
                 If nan, the mouse hover side profile and the value is the sum
            column: Integer as float value of the column (always 1.0 2.0).
                    If nan, the mouse hover side profile and the value is the sum
            value: Value of the ouvered pixel (or sum in case of the side profile)
        """
        tooltip = TooltipFactory()

        def normalize(v) -> int | None:
            if numpy.isnan(v):
                return None
            return int(v)

        irow = normalize(row)
        icolumn = normalize(column)

        if irow is None or icolumn is None:
            # Triggered with mouse over the side histograms
            if icolumn is not None:
                tooltip.addQuantity("Column/x", icolumn)
                # Value of the profile
                tooltip.addQuantity("Sum", value)
            if irow is not None:
                tooltip.addQuantity("Row/y", irow)
                # Value of the profile
                tooltip.addQuantity("Sum", value)
        else:
            tooltip.addQuantity("Column/x", icolumn)
            tooltip.addQuantity("Row/y", irow)
            name, v = self._formatPixelValue(value)
            tooltip.addQuantity(name, v)

        cursorPos = qt.QCursor.pos() + qt.QPoint(10, 10)
        uniqueid = f'<meta name="foo" content="{cursorPos.x()}-{cursorPos.y()}" />'

        if not tooltip.isEmpty():
            text = f"<html>{tooltip.text()}{uniqueid}</html>"
        else:
            text = f"<html>No data{uniqueid}</html>"
        qt.QToolTip.showText(cursorPos, text, widget)
