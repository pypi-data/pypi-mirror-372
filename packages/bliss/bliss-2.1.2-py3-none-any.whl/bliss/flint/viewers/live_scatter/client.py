# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.
"""
Provides plot interface exposed inside BLISS shell.
"""

from __future__ import annotations

import logging

from bliss.flint.client.base_plot import BasePlot

_logger = logging.getLogger(__name__)


class LiveScatterPlot(BasePlot):

    ALIASES = ["scatter"]

    def _init(self):
        # Make it public
        self.set_colormap = self._set_colormap

    @property
    def xaxis_channel_name(self) -> str | None:
        """Returns the channel name used as x-axis, else None"""
        return self.submit("getXAxisChannelName")

    @property
    def yaxis_channel_name(self) -> str | None:
        """Returns the channel name used as y-axis, else None"""
        return self.submit("getYAxisChannelName")

    @property
    def displayed_channels(self) -> list[str]:
        """Channel names actually displayed"""
        return self.submit("getDisplayedChannels")

    @displayed_channels.setter
    def displayed_channels(self, channels: list[str]):
        self.submit("setDisplayedChannels", channels)

    def _plotselect(self, channels: list[str]):
        """Internal BLISS API to propagate plotselect to this plot"""
        self.submit("setDisplayedChannels", channels, role="plotselect")

    def select_data_index(self) -> int | None:
        """Request user selection of a data.

        Returns it's index, else None.
        """
        flint = self._flint
        request_id = flint.request_select_data_index(self._plot_id)
        return self._wait_for_user_selection(request_id)
