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

import weakref
import logging
from ..model import scan_model


_logger = logging.getLogger(__name__)


class _ProgressStrategy:
    def compute(self, scan: scan_model.Scan) -> float | None:
        """Returns the percent of progress of this strategy.

        Returns a value between 0..1, else None if it is not appliable.
        """
        raise NotImplementedError

    def channelSize(self, channel: scan_model.Channel) -> int:
        data = channel.data()
        if data is None:
            return 0

        frameId = data.frameId()
        if frameId is not None:
            return frameId + 1
        array = data.array()
        if array is not None:
            return len(array)
        return 0


_PROGRESS_STRATEGIES: weakref.WeakKeyDictionary[
    scan_model.Scan, list[_ProgressStrategy]
] = weakref.WeakKeyDictionary()


class _ProgressOfAnyChannels(_ProgressStrategy):
    """Compute the progress according to any of the available channels"""

    def __init__(self, maxPoints: int):
        self.__maxPoints = maxPoints

    def compute(self, scan: scan_model.Scan) -> float | None:
        scan_info = scan.scanInfo()
        master_channels: list[str] = []
        for channel_name, meta in scan_info["channels"].items():
            dim = meta.get("dim", 0)
            if dim in [0, 2]:
                master_channels.append(channel_name)

        for master_channel in master_channels:
            channel = scan.getChannelByName(master_channel)
            if channel is None:
                continue
            size = self.channelSize(channel)
            return size / self.__maxPoints

        return None


class _ProgressOfChannel(_ProgressStrategy):
    def __init__(self, channelName: str, maxPoints: int):
        self.__maxPoints = maxPoints
        self.__channelName = channelName

    def compute(self, scan: scan_model.Scan) -> float | None:
        channel = scan.getChannelByName(self.__channelName)
        if channel is None:
            return None
        size = self.channelSize(channel)
        return size / self.__maxPoints


class _ProgressOfInfinityScan(_ProgressStrategy):
    def __init__(self, channelName):
        self.__channelName = channelName

    def compute(self, scan: scan_model.Scan) -> float | None:
        channel = scan.getChannelByName(self.__channelName)
        if channel is None:
            return None
        size = self.channelSize(channel)
        if scan.state() == scan_model.ScanState.FINISHED:
            return 1.0
        if size == 0:
            return 0
        return 0.5


class _ProgressOfSequence(_ProgressStrategy):
    def __init__(self, scan: scan_model.Scan):
        super(_ProgressOfSequence, self).__init__()
        scanInfo = scan.scanInfo()
        sequenceInfo = scanInfo.get("sequence_info", {})
        assert isinstance(sequenceInfo, dict)
        scanCount = sequenceInfo.get("scan_count", None)
        self.__scanCount: int | None
        if isinstance(scanCount, int) and scanCount > 0:
            self.__scanCount = scanCount
        else:
            self.__scanCount = None

    def compute(self, scan: scan_model.Scan) -> float | None:
        if self.__scanCount is None:
            return None

        subScans = scan.subScans()
        if len(subScans) == 0:
            return 0
        lastScan = subScans[-1]
        index = lastScan.scanInfo().get("index_in_sequence", len(subScans) - 1)
        print(lastScan.state())
        if lastScan.state() == scan_model.ScanState.FINISHED:
            index += 1
        return index / self.__scanCount


def _create_progress_strategies(scan: scan_model.Scan) -> list[_ProgressStrategy]:
    scan_info = scan.scanInfo()
    if scan_info is None:
        return []

    strategies: list[_ProgressStrategy] = []

    strategy: _ProgressStrategy
    if isinstance(scan, scan_model.ScanGroup):
        strategy = _ProgressOfSequence(scan)
        strategies.append(strategy)

    channels = scan_info.get("channels", None)
    if channels is not None:
        # Reach on channel per npoints (in case of many top masters without
        # same size)
        strategy_per_npoints: dict[int, _ProgressStrategy] = {}
        for channel_name, metadata_dict in channels.items():
            if "points" in metadata_dict:
                try:
                    npoints = int(metadata_dict["points"])
                except Exception:
                    # It's about parsing user input, everything can happen
                    _logger.error("Error while reading scan_info", exc_info=True)
                    continue

                if npoints in strategy_per_npoints:
                    continue
                strategy = _ProgressOfChannel(channel_name, npoints)
                strategy_per_npoints[npoints] = strategy

        for _, s in strategy_per_npoints.items():
            strategies.append(s)

    if scan_model.ScanFeatures.INFINITY_SCAN in scan.features():
        if channels is not None:
            channel_names = list(channels.keys())
            if len(channel_names) > 0:
                strategy = _ProgressOfInfinityScan(channel_names[0])
                strategies.append(strategy)

    if len(strategies) == 0:
        # npoints do not distinguish many top masters
        # It only use it if there is no other choises
        try:
            npoints = scan_info.get("npoints", None)
            if npoints is None:
                # Mesh scans
                npoints1 = scan_info.get("npoints1", 0)
                npoints2 = scan_info.get("npoints2", 0)
                npoints = int(npoints1) * int(npoints2)
            else:
                npoints = int(npoints)

            if npoints is not None and npoints != 0:
                strategies.append(_ProgressOfAnyChannels(npoints))
        except Exception:
            # It's about parsing user input, everything can happen
            _logger.error("Error while reading scan_info", exc_info=True)

    return strategies


def get_scan_progress_percent(scan: scan_model.Scan | None) -> float | None:
    """Returns the percent of progress of this strategy.

    Returns a value between 0..1, else None if it is not applicable.
    """
    if scan is None:
        return None
    strategies = _PROGRESS_STRATEGIES.get(scan, None)
    if strategies is None:
        strategies = _create_progress_strategies(scan)
        _PROGRESS_STRATEGIES[scan] = strategies

    values = [s.compute(scan) for s in strategies]
    values2 = [v for v in values if v is not None]
    if len(values2) == 0:
        return None

    result = sum(values2) / len(values2)
    return result
