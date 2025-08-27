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
from ..model import scan_model

import logging


_logger = logging.getLogger(__name__)


class ChannelInfo(NamedTuple):
    name: str
    info: dict[str, object] | None
    device: str | None
    master: str | None


def _iter_device_keys(scan_info: dict[str, object], master: str) -> Iterator[str]:
    """Iter every devices triggered by a master"""
    scan_info_devices = scan_info.get("devices", {})
    assert isinstance(scan_info_devices, dict)
    to_process: list[str] = [master]
    processed = set()
    while len(to_process) != 0:
        device_key = to_process.pop(0)
        device_info = scan_info_devices.get(device_key)
        if device_info is None:
            raise RuntimeError(f"Device {device_key} not part of the scan info")
        assert isinstance(device_info, dict)
        yield device_key
        if device_key in processed:
            raise RuntimeError("Cyclic link detected")
        processed.add(device_key)
        triggered_devices = device_info.get("triggered_devices")
        if triggered_devices is not None:
            assert isinstance(triggered_devices, list)
            to_process.extend(triggered_devices)


def iter_channels(scan_info: dict[str, object]) -> Iterator[ChannelInfo]:
    acquisition_chain_description = scan_info.get("acquisition_chain", {})
    assert isinstance(acquisition_chain_description, dict)

    scan_info_channels = scan_info.get("channels", {})
    scan_info_devices = scan_info.get("devices", {})
    if not isinstance(scan_info_channels, dict):
        _logger.warning("scan_info.channels is not a dict")
        scan_info_channels = {}
    if not isinstance(scan_info_devices, dict):
        _logger.warning("scan_info.devices is not a dict")
        scan_info_devices = {}

    def _get_device_from_channel_name(channel_name) -> str | None:
        """Returns the device name from the channel name, else None"""
        device_key = scan_info_channels.get(channel_name, {}).get("device")
        if device_key is None:
            return None
        name = scan_info_devices.get(device_key, {}).get("name")
        if isinstance(name, str):
            return name
        return None

    channels = set([])

    for chain_name, chain_info in acquisition_chain_description.items():
        top_master_key = chain_info.get("top_master")
        if top_master_key is None:
            top_master_key = chain_info.get("devices")[0]
        assert isinstance(top_master_key, str)
        for device_key in _iter_device_keys(scan_info, top_master_key):
            device_channels = scan_info_devices[device_key].get("channels", [])
            for channel_name in device_channels:
                channel_info = scan_info_channels.get(channel_name, {})
                device_name = _get_device_from_channel_name(channel_name)
                channel = ChannelInfo(
                    channel_name, channel_info, device_name, chain_name
                )
                yield channel
                channels.add(channel_name)

    for channel_name, channel_info in scan_info_channels.items():
        if channel_name in channels:
            continue
        device_name = _get_device_from_channel_name(channel_name)
        channel = ChannelInfo(channel_name, channel_info, device_name, "custom")
        yield channel


def _pop_and_convert(meta, key, func):
    value = meta.pop(key, None)
    if value is None:
        return None
    try:
        value = func(value)
    except ValueError:
        _logger.warning("%s %s is not a valid value. Field ignored.", key, value)
        value = None
    return value


def parse_channel_metadata(meta: dict) -> scan_model.ChannelMetadata:
    meta = meta.copy()

    # Link from channels to device
    # We can skip it
    meta.pop("device", None)

    # Compatibility Bliss 1.0
    if "axes-points" in meta and "axis_points" not in meta:
        _logger.warning("Metadata axes-points have to be replaced by axis_points.")
        meta["axis_points"] = meta.pop("axes-points")
    if "axes-kind" in meta and "axis_kind" not in meta:
        _logger.warning("Metadata axes-kind have to be replaced by axis_kind.")
        meta["axis_kind"] = meta.pop("axes-kind")

    start = _pop_and_convert(meta, "start", float)
    stop = _pop_and_convert(meta, "stop", float)
    vmin = _pop_and_convert(meta, "min", float)
    vmax = _pop_and_convert(meta, "max", float)
    points = _pop_and_convert(meta, "points", int)
    axisPoints = _pop_and_convert(meta, "axis_points", int)
    axisPointsHint = _pop_and_convert(meta, "axis_points_hint", int)
    axisKind = _pop_and_convert(meta, "axis_kind", scan_model.AxisKind)
    axisId = _pop_and_convert(meta, "axis_id", int)
    group = _pop_and_convert(meta, "group", str)
    dim = _pop_and_convert(meta, "dim", int)
    decimals = _pop_and_convert(meta, "decimals", int)

    # Compatibility code with existing user scripts written for BLISS 1.4
    mapping = {
        scan_model.AxisKind.FAST: (0, scan_model.AxisKind.FORTH),
        scan_model.AxisKind.FAST_BACKNFORTH: (0, scan_model.AxisKind.BACKNFORTH),
        scan_model.AxisKind.SLOW: (1, scan_model.AxisKind.FORTH),
        scan_model.AxisKind.SLOW_BACKNFORTH: (1, scan_model.AxisKind.BACKNFORTH),
    }
    if axisKind in mapping:
        if axisId is not None:
            _logger.warning(
                "Both axis_id and axis_kind with flat/slow is used. axis_id will be ignored"
            )
        axisId, axisKind = mapping[axisKind]

    for key in meta.keys():
        _logger.warning("Metadata key %s is unknown. Field ignored.", key)

    return scan_model.ChannelMetadata(
        start,
        stop,
        vmin,
        vmax,
        points,
        axisId,
        axisPoints,
        axisKind,
        group,
        axisPointsHint,
        dim,
        decimals,
    )
