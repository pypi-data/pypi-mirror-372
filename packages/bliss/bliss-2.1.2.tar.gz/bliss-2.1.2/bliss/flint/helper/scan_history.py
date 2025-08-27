# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

"""
Helper to read scans from the history
"""

from __future__ import annotations
from typing import NamedTuple

import logging
import numpy
from datetime import datetime

from bliss.common.data_store import get_default_data_store
from bliss.flint.scan_info_parser.scans import create_scan_model
from bliss.flint.scan_info_parser.channels import iter_channels
from bliss.flint.model import scan_model
from blissdata.redis_engine.store import DataStore
from blissdata.redis_engine.exceptions import ScanLoadError, ScanNotFoundError


_logger = logging.getLogger(__name__)


class ScanDesc(NamedTuple):
    scan_key: str
    start_time: object
    scan_nb: int
    scan_type: str
    title: str


def get_all_scans(
    session_name: str, data_store: DataStore | None = None
) -> list[ScanDesc]:
    """
    Returns all scans still referenced from the history.

    .. code-block:: python

        from bliss import current_session
        scans = get_all_scans(current_session.name, data_store)
        print(scans[0].title)
    """
    if data_store is None:
        data_store = get_default_data_store()
    _, scan_keys = data_store.search_existing_scans(session=session_name)
    scan_descs = []
    for scan_key in scan_keys:
        try:
            scan = data_store.load_scan(scan_key)
        except ScanNotFoundError:
            # scan already deleted from Redis by user, skip it
            continue
        except ScanLoadError:
            _logger.warning("Cannot load scan %r", scan_key, exc_info=True)
            continue
        desc = ScanDesc(
            scan_key,
            datetime.fromisoformat(scan.info["start_time"]),
            scan.number,
            scan.info.get("type", None),
            scan.info.get("title", ""),
        )
        scan_descs.append(desc)
    return scan_descs


def get_scan_info(scan_key: str, data_store: DataStore | None = None) -> dict:
    """Return a scan_info dict from the scan `scan_key`"""
    if data_store is None:
        data_store = get_default_data_store()
    scan = data_store.load_scan(scan_key)
    return scan.info


def get_data(
    scan_key: str, scan_info: dict, data_store: DataStore | None = None
) -> dict[str, numpy.ndarray]:
    """Read channel data from redis, and referenced by this scan_info"""
    if data_store is None:
        data_store = get_default_data_store()
    scan = data_store.load_scan(scan_key)

    channels = list(iter_channels(scan_info))
    channel_names = set([c.name for c in channels if c.info.get("dim", 0) == 0])

    result = {}
    for channel_name in channel_names:
        try:
            stream = scan.streams[channel_name]
        except KeyError:
            # It is supposed to fail if part of the measurements was dropped
            _logger.debug("Backtrace", exc_info=True)
            _logger.warning("Channel %s is not reachable", channel_name)
        else:
            result[channel_name] = stream[:]
    return result


def create_scan(scan_key: str, data_store: DataStore | None = None) -> scan_model.Scan:
    """Create a scan with it's data from a Redis `scan_key`.

    The scan could contain empty channels.
    """
    scan_info = get_scan_info(scan_key, data_store)
    scan = create_scan_model(scan_info)

    channels = list(iter_channels(scan_info))
    channel_names = set([c.name for c in channels if c.info.get("dim", 0) == 0])

    bundled_data = get_data(scan_key, scan_info, data_store)
    for channel_name, array in bundled_data.items():
        data = scan_model.Data(parent=None, array=array)
        channel = scan.getChannelByName(channel_name)
        channel.setData(data)
        channel_names.discard(channel_name)

    if len(channel_names) > 0:
        names = ", ".join(channel_names)
        _logger.error("Few channel data was not read '%s'", names)

    # I guess there is no way to reach the early scan_info
    scan._setFinalScanInfo(scan_info)
    scan._setState(scan_model.ScanState.FINISHED)
    return scan
