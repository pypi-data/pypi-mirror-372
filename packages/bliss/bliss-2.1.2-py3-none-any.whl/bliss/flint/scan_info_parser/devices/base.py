# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

from __future__ import annotations

import numpy
import logging
from ...model import scan_model
from ..channels import parse_channel_metadata
from ..reader import ScanInfoReader

_logger = logging.getLogger(__name__)


DEVICE_TYPES = {
    None: scan_model.DeviceType.NONE,
    "lima": scan_model.DeviceType.LIMA,
    "lima2": scan_model.DeviceType.LIMA2,
    "mca": scan_model.DeviceType.MCA,
    "mosca": scan_model.DeviceType.MOSCA,
}


class BaseDeviceParser:
    def __init__(self, parser, reader: ScanInfoReader):
        self.parser = parser
        self.reader = reader

    def parse(self, name: str, meta: dict, parent: scan_model.Device):
        device = self.create_device(name, meta, parent)
        self.parse_sub_devices(device, meta)
        self.parse_channels(device, meta)

    def create_device(
        self, name: str, meta: dict, parent: scan_model.Device
    ) -> scan_model.Device:
        device = scan_model.Device(self.parser._scan)
        device.setName(name)
        device.setMaster(parent)
        device_type = meta.get("type", None)
        device_type = DEVICE_TYPES.get(device_type, scan_model.DeviceType.UNKNOWN)
        device.setType(device_type)
        metadata = scan_model.DeviceMetadata(info=meta, roi=None)
        device.setMetadata(metadata)
        return device

    def parse_sub_devices(self, device: scan_model.Device, meta: dict):
        device_ids = meta.get("triggered_devices", [])
        if len(device_ids) >= 1:
            device.setIsMaster(True)
        for device_id in device_ids:
            sub_meta = self.reader.consume_device_key(device_id)
            if sub_meta is None:
                continue
            sub_name = sub_meta["name"]
            self.parse_sub_device(sub_name, sub_meta, parent=device)

    def parse_sub_device(self, name: str, meta: dict, parent: scan_model.Device):
        self.parser._parse_device(name, meta, parent=parent)

    def parse_channels(self, device: scan_model.Device, meta):
        channel_names = meta.get("channels", [])
        for channel_fullname in channel_names:
            channel_meta = self.reader.consume_channel_key(channel_fullname)
            if channel_meta is None:
                continue
            self.parse_channel(channel_fullname, channel_meta, parent=device)

        devicemeta = meta.get("metadata", {})
        xaxis_array = devicemeta.get("xaxis_array", None)
        if xaxis_array is not None:
            # Create a virtual channel already feed with data
            try:
                xaxis_array = numpy.array(xaxis_array)
                if len(xaxis_array.shape) != 1:
                    raise RuntimeError("scan_info xaxis_array expect a 1D data")
            except Exception:
                _logger.warning("scan_info contains wrong xaxis_array: %s", xaxis_array)
                xaxis_array = numpy.array([])

            unit = devicemeta.get("xaxis_array_unit", None)
            label = devicemeta.get("xaxis_array_label", None)
            channel = scan_model.Channel(device)
            channel.setType(scan_model.ChannelType.VECTOR)
            if unit is not None:
                channel.setUnit(unit)
            if label is not None:
                channel.setDisplayName(label)
            data = scan_model.Data(array=xaxis_array)
            channel.setData(data)
            fullname = device.name()
            channel.setName(f"{fullname}:#:xaxis_array")

    def _pop_as_str(self, channel_name: str, meta: dict, key: str) -> str | None:
        v = meta.pop(key, None)
        if v is None:
            return None
        if isinstance(v, str):
            return str(v)
        _logger.error(
            "Error while reading channel %s@%s as str. Found %s",
            channel_name,
            key,
            type(v),
        )
        return None

    def parse_channel(
        self, channel_fullname: str, meta: dict, parent: scan_model.Device
    ):
        file_only = meta.pop("file_only", False)
        if file_only:
            return

        channel = scan_model.Channel(parent)
        channel.setName(channel_fullname)

        # protect mutation of the original object, with the following `pop`
        meta = dict(meta)

        # FIXME: This have to be cleaned up (unit and display name are part of the metadata)
        unit = self._pop_as_str(channel_fullname, meta, "unit")
        if unit is not None:
            channel.setUnit(unit)
        display_name = self._pop_as_str(channel_fullname, meta, "display_name")
        if display_name is not None:
            channel.setDisplayName(display_name)

        metadata = parse_channel_metadata(meta)
        channel.setMetadata(metadata)
        return channel
