# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

from __future__ import annotations

import logging
from ...model import scan_model
from .base import BaseDeviceParser

_logger = logging.getLogger(__name__)


class DeviceParser(BaseDeviceParser):
    def parse_channels(self, device, meta):
        # cache virtual roi devices
        virtual_detectors: dict[str, scan_model.Device] = {}

        def get_virtual_detector(channel_fullname):
            """Some magic to create virtual device for each ROIs"""
            short_name = channel_fullname.rsplit(":", 1)[-1]

            # FIXME: It would be good to have a real detector concept in BLISS
            if "_" in short_name:
                _, detector_name = short_name.rsplit("_", 1)
            else:
                detector_name = short_name

            key = f"{device.name()}:{detector_name}"
            if key in virtual_detectors:
                return virtual_detectors[key]

            detector_device = scan_model.Device(self.parser._scan)
            detector_device.setName(detector_name)
            detector_device.setMaster(device)
            detector_device.setType(scan_model.DeviceType.VIRTUAL_MCA_DETECTOR)
            virtual_detectors[key] = detector_device
            return detector_device

        channel_names = meta.get("channels", [])
        for channel_fullname in channel_names:
            channel_meta = self.reader.consume_channel_key(channel_fullname)
            if channel_meta is None:
                continue
            roi_device = get_virtual_detector(channel_fullname)
            channel = self.parse_channel(
                channel_fullname, channel_meta, parent=roi_device
            )
            if channel.type() == scan_model.ChannelType.VECTOR:
                channel.setType(scan_model.ChannelType.SPECTRUM)
