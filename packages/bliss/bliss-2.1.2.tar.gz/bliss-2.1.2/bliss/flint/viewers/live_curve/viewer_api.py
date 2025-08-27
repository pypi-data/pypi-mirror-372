# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

from __future__ import annotations

import logging


from bliss.flint.model import plot_model
from bliss.flint.model import plot_item_model
from bliss.flint.helper import model_helper


_logger = logging.getLogger(__name__)


class CurvePlotWidgetApi:
    def __init__(self, parent):
        from .viewer import CurvePlotWidget

        self._parent: CurvePlotWidget = parent

    def getXAxisChannelName(self) -> str | None:
        """Returns the channel name used as x-axis"""
        plot = self._parent.plotModel()
        if plot is None:
            return None
        for item in plot.items():
            if not item.isValid():
                continue
            if not item.isVisible():
                continue
            if isinstance(item, plot_item_model.CurveItem):
                channel = item.xChannel()
                if channel:
                    return channel.name()
        return None

    def setDisplayedChannels(self, channel_names: list[str], role: str | None = None):
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
        if scan is None:
            # If there is no scan, we can't pick anything
            return

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
            if channelName is not None:
                try:
                    channels.remove(channelName)
                    channels.insert(0, channelName)
                except Exception:
                    pass

        return channels

    def clearUserMarkers(self):
        """List the channels displayed."""
        widget = self._parent

        plotModel = widget.plotModel()
        if plotModel is None:
            return

        with plotModel.transaction():
            # Clean up temporary items
            for item in list(plotModel.items()):
                if isinstance(item, plot_model.NotReused):
                    try:
                        plotModel.removeItem(item)
                    except Exception:
                        pass

        plot = widget._silxPlot()
        for i in plot.getItems():
            name = i.getName()
            if name is None:
                continue
            # Guess the name of the items created by the fit tool
            if name.startswith("Fit "):
                plot.removeItem(i)

    def scanKey(self) -> str | None:
        widget = self._parent
        scan = widget.scan()
        if scan is None:
            return None
        return scan.blissDataScanKey()
