# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.
"""
Entry point to read a scan info
"""
from __future__ import annotations
from collections.abc import Generator

import logging
import importlib
from ..model import scan_model
from .devices.base import BaseDeviceParser
from .reader import ScanInfoReader

_logger = logging.getLogger(__name__)


class TopDeviceParser(BaseDeviceParser):
    def parse_sub_devices(self, device: scan_model.Device, meta: dict):
        BaseDeviceParser.parse_sub_devices(self, device, meta)
        # The top master is anyway a master
        device.setIsMaster(True)


class ScanModelReader:
    """Object reading a scan_info and generating a scan model"""

    def __init__(self, scan_info):
        self._scan_info = scan_info
        self._reader = ScanInfoReader(scan_info)

        is_group = scan_info.get("is_scan_sequence", False)
        scan: scan_model.Scan
        if is_group:
            scan = scan_model.ScanGroup()
        else:
            scan = scan_model.Scan()

        scan.setScanInfo(scan_info)
        self._scan: scan_model.Scan | None = scan

    def parse(self):
        """Parse the whole scan info and return scan model"""
        assert self._scan is not None, "The scan was already parsed"
        self._parse_scan()
        scan = self._scan
        _precache_scatter_constraints(scan)
        self._scan = None
        scan.seal()
        return scan

    def _parse_scan(self):
        """Parse the whole scan structure"""
        for chain_name, meta in self._reader.chains():
            self._parse_chain(chain_name, meta)

    def _iter_chain_device_names(self, chain_name: str) -> Generator[str]:
        devices = self._scan_info["devices"]
        acquisition_chain = self._scan_info["acquisition_chain"]
        items: list[str] = [acquisition_chain[chain_name]["top_master"]]
        while items:
            n = items.pop()
            yield n
            items.extend(devices[n].get("devices", []))

    def _parse_chain(self, name: str, meta: dict):
        assert self._scan is not None
        top_master = scan_model.Device(self._scan)
        top_master.setType(scan_model.DeviceType.VIRTUAL_CHAIN)
        top_master.setName(name)

        device_keys = self._iter_chain_device_names(name)
        for i, sub_device_key in enumerate(device_keys):
            sub_meta = self._reader.consume_device_key(sub_device_key)
            if sub_meta is None:
                continue
            sub_name = sub_meta["name"]
            if i == 0:
                parser_class = TopDeviceParser
            else:
                parser_class = None
            self._parse_device(
                sub_name, sub_meta, parent=top_master, parser_class=parser_class
            )

    def _parse_device(
        self, name: str, meta: dict, parent: scan_model.Device, parser_class=None
    ):
        if parser_class is None:
            device_type = meta.get("type")
            parser_class = None
            if device_type is not None:
                try:
                    if "." in device_type:
                        # Make sure we are not about to load weird stuffs
                        raise RuntimeError(f"Unsafe device type '{device_type}'")
                        # safety
                    try:
                        module = importlib.import_module(
                            f".{device_type}", "bliss.flint.scan_info_parser.devices"
                        )
                        try:
                            parser_class = module.DeviceParser
                        except AttributeError:
                            _logger.warning(
                                "Module connector %s does not contain expected DeviceParser class",
                                device_type,
                            )
                    except ImportError:
                        _logger.debug(
                            "Unsupported device type '%s', use default parser",
                            device_type,
                            exc_info=True,
                        )
                except RuntimeError as e:
                    _logger.warning("%s", e.args[0])

            if parser_class is None:
                parser_class = BaseDeviceParser

        node_parser = parser_class(self, reader=self._reader)
        node_parser.parse(name, meta, parent=parent)


def _precache_scatter_constraints(scan):
    """Precache information about group of data and available scatter axis"""
    assert scan is not None
    scatterDataDict: dict[str, scan_model.ScatterData] = {}
    for device in scan.devices():
        for channel in device.channels():
            metadata = channel.metadata()
            if metadata.group is not None:
                scatterData = scatterDataDict.get(metadata.group, None)
                if scatterData is None:
                    scatterData = scan_model.ScatterData()
                    scatterDataDict[metadata.group] = scatterData
                if metadata.axisKind is not None or metadata.axisId is not None:
                    scatterData.addAxisChannel(channel, metadata.axisId)
                else:
                    scatterData.addCounterChannel(channel)

    for scatterData in scatterDataDict.values():
        scan.addScatterData(scatterData)


def create_scan_model(scan_info: dict):
    reader = ScanModelReader(scan_info)
    return reader.parse()
