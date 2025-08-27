# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.
"""
Provides plot helper class to deal with flint proxy.
"""

from __future__ import annotations

import contextlib
import logging

from bliss.flint.client.base_plot import BasePlot


_logger = logging.getLogger(__name__)


class GridContainer(BasePlot):

    # Name of the corresponding silx widget
    WIDGET = "bliss.flint.viewers.custom_grid_container.viewer.GridContainer"

    # Available name to identify this plot
    ALIASES = ["grid"]

    def get_plot(
        self,
        plot_class: str | object,
        name: str | None = None,
        unique_name: str | None = None,
        selected: bool = False,
        closeable: bool = True,
        row: int | None = None,
        col: int | None = None,
        row_span: int | None = None,
        col_span: int | None = None,
    ):
        """Create or retrieve a plot from this flint instance.

        If the plot does not exists, it will be created in a new tab on Flint.

        Arguments:
            plot_class: A class defined in `bliss.flint.client.plot`, or a
                silx class name. Can be one of "Plot1D", "Plot2D", "ImageView",
                "StackView", "ScatterView".
            name: Not applicable for this container
            unique_name: If defined the plot can be retrieved from flint.
            selected: Not applicable for this container
            closeable: Not applicable for this container
            row: Row number where to place the new widget
            col: Column number where to place the new widget
            row_span: Number of rows to use to place the new widget
            col_span: Number of columns to use to place the new widget
        """
        return self._flint.get_plot(
            plot_class=plot_class,
            name=name,
            selected=selected,
            closeable=closeable,
            unique_name=unique_name,
            parent_id=self._plot_id,
            parent_layout_params=(row, col, row_span, col_span),
        )

    @contextlib.contextmanager
    def hide_context(self):
        self.submit("setVisible", False)
        try:
            yield
        finally:
            try:
                self.submit("setVisible", True)
            except Exception:
                pass
