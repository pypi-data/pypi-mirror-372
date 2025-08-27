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
        virtual_parents: dict[str, scan_model.Device] = {}

        def get_virtual_parent(channel_fullname):
            """Some magic to create virtual device for each ROIs"""
            if ":spectrum:" in channel_fullname:
                return device

            if ":roi:" in channel_fullname:
                # It's a ROI
                key = "rois"
                if key in virtual_parents:
                    return virtual_parents[key]
                detector_device = scan_model.Device(self.parser._scan)
                detector_device.setName("rois")
                detector_device.setMaster(device)
                detector_device.setType(scan_model.DeviceType.VIRTUAL_MCA_DETECTOR)
                virtual_parents[key] = detector_device
                return detector_device

            short_name = channel_fullname.rsplit(":", 1)[-1]

            # FIXME: It would be good to have a real detector concept in BLISS
            if "_" in short_name:
                _, detector_name = short_name.rsplit("_", 1)
            else:
                detector_name = short_name

            key = f"{device.name()}:{detector_name}"
            if key in virtual_parents:
                return virtual_parents[key]

            detector_device = scan_model.Device(self.parser._scan)
            detector_device.setName(detector_name)
            detector_device.setMaster(device)
            detector_device.setType(scan_model.DeviceType.VIRTUAL_MOSCA_STATS)
            virtual_parents[key] = detector_device
            return detector_device

        channel_names = meta.get("channels", [])
        for channel_fullname in channel_names:
            channel_meta = self.reader.consume_channel_key(channel_fullname)
            if channel_meta is None:
                continue
            sub_device = get_virtual_parent(channel_fullname)
            channel = self.parse_channel(
                channel_fullname, channel_meta, parent=sub_device
            )
            if channel.type() == scan_model.ChannelType.VECTOR:
                channel.setType(scan_model.ChannelType.SPECTRUM)

        desc_corr = self.reader.consume_device_name(f"{device.name()}:roi_correction")
        desc_sum = self.reader.consume_device_name(f"{device.name()}:roi_sum")

        if desc_corr is not None or desc_sum is not None:
            corr_roi_device = scan_model.Device(self.parser._scan)
            corr_roi_device.setName("rois_corrected")
            corr_roi_device.setMaster(device)
            corr_roi_device.setType(scan_model.DeviceType.VIRTUAL_MCA_DETECTOR)
            if desc_corr is not None:
                super().parse_channels(corr_roi_device, desc_corr)
            if desc_sum is not None:
                super().parse_channels(corr_roi_device, desc_sum)
