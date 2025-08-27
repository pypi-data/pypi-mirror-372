# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

from __future__ import annotations
from typing import Any

import logging

from silx.gui import qt
from bliss.flint.widgets.custom_plot import CustomPlot

_logger = logging.getLogger(__name__)


class GridContainer(qt.QWidget):
    def __init__(self, parent=None):
        super(GridContainer, self).__init__(parent=parent)
        layout = qt.QGridLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        self.__layout = layout
        self.__customPlots: dict[str, qt.QWidget] = {}

    def _createHolder(
        self, label, widgetClass=qt.QWidget, closeable=False, selected=False
    ):
        widget = widgetClass(parent=self)
        return widget

    def _removeHolder(self, widget: qt.QWidget):
        widget.deleteLater()

    def createCustomPlot(
        self,
        plotWidget: qt.QWidget,
        name: str,
        plot_id: str,
        selected: bool,
        closeable: bool,
        parentLayoutParams: Any,
    ) -> CustomPlot:
        """Create a custom plot"""

        def parseIntNone(param: Any) -> int | None:
            if param is None:
                return param
            return int(param)

        def parse(params: Any) -> tuple[int | None, int | None, int | None, int | None]:
            try:
                row, col, rowSpan, columnSpan = parentLayoutParams
                return (
                    parseIntNone(row),
                    parseIntNone(col),
                    parseIntNone(rowSpan),
                    parseIntNone(columnSpan),
                )
            except Exception:
                raise ValueError(
                    "parentLayoutParams have to be of type 'tuple[int | None, int | None, int | None, int | None]'"
                )

        row, col, rowSpan, columnSpan = parse(parentLayoutParams)
        if row is None:
            row = 0
        if col is None:
            col = 0
        if rowSpan is None:
            rowSpan = 1
        if columnSpan is None:
            columnSpan = 1
        customPlot = self._createHolder(
            name, widgetClass=CustomPlot, selected=selected, closeable=closeable
        )
        self.__layout.addWidget(customPlot, row, col, rowSpan, columnSpan)
        customPlot.setPlotId(plot_id)
        customPlot.setName(name)
        customPlot.setPlot(plotWidget)
        self.__customPlots[plot_id] = customPlot
        plotWidget.show()
        return customPlot

    def subPlotIds(self) -> list[str]:
        return list(self.__customPlots.keys())

    def removeCustomPlot(self, plot_id: str):
        """Remove a custom plot by its id

        Raises:
            ValueError: If the plot id does not exist
        """
        customPlot = self.__customPlots.pop(plot_id, None)
        if customPlot is None:
            raise ValueError(f"Plot id '{plot_id}' does not exist")
        self._removeHolder(customPlot)

    def customPlot(self, plot_id) -> CustomPlot | None:
        """If the plot does not exist, returns None"""
        plot = self.__customPlots.get(plot_id)
        return plot
