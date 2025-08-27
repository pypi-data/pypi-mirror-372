# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

from __future__ import annotations

import logging

from bliss.flint.model import plot_item_model
from bliss.flint.helper import model_helper


_logger = logging.getLogger(__name__)


class ScatterPlotWidgetApi:
    def __init__(self, parent):
        from .viewer import ScatterPlotWidget

        self._parent: ScatterPlotWidget = parent

    def getXAxisChannelName(self) -> str | None:
        """Returns the channel name used as x-axis, else None"""
        plot = self._parent.plotModel()
        if plot is None:
            return None
        for item in plot.items():
            if not item.isValid():
                continue
            if not item.isVisible():
                continue
            if isinstance(item, plot_item_model.ScatterItem):
                channel = item.xChannel()
                if channel:
                    return channel.name()
        return None

    def getYAxisChannelName(self) -> str | None:
        """Returns the channel name used as y-axis, else None"""
        plot = self._parent.plotModel()
        if plot is None:
            return None
        for item in plot.items():
            if not item.isValid():
                continue
            if not item.isVisible():
                continue
            if isinstance(item, plot_item_model.ScatterItem):
                channel = item.yChannel()
                if channel:
                    return channel.name()
        return None

    def setDisplayedChannels(self, channel_names: list[str], role: str = None):
        """Enforce channels to be displayed.

        - If a channel was not part of the plot, an item is added
        - If a channel was hidden, it become visible
        - If a channel is in the plot but not part of this list, it is removed

        Arguments:
            channel_names: List of channel names to display
            role: Could be use to know the kind of source for this request
                  For now it is used with "plotselect" when it is called from
                  BLISS plotselect command.
        """
        widget = self._parent
        plotModel = widget.plotModel()
        if plotModel is None:
            # If there is no plot, there is nothing to select
            return

        scan = widget.scan()
        model_helper.updateDisplayedChannelNames(
            plotModel, scan, channel_names, ignoreMissingChannels=True
        )
        if role == "plotselect":
            plotModel.tagPlotselectEdit()

    def getDisplayedChannels(self) -> list[str]:
        """List the channels displayed."""
        widget = self._parent

        plotModel = widget.plotModel()
        if plotModel is None:
            return []

        channels = model_helper.getChannelNamesDisplayedAsValue(plotModel)

        # Move the selected channel in first
        item = widget.selectedPlotItem()
        if item is not None:
            channelName = None
            try:
                yChannel = item.yChannel()
                if yChannel is not None:
                    channelName = item.yChannel().name()
            except Exception:
                pass
            try:
                channels.remove(channelName)
                channels.insert(0, channelName)
            except Exception:
                pass

        return channels
