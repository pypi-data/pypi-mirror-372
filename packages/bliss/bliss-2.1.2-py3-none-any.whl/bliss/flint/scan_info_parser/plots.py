# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.
"""
Provides helper to read scan_info.
"""
from __future__ import annotations
from typing import NamedTuple
from collections.abc import Iterator

import logging
from ..model import scan_model
from ..model import plot_model
from ..model import plot_item_model
from ..helper import model_helper


_logger = logging.getLogger(__name__)


def _get_device_from_channel(channel_name: str) -> str:
    elements = channel_name.split(":")
    return elements[0]


def _get_channels(
    scan: scan_model.Scan, parent: scan_model.Device, master: bool, dim: int
) -> list[str]:
    result: list[str] = []
    for device in scan.devices():
        if not device.isChildOf(parent):
            continue
        if master ^ device.isMaster():
            continue
        for channel in device.channels():
            if channel.metadata().dim != dim:
                continue
            result.append(channel.name())

    return result


def _get_unit(scan: scan_model.Scan, channel_name: str) -> str | None:
    channel = scan.getChannelByName(channel_name)
    if channel is None:
        return None
    return channel.unit()


def _iter_chains(scan: scan_model.Scan) -> Iterator[scan_model.Device]:
    """Iter the top masters of the scan."""
    scan_info = scan.scanInfo()
    acquisition_chain = scan_info.get("acquisition_chain", {})
    assert isinstance(acquisition_chain, dict)
    for chain_name in acquisition_chain.keys():
        assert isinstance(chain_name, str)
        chain = scan.findDeviceByName(
            chain_name, devtype=scan_model.DeviceType.VIRTUAL_CHAIN
        )
        assert chain is not None
        yield chain


def _select_default_counter(scan: scan_model.Scan, plot: plot_model.Plot):
    """Select a default counter if needed."""
    for item in plot.items():
        if isinstance(item, plot_item_model.ScatterItem):
            if item.valueChannel() is None:
                # If there is an axis but no value
                # Pick a value
                axisChannelRef = item.xChannel()
                if axisChannelRef is None:
                    axisChannelRef = item.yChannel()
                if axisChannelRef is None:
                    continue
                axisChannel = axisChannelRef.channel(scan)
                if axisChannel is None:
                    continue

                scatterData = scan.getScatterDataByChannel(axisChannel)
                names: list[str]
                if scatterData is not None:
                    counters = scatterData.counterChannels()
                    names = [c.name() for c in counters]
                else:
                    names = []
                    for chain in _iter_chains(scan):
                        counter_scalars = _get_channels(
                            scan, chain, master=False, dim=0
                        )
                        names.extend(counter_scalars)
                if len(names) > 0:
                    # Try to use a default counter which is not an elapse time
                    quantityNames = [n for n in names if _get_unit(scan, n) != "s"]
                    if len(quantityNames) > 0:
                        names = quantityNames
                    channelRef = plot_model.ChannelRef(plot, names[0])
                    item.setValueChannel(channelRef)


class DisplayExtra(NamedTuple):
    displayed_channels: list[str] | None
    """Enforced list of channels to display for this specific scan"""

    plotselect: list[str] | None
    """List of name selected by plot select"""

    plotselect_time: int | None
    """Time from `time.time()` of the last plotselect"""


def parse_display_extra(scan_info: dict) -> DisplayExtra:
    """Return the list of the displayed channels stored in the scan"""

    def parse_optional_list_of_string(data, name):
        """Sanitize data from scan_info protocol"""
        if data is None:
            return None

        if not isinstance(data, list):
            _logger.warning("%s is not a list: Key ignored", name)
            return None

        if not all([isinstance(i, str) for i in data]):
            _logger.warning("%s must only contains strings: Key ignored", name)
            return None

        return data

    display_extra = scan_info.get("display_extra", None)
    if display_extra is not None:
        raw = display_extra.get("displayed_channels", None)
        displayed_channels = parse_optional_list_of_string(
            raw, "display_extra.displayed_channels"
        )
        raw = display_extra.get("plotselect", None)
        plotselect = parse_optional_list_of_string(raw, "display_extra.plotselect")
        plotselect_time = display_extra.get("plotselect_time", None)
    else:
        displayed_channels = None
        plotselect = None
        plotselect_time = None
    return DisplayExtra(displayed_channels, plotselect, plotselect_time)


def plot_priority(scan: scan_model.Scan, plot: plot_model.Plot) -> int:
    """Guess a priority for a plot

    The default returned value is 50

    For now it is only used to reduce the priority of some plots
    which dosn't contain any meaningful information
    """
    if isinstance(plot, (plot_item_model.CurvePlot, plot_item_model.ScatterPlot)):
        containsSomething = False
        for item in plot.items():
            if isinstance(item, plot_item_model.CurveItem):
                channelRef = item.yChannel()
                if channelRef is not None:
                    channel = channelRef.channel(scan)
                    if channel is not None:
                        unit = channel.unit()
                        if unit != "s":
                            containsSomething = True
                            break
            if isinstance(item, plot_item_model.ScatterItem):
                channelRef = item.valueChannel()
                if channelRef is not None:
                    channel = channelRef.channel(scan)
                    if channel is not None:
                        if channel.unit() != "s":
                            containsSomething = True
                            break
        if not containsSomething:
            counldContainSomething = False
            for channel in scan.channels():
                if channel.ndim != 1:
                    continue
                unit = channel.unit()
                if unit == "s":
                    continue
                counldContainSomething = True
                break
            if not counldContainSomething:
                return 0
    return 50


def _reorder_plots(
    scan: scan_model.Scan, plots: list[plot_model.Plot]
) -> list[plot_model.Plot]:
    base_priorities: dict[plot_model.Plot, float] = {
        p: len(plots) - e for e, p in enumerate(plots)
    }

    def get_priority(plot):
        return plot_priority(scan, plot), base_priorities[plot]

    return sorted(plots, key=get_priority, reverse=True)


def create_plot_model(
    scan_info: dict, scan: scan_model.Scan | None = None
) -> list[plot_model.Plot]:
    """Create plot models from a scan_info.

    If a `plots` key exists from the `scan_info`, scatter and curve plots will
    created following this description. Else, plots will be inferred from the
    acquisition chain.

    Finally the selection is updated using `display_extra` field. This should
    be removed a one point.

    Special kind of plots depending on devices and data kind, like Lima, MCAs
    and 1D data will always be inferred.
    """
    if scan is None:
        from .scans import ScanModelReader

        reader = ScanModelReader(scan_info)
        scan = reader.parse()

    if "plots" in scan_info:
        plots = read_plot_models(scan_info)
        for plot in plots:
            _select_default_counter(scan, plot)

        def contains_default_plot_kind(plots, plot):
            """Returns true if the list contain a default plot for this kind."""
            for p in plots:
                if p.hasSameTarget(plot):
                    return True
            return False

        has_one_dim = (
            len([p for p in plots if isinstance(p, plot_item_model.OneDimDataPlot)]) > 0
        )

        aq_plots = infer_plot_models(scan)
        for plot in aq_plots:
            if isinstance(
                plot, (plot_item_model.CurvePlot, plot_item_model.ScatterPlot)
            ):
                # This kind of plots are already constrained by the `plots` key
                continue
            if has_one_dim and isinstance(plot, plot_item_model.OneDimDataPlot):
                # This kind of plots are already constrained by the `plots` key
                continue
            if not contains_default_plot_kind(plots, plot):
                plots.append(plot)
    else:
        plots = infer_plot_models(scan)

    def filter_with_scan_content(channel_names, scan):
        if scan is None:
            return channel_names
        if channel_names is None:
            return channel_names
        # Filter selection by available channels
        intersection = set(channel_names) & set(scan.getChannelNames())
        if len(channel_names) != len(intersection):
            # Remove missing without breaking the order
            for name in list(channel_names):
                if name not in intersection:
                    channel_names.remove(name)
                    _logger.warning(
                        "Skip display of channel '%s' from scan_info. Not part of the scan",
                        name,
                    )
            if len(channel_names) == 0:
                channel_names = None
        return channel_names

    display_extra = parse_display_extra(scan_info)
    displayed_channels = filter_with_scan_content(
        display_extra.displayed_channels, scan
    )

    for plot in plots:
        channel_names = None
        if isinstance(plot, plot_item_model.CurvePlot):
            if displayed_channels is None:
                channel_names = filter_with_scan_content(display_extra.plotselect, scan)
                plot.tagPlotselectEdit()
            else:
                channel_names = displayed_channels
        elif isinstance(plot, plot_item_model.ScatterPlot):
            if displayed_channels:
                channel_names = displayed_channels
        if channel_names:
            model_helper.updateDisplayedChannelNames(plot, scan, channel_names)

    plots = _reorder_plots(scan, plots)

    return plots


def _read_scatter_plot(plot_description: dict) -> plot_model.Plot:
    """Read a scatter plot definition from the scan_info"""
    plot = plot_item_model.ScatterPlot()

    name = plot_description.get("name", None)
    if name is not None:
        plot.setName(name)

    items = plot_description.get("items", None)
    if not isinstance(items, list):
        _logger.warning("'items' not using the right type. List expected. Ignored.")
        items = []

    for item_description in items:
        kind = item_description.get("kind", None)
        if kind == "scatter":
            item = plot_item_model.ScatterItem(plot)

            xname = item_description.get("x", None)
            if xname is not None:
                x_channel = plot_model.ChannelRef(plot, xname)
                item.setXChannel(x_channel)
            yname = item_description.get("y", None)
            if yname is not None:
                y_channel = plot_model.ChannelRef(plot, yname)
                item.setYChannel(y_channel)
            valuename = item_description.get("value", None)
            if valuename is not None:
                value_channel = plot_model.ChannelRef(plot, valuename)
                item.setValueChannel(value_channel)
            plot.addItem(item)
        else:
            _logger.warning("Item 'kind' %s unsupported. Item ignored.", kind)
    return plot


def _read_curve_plot(plot_description: dict) -> plot_model.Plot:
    """Read a curve plot definition from the scan_info"""
    plot = plot_item_model.CurvePlot()

    name = plot_description.get("name", None)
    if name is not None:
        plot.setName(name)

    items = plot_description.get("items", None)
    if not isinstance(items, list):
        _logger.warning("'items' not using the right type. List expected. Ignored.")
        items = []

    for item_description in items:
        kind = item_description.get("kind", None)
        if kind == "curve":
            item = plot_item_model.CurveItem(plot)

            xname = item_description.get("x", None)
            if xname is not None:
                x_channel = plot_model.ChannelRef(plot, xname)
                item.setXChannel(x_channel)
            yname = item_description.get("y", None)
            if yname is not None:
                y_channel = plot_model.ChannelRef(plot, yname)
                item.setYChannel(y_channel)
            y_axis = item_description.get("y_axis", None)
            if y_axis in ("left", "right"):
                item.setYAxis(y_axis)
            plot.addItem(item)
        else:
            _logger.warning("Item 'kind' %s unsupported. Item ignored.", kind)
    return plot


def _read_1d_plot(plot_description: dict) -> plot_model.Plot:
    """Read a 1D plot definition from the scan_info"""
    plot = plot_item_model.OneDimDataPlot()

    name = plot_description.get("name", None)
    if name is not None:
        plot.setName(name)

    items = plot_description.get("items", None)
    if not isinstance(items, list):
        _logger.warning("'items' not using the right type. List expected. Ignored.")
        items = []

    xaxis_channel_name = plot_description.get("x", None)

    for item_description in items:
        kind = item_description.get("kind", None)
        if kind == "curve":
            item = plot_item_model.CurveItem(plot)

            yname = item_description.get("y", None)
            item = plot_item_model.CurveItem(plot)
            y_channel = plot_model.ChannelRef(plot, yname)
            item.setYChannel(y_channel)
            if xaxis_channel_name is not None:
                xchannel = plot_model.ChannelRef(plot, xaxis_channel_name)
            else:
                xchannel = item = plot_model.XIndexChannelRef(plot)
            item.setXChannel(xchannel)
            plot.addItem(item)
        else:
            _logger.warning("Item 'kind' %s unsupported. Item ignored.", kind)
    return plot


def _read_table_plot(plot_description: dict) -> plot_model.Plot:
    """Read a table plot definition from the scan_info"""
    plot = plot_item_model.TablePlot()

    name = plot_description.get("name", None)
    if name is not None:
        plot.setName(name)
    return plot


def read_plot_models(scan_info: dict) -> list[plot_model.Plot]:
    """Read description of plot models from a scan_info"""
    result: list[plot_model.Plot] = []

    plots = scan_info.get("plots", None)
    if not isinstance(plots, list):
        return []

    for plot_description in plots:
        if not isinstance(plot_description, dict):
            _logger.warning("Plot description is not a dict. Skipped.")
            continue

        kind = plot_description.get("kind", None)
        if kind == "scatter-plot":
            plot = _read_scatter_plot(plot_description)
        elif kind == "curve-plot":
            plot = _read_curve_plot(plot_description)
        elif kind == "1d-plot":
            plot = _read_1d_plot(plot_description)
        elif kind == "table-plot":
            plot = _read_table_plot(plot_description)
        else:
            _logger.warning("Kind %s unsupported. Skipped.", kind)
            continue

        result.append(plot)

    return result


def _infer_default_curve_plot(
    scan: scan_model.Scan, have_scatter: bool
) -> plot_model.Plot | None:
    """Create a curve plot by inferring the acquisition chain content.

    If there is a scatter as main plot, try to use a time counter as axis.
    """
    plot = plot_item_model.CurvePlot()
    for chain in _iter_chains(scan):
        scalars = _get_channels(scan, chain, dim=0, master=False)
        master_channels = _get_channels(scan, chain, dim=0, master=True)

        if have_scatter:
            # In case of scatter the curve plot have to plot the time in x
            # Masters in y1 and the first value in y2

            timer: str | None
            for timer in scalars:
                if timer in master_channels:
                    # skip the masters
                    continue
                if _get_unit(scan, timer) != "s":
                    # skip non time base
                    continue
                break
            else:
                timer = None
            if timer is None:
                # NOTE: New code, elapse time is supposed to be part of a master
                #       The previous code sounds weird
                for timer in master_channels:
                    if _get_unit(scan, timer) != "s":
                        # skip non time base
                        continue
                    break
            else:
                timer = None

            scalar: str | None
            for scalar in scalars:
                if scalar in master_channels:
                    # skip the masters
                    continue
                if _get_unit(scan, scalar) == "s":
                    # skip the time base
                    continue
                break
            else:
                scalar = None

            if timer is not None:
                if scalar is not None:
                    item = plot_item_model.CurveItem(plot)
                    x_channel = plot_model.ChannelRef(plot, timer)
                    y_channel = plot_model.ChannelRef(plot, scalar)
                    item.setXChannel(x_channel)
                    item.setYChannel(y_channel)
                    item.setYAxis("left")
                    plot.addItem(item)

                for channel_name in master_channels:
                    item = plot_item_model.CurveItem(plot)
                    x_channel = plot_model.ChannelRef(plot, timer)
                    y_channel = plot_model.ChannelRef(plot, channel_name)
                    item.setXChannel(x_channel)
                    item.setYChannel(y_channel)
                    item.setYAxis("right")
                    plot.addItem(item)
            else:
                # The plot will be empty
                pass
        else:
            if len(master_channels) > 0 and master_channels[0].startswith("axis:"):
                master_channel0 = master_channels[0]
                master_channel_unit = _get_unit(scan, master_channel0)
                is_motor_scan = master_channel_unit != "s"
            else:
                is_motor_scan = False

            for channel_name in scalars:
                if is_motor_scan and _get_unit(scan, channel_name) == "s":
                    # Do not display base time for motor based scan
                    continue

                item = plot_item_model.CurveItem(plot)
                data_channel = plot_model.ChannelRef(plot, channel_name)

                master_channel: plot_model.ChannelRef | None
                if len(master_channels) == 0:
                    master_channel = None
                else:
                    master_channel = plot_model.ChannelRef(plot, master_channels[0])

                item.setXChannel(master_channel)
                item.setYChannel(data_channel)
                plot.addItem(item)
                # Only display the first counter
                break
    return plot


def _infer_default_scatter_plot(scan: scan_model.Scan) -> list[plot_model.Plot]:
    """Create a set of scatter plots according to the content of acquisition
    chain"""
    plots: list[plot_model.Plot] = []
    for chain in _iter_chains(scan):
        plot = plot_item_model.ScatterPlot()
        scalars = _get_channels(scan, chain, dim=0, master=False)
        axes_channels = _get_channels(scan, chain, dim=0, master=True)

        # Reach the first scalar which is not a time unit
        scalar: str | None
        for scalar in scalars:
            if scalar in axes_channels:
                # skip the masters
                continue
            if _get_unit(scan, scalar) == "s":
                # skip the time base
                continue
            break
        else:
            scalar = None

        if len(axes_channels) >= 1:
            x_channel = plot_model.ChannelRef(plot, axes_channels[0])
        else:
            x_channel = None

        if len(axes_channels) >= 2:
            y_channel = plot_model.ChannelRef(plot, axes_channels[1])
        else:
            y_channel = None

        if scalar is not None:
            data_channel = plot_model.ChannelRef(plot, scalar)
        else:
            data_channel = None

        item = plot_item_model.ScatterItem(plot)
        item.setXChannel(x_channel)
        item.setYChannel(y_channel)
        item.setValueChannel(data_channel)
        plot.addItem(item)
        plots.append(plot)

    return plots


def _initialize_image_plot_from_device(
    device: scan_model.Device, channel: scan_model.Channel
) -> tuple[plot_model.Plot | None, bool]:
    """Initialize an ImagePlot from from a device and it's channel"""
    if channel.type() not in [
        scan_model.ChannelType.IMAGE,
        scan_model.ChannelType.IMAGE_C_Y_X,
    ]:
        return None, False

    if device.type() == scan_model.DeviceType.LIMA2:
        is_default = channel.name().endswith(":frame")
    elif device.type() == scan_model.DeviceType.LIMA:
        is_default = channel.name().endswith(":image")
    else:
        is_default = False

    plot = plot_item_model.ImagePlot()
    if is_default:
        stable_name = device.name()
        plot.setDeviceName(stable_name)
    else:
        plot.setDeviceName(channel.name())

    image_channel = plot_model.ChannelRef(plot, channel.name())
    item = plot_item_model.ImageItem(plot)
    item.setImageChannel(image_channel)
    plot.addItem(item)

    if is_default:
        if device.type() in [
            scan_model.DeviceType.LIMA,
            scan_model.DeviceType.LIMA2,
        ]:
            for sub_device in device.devices():
                if sub_device.type() == scan_model.DeviceType.LIMA_SUB_DEVICE:
                    for roi_device in sub_device.devices():
                        if roi_device.type() != scan_model.DeviceType.VIRTUAL_ROI:
                            continue
                        roi_item = plot_item_model.RoiItem(plot)
                        roi_item.setDeviceName(roi_device.fullName())
                        plot.addItem(roi_item)

    return plot, is_default


def infer_plot_models(scan: scan_model.Scan) -> list[plot_model.Plot]:
    """Infer description of plot models from a scan

    - Dedicated default plot is created for 0D channels according to the kind
      of scan. It could be:

       - ct plot
       - curve plot
       - scatter plot

    - A dedicated image plot is created per lima detectors
    - A dedicated MCA plot is created per mca detectors
    - Remaining 2D channels are displayed as an image widget
    - Remaining 1D channels are displayed as a 1D plot
    """
    result: list[plot_model.Plot] = []

    default_plot = None
    scan_info = scan.scanInfo()

    acquisition_chain = scan_info.get("acquisition_chain", {})
    assert isinstance(acquisition_chain, dict)
    if isinstance(scan, scan_model.ScanGroup):
        # Make sure groups does not generate any plots
        return []

    # ct / curve / scatter
    plot: plot_model.Plot | None = None

    if scan_info.get("type", None) == "ct":
        plot = plot_item_model.ScalarPlot()
        result.append(plot)
    else:
        have_scalar = False
        have_scatter = False
        for chain in _iter_chains(scan):
            scalars = _get_channels(scan, chain, dim=0, master=False)
            if len(scalars) > 0:
                have_scalar = True
            if scan_info.get("data_dim", 1) == 2 or scan_info.get("dim", 1) == 2:
                have_scatter = True

        if have_scalar:
            plot = _infer_default_curve_plot(scan, have_scatter)
            if plot is not None:
                result.append(plot)
                if not have_scalar:
                    default_plot = plot
        if have_scatter:
            plots = _infer_default_scatter_plot(scan)
            if len(plots) > 0:
                result.extend(plots)
                if default_plot is None:
                    default_plot = plots[0]

    # MCA devices

    for device in scan.devices():
        if device.type() not in [
            scan_model.DeviceType.MCA,
            scan_model.DeviceType.MOSCA,
            scan_model.DeviceType.LIMA,
        ]:
            continue

        plot = None

        def parse_channels(d: scan_model.Device):
            nonlocal plot, default_plot, device
            for channel in d.channels():
                if channel.type() not in [
                    scan_model.ChannelType.SPECTRUM,
                    scan_model.ChannelType.SPECTRUM_D_C,
                ]:
                    continue

                if plot is None:
                    plot = plot_item_model.McaPlot()
                    plot.setDeviceName(device.name())
                    if default_plot is None:
                        default_plot = plot

                channelRef = plot_model.ChannelRef(plot, channel.name())
                item = plot_item_model.McaItem(plot)
                item.setMcaChannel(channelRef)

                plot.addItem(item)

        parse_channels(device)
        for detector in device.devices():
            if detector.type() != scan_model.DeviceType.VIRTUAL_MCA_DETECTOR:
                continue
            parse_channels(detector)

        if plot is not None:
            result.append(plot)

    # Other 1D devices

    for device in scan.devices():
        if device.type() in [scan_model.DeviceType.MCA, scan_model.DeviceType.MOSCA]:
            continue
        master = device.master()
        if master is not None and master.type() in [
            scan_model.DeviceType.MCA,
            scan_model.DeviceType.MOSCA,
        ]:
            continue
        device_name = device.name()
        device_metadata = device.metadata().info.get("metadata", {})
        assert isinstance(device_metadata, dict)

        xaxis_channel_name = device_metadata.get("xaxis_channel", None)
        xaxis_array = device_metadata.get("xaxis_array", None)
        if xaxis_channel_name is not None and xaxis_array is not None:
            _logger.warning(
                "Both xaxis_array and xaxis_channel are defined. xaxis_array will be ignored"
            )
            xaxis_array = None

        if xaxis_array is not None:
            xaxis_channel_name = f"{device_name}:#:xaxis_array"
            xaxis_array = None

        plot = None

        for channel in device.channels():
            if channel.type() != scan_model.ChannelType.VECTOR:
                continue

            if channel.name() == xaxis_channel_name:
                # remove the axis from the selection
                continue

            if plot is None:
                plot = plot_item_model.OneDimDataPlot()

                if device_name == "roi_collection":
                    plot.setDeviceName(device.stableName())
                    plot.setPlotTitle(f"{device.name()} (roi collection)")
                elif device_name == "roi_profile":
                    plot.setDeviceName(device.stableName())
                    plot.setPlotTitle(f"{device.name()} (roi profiles)")
                else:
                    plot.setDeviceName(device.stableName())
                    plot.setPlotTitle(device.name())
                if default_plot is None:
                    default_plot = plot

            channelRef = plot_model.ChannelRef(plot, channel.name())

            item = plot_item_model.CurveItem(plot)
            item.setYChannel(channelRef)
            if xaxis_channel_name is not None:
                xchannel = plot_model.ChannelRef(plot, xaxis_channel_name)
            else:
                xchannel = plot_model.XIndexChannelRef(plot)
            item.setXChannel(xchannel)

            plot.addItem(item)

        if plot is not None:
            result.append(plot)

    # Image plot

    for device in scan.devices():
        plot = None
        for channel in device.channels():
            plot, is_default = _initialize_image_plot_from_device(device, channel)
            if plot is not None:
                result.append(plot)
                if is_default and default_plot is None:
                    default_plot = plot

    # Move the default plot on top
    if default_plot is not None:
        result.remove(default_plot)
        result.insert(0, default_plot)

    return result
