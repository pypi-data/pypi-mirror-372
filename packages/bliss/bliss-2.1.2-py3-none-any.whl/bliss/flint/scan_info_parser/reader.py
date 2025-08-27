# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.
"""
Context to read the scan info
"""
from __future__ import annotations


import logging

_logger = logging.getLogger(__name__)


class ScanInfoReader:
    """Context to read safely a scan info from BLISS.

    Mostly designed to read the structure.
    """

    def __init__(self, scan_info: dict):
        self._scan_info = scan_info
        self._read_chains: set[str] = set()
        self._read_devices: set[str] = set()
        self._read_channels: set[str] = set()

    def chains(self):
        chains = self._scan_info.get("acquisition_chain", {})
        for top_master_name, meta in chains.items():
            if top_master_name in self._read_chains:
                continue
            yield top_master_name, meta

    def consume_chain_key(self, name: str) -> dict | None:
        if name in self._read_chains:
            return None
        meta = self._scan_info["acquisition_chain"].get(name)
        if meta is None:
            _logger.error(
                "scan_info mismatch. Chain name %s not found",
                name,
            )
            return None
        self._read_chains.add(name)
        return meta

    def consume_device_key(self, key: str) -> dict | None:
        if key in self._read_devices:
            return None
        meta = self._scan_info["devices"].get(key)
        if meta is None:
            _logger.error(
                "scan_info mismatch. Device name %s not found",
                key,
            )
            return None
        self._read_devices.add(key)
        return meta

    def consume_device_name(self, device_name: str) -> dict | None:
        """Consume a device description by name if available"""
        devices = self._scan_info["devices"]
        for device_key, meta in devices.items():
            if device_key in self._read_devices:
                continue
            if meta["name"] == device_name:
                self._read_devices.add(device_key)
                return meta
        return None

    def consume_channel_key(self, name: str) -> dict | None:
        if name in self._read_channels:
            return None
        meta = self._scan_info["channels"].get(name)
        if meta is None:
            _logger.error(
                "scan_info mismatch. Channel name %s not found",
                name,
            )
            return None
        self._read_channels.add(name)
        return meta
