# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.
"""
Helper functions to deal with Flint models
"""

from __future__ import annotations

import logging

from silx.gui import colors

from bliss.flint.model import plot_model
from bliss.flint.model import plot_item_model
from bliss.flint.model import scan_model
from bliss.flint.model import style_model


_logger = logging.getLogger(__name__)


def reachAnyCurveItemFromDevice(
    plot: plot_model.Plot, scan: scan_model.Scan, topMaster: scan_model.Device
) -> plot_item_model.CurveItem | None:
    """
    Reach any plot item from this top master
    """
    for item in plot.items():
        if not isinstance(item, plot_item_model.CurveItem):
            continue
        itemChannel = item.xChannel()
        if isinstance(itemChannel, plot_model.XIndexChannelRef):
            itemChannel = None
        if itemChannel is None:
            itemChannel = item.yChannel()
        if itemChannel is None:
            if isinstance(item.xChannel(), plot_model.XIndexChannelRef):
                # That's the only item of the plot
                return item
            continue
        channelName = itemChannel.name()
        channel = scan.getChannelByName(channelName)
        if channel is None:
            continue
        itemMaster = channel.device().topMaster()
        if itemMaster is topMaster:
            return item
    return None


def reachAllCurveItemFromDevice(
    plot: plot_model.Plot, scan: scan_model.Scan, topMaster: scan_model.Device
) -> list[plot_item_model.CurveItem]:
    """
    Reach all plot items from this top master
    """
    curves = []
    for item in plot.items():
        if not isinstance(item, plot_item_model.CurveItem):
            continue
        itemChannel = item.xChannel()
        if itemChannel is None or isinstance(itemChannel, plot_model.XIndexChannelRef):
            itemChannel = item.yChannel()
        if itemChannel is None:
            continue
        channelName = itemChannel.name()
        channel = scan.getChannelByName(channelName)
        if channel is None:
            continue
        itemMaster = channel.device().topMaster()
        if itemMaster is topMaster:
            curves.append(item)
    return curves


def getConsistentTopMaster(
    scan: scan_model.Scan, plotItem: plot_item_model.CurveItem
) -> scan_model.Device | None:
    """Returns a top master from this item only if channels comes from the
    same top master.

    If there is a single top master (x-channel or y-channel is missing), this
    top master is returned.
    """
    xChannel = plotItem.xChannel()
    if isinstance(xChannel, plot_model.XIndexChannelRef):
        xChannel = None
    yChannel = plotItem.yChannel()
    if xChannel is None and yChannel is None:
        return None

    if xChannel is None or yChannel is None:
        # One or the other is valid
        channelRef = xChannel if xChannel is not None else yChannel
        assert channelRef is not None
        # With one or the other the master channel is valid
        name = channelRef.name()
        channel = scan.getChannelByName(name)
        if channel is None:
            return None
        return channel.device().topMaster()

    x = xChannel.name()
    channelX = scan.getChannelByName(x)
    if channelX is None:
        return None

    y = yChannel.name()
    channelY = scan.getChannelByName(y)
    if channelY is None:
        return None

    topMasterX = channelX.device().topMaster()
    topMasterY = channelY.device().topMaster()
    if topMasterX is not topMasterY:
        return None
    return topMasterX


INDEX_REF = "##INDEX##"


def getMostUsedXChannelPerMasters(
    scan: scan_model.Scan | None, plotModel: plot_item_model.CurvePlot
) -> dict[scan_model.Device, str]:
    """
    Returns a dictionary mapping top master with the most used x-channels.
    """
    if scan is None:
        return {}
    if plotModel is None:
        return {}

    # Count the amount of same x-channel per top masters
    xChannelsPerMaster: dict[scan_model.Device, dict[str, int]] = {}
    for plotItem in plotModel.items():
        if not isinstance(plotItem, plot_item_model.CurveItem):
            continue
        # Here is only top level curve items
        xChannel = plotItem.xChannel()
        if xChannel is None:
            continue
        if isinstance(xChannel, plot_model.XIndexChannelRef):
            xChannelName = INDEX_REF
            yChannel = plotItem.yChannel()
            if yChannel is not None:
                channel = scan.getChannelByName(yChannel.name())
            else:
                channel = None
        else:
            xChannelName = xChannel.name()
            channel = scan.getChannelByName(xChannelName)
        if channel is not None:
            topMaster = channel.device().topMaster()
            if topMaster not in xChannelsPerMaster:
                counts: dict[str, int] = {}
                xChannelsPerMaster[topMaster] = counts
            else:
                counts = xChannelsPerMaster[topMaster]

            counts[xChannelName] = counts.get(xChannelName, 0) + 1

    # Returns the most used channels
    xChannelPerMaster = {}
    for master, counts in xChannelsPerMaster.items():
        channels = sorted(counts.keys(), key=lambda x: counts[x], reverse=True)
        most_often_used_channel = channels[0]
        xChannelPerMaster[master] = most_often_used_channel

    return xChannelPerMaster


def getChannelNameGroups(scan: scan_model.Scan) -> list[list[str]]:
    """Returns the list of channels which are in the same group.

    A group is supposed to contain only channels with, in the end, the same
    amount of measurements.
    """
    channels: dict[scan_model.Device, list[scan_model.Channel]] = {}
    for device in scan.devices():
        if device.isMaster():
            channels[device] = list(device.channels())
        else:
            topMaster = device.topMaster()
            chs = channels.setdefault(topMaster, [])
            chs.extend(device.channels())

    result: list[list[str]] = []
    for data in channels.values():
        ch = [c.name() for c in data]
        result.append(ch)
    return result


def cloneChannelRef(
    plot: plot_model.Plot, channel: plot_model.ChannelRef | None
) -> plot_model.ChannelRef | None:
    if channel is None:
        return None
    if isinstance(channel, plot_model.XIndexChannelRef):
        return plot_model.XIndexChannelRef(parent=plot)
    name = channel.name()
    cloned = plot_model.ChannelRef(parent=plot, channelName=name)
    return cloned


def removeItemAndKeepAxes(plot: plot_model.Plot, item: plot_model.Item):
    """
    Remove an item from the model and keep the axes, if available.

    If the item is the last one, create a new item to keep the available axes.

    Only CurveItem and ScatterItem provides axes. For other ones the item is
    just removed.
    """
    if isinstance(item, plot_item_model.ScatterItem):
        scatters = []
        for scatter in plot.items():
            if isinstance(scatter, plot_item_model.ScatterItem):
                scatters.append(scatter)

        if len(scatters) == 1:
            # Only remove the value to remember the axes
            newItem = plot_item_model.ScatterItem(plot)
            xChannel = cloneChannelRef(plot, item.xChannel())
            yChannel = cloneChannelRef(plot, item.yChannel())
            if xChannel is None and yChannel is None:
                # It does not contain x or y-axis to keep
                plot.removeItem(item)
            else:
                if xChannel is not None:
                    newItem.setXChannel(xChannel)
                if yChannel is not None:
                    newItem.setYChannel(yChannel)
                with plot.transaction():
                    plot.removeItem(item)
                    plot.addItem(newItem)
        else:
            # It's not the last one
            plot.removeItem(item)
    elif isinstance(item, plot_item_model.CurveItem):
        xChannel = item.xChannel()
        if xChannel is not None:
            # Reach curves sharing the same x-channel
            curves = []
            for curve in plot.items():
                if isinstance(curve, plot_item_model.CurveItem):
                    if xChannel == curve.xChannel():
                        curves.append(curve)

            if len(curves) == 1:
                # Only remove the value to remember the axes
                xChannel = cloneChannelRef(plot, xChannel)
                newItem2 = plot_item_model.CurveItem(plot)
                newItem2.setXChannel(xChannel)
                with plot.transaction():
                    plot.removeItem(item)
                    plot.addItem(newItem2)
            else:
                # It's not the last one
                plot.removeItem(item)
        else:
            # It does not contain x-axis to keep
            plot.removeItem(item)
    else:
        # It's something else than curve or scatter
        plot.removeItem(item)


def createScatterItem(
    plot: plot_model.Plot, channel: scan_model.Channel
) -> tuple[plot_item_model.ScatterItem, bool]:
    """
    Create an item to a plot using a channel.

    Returns a tuple containing the created or updated item, plus a boolean to know if the item was updated.
    """
    channel_name = channel.name()

    # Reach any plot item from this master
    baseItem: plot_model.Item | None
    for baseItem in plot.items():
        if isinstance(baseItem, plot_item_model.ScatterItem):
            break
    else:
        baseItem = None

    if baseItem is not None:
        isAxis = baseItem.valueChannel() is None
        if isAxis:
            baseItem.setValueChannel(plot_model.ChannelRef(plot, channel_name))
            # It's now an item with a value
            return baseItem, True
        else:
            # Create a new item using axis from baseItem
            xChannel = cloneChannelRef(plot, baseItem.xChannel())
            yChannel = cloneChannelRef(plot, baseItem.yChannel())
            newItem = plot_item_model.ScatterItem(plot)
            if xChannel is not None:
                newItem.setXChannel(xChannel)
            if yChannel is not None:
                newItem.setYChannel(yChannel)
            newItem.setValueChannel(plot_model.ChannelRef(plot, channel_name))
    else:
        # No axes are specified
        # FIXME: Maybe we could use scan infos to reach the default axes
        newItem = plot_item_model.ScatterItem(plot)
        newItem.setValueChannel(plot_model.ChannelRef(plot, channel_name))
    plot.addItem(newItem)
    return newItem, False


def createCurveItem(
    plot: plot_model.Plot, channel: scan_model.Channel, yAxis: str, allowIndexed=False
) -> tuple[plot_model.Item, bool]:
    """
    Create an item to a plot using a channel.

    Returns a tuple containing the created or updated item, plus a boolean to know if the item was updated.
    """
    # Reach the master device
    topMaster = channel.device().topMaster()
    scan = topMaster.scan()

    # Reach any plot item from this master
    item = reachAnyCurveItemFromDevice(plot, scan, topMaster)

    if item is not None:
        isAxis = item.yChannel() is None
        if isAxis:
            item.setYChannel(plot_model.ChannelRef(plot, channel.name()))
            item.setYAxis(yAxis)
            return item, True
        else:
            newItem = None
            if allowIndexed:
                if isinstance(item.xChannel(), plot_model.XIndexChannelRef):
                    newItem = plot_item_model.CurveItem(plot)
                    newItem.setXChannel(plot_model.XIndexChannelRef(plot, None))
            if newItem is None:
                newItem = plot_item_model.CurveItem(plot)
                xChannel = cloneChannelRef(plot, item.xChannel())
                newItem.setXChannel(xChannel)
            newItem.setYChannel(plot_model.ChannelRef(plot, channel.name()))
            newItem.setYAxis(yAxis)
    else:
        # No other x-axis is specified
        # Reach another channel name from the same top master
        if allowIndexed:
            newItem = plot_item_model.CurveItem(plot)
            newItem.setXChannel(plot_model.XIndexChannelRef(plot, None))
        else:
            channelNames = []
            for device in scan.devices():
                if device.topMaster() is not topMaster:
                    continue
                channelNames.extend([c.name() for c in device.channels()])
            channelNames.remove(channel.name())

            if len(channelNames) > 0:
                # Pick the first one
                # FIXME: Maybe we could use scan infos to reach the default channel
                channelName = channelNames[0]
            else:
                # FIXME: Maybe it's better idea to display it with x-index
                channelName = channel.name()
            newItem = plot_item_model.CurveItem(plot)
            newItem.setXChannel(plot_model.ChannelRef(plot, channelName))

        newItem.setYChannel(plot_model.ChannelRef(plot, channel.name()))
        newItem.setYAxis(yAxis)

    plot.addItem(newItem)
    return newItem, False


def filterUsedDataItems(
    plot, channel_names
) -> tuple[list[plot_model.Item], list[plot_model.Item], list[plot_model.Item]]:
    """Filter plot items according to expected channel names.

    Returns a tuple within channels which have items, items which are
    not needed and channel names which have no equivalent items.

    The existing items are ordered according to the `channel_names` params.
    """
    expected: dict[str, plot_model.Item] = {}
    remaining_names = set(channel_names)
    unneeded_items = []
    for item in plot.items():
        if isinstance(item, plot_item_model.ScatterItem):
            channel = item.valueChannel()
        elif isinstance(item, plot_item_model.CurveItem):
            channel = item.yChannel()
        elif isinstance(item, plot_item_model.ImageItem):
            channel = item.imageChannel()
        elif isinstance(item, plot_item_model.McaItem):
            channel = item.mcaChannel()
        else:
            _logger.debug("Item %s skipped", type(item))
            continue
        if channel is not None:
            if channel.name() in channel_names:
                expected[channel.name()] = item
                remaining_names.remove(channel.name())
                continue
        unneeded_items.append(item)

    unused_channels = list(remaining_names)
    used_items = [expected[c] for c in channel_names if c in expected]
    return used_items, unneeded_items, unused_channels


def getChannelNamesDisplayedAsValue(plot: plot_model.Plot) -> list[str]:
    names = []
    for item in plot.items():
        if isinstance(item, plot_item_model.CurveItem):
            channel = item.yChannel()
            if channel is None:
                continue
            names.append(channel.name())
        elif isinstance(item, plot_item_model.McaItem):
            channel = item.mcaChannel()
            if channel is None:
                continue
            names.append(channel.name())
        if isinstance(item, plot_item_model.ScatterItem):
            channel = item.valueChannel()
            if channel is None:
                continue
            names.append(channel.name())
        if isinstance(item, plot_item_model.ImageItem):
            channel = item.imageChannel()
            if channel is None:
                continue
            names.append(channel.name())
    return names


def discardMissingChannels(plot: plot_model.Plot, scan: scan_model.Scan):
    """Remove items which are not availabe in the plot.

    This also logs the remove as an error.
    """
    groups = getChannelNameGroups(scan)
    available = set([])
    for g in groups:
        available.update(g)

    with plot.transaction():
        for item in plot.items():
            if isinstance(item, plot_item_model.CurveItem):
                # If y is not available the item have no meaning
                yChannel = item.yChannel()
                xChannel = item.xChannel()
                if yChannel is not None:
                    if yChannel.name() not in available:
                        _logger.error(
                            "Channel '%s' not availabled. Discarded from the plot",
                            yChannel.name(),
                        )
                        if xChannel is None:
                            plot.removeItem(item)
                            continue
                        else:
                            item.setYChannel(None)
                if xChannel is not None:
                    if xChannel.name() not in available:
                        _logger.error(
                            "Channel '%s' not availabled. Discarded from the plot",
                            xChannel.name(),
                        )
                        if yChannel is None:
                            plot.removeItem(item)
                            continue
                        else:
                            item.setXChannel(None)


def removeNotAvailableChannels(
    plot: plot_model.Plot, basePlot: plot_model.Plot, baseScan: scan_model.Scan
):
    """Remove from `plot` channels which are not available in this `scan`.
    The `basePlot` generated from this `scan` can help to improve the result.

    As result:

    - Channels used as value by `plot` have to exist in the scan
    - Axes also have to exists
        - Else it is reach from the basePlot
            - Else there is none
    """
    groups = getChannelNameGroups(baseScan)

    def findGroupId(name: str):
        for groupId, group in enumerate(groups):
            if name in group:
                return groupId
        return None

    # Try to identify the default axis for each groups
    defaultAxis = [None] * len(groups)
    for item in basePlot.items():
        xChannel = item.xChannel()
        if xChannel is None:
            continue
        yChannel = item.yChannel()
        if yChannel is not None:
            groupId = findGroupId(yChannel.name())
            if groupId is not None:
                defaultAxis[groupId] = xChannel.name()

    def isConsistent(item):
        xChannel = item.xChannel()
        yChannel = item.yChannel()
        if xChannel is None:
            return False
        if yChannel is None:
            return False
        g1 = findGroupId(xChannel.name())
        g2 = findGroupId(yChannel.name())
        if g1 is None or g2 is None:
            # Not supposed to happen
            assert False
        return g1 == g2

    def getDefaultAxis(name: str):
        g = findGroupId(name)
        if g is None:
            return None
        return defaultAxis[g]

    available = set([])
    for g in groups:
        available.update(g)

    with plot.transaction():
        for item in plot.items():
            if isinstance(item, plot_item_model.CurveItem):
                # If y is not available the item have no meaning
                yChannel = item.yChannel()
                if yChannel is not None:
                    if yChannel.name() not in available:
                        plot.removeItem(item)
                        continue

                # If x is not there we still can do something
                xChannel = item.xChannel()
                if xChannel is not None:
                    if xChannel.name() not in available:
                        if yChannel is None:
                            plot.removeItem(item)
                            continue
                        else:
                            item.setXChannel(None)

                if yChannel is not None and not isConsistent(item):
                    # We have to found a new axis
                    axisName = getDefaultAxis(yChannel.name())
                    if axisName is None:
                        item.setXChannel(None)
                    else:
                        channel = plot_model.ChannelRef(item, axisName)
                        item.setXChannel(channel)


def isChannelUsedAsAxes(plot: plot_model.Plot, channel: scan_model.Channel):
    if channel is None:
        return False
    channel_name = channel.name()
    for item in plot.items():
        if isinstance(item, plot_item_model.CurveItem):
            channel2 = item.xChannel()
            if channel2 is None:
                continue
            if channel2.name() == channel_name:
                return True
        elif isinstance(item, plot_item_model.ScatterItem):
            channel2 = item.xChannel()
            if channel2 is not None:
                if channel2.name() == channel_name:
                    return True
            channel2 = item.yChannel()
            if channel2 is not None:
                if channel2.name() == channel_name:
                    return True

    return False


def isAnyItemValid(plot: plot_model.Plot) -> bool:
    """Returns True if any item is valid, and then could be displayed.

    Basically it checks if the plot is not empty"""
    for item in plot.items():
        if item.isValid():
            return True
    return False


def isAnyValue(plot: plot_model.Plot) -> bool:
    """Returns True if any value channel is selected, and then could be displayed.

    Basically it checks if the plot is not empty"""
    for item in plot.items():
        if isinstance(item, plot_item_model.CurveItem):
            if item.yChannel() is not None:
                return True
        elif isinstance(item, plot_item_model.ScatterItem):
            if item.valueChannel() is not None:
                return True
    return False


def isChannelDisplayedAsValue(plot: plot_model.Plot, channel: scan_model.Channel):
    if channel is None:
        return False
    channel_name = channel.name()
    for item in plot.items():
        if isinstance(item, plot_item_model.CurveItem):
            channel2 = item.yChannel()
            if channel2 is None:
                continue
            if channel2.name() == channel_name:
                return True
        elif isinstance(item, plot_item_model.McaItem):
            channel2 = item.mcaChannel()
            if channel2 is None:
                continue
            if channel2.name() == channel_name:
                return True
        elif isinstance(item, plot_item_model.ScatterItem):
            channel2 = item.valueChannel()
            if channel2 is None:
                continue
            if channel2.name() == channel_name:
                return True
        elif isinstance(item, plot_item_model.ImageItem):
            channel2 = item.imageChannel()
            if channel2 is None:
                continue
            if channel2.name() == channel_name:
                return True

    return False


def getFastChannel(
    channel1: scan_model.Channel, channel2: scan_model.Channel
) -> scan_model.Channel | None:
    """Returns the fast channel from input channels.

    If no one is a fast channel, None is returned
    """
    for channel in [channel1, channel2]:
        m = channel.metadata()
        if m is not None:
            if m.axisId == 0:
                return channel
    return None


def getColormapFromItem(
    item: plot_model.Item,
    style: style_model.Style,
    defaultColormap: colors.Colormap | None = None,
) -> colors.Colormap:
    """Returns the colormap from an item, taking care of the cache."""
    colormap = item.colormap()
    if colormap is None:
        if defaultColormap is None:
            # Store the colormap
            # FIXME as the colormap is exposed to the colormap dialog
            # it have to be synchronized to the item style
            colormap = colors.Colormap(style.colormapLut)
        else:
            colormap = defaultColormap
        item.setColormap(colormap)
    else:
        if colormap is defaultColormap:
            # The default colormap must not be changed
            pass
        else:
            colormap.setName(style.colormapLut)
    return colormap


def updateDisplayedChannelNames(
    plot: plot_model.Plot,
    scan: scan_model.Scan,
    channel_names: list[str],
    ignoreMissingChannels=False,
):
    """Helper to update displayed channels without changing the axis."""

    used_items, unneeded_items, expected_new_channels = filterUsedDataItems(
        plot, channel_names
    )

    if isinstance(plot, plot_item_model.ScatterPlot):
        kind = "scatter"
    elif isinstance(plot, plot_item_model.CurvePlot):
        kind = "curve"
    else:
        raise ValueError("This plot type %s is not supported" % type(plot))

    remaining_items = set(unneeded_items)
    with plot.transaction():
        for item in used_items:
            item.setVisible(True)
        if len(expected_new_channels) > 0:
            for channel_name in expected_new_channels:
                channel = scan.getChannelByName(channel_name)
                if channel is None:
                    if ignoreMissingChannels:
                        continue
                    # Create an item pointing to a non existing channel
                    channelRef = plot_model.ChannelRef(plot, channel_name)
                    if kind == "scatter":
                        item = plot_item_model.ScatterItem(plot)
                        item.setValueChannel(channelRef)
                    elif kind == "curve":
                        item = plot_item_model.CurveItem(plot)
                        item.setYChannel(channelRef)
                    plot.addItem(item)
                else:
                    if kind == "scatter":
                        item, updated = createScatterItem(plot, channel)
                        if updated:
                            remaining_items.discard(item)
                    elif kind == "curve":
                        # FIXME: We have to deal with left/right axis
                        # FIXME: Item can't be added without topmaster
                        item, updated = createCurveItem(
                            plot, channel, yAxis="left", allowIndexed=True
                        )
                        if updated:
                            remaining_items.discard(item)
                    else:
                        assert False
                item.setVisible(True)
        for item in remaining_items:
            removeItemAndKeepAxes(plot, item)


def reorderDisplayedItems(
    plot: plot_model.Plot,
    channel_names: list[str],
):
    """Reorder the items to follow the displayed channel list"""
    used_items, unneeded_items, _expected_new_channels = filterUsedDataItems(
        plot, channel_names
    )
    with plot.transaction():
        for item in unneeded_items:
            plot.removeItem(item)
        for item in used_items:
            plot.removeItem(item)
            plot.addItem(item)
        for item in unneeded_items:
            plot.addItem(item)


def copyItemsFromChannelNames(
    sourcePlot: plot_model.Plot,
    destinationPlot: plot_model.Plot,
    scan: scan_model.Scan | None = None,
):
    """Copy from the source plot the item which was setup into the destination plot.

    If the destination plot do not contain the expected items, the scan is used
    to know if they are available, and are then created. Else source item is
    skipped.
    """
    if not isinstance(sourcePlot, plot_item_model.CurvePlot):
        raise TypeError("Only available for curve plot. Found %s" % type(sourcePlot))
    if not isinstance(destinationPlot, type(sourcePlot)):
        raise TypeError(
            "Both plots must have the same type. Found %s" % type(destinationPlot)
        )

    availableItems = {}
    for item in sourcePlot.items():
        if isinstance(item, plot_item_model.CurveItem):
            channel = item.yChannel()
            if channel is None:
                continue
            name = channel.name()
            availableItems[name] = item

    with destinationPlot.transaction():
        for item in destinationPlot.items():
            if isinstance(item, plot_item_model.CurveItem):
                channel = item.yChannel()
                if channel is None:
                    continue
                name = channel.name()
                sourceItem = availableItems.pop(name, None)
                if sourceItem is not None:
                    copyItemConfig(sourceItem, item)

        if len(availableItems) > 0 and scan is not None:
            # Some items could be created
            for name, sourceItem in availableItems.items():
                channel = scan.getChannelByName(name)
                if channel is None:
                    # Not part of the scan
                    continue

                item, _updated = createCurveItem(
                    destinationPlot,
                    channel,
                    yAxis=sourceItem.yAxis(),
                    allowIndexed=True,
                )
                copyItemConfig(sourceItem, item)


def copyItemsFromRoiNames(
    sourcePlot: plot_model.Plot, destinationPlot: plot_model.Plot
):
    """Copy from the source plot the item which was setup into the destination plot.

    ROIs already contained in the destination plot will be setup the same way it is
    done for the source plot.
    """
    availableItems = {}
    for item in sourcePlot.items():
        if isinstance(item, plot_item_model.RoiItem):
            name = item.roiName()
            if name is None:
                continue
            availableItems[name] = item

    with destinationPlot.transaction():
        for item in destinationPlot.items():
            if isinstance(item, plot_item_model.RoiItem):
                name = item.roiName()
                if name is None:
                    continue
                sourceItem = availableItems.pop(name, None)
                if sourceItem is not None:
                    copyItemConfig(sourceItem, item)


def copyItemConfig(sourceItem: plot_model.Item, destinationItem: plot_model.Item):
    """Copy the configuration and the item tree from a source item to a
    destination item"""
    if isinstance(sourceItem, plot_item_model.CurveItem) and isinstance(
        destinationItem, plot_item_model.CurveItem
    ):
        destinationItem.setVisible(sourceItem.isVisible())
        destinationItem.setYAxis(sourceItem.yAxis())

        sourceToDest = {}
        sourceToDest[sourceItem] = destinationItem

        destinationPlot = destinationItem.plot()
        assert destinationPlot is not None
        plot = sourceItem.plot()
        assert plot is not None
        for item in plot.items():
            if item.isChildOf(sourceItem):
                newItem = item.copy(destinationPlot)
                newItem.setParent(destinationPlot)
                destinationSource = sourceToDest[item.source()]
                newItem.setSource(destinationSource)
                destinationPlot.addItem(newItem)
                sourceToDest[item] = newItem

    elif isinstance(sourceItem, plot_item_model.RoiItem) and isinstance(
        destinationItem, plot_item_model.RoiItem
    ):
        destinationItem.setVisible(sourceItem.isVisible())
    else:
        raise TypeError(
            "No copy available from item type %s to %s"
            % (type(sourceItem), type(destinationItem))
        )


def replaceItem(fromItem: plot_model.Item, toItem: plot_model.Item):
    """Replace an item from the plot by another one.

    The source have to be part of the plot and the destination have to a new item.

    The sub items from the source are recreated.

    FIXME: This could be replaced by a much faster function, part of the plot
    model. But `Item.setSource` have to properly handle the update.
    """
    plotModel = fromItem.plot()
    assert plotModel is not None
    with plotModel.transaction():
        plotModel.addItem(toItem)
        copyItemConfig(fromItem, toItem)
        plotModel.removeItem(fromItem)


def updateXAxis(
    plotModel: plot_model.Plot,
    scan: scan_model.Scan,
    topMaster: scan_model.Device,
    xChannelName: str | None = None,
    xIndex: bool = False,
):
    """Update the x-axis used by a plot

    Arguments:
        xChannelName: If set, Name of the channel to use as X-axis
        xIndex: If true, use Y data index as X-axis
    """
    assert xChannelName is not None or xIndex
    # Reach all plot items from this top master
    curves = reachAllCurveItemFromDevice(plotModel, scan, topMaster)

    if len(curves) == 0:
        with plotModel.transaction():
            items = plotModel.items()
            plotModel.clear()
            newItem = plot_item_model.CurveItem(plotModel)
            if xChannelName is not None:
                # Create an item to store the x-value
                xChannel = plot_model.ChannelRef(plotModel, xChannelName)
            elif xIndex:
                xChannel = plot_model.XIndexChannelRef(plotModel, None)
            else:
                xChannel = None
            newItem.setXChannel(xChannel)
            plotModel.addItem(newItem)
            # Restore everything but curves
            for item in items:
                if not isinstance(item, plot_item_model.CurveItem):
                    plotModel.addItem(item)
    else:
        # Update the x-channel of all this curves
        with plotModel.transaction():
            for curve in curves:
                if xChannelName:
                    xChannel = plot_model.ChannelRef(curve, xChannelName)
                else:
                    xChannel = plot_model.XIndexChannelRef(curve, None)
                curve.setXChannel(xChannel)


def updateXAxisPerMasters(
    scan: scan_model.Scan,
    plotModel: plot_item_model.CurvePlot,
    xaxis: dict[scan_model.Device, str],
):
    """Update the x-axis of a plot from the result of `getMostUsedXChannelPerMasters`

    If the devices are not part of the right scan, the top master is reached from
    the channel name.
    """
    if list(set(xaxis.values())) == [INDEX_REF]:
        topMasters = set([d.topMaster() for d in scan.devices()])
        for topMaster in topMasters:
            updateXAxis(plotModel, scan, topMaster, xIndex=True)
        return

    for topMaster, xChannelName in xaxis.items():
        if topMaster.scan() is not scan:
            xChannel = scan.getChannelByName(xChannelName)
            if xChannel is None:
                continue
            topMaster = xChannel.device().topMaster()
        if xChannelName == INDEX_REF:
            updateXAxis(plotModel, scan, topMaster, xIndex=True)
        else:
            updateXAxis(plotModel, scan, topMaster, xChannelName, xIndex=False)


def selectSomethingToPlotIfNone(
    plotModel: plot_item_model.CurvePlot, scan: scan_model.Scan
):
    """If nothing is displayed select one of the channels"""
    if plotModel is None:
        return
    if isAnyValue(plotModel):
        return

    if len(plotModel.items()) > 0:
        item = plotModel.items()[0]
        xChannel = item.xChannel()
        if isinstance(xChannel, plot_model.XIndexChannelRef):
            xAxisName = None
        else:
            xAxisName = None if xChannel is None else xChannel.name()
    else:
        xAxisName = None

    channels = [scan.getChannelByName(n) for n in scan.getChannelNames()]
    counters = [c for c in channels if c.type() == scan_model.ChannelType.COUNTER]
    if len(counters) == 0:
        return

    def score(channel):
        channelName = channel.name()
        score = 0
        if channelName == xAxisName:
            # Try not to display selected x-axis
            score += 10
        if channelName.startswith("axis:"):
            # Try not to display axis
            score += 1
        else:
            if channel.unit() == "s":
                # Try not to display the time
                score += 1
        return score

    counters = sorted(counters, key=score)
    channel = counters[0]
    if channel is not None:
        updateDisplayedChannelNames(plotModel, scan, [channel.name()])


def _getChannelNamesByFilter(
    scan: scan_model.Scan,
    master: bool,
    topMaster: scan_model.Device | None = None,
    dim: int | None = None,
) -> list[str]:
    result: list[str] = []
    for device in scan.devices():
        if topMaster is not None and not device.isChildOf(topMaster):
            continue
        for channel in device.channels():
            if dim is not None and channel.metadata().dim != dim:
                continue
            result.append(channel.name())

    return result


def isSame(scan1: scan_model.Scan | None, scan2: scan_model.Scan | None) -> bool:
    """Returns true if both scans have the same structure

    This function check the type of the scan and it's masters
    """
    if scan1 is scan2:
        # Also true when both are None
        return True
    if scan1 is None or scan2 is None:
        return False
    scan_info1 = scan1.scanInfo()
    scan_info2 = scan2.scanInfo()
    type1 = scan_info1.get("type", None)
    type2 = scan_info2.get("type", None)
    if type1 != type2:
        return False
    masters1 = _getChannelNamesByFilter(scan1, master=True)
    masters2 = _getChannelNamesByFilter(scan2, master=True)
    return masters1 == masters2
