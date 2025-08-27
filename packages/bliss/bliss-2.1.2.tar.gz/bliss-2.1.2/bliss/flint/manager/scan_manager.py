# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.
"""
This module provides processing to listen scan events from Redis and to feed
with it the flint modelization relative to scans.

Here is a simplified sequence of events managed by the :class:`ScanManager`.
But events are not yet managed this way.

.. image:: _static/flint/receive-image-data.svg
    :alt: Sequence of events to deal with a Lima detector
    :align: center

The :class:`ScanManager` is then responsible to:

- Try to expose strict events of the life-cycle of the scans
- Handle data events and reach data stored in Redis or in detectors (in case of
  image data, for example)
- Send update only when data are synchronized (to avoid extra computation on
  the GUI side).
"""
from __future__ import annotations
from typing import NamedTuple

import logging
import numpy
import time
import os

import gevent.event

from bliss.scanning import scan_events as bliss_scan
from blissdata.lima.client import LimaClientInterface
from blissdata.lima.client import LimaClient, Lima2Client
from blissdata.lima.image_utils import NoImageAvailable
from .data_storage import DataStorage
from blissdata.redis_engine.store import DataStore
from bliss.flint.scan_info_parser.channels import iter_channels
from bliss.flint.model import flint_model
from bliss.flint.model import scan_model
from bliss.flint.scan_info_parser.scans import create_scan_model
from bliss.flint.scan_info_parser.categories import get_scan_category


_logger = logging.getLogger(__name__)


class _ScalarDataEvent(NamedTuple):
    """Store scalar data event before been processing in the display pipeline

    As the data have to be processed on the fly, it is stored at another place.
    """

    scan_key: str
    channel_name: str


class _NdimDataEvent(NamedTuple):
    """Store an ndim data (like MCAs) data event before been processing in the
    display pipeline"""

    scan_key: str
    channel_name: str
    data_index: int
    data_bunch: list[numpy.ndarray] | numpy.ndarray


class _LimaRefDataEvent(NamedTuple):
    """Store a lima ref data event before been processing in the
    display pipeline"""

    scan_key: str
    channel_name: str
    last_index: int
    lima_client: LimaClientInterface


class _ScanCache:
    def __init__(self, scan_id: str, scan: scan_model.Scan):
        self.scan_id: str = scan_id
        """Unique id of a scan"""
        self.scan: scan_model.Scan = scan
        """Store the modelization of the scan"""
        self.data_storage = DataStorage()
        """"Store 0d grouped by masters"""
        self.__lima_clients: dict[str, object] = {}
        """Store lima client per channel name"""
        self.__ignored_channels: set[str] = set([])
        """Store a set of channels"""

    def ignore_channel(self, channel_name: str):
        self.__ignored_channels.add(channel_name)

    def is_ignored(self, channel_name: str):
        return channel_name in self.__ignored_channels

    def store_lima_client(self, channel_name, lima_client):
        self.__lima_clients[channel_name] = lima_client

    def lima_clients(self):
        """Returns an iterator containing channel name an it's lima_client"""
        return self.__lima_clients.items()


def _getRedisDataUrl() -> str:
    """
    Returns the URL of redis data.

    FIXME: It would be better to expose that through the flitn context instead
    """
    if "REDIS_DATA_URL" in os.environ:
        return os.environ["REDIS_DATA_URL"]
    from bliss.config.conductor.client import get_default_connection

    beacon_connection = get_default_connection()
    return beacon_connection.get_redis_data_server_connection_address().url


class ScanManager(bliss_scan.ScansObserver):
    """Manage scan events emitted by redis.

    A new scan create a `scan_model.Scan` object. This object is registered to
    flint as a new scan. Each further events are propagated to this scan
    structure.
    """

    def __init__(self, flintModel: flint_model.FlintState):
        self.__flintModel = flintModel
        self._refresh_task = None
        self.__cache: dict[str, _ScanCache] = {}

        self._last_events: dict[str, _NdimDataEvent | _LimaRefDataEvent] = {}
        self._last_scalar_events: dict[str, _ScalarDataEvent] = {}

        self._end_scan_event = gevent.event.Event()
        """Event to allow to wait for the the end of current scans"""

        self._end_data_process_event = gevent.event.Event()
        """Event to allow to wait for the the end of data processing"""

        self._end_scan_event.set()
        self._end_data_process_event.set()

        self.__watcher: bliss_scan.ScansWatcher | None = None
        """Process following scans events from a BLISS session"""
        self.__scans_watch_task = None
        """Process following scans events from a BLISS session"""

        if self.__flintModel is not None:
            self.__flintModel.blissSessionChanged.connect(self.__bliss_session_changed)
            self.__bliss_session_changed()

    def _cache(self):
        return self.__cache

    def __bliss_session_changed(self):
        session_name = self.__flintModel.blissSessionName()
        if session_name is not None:
            self._spawn_scans_session_watch(session_name)

    def _spawn_scans_session_watch(self, session_name: str):
        self.__flintModel.setDataProvider(None)

        if self.__watcher is not None:
            self.__watcher.stop()
            self.__watcher = None
        if self.__scans_watch_task:
            self.__scans_watch_task.kill()
            self.__scans_watch_task = None

        # configure default blissdata service
        redisUrl = _getRedisDataUrl()
        dataProvider = DataStore(redisUrl)
        self.__flintModel.setDataProvider(dataProvider)

        if session_name is None:
            return

        watcher = bliss_scan.ScansWatcher(session_name, dataProvider)
        watcher.set_observer(self)
        watcher.set_watch_scan_group(True)
        task = gevent.spawn(watcher.run)

        def exception_occurred(future_exception):
            try:
                future_exception.get()
            except Exception:
                _logger.error("Error occurred in ScansWatcher.run", exc_info=True)
            delay = 5
            _logger.warning("Retry the Redis connect in %s seconds", delay)
            gevent.sleep(delay)
            self._spawn_scans_session_watch(session_name)

        task.link_exception(exception_occurred)

        self.__scans_watch_task = task
        self.__watcher = watcher

    def __get_scan_cache(self, scan_id) -> _ScanCache | None:
        """Returns the scna cache, else None"""
        return self.__cache.get(scan_id, None)

    def __is_alive_scan(self, scan_key: str) -> bool:
        """Returns true if the scan using this scan info is still alive (still
        managed)."""
        return scan_key in self.__cache

    def on_scan_created(self, scan_key: str, scan_info: dict):
        _logger.debug("on_scan_created %s", scan_key)

    def on_scan_started(self, scan_key: str, scan_info: dict):
        _logger.info("Scan started: %s", scan_info.get("title", scan_key))
        _logger.debug("on_scan_started %s", scan_key)
        if scan_key in self.__cache:
            # We should receive a single new_scan per scan, but let's check anyway
            _logger.debug("new_scan from %s ignored", scan_key)
            return

        # Initialize cache structure
        try:
            scan = create_scan_model(scan_info)
        except Exception:
            _logger.error("Error while parsing scan_info", exc_info=True)
            _logger.error("Scan %s skipped", scan_info.get("title", scan_key))
            return

        self._end_scan_event.clear()
        scan.setBlissDataScanKey(scan_key)
        cache = _ScanCache(scan_key, scan)

        group_name = scan_info.get("group", None)
        if group_name is not None:
            group = self.__get_scan_cache(group_name)
            if group is not None:
                scan.setGroup(group.scan)
                group.scan.addSubScan(scan)

        # Initialize the storage for the channel data
        channels = iter_channels(scan_info)
        for channel_info in channels:
            group_name = None
            channel = scan.getChannelByName(channel_info.name)
            if channel is None:
                continue
            channel_meta = channel.metadata()
            if channel_meta.dim not in [None, 0]:
                continue
            if channel_meta.group is not None:
                group_name = channel_meta.group
            if group_name is None:
                group_name = "top:" + channel_info.master
            cache.data_storage.create_channel(channel.name(), group_name)

        if self.__flintModel is not None:
            self.__flintModel.addAliveScan(scan)

        self.__cache[scan_key] = cache

        scan._setState(scan_model.ScanState.PROCESSING)
        scan.scanStarted.emit()

    def on_child_created(self, scan_key: str, node):
        _logger.debug("on_child_created %s: %s", scan_key, node.db_name)

    def on_scalar_data_received(
        self,
        scan_key: str,
        channel_name: str,
        index: int,
        data_bunch: list | numpy.ndarray,
    ):
        _logger.debug("on_scalar_data_received %s %s", scan_key, channel_name)
        if not self.__is_alive_scan(scan_key):
            _logger.error(
                "New scalar data (%s) was received before the start of the scan (%s)",
                channel_name,
                scan_key,
            )
            return

        # The data have to be stored here on the callback event
        cache = self.__get_scan_cache(scan_key)
        if cache is None:
            return

        size = cache.data_storage.get_data_size(channel_name)
        if index > size:
            _logger.error("Data from Redis (channel %s) were lost", channel_name)
            # Append NaN values
            cache.data_storage.append_data(
                channel_name, numpy.array([numpy.nan] * (index - size))
            )

        cache.data_storage.append_data(channel_name, data_bunch)

        data_event = _ScalarDataEvent(scan_key=scan_key, channel_name=channel_name)
        self.__push_scan_data(data_event)

    def on_ndim_data_received(
        self,
        scan_key: str,
        channel_name: str,
        dim: int,
        index: int,
        data_bunch: list | numpy.ndarray,
    ):
        _logger.debug("on_ndim_data_received %s %s", scan_key, channel_name)
        if not self.__is_alive_scan(scan_key):
            _logger.error(
                "New ndim data (%s) was received before the start of the scan (%s)",
                channel_name,
                scan_key,
            )
            return

        data_event = _NdimDataEvent(
            scan_key=scan_key,
            channel_name=channel_name,
            data_index=index,
            data_bunch=data_bunch,
        )
        self.__push_scan_data(data_event)

    def on_lima_event_received(
        self,
        scan_key: str,
        channel_name: str,
        last_index: int,
        lima_client: LimaClientInterface,
    ):
        _logger.debug("on_lima_event_received %s %s", scan_key, channel_name)
        if not self.__is_alive_scan(scan_key):
            _logger.error(
                "New lima ref (%s) was received before the start of the scan (%s)",
                channel_name,
                scan_key,
            )
            return

        cache = self.__get_scan_cache(scan_key)
        assert cache is not None
        if cache.is_ignored(channel_name):
            # Was already ignored, in order to mitigate logging
            return

        if not isinstance(lima_client, (LimaClient, Lima2Client)):
            _logger.error(
                "Channel %s use an unsupported client for data fetching (found %s)",
                channel_name,
                type(lima_client),
            )
            cache.ignore_channel(channel_name)
            return

        channel = cache.scan.getChannelByName(channel_name)
        if channel is None:
            # Probably because it was inhibited: file_only
            cache.ignore_channel(channel_name)
            return

        # FIXME: It would be better not to access to _server_url
        server_url = getattr(lima_client, "_server_url", None)

        if server_url == "MOCKED":
            # FIXME: Workaround for scripts/scanning/withoutbliss/runscans.py
            # It would be better to provide a "fileref" protocol for example
            cache = self.__get_scan_cache(scan_key)
            if cache is not None:
                if cache.is_ignored(channel_name):
                    # Was already ignored, in order to mitigate logging
                    return
            _logger.warning(
                "Channel %s use a mocked lima client. Channel skipped.",
                channel_name,
            )
            cache.ignore_channel(channel_name)
            return

        channel = cache.scan.getChannelByName(channel_name)
        if channel is None:
            # Probably because it was inhibited: file_only
            cache.ignore_channel(channel_name)
            return

        data_event = _LimaRefDataEvent(
            scan_key=scan_key,
            channel_name=channel_name,
            last_index=last_index,
            lima_client=lima_client,
        )
        self.__push_scan_data(data_event)

    def __push_scan_data(self, data_event):
        if isinstance(data_event, _ScalarDataEvent):
            self._last_scalar_events[data_event.channel_name] = data_event
        else:
            self._last_events[data_event.channel_name] = data_event

        self._end_data_process_event.clear()
        if self._refresh_task is None:
            self._refresh_task = gevent.spawn(self.__refresh)

    def __refresh(self):
        try:
            while self._last_events or self._last_scalar_events:
                if self._last_scalar_events:
                    bunch_scalar_events = self._last_scalar_events
                    self._last_scalar_events = {}
                    self.__process_bunch_of_scalar_data_event(bunch_scalar_events)
                if self._last_events:
                    local_events = self._last_events
                    self._last_events = {}
                    for data_event in local_events.values():
                        try:
                            self.__process_data_event(data_event)
                        except NoImageAvailable:
                            # Assume this event is skipped but the frame will be
                            # read for the next event or at the end of the scan
                            _logger.debug("Error while reaching data", exc_info=True)
                        except Exception:
                            _logger.error("Error while reaching data", exc_info=True)
        finally:
            self._refresh_task = None
            self._end_data_process_event.set()

    def __is_image_must_be_read(
        self, scan: scan_model.Scan, channel_name, last_index
    ) -> bool:
        stored_channel = scan.getChannelByName(channel_name)
        if stored_channel is None:
            return True

        stored_data = stored_channel.data()
        if stored_data is None:
            # Not yet data, then update is needed
            return True

        rate = stored_channel.preferedRefreshRate()
        if rate is not None:
            now = time.time()
            # FIXME: This could be computed dinamically
            time_to_receive_data = 0.01
            receivedTime = stored_data.receivedTime()
            assert receivedTime is not None
            next_image_time = receivedTime + (rate / 1000.0) - time_to_receive_data
            return now > next_image_time

        stored_frame_id = stored_data.frameId()
        if stored_frame_id is None:
            # The data is something else that an image?
            # It's weird, then update the data
            return True

        if stored_frame_id == 0:
            # Some detectors (like andor) which do not provide
            # TRIGGER_SOFT_MULTI will always returns frame_id = 0 (from video image)
            # Then if a 0 was stored it is better to update anyway
            # FIXME: This case should be managed by bliss
            return True

        # An update is needed when bliss provides a more recent frame
        return last_index > stored_frame_id

    def __process_data_event(self, data_event):
        scan_key = data_event.scan_key
        cache = self.__get_scan_cache(scan_key)
        if cache is None:
            return

        channel_name = data_event.channel_name
        if isinstance(data_event, _ScalarDataEvent):
            # This object should go to another place
            assert False
        elif isinstance(data_event, _NdimDataEvent):
            frame_id = data_event.data_index + len(data_event.data_bunch) - 1
            raw_data = data_event.data_bunch[-1]
            self.__update_channel_data(cache, channel_name, raw_data, frame_id=frame_id)
        elif isinstance(data_event, _LimaRefDataEvent):
            lima_client = data_event.lima_client
            cache.store_lima_client(channel_name, lima_client)
            must_update = self.__is_image_must_be_read(
                cache.scan, channel_name, data_event.last_index
            )
            if must_update:
                image_data = lima_client.get_last_live_image()
                self.__update_channel_data(
                    cache,
                    channel_name,
                    raw_data=image_data.array,
                    frame_id=image_data.frame_id,
                    source="memory",
                )
        else:
            assert False

    def __process_bunch_of_scalar_data_event(self, bunch_scalar_events):
        """Process scalar events and split then into groups in order to update
        the GUI in synchronized way"""

        now = time.time()
        groups = {}

        # Groups synchronized events together
        for channel_name, data_event in bunch_scalar_events.items():
            scan_key = data_event.scan_key
            cache = self.__get_scan_cache(scan_key)
            assert cache is not None
            group_name = cache.data_storage.get_group(channel_name)
            key = scan_key, group_name
            if key not in groups:
                groups[key] = [channel_name]
            else:
                groups[key].append(channel_name)

        # Check for update on each groups of data
        for (scan_key, group_name), channel_names in groups.items():
            cache = self.__get_scan_cache(scan_key)
            assert cache is not None
            scan = cache.scan
            updated_group_size = cache.data_storage.update_group_size(group_name)
            if updated_group_size is not None:
                channel_names = cache.data_storage.get_channels_by_group(group_name)
                channels = []
                for channel_name in channel_names:
                    channel = scan.getChannelByName(channel_name)
                    assert channel is not None

                    array = cache.data_storage.get_data(channel_name)
                    # Create a view
                    array = array[0:updated_group_size]
                    # NOTE: No parent for the data, Python managing the life cycle of it (not Qt)
                    data = scan_model.Data(None, array, receivedTime=now)
                    channel.setData(data)
                    channels.append(channel)

                # The group name can be the master device name
                if group_name.startswith("top:"):
                    master_name = group_name[4:]
                    # FIXME: Should be fired by the Scan object (but here we have more informations)
                    scan._fireScanDataUpdated(masterDeviceName=master_name)
                else:
                    # FIXME: Should be fired by the Scan object (but here we have more informations)
                    scan._fireScanDataUpdated(channels=channels)

    def __update_channel_data(
        self, cache: _ScanCache, channel_name, raw_data, frame_id=None, source=None
    ):
        now = time.time()
        scan = cache.scan

        if cache.is_ignored(channel_name):
            return

        if cache.data_storage.has_channel(channel_name):
            # This object should go to another place
            assert False
        else:
            # Everything which do not except synchronization (images and MCAs)
            channel = scan.getChannelByName(channel_name)
            if channel is None:
                cache.ignore_channel(channel_name)
                _logger.error("Channel '%s' not described in scan_info", channel_name)
            else:
                # NOTE: No parent for the data, Python managing the life cycle of it (not Qt)
                data = scan_model.Data(
                    None, raw_data, frameId=frame_id, source=source, receivedTime=now
                )
                channel.setData(data)
                # FIXME: Should be fired by the Scan object (but here we have more informations)
                scan._fireScanDataUpdated(channelName=channel.name())

    def get_alive_scans(self) -> list[scan_model.Scan]:
        return [v.scan for v in self.__cache.values()]

    def on_scan_finished(self, scan_key: str, scan_info: dict):
        _logger.debug("on_scan_finished %s", scan_key)
        if not self.__is_alive_scan(scan_key):
            _logger.debug("end_scan from %s ignored", scan_key)
            return

        cache = self.__get_scan_cache(scan_key)
        if cache is None:
            return
        try:
            self._end_scan(cache)
        finally:
            # Clean up cache
            del self.__cache[cache.scan_id]

            scan = cache.scan
            scan._setFinalScanInfo(scan_info)
            scan._setState(scan_model.ScanState.FINISHED)
            scan.scanFinished.emit()

            if self.__flintModel is not None:
                self.__flintModel.removeAliveScan(scan)

            if len(self.__cache) == 0:
                self._end_scan_event.set()

    def _end_scan(self, cache: _ScanCache):
        # Make sure all the previous data was processed
        # Cause it can be processed by another greenlet
        self._end_data_process_event.wait()
        scan = cache.scan

        get_scan_category(scan_info=scan.scanInfo())
        scan_category = scan.type()
        # If not None, that's default scans known to have aligned data
        default_scan = scan_category is not None
        push_non_aligned_data = not default_scan

        def is_same_data(
            array1: numpy.ndarray | None, data2: scan_model.Data | None
        ) -> bool:
            if data2 is not None:
                array2 = data2.array()
            else:
                array2 = None
            if array1 is None and array2 is None:
                return True
            if array1 is None or array2 is None:
                return False
            return array1.shape == array2.shape

        updated_masters = set([])
        for group_name in cache.data_storage.groups():
            channels0 = cache.data_storage.get_channels_by_group(group_name)
            for channel_name in channels0:
                channel = scan.getChannelByName(channel_name)
                if channel is None:
                    _logger.error("Channel '%s' is not available", channel_name)
                    continue
                array = cache.data_storage.get_data_else_none(channel_name)
                previous_data = channel.data()
                if not is_same_data(array, previous_data):
                    if push_non_aligned_data:
                        # NOTE: No parent for the data, Python managing the life cycle of it (not Qt)
                        data = scan_model.Data(None, array)
                        channel.setData(data)
                        updated_masters.add(group_name)
                    else:
                        # FIXME: THis is a hack, this should be managed in the GUI side
                        _logger.warning(
                            "Channel '%s' truncated to be able to display the data",
                            channel_name,
                        )

        # Make sure the last image is displayed
        for channel_name, lima_client in cache.lima_clients():
            # TODO should image be read anyway there ? Maybe we already have it
            image_data = lima_client.get_last_live_image()
            self.__update_channel_data(
                cache,
                channel_name,
                raw_data=image_data.array,
                frame_id=image_data.frame_id,
                source="memory",
            )

        if len(updated_masters) > 0:
            # FIXME: Should be fired by the Scan object (but here we have more informations)
            for group_name in updated_masters:
                if group_name.startswith("top:"):
                    master_name = group_name[4:]
                    scan._fireScanDataUpdated(masterDeviceName=master_name)
                else:
                    channels: list[scan_model.Channel] = []
                    channel_names = cache.data_storage.get_channels_by_group(group_name)
                    for channel_name in channel_names:
                        channel = scan.getChannelByName(channel_name)
                        if channel is not None:
                            channels.append(channel)
                    scan._fireScanDataUpdated(channels=channels)

    def wait_end_of_scans(self):
        self._end_scan_event.wait()

    def wait_data_processed(self):
        """Wait gevent processing of the already received data

        This should only be used by use tests.
        """
        self._end_data_process_event.wait()
