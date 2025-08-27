# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

"""Listen the scan data and display in a selected ptpython buffer console """

from __future__ import annotations

import time
import numpy
import shutil
import typing
import numbers
import gevent
from collections.abc import Iterator
from datetime import datetime

from bliss.scanning import scan_events as scan_mdl
from bliss import global_map
from bliss.common.utils import nonblocking_print
from bliss.scanning.scan_display import ScanDisplay
from bliss.scanning.scan_progress import ScanProgress
from bliss.scanning.scan import ScanState
from bliss.shell.formatters.table import IncrementalTable
from bliss.shell.formatters.ansi import GREEN, RED
from bliss.common import timedisplay


def get_decorated_line(msg, width=None, deco="=", head="\n", tail="\n", rdeco=None):
    if not width:
        width = shutil.get_terminal_size().columns

    ldeco = deco
    if rdeco is None:
        rdeco = deco

    diff = width - len(msg)
    if diff > 1:
        ldeco = ldeco * (diff // 2)
        rdeco = rdeco * (diff - diff // 2)

    return "".join([head, ldeco, msg, rdeco, tail])


def _find_obj(name: str):
    """Return the object (Axis or Counter) corresponding to the given name"""
    for axis in global_map.get_axes_iter():
        if axis.name == name:
            return axis
    for cnt in global_map.get_counters_iter():
        if cnt.name == name:
            return cnt


def _find_unit(obj):
    try:
        if isinstance(obj, str):
            # in the form obj.x.y
            obj = _find_obj(obj)
        if hasattr(obj, "unit"):
            return obj.unit
        if hasattr(obj, "config"):
            return obj.config.get("unit")
        if hasattr(obj, "controller"):
            return _find_unit(obj.controller)
    except Exception:
        return


def is_scan_supported(scan_info):
    """Returns true if the scan is supported"""
    if len(scan_info["acquisition_chain"].keys()) != 1:
        return False

    # Skip scans without a type or without a number of points
    scan_type = scan_info.get("type")
    npoints = scan_info.get("npoints")
    if None in [scan_type, npoints]:
        return False

    return True


class ChannelMetadata(typing.NamedTuple):
    """Store metadata about a channel"""

    display_name: str
    unit: typing.Optional[str]


class ScanRenderer:
    """Reach information from scan_info and provide an helper to display
    top down data table view."""

    HEADER = (
        GREEN("** Scan {scan_nb}: {title} **")
        + "\n\n"
        + "   date      : {start_time:%H:%M:%S, %d %h %Y, %Z}\n"
        + "   file      : {filename}\n"
        + "   user      : {user_name}\n"
        + "   session   : {session_name}\n"
        + "   masters   : [ {master_names} ]\n"
        + "   skipped   : [ {not_shown_counters_str} ]\n"
    )

    EXTRA_HEADER = (
        "   unselected: [ {not_selected} ]\n"
        + "                 (use plotselect to customize this list)\n"
    )

    EXTRA_HEADER_2 = "                 (use plotselect to filter this list)\n"

    DEFAULT_WIDTH = 12

    COL_SEP = "|"
    RAW_SEP = "-"
    NO_NAME = "-"

    def __init__(self, scan_info):
        self._displayable_channel_names = None
        self._master_channel_names = []
        self._sorted_channel_names = []
        self._channels_meta = {}
        self._other_channels = None
        self._scan_info = scan_info
        self._tab = None
        self._nb_data_rows = 0
        self._channels_number = None
        self._collect_channels_info(scan_info)
        self._row_data = []

    @property
    def nb_data_rows(self) -> int:
        """Returns rows already received"""
        return self._nb_data_rows

    @property
    def scan_type(self) -> str:
        """Returns the kind of the scan"""
        return self._scan_type

    @property
    def sorted_channel_names(self):
        """List of channel names displayed in columns"""
        return self._sorted_channel_names

    @property
    def displayable_channel_names(self):
        """Channel names from this scans which displayable.

        For example images and MCAs are not displayable.
        """
        return self._displayable_channel_names

    @property
    def master_scalar_channel_names(self):
        """Channel names from this scans which are both masters and scalars."""
        return self._master_channel_names

    def _collect_channels_info(self, scan_info):
        """Collect information from scan_info

        Only the first top master is reached. Others are ignored.
        """
        self._scan_type = scan_info.get("type")

        # only the first top master is used
        top_master, chain_description = next(
            iter(scan_info["acquisition_chain"].items())
        )

        # get the total number of channels
        channels_number = 0
        # get master scalar channels (remove epoch)
        master_scalar_channels = []
        # get scalar channels (remove epoch)
        scalar_channels = []
        # store channels which can't be displayed
        other_channels = []

        for device_name in chain_description["devices"]:
            device_meta = scan_info["devices"][device_name]
            is_master = len(device_meta.get("triggered_devices", [])) > 0
            for channel_name in device_meta.get("channels", []):
                channel_meta = scan_info["channels"].get(channel_name)
                dim = channel_meta.get("dim", 0)
                if dim != 0:
                    other_channels.append(channel_name)
                    continue
                if channel_name != "timer:epoch":
                    if is_master:
                        master_scalar_channels.append(channel_name)
                    else:
                        scalar_channels.append(channel_name)
                channels_number += 1

        self.channels_number = channels_number
        self.other_channels = other_channels

        # get all channels fullname, display names and units
        channel_names = master_scalar_channels + scalar_channels

        channels_meta = {}
        for channel_name, meta in scan_info["channels"].items():
            display_name = meta.get("display_name")
            if display_name is None:
                display_name = channel_name.split(":")[-1]
            unit = meta.get("unit")
            metadata = ChannelMetadata(display_name, unit)
            channels_meta[channel_name] = metadata
        self._channels_meta = channels_meta

        displayable_channels = []

        # First the timer channel if any
        timer_cname = "timer:elapsed_time"
        if timer_cname in channel_names:
            displayable_channels.append(timer_cname)
        # Then masters
        for cname in master_scalar_channels:
            if cname not in displayable_channels:
                displayable_channels.append(cname)
        # Finally the other scalars channels
        for cname in scalar_channels:
            if cname not in displayable_channels:
                displayable_channels.append(cname)

        #  Store the channels contained in the scan_info
        self._master_channel_names = master_scalar_channels
        self._displayable_channel_names = displayable_channels
        self._sorted_channel_names = list(displayable_channels)

    def set_displayed_channels(self, channel_names):
        """Set the list of column names to display.

        The input argument is filtered.
        """
        # Check if the content or the order have changed
        if self._sorted_channel_names != channel_names:
            # Filter it with available channels
            requested_channels = [
                r for r in channel_names if r in self._displayable_channel_names
            ]
            if self._sorted_channel_names != requested_channels:
                self._sorted_channel_names = requested_channels

    def print_table_header(self):
        """Print the header of the data table."""
        if self._scan_type != "ct":
            col_max_width = 40
            labels = self._build_columns_labels()
            self._tab = IncrementalTable(
                labels,
                minwidth=self.DEFAULT_WIDTH,
                maxwidth=col_max_width,
                col_sep=self.COL_SEP,
                lmargin="   ",
            )

            self._tab.set_column_params(0, {"flag": ""})

            # auto adjust columns widths in order to fit the screen
            screen_width = int(shutil.get_terminal_size().columns)
            while (self._tab.full_width + len(self._tab.lmargin) + 1) > screen_width:
                col_max_width -= 1
                self._tab.resize(maxwidth=col_max_width)
                if col_max_width <= self.DEFAULT_WIDTH:
                    break

            self._tab.add_separator(self.RAW_SEP)
            print(str(self._tab))

    def _build_columns_labels(self):
        # Build the columns labels (multi-line with counter and controller names)
        channel_labels = []
        counter_labels = []
        controller_labels = []

        for cname in self._sorted_channel_names:
            channel_meta = self._channels_meta[cname]

            # build the channel label
            if cname == "timer:elapsed_time":
                disp_name = "dt"
            else:
                disp_name = channel_meta.display_name

            # check if the unit must be added to channel label
            unit = channel_meta.unit
            if unit:
                disp_name += f"[{unit}]"

            channel_labels.append(disp_name)

            # try to get controller and counter names
            try:
                ctrl, cnt = cname.split(":")[0:2]
                if cnt == channel_meta.display_name:
                    cnt = self.NO_NAME
                counter_labels.append(cnt)
                controller_labels.append(ctrl)
            except Exception:
                counter_labels.append("")
                controller_labels.append("")

        controller_labels.insert(0, "")
        counter_labels.insert(0, "")  # 'index'
        channel_labels.insert(0, "#")

        return [controller_labels, channel_labels]  # counter_labels useless in table

    def print_scan_header(self):
        """Print the header of a new scan"""
        header = self._build_scan_header()
        print(header)

    def _build_scan_header(self):
        """Build the header to be displayed"""
        # A message about not shown channels
        not_shown_counters_str = ""
        if self._other_channels:
            not_shown_counters_str = ", ".join(self._other_channels)

        master_names = ", ".join(self._master_channel_names)

        header = self.HEADER.format(
            not_shown_counters_str=not_shown_counters_str,
            master_names=master_names,
            scan_nb=self._scan_info["scan_nb"],
            title=self._scan_info["title"],
            filename=self._scan_info["filename"],
            user_name=self._scan_info["user_name"],
            session_name=self._scan_info["session_name"],
            start_time=datetime.fromisoformat(self._scan_info["start_time"]),
        )

        if self._scan_type != "ct":
            header += self._build_extra_scan_header()

        return header

    def _build_extra_scan_header(self):
        not_selected = [
            c
            for c in self._displayable_channel_names
            if c not in self._sorted_channel_names
        ]
        if len(not_selected) == 0:
            return self.EXTRA_HEADER_2

        not_selected = [f"'{RED(f'{c}')}'" for c in not_selected]
        not_selected = ", ".join(not_selected)
        return self.EXTRA_HEADER.format(not_selected=not_selected)

    def append_data(self, data):
        """Append data before printing"""
        if not set(data.keys()).issuperset(self._sorted_channel_names):
            return

        self._row_data.append(data)
        self._nb_data_rows += 1

    def print_data_rows(self):
        """Print and flush the available data rows"""
        if len(self._row_data) == 0:
            # Nothing new
            return
        rows = self._row_data
        self._row_data = []

        lines = []
        for i, r in enumerate(rows):
            index = self._nb_data_rows + i - len(rows)
            lines.append(self._build_data_row(index, r))
        block = "\n".join(lines)
        print(block)

    def print_data_ct(self, scan_info):
        # ct is actually a timescan(npoints=1).
        if self._row_data:
            data = self._row_data[-1]
            values = [data[cname] for cname in self._sorted_channel_names]
            norm_values = numpy.array(values) / self._scan_info["count_time"]
            block = self._build_ct_output(values, norm_values)
            print(block)

    def _build_data_row(self, index, data):
        """`data` is a dict, one scalar per channel (last point)"""
        values = [data[cname] for cname in self._sorted_channel_names]
        values.insert(0, index)
        line = self._tab.add_line(values)
        return line

    def _format_number(self, value, length_before, length_after) -> str:
        """Format a number in order to center the dot.

        Arguments:
            length_before: Expected size before (the content is padded
                           right if small)
            length_after: Expected size after (the content is padded left
                          if smaller)
        Returns:
            A string with always a size of (length_before + length_after + 1)
        """
        if isinstance(value, numbers.Integral):
            v = str(value)
        else:
            v = f"{value:#g}"
        prefix_size = len(v.split(".")[0])
        suffix_size = len(v) - prefix_size - 1
        if length_before > prefix_size:
            prefix = " " * (length_before - prefix_size)
        else:
            prefix = ""
        if length_after > suffix_size:
            suffix = " " * (length_after - suffix_size)
        else:
            suffix = ""
        return f"{prefix}{v}{suffix}"

    def _build_ct_output(self, values, norm_values):

        info_dict = {}
        name_width = 20
        unit_width = 0
        for i, cname in enumerate(self._sorted_channel_names):
            channel_meta = self._channels_meta[cname]

            # display name
            if cname == "timer:elapsed_time":
                # disp_name = "dt"
                continue
            else:
                disp_name = channel_meta.display_name

            # unit
            unit = channel_meta.unit
            disp_unit = unit if unit else ""

            name_width = max(name_width, len(disp_name))
            unit_width = max(unit_width, len(disp_unit))

            # sort by controller name
            ctrl, _ = cname.split(":")[0:2]
            if info_dict.get(ctrl):
                info_dict[ctrl].append(
                    [disp_name, disp_unit, values[i], norm_values[i]]
                )
            else:
                info_dict[ctrl] = [[disp_name, disp_unit, values[i], norm_values[i]]]

        name_width = min(50, name_width)
        unit_width = min(8, unit_width)

        lines = []
        for ctrl, values in info_dict.items():
            for dname, u, v, nv in values:
                u = f"{u:>{unit_width}}"
                v = self._format_number(v, 8, 9)
                nv = self._format_number(nv, 8, 11)
                lines.append(f"  {dname:>{name_width}}  = {v}{u} ({nv}{u}/s)  {ctrl}")

        return "\n".join(lines)

    def print_scan_end(self, scan_info):
        """Print the end of the scan.

        Argument:
            scan_info: The final state of the `scan_info`
        """
        end = datetime.now().astimezone()
        start = datetime.fromisoformat(scan_info["start_time"])
        dt = end - start
        print(f"\n   Took {dt}[s] \n")


class ScanDataRowStream:
    """Hold the data received from Redis to follow the last available row.

    When the row is read the data is released.
    """

    def __init__(self):
        self._data_per_channels = {}
        self._nb_per_channels = {}
        self._nb_full_rows = 0
        self._current = -1

    def register(self, name: str):
        self._data_per_channels[name] = []
        self._nb_per_channels[name] = 0

    def is_registered(self, name: str) -> bool:
        return name in self._data_per_channels

    def received_size(self, name: str) -> int:
        return self._nb_per_channels[name]

    def add_channel_data(self, name: str, index: int, data_bunch: numpy.ndarray):
        row = self._data_per_channels.setdefault(name, [])
        row.append([index, data_bunch])
        self._nb_per_channels[name] = index + len(data_bunch)

    def _pop_channel_value(self, name: str, index: int):
        row = self._data_per_channels[name]
        data_index, data_bunch = row[0]
        while not (index < data_index + len(data_bunch)):
            row.pop(0)
            data_index, data_bunch = row[0]
        return data_bunch[index - data_index]

    def next_rows(self) -> Iterator[dict[str, float]]:
        """Returns a dict containing the next value of each channels.

        Else returns None
        """
        self._nb_full_rows = min(self._nb_per_channels.values())
        if self._nb_full_rows == 0:
            return
        for i in range(self._current + 1, self._nb_full_rows):
            data = {
                k: self._pop_channel_value(k, i) for k in self._data_per_channels.keys()
            }
            yield data
        self._current = self._nb_full_rows - 1


class ScanPrinterFromRedis(scan_mdl.ScansObserver):
    def __init__(self, scan_display):
        super(ScanPrinterFromRedis, self).__init__()
        self.scan_display = scan_display
        self.update_header = False
        self.scan_renderer = None
        self._rows = ScanDataRowStream()

    def update_displayed_channels_from_user_request(self) -> bool:
        """If enabled, check ScanDisplay content and compare it to the
        current displayed channel selection.

        If there is a mismatch, update the selection and redisplay the
        table header.

        Returns:
            True if the channel selection was changed.
        """
        requested_channels = []
        scan_renderer = self.scan_renderer
        if self.scan_display.scan_display_filter_enabled:
            # Use master channel plus user request
            requested_channels = self.scan_display.displayed_channels.copy()
            if len(requested_channels) == 0:
                return
            for m in scan_renderer.master_scalar_channel_names:
                if m in requested_channels:
                    requested_channels.remove(m)
            # Always use the masters
            requested_channels = (
                scan_renderer.master_scalar_channel_names + requested_channels
            )
            if not requested_channels:
                requested_channels = scan_renderer.displayable_channel_names.copy()
            scan_renderer.set_displayed_channels(requested_channels)

    def on_scan_created(self, scan_key: str, scan_info: dict):
        self.scan_renderer = ScanRenderer(scan_info)
        # Update the displayed channels before printing the scan header
        if self.scan_renderer.scan_type != "ct":
            self.update_displayed_channels_from_user_request()
        for n in self.scan_renderer.sorted_channel_names:
            self._rows.register(n)
        self.scan_renderer.print_scan_header()
        self.scan_renderer.print_table_header()

    def on_scan_finished(self, scan_key: str, scan_info: dict):
        if self.scan_renderer.scan_type == "ct":
            self.scan_renderer.print_data_ct(scan_info)
        self.scan_renderer.print_scan_end(scan_info)

    def on_scalar_data_received(
        self,
        scan_key: str,
        channel_name: str,
        index: int,
        data_bunch: typing.Union[list, numpy.ndarray],
    ):
        if not self._rows.is_registered(channel_name):
            return

        size = self._rows.received_size(channel_name)
        if index > size:
            # Append NaN values
            data_gap = [numpy.nan] * (index - size)
            self._rows.add_channel_data(channel_name, size, data_gap)

        self._rows.add_channel_data(channel_name, index, data_bunch)
        for row in self._rows.next_rows():
            self.scan_renderer.append_data(row)

        if self.scan_renderer.scan_type != "ct":
            with nonblocking_print():
                self.scan_renderer.print_data_rows()


class ScanDataListener(scan_mdl.ScansObserver):
    """Listen all the scans of a session from Redis and dispatch them to a
    dedicated printer"""

    def __init__(self, session_name):
        super().__init__()
        self.session_name = session_name
        self.scan_display = ScanDisplay(self.session_name)

        self._scan_displayer = None
        """Current scan displayer"""

        self._scan_id = None
        """Current scan id"""

        self._warning_messages = []

    def _create_scan_displayer(self, scan_info):
        """Create a scan displayer for a specific scan"""
        if not is_scan_supported(scan_info):
            return None
        return ScanPrinterFromRedis(self.scan_display)

    def on_scan_created(self, scan_key: str, scan_info: dict):
        """Called from Redis callback on scan started"""
        if self._scan_displayer is None:
            self._scan_displayer = self._create_scan_displayer(scan_info)
            if self._scan_displayer is not None:
                self._scan_id = scan_key
                self._scan_displayer.on_scan_created(scan_key, scan_info)
        else:
            self._warning_messages.append(
                f"\nWarning: a new scan '{scan_key}' has been started while scan '{self._scan_id}' is running.\nNew scan outputs will be ignored."
            )

    def on_scan_finished(self, scan_key: str, scan_info: dict):
        """Called from Redis callback on scan ending"""
        scan_id = scan_key
        if self._scan_id == scan_id:
            try:
                if self._scan_displayer is not None:
                    self._scan_displayer.on_scan_finished(scan_key, scan_info)
            finally:
                self._scan_displayer = None
                self._scan_id = None

        messages = self._warning_messages
        self._warning_messages.clear()
        for msg in messages:
            print(msg)

    def on_scalar_data_received(
        self,
        scan_key: str,
        channel_name: str,
        index: int,
        data_bunch: typing.Union[list, numpy.ndarray],
    ):
        """Called from Redis callback on a scalar data received"""
        if self._scan_id == scan_key:
            if self._scan_displayer is not None:
                self._scan_displayer.on_scalar_data_received(
                    scan_key, channel_name, index, data_bunch
                )

    def start(self):
        # wait for the watcher to be ready to print the message, because some
        # test fixtures rely on that message to start scans.
        def print_ready(ready_event):
            ready_event.wait()
            msg = f" Watching scans from Bliss session: '{self.session_name}' "
            print(get_decorated_line(msg, deco=">", rdeco="<", head="\n", tail="\n"))

        watcher = scan_mdl.ScansWatcher(self.session_name)
        watcher.set_observer(self)
        try:
            printer_greenlet = gevent.spawn(print_ready, watcher.ready_event)
            watcher.run()
        finally:
            printer_greenlet.kill()


class StepScanProgress(ScanProgress):

    USE_TEXTBLOCK = True

    def __init__(self, tracked_channels=None):
        super().__init__(tracked_channels)

    def scan_init_callback(self):
        self._start_time = time.perf_counter()
        if self.scan_type == "ct":
            self._scan_renderer = ScanRenderer(self.scan_info)
            self._tracked_channels = (
                "all"  # listen all scan channels in order to display ct output
            )

    def scan_new_callback(self):
        print(f"INFO: starting {self._scan}")

    def scan_end_callback(self):
        if self.scan_type == "ct":
            self._scan_renderer.print_table_header()
            self._scan_renderer.append_data(self._data_dict)
            self._scan_renderer.print_data_ct(None)

    def _formated_scan_state(self) -> tuple[str, str]:
        state = self._scan.state
        if state == ScanState.STARTING:
            name = "RUNNING"
        elif state == ScanState.USER_ABORTED:
            name = "ABORTED"
        else:
            name = state.name

        if state == ScanState.STARTING:
            style = "class:info"
        elif state == ScanState.USER_ABORTED:
            npoints = self.scan_info.get("npoints", 1)
            if npoints == 0:
                style = "class:success"
            else:
                style = "class:danger"
        elif state == ScanState.KILLED:
            style = "class:danger"
        elif state == ScanState.DONE:
            style = "class:success"
        else:
            style = ""
        # Make sure to always have the same size
        return style, f"{name:>9}"

    def build_progress_message(self):
        from bliss.shell.formatters import tabulate

        headers: list[tuple[str, str]] = []
        values: list[tuple[str, str]] = []

        now = time.perf_counter()
        elapsed = now - self._start_time
        npoints = self.scan_info["npoints"]

        if not self._scan._acq_chain.iterators:
            curr_iter = 0
        else:
            curr_iter = self._scan._acq_chain.iterators[0].sequence_index
            # iterators[0] => step_by_step scan has only one top_master

        head = f"{self.scan_type}:"
        headers.append(("class:header", head))
        values.append(("", ""))

        headers.append(("class:header", "state"))
        values.append(self._formated_scan_state())

        def format_duration(elapsed_time) -> str:
            elapsed_time = int(elapsed_time)
            if elapsed_time <= 0:
                return "0s"
            return timedisplay.duration_format(int(elapsed_time))

        if self.scan_type == "ct":
            headers.append(("class:header", "elapsed"))
            values.append(("", f"{format_duration(elapsed)}"))
        else:
            if npoints == 0:
                length = 3
                curr_iter_string = f"{str(curr_iter):>{length}}"
            else:
                length = int(numpy.ceil(numpy.log10(npoints))) + 1
                curr_iter_string = f"{str(curr_iter):>{length}}/{npoints}"
            headers.append(("class:header", "point"))
            values.append(("", curr_iter_string))

            headers.append(("class:header", "elapsed"))
            values.append(("", f"{format_duration(elapsed)}"))

            for axis, pos in self._scan_axes_pos.items():
                headers.append(("class:header", axis.name))
                values.append(("", f"{pos:.{axis.display_digits}f}"))

        return 2, tabulate.tabulate(
            [headers, values],
            stralign="right",
            numalign="right",
        )
