# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

from __future__ import annotations
from typing import Any

import logging
from ...model import scan_model
from bliss.controllers.lima import roi as lima_roi
from .base import BaseDeviceParser

_logger = logging.getLogger(__name__)


class DeviceParser(BaseDeviceParser):
    def parse_channel(self, channel_fullname: str, meta, parent: scan_model.Device):
        channel = super().parse_channel(channel_fullname, meta, parent)
        devicemeta = parent.metadata().info.get("metadata", {})
        assert isinstance(devicemeta, dict)
        representation = devicemeta.get("representation", None)
        if representation == "mca" and channel.type() == scan_model.ChannelType.IMAGE:
            channel.setType(scan_model.ChannelType.SPECTRUM_D_C)
        return channel

    def parse_sub_device(self, name: str, meta: dict, parent: scan_model.Device):
        if name == "roi_counters" or name == "roi_profiles":
            parser = LimaRoiDeviceParser(self.parser, self.reader)
            parser.parse(name, meta, parent)
        else:
            BaseDeviceParser.parse_sub_device(self, name, meta, parent)


class LimaRoiDeviceParser(BaseDeviceParser):
    def create_device(
        self,
        name: str,
        meta: dict[str, Any],
        parent: scan_model.Device,
    ) -> scan_model.Device:
        device = BaseDeviceParser.create_device(self, name, meta, parent)
        device.setType(scan_model.DeviceType.LIMA_SUB_DEVICE)
        return device

    def parse_channels(self, device: scan_model.Device, meta: dict):
        # cache virtual roi devices
        virtual_rois = {}

        # FIXME: It would be good to have a real ROI concept in BLISS
        # Here we iterate the set of metadata to try to find something interesting
        devicemeta = meta.get("metadata", {})

        for roi_name, roi_dict in devicemeta.items():
            if not isinstance(roi_dict, dict):
                continue
            if "kind" not in roi_dict:
                continue
            roi_device = self.create_virtual_roi(roi_name, roi_dict, device)
            virtual_rois[roi_name] = roi_device

        def get_virtual_roi(channel_fullname):
            """Retrieve roi device from channel name"""
            nonlocal virtual_rois
            short_name = channel_fullname.rsplit(":", 1)[-1]

            if "_" in short_name:
                roi_name, _ = short_name.rsplit("_", 1)
            else:
                roi_name = short_name

            return virtual_rois.get(roi_name, None)

        channel_names = meta.get("channels", [])
        for channel_fullname in channel_names:
            channel_meta = self.reader.consume_channel_key(channel_fullname)
            if channel_meta is None:
                continue
            roi_device = get_virtual_roi(channel_fullname)
            if roi_device is not None:
                parent_channel = roi_device
            else:
                parent_channel = device
            self.parse_channel(channel_fullname, channel_meta, parent=parent_channel)

    def create_virtual_roi(self, roi_name, roi_dict, parent):
        device = scan_model.Device(self.parser._scan)
        device.setName(roi_name)
        device.setMaster(parent)
        device.setType(scan_model.DeviceType.VIRTUAL_ROI)

        # Read metadata
        roi = None
        if roi_dict is not None:
            try:
                roi = lima_roi.dict_to_roi(roi_dict)
            except Exception:
                _logger.warning(
                    "Error while reading roi '%s' from '%s'",
                    roi_name,
                    device.fullName(),
                    exc_info=True,
                )

        metadata = scan_model.DeviceMetadata({}, roi)
        device.setMetadata(metadata)
        return device
