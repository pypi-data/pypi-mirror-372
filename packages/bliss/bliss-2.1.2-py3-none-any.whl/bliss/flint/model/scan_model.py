# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.
"""This module provides object to model a scan acquisition process.

This tree structure is supposed to be real-only when a scan was
started. During the scan, only data of channels are updated.

.. image:: _static/flint/model/scan_model.png
    :alt: Scan model
    :align: center

.. image:: _static/flint/model/scan_model_group.png
    :alt: Scan model
    :align: center

Channels can be structured by groups. Scatter groups are described in a specific
structure to provide helpers. Channels can be reached by axis id, or channels
which are not part of axis (named counters).
"""

from __future__ import annotations
from typing import NamedTuple, Any
from collections.abc import Iterator

import logging
import numpy
import enum
import weakref
import datetime

from silx.gui import qt


_logger = logging.getLogger(__name__)


class SealedError(Exception):
    """Exception occurred when an object is sealed."""

    def __init__(self, message=None):
        if message is None:
            message = "The object is sealed, then not anymore editable."
        super(SealedError, self).__init__(message)


class _Sealable:
    """Abstract class for sealable object."""

    def __init__(self):
        self.__isSealed = False

    def seal(self):
        self.__isSealed = True

    def isSealed(self):
        return self.__isSealed


class ScanDataUpdateEvent:
    """Event containing the list of the updated channels.

    This event is shared by the `Scan` signal `scanDataUpdated`.
    """

    def __init__(
        self,
        scan: Scan,
        masterDevice: Device | None = None,
        channel: Channel | None = None,
        channels: list[Channel] | None = None,
    ):
        """Event emitted when data from a scan is updated.

        `masterDevice` and `channel` can't be used both at the same time.

        Args:
            scan: The source scan of this event
            masterDevice: The root device from the acquisition chain tree which
                emit this event. In this case all the sub-channels have to be
                updated (except image and MCA channels, which always have specific
                event).
            channel: The channel source of this event
        """
        nb = sum([channel is not None, channels is not None, masterDevice is not None])
        if nb > 1:
            raise ValueError("Only a single attribute have to be set")
        self.__masterDevice = masterDevice
        self.__channel = channel
        self.__channels = channels
        self.__scan = scan
        self.__channelNames: set[str] | None = None
        """Cache used channel names, in case it was reached"""

    def scan(self) -> Scan:
        return self.__scan

    def selectedDevice(self) -> Device | None:
        return self.__masterDevice

    def selectedChannel(self) -> Channel | None:
        return self.__channel

    def selectedChannels(self) -> list[Channel] | None:
        return self.__channels

    def __eq__(self, other):
        if not isinstance(other, ScanDataUpdateEvent):
            return False
        return self.__channel is other.selectedChannel()

    def updatedChannelNames(self) -> set[str]:
        if self.__channelNames is None:
            channelNames = {c.name() for c in self.iterUpdatedChannels()}
            self.__channelNames = channelNames
        return self.__channelNames

    def isUpdatedChannelName(self, channelName: str) -> bool:
        updatedChannels = self.updatedChannelNames()
        return channelName in updatedChannels

    def __iterUpdatedDevices(self):
        if self.__channel is not None:
            yield self.__channel.device()
            return
        for device in self.__scan.devices():
            if self.__masterDevice is not None:
                if device is not self.__masterDevice:
                    if not device.isChildOf(self.__masterDevice):
                        continue
            yield device

    def iterUpdatedChannels(self):
        if self.__channel is not None:
            yield self.__channel
            return
        if self.__channels is not None:
            for channel in self.__channels:
                yield channel
            return
        for device in self.__iterUpdatedDevices():
            for channel in device.channels():
                if channel.type() == ChannelType.COUNTER:
                    yield channel

    def __str__(self):
        # Update the cache
        self.updatedChannelNames()
        return f"md:{self.__masterDevice} c:{self.__channel} cs:{self.__channels} sc:{self.__scan} cns:{self.__channelNames}"


class ScanFeatures(enum.Flag):
    """Normalized set of features that can be extracted from the scan description"""

    NONE = 0
    """None state"""

    INFINITY_SCAN = enum.auto()
    """An infinity amount of points stomanually stopped by the user at some point"""

    DEFAULT_POINT = enum.auto()
    """A default single point"""

    DEFAULT_NSCAN = enum.auto()
    """A default npoint scan"""

    DEFAULT_MESH = enum.auto()
    """A default mesh scan"""


class ScanState(enum.Enum):
    INITIALIZED = 0
    PROCESSING = 1
    FINISHED = 2


class ScanEndReason(enum.Enum):
    FAILURE = "FAILURE"
    DELETION = "DELETION"
    USER_ABORT = "USER_ABORT"
    SUCCESS = "SUCCESS"
    UNKNOWN = "UNKNOWN"
    """The state returned by BLISS is unkown"""


class Scan(qt.QObject, _Sealable):
    """Description of the scan object.

    A scan object contains all the informations generated by Redis about a scan.

    The data structure is fixed during a scan. Only channel data will be updated
    to be updated.

    It provides:

    - Signals for the life cycle of the scan (`scanStarted`, `scanDataUpdated`...)
    - A tree of `Device`, and `Channel` objects, plus helper to reach them.
    - The raw `scan_info`
    - Helper to cache information at the `Scan` level (which have a meaning
        during the scan life cycle)
    """

    scanStarted = qt.Signal()
    """Emitted when the scan acquisition starts"""

    scanSuccessed = qt.Signal()
    """Emitted when the scan acquisition succeeded."""

    scanFailed = qt.Signal()
    """Emitted when the scan acquisition failed."""

    scanFinished = qt.Signal()
    """Emitted when the scan acquisition finished.

    This signal is emitted after `scanFailed` or `scanFinished`.
    """

    scanDataUpdated = qt.Signal([], [ScanDataUpdateEvent])

    def __init__(self, parent=None):
        qt.QObject.__init__(self, parent=parent)
        _Sealable.__init__(self)
        self.__devices: list[Device] = []
        self.__channels: dict[str, Channel] | None = None
        self.__cacheData: dict[object, object] = {}
        self.__cacheMessage: dict[object, tuple[int, str | None]] = {}
        self.__scanInfo = {}
        self.__finalScanInfo = {}
        self.__state = ScanState.INITIALIZED
        self.__group = None
        self.__scatterData: list[ScatterData] = []
        self.__scanKey: str | None = None
        self.__features: ScanFeatures = ScanFeatures.NONE

    def _setState(self, state: ScanState):
        """Private method to set the state of the scan."""
        self.__state = state

    def state(self) -> ScanState:
        """Returns the state of the scan."""
        return self.__state

    def seal(self):
        for device in self.__devices:
            device.seal()
        for scatterData in self.__scatterData:
            scatterData.seal()
        self.__cacheChannels()
        super(Scan, self).seal()

    def setGroup(self, group):
        self.__group = weakref.ref(group)

    def group(self):
        if self.__group is None:
            return None
        return self.__group()

    def setBlissDataScanKey(self, scanKey: str):
        self.__scanKey = scanKey

    def blissDataScanKey(self) -> str | None:
        return self.__scanKey

    def setScanInfo(self, scanInfo: dict[str, Any]):
        if self.isSealed():
            raise SealedError()
        # FIXME: It would be good to create a read-only recursive proxy to expose it
        self.__scanInfo = scanInfo
        from ..scan_info_parser import categories

        self.__features = categories.parse_features(scanInfo)

    def scanInfo(self) -> dict[str, object]:
        return self.__scanInfo

    def features(self) -> ScanFeatures:
        return self.__features

    def scanId(self) -> int | None:
        """Number which is not expected to be unique.

        It is most probably unique (only during a single live cycle of a BLISS session).
        """
        scan_nb = self.scanInfo().get("scan_nb", None)
        if scan_nb is None:
            return None
        try:
            return int(scan_nb)  # type: ignore
        except ValueError:
            _logger.debug("Scan contains wrong scan_nb field. Found %s", type(scan_nb))
            return None

    def scanUniqueId(self) -> str:
        """String which is unique and shared with the BLISS session.

        For now it returns the scan `scan_key` else the mangled python id.
        """
        if self.__scanKey is None:
            return f"python:{id(self)}"
        return self.__scanKey

    def type(self) -> str | None:
        """Returns the scan type stored in the scan info"""
        return self.__scanInfo.get("type", None)

    def hasPlotDescription(self) -> bool:
        """True if the scan contains plot description"""
        return len(self.__scanInfo.get("plots", [])) > 0

    def _setFinalScanInfo(self, scanInfo: dict[str, object]):
        self.__finalScanInfo = scanInfo

    def finalScanInfo(self) -> dict[str, object]:
        return self.__finalScanInfo

    def endReason(self) -> ScanEndReason:
        """Reason at the termination of the scan"""
        info = self.finalScanInfo()
        reason = info.get("end_reason")
        try:
            return ScanEndReason(reason)
        except ValueError:
            _logger.warning("Scan %s end_reason %s is unknown", self.scanId(), reason)
            return ScanEndReason.UNKNOWN

    def addDevice(self, device: Device):
        if self.isSealed():
            raise SealedError()
        if device in self.__devices:
            raise ValueError("Already in the device list")
        self.__devices.append(device)

    def findDeviceByName(
        self, name: str, devtype: DeviceType | None = None
    ) -> Device | None:
        """
        Returns a device from an absolute path name.

        Arguments:
            name: Name of the device
            devtype: Type of the device
        """
        for device in self.__devices:
            if device.name() != name:
                continue
            if type is not None and device.type() != devtype:
                continue
            return device
        return None

    def getDeviceByName(self, name: str, fromTopMaster=False, oneOf=False) -> Device:
        """
        Returns a device from an absolute path name.

        Arguments:
            fromTopMaster: If true, the path is relative to the top master
            oneOf: If true returns the first device found using this name.
                   It's a work around, BLISS do not ensure device name to be unique,
                   cause we can find from unittest non unique device names. But
                   this should be enforced at some other places anyway.
        """
        if oneOf:
            for device in self.__devices:
                if device.name() == name:
                    return device
        elif fromTopMaster:
            for topmaster in self.__devices:
                if topmaster.master() is not None:
                    continue
                try:
                    return self.getDeviceByName(topmaster.name() + ":" + name)
                except ValueError:
                    continue
        else:
            elements = name.split(":")
            for device in self.__devices:
                current: Device | None = device
                for e in reversed(elements):
                    if current is None or current.name() != e:
                        break
                    current = current.master()
                else:
                    # The item was found
                    if current is None:
                        return device

        raise ValueError("Device %s not found." % name)

    def _fireScanDataUpdated(
        self,
        channelName: str | None = None,
        masterDeviceName: str | None = None,
        channels: list[Channel] | None = None,
    ):
        self.__cacheData = {}
        # FIXME: Only clean up object relative to the edited channels
        self.__cacheMessage = {}

        if masterDeviceName is None and channelName is None and channels is None:
            # Propagate the event to all the channels of the this scan
            event = ScanDataUpdateEvent(self)
        elif masterDeviceName is not None:
            # Propagate the event to all the channels contained on this device (recursively)
            device = self.getDeviceByName(masterDeviceName)
            event = ScanDataUpdateEvent(self, masterDevice=device)
        elif channels is not None:
            # Propagate the event to many channels
            channel = self.getChannelByName(channelName)
            event = ScanDataUpdateEvent(self, channels=channels)
        elif channelName is not None:
            # Propagate the event to a single channel
            channel = self.getChannelByName(channelName)
            event = ScanDataUpdateEvent(self, channel=channel)
        else:
            assert False
        self.scanDataUpdated[ScanDataUpdateEvent].emit(event)
        self.scanDataUpdated.emit()

    def __cacheChannels(self):
        assert self.__channels is None
        channels = {}
        for device in self.__devices:
            for channel in device.channels():
                name = channel.name()
                if name in channels:
                    _logger.error("Channel named %s is registered 2 times", name)
                channels[name] = channel
        self.__channels = channels

    def devices(self) -> Iterator[Device]:
        return iter(self.__devices)

    def channels(self) -> list[Channel]:
        assert self.__channels is not None
        return list(self.__channels.values())

    def getChannelByName(self, name) -> Channel | None:
        assert self.__channels is not None
        return self.__channels.get(name, None)

    def getChannelNames(self) -> list[str]:
        assert self.__channels is not None
        return list(self.__channels.keys())

    def addScatterData(self, scatterData: ScatterData):
        if self.isSealed():
            raise SealedError()
        self.__scatterData.append(scatterData)

    def getScatterDataByChannel(self, channel: Channel) -> ScatterData | None:
        for data in self.__scatterData:
            if data.contains(channel):
                return data
        return None

    def hasCachedResult(self, obj: object) -> bool:
        """True if the `obj` object have stored cache in this scan."""
        return obj in self.__cacheData

    def getCachedResult(self, obj: object) -> object:
        """Returns a cached data relative to `obj` else raise a `KeyError`."""
        return self.__cacheData[obj]

    def setCachedResult(self, obj: object, result: object):
        """Store a cache data relative to `obj`."""
        self.__cacheData[obj] = result

    def hasCacheValidation(self, obj: object, version: int) -> bool:
        """
        Returns true if this version of the object was validated.
        """
        result = self.__cacheMessage.get(obj, None)
        if result is None:
            return False
        if result[0] != version:
            return False
        return True

    def setCacheValidation(self, obj: object, version: int, result: str | None):
        """
        Set the validation of a mutable object.

        This feature is used to store validation message relative to a scan time.
        When the scan data is updated, this cache have to be stored again.

        The implementation only store a validation for a single version of an
        object. This could change.
        """
        current = self.__cacheMessage.get(obj)
        if current is not None and current[0] == version:
            raise KeyError("Result already stored for this object version")
        self.__cacheMessage[obj] = (version, result)

    def getCacheValidation(self, obj: object, version: int) -> str | None:
        """
        Returns None if the object was validated, else returns a message
        """
        result = self.__cacheMessage[obj]
        if result[0] != version:
            raise KeyError("Version do not match")
        return result[1]

    def startTime(self) -> datetime.datetime | None:
        scanInfo = self.scanInfo()
        startTime = scanInfo.get("start_time", None)
        if startTime is None:
            return None
        # FIXME: Could be cached
        return datetime.datetime.fromisoformat(str(startTime))

    def asTree(self, displayChannels: bool = True) -> str:
        """Debug function to display the scan description as a tree"""
        result = ""

        def printChannels(device: Device, indent: int):
            nonlocal result
            for c in device.channels():
                result += f"{'   ' * indent}|- channel: {c.name()}\n"

        def printDevice(device: Device, indent: int):
            nonlocal result
            result += "   " * indent
            result += "|- "
            result += device.name()
            result += "\n"
            if displayChannels:
                printChannels(device, indent=indent + 1)
            for d in self.__devices:
                if d.master() is device:
                    printDevice(d, indent=indent + 1)

        result += "Scan\n"
        for d in self.__devices:
            if d.master() is None:
                printDevice(d, indent=0)

        return result


class ScanGroup(Scan):
    """Scan group object.

    It can be a normal scan but can contains extra scans.
    """

    subScanAdded = qt.Signal(object)
    """Emitted when a sub scan is added to this scan."""

    def __init__(self, parent=None):
        Scan.__init__(self, parent=parent)
        self.__subScans = []

    def addSubScan(self, scan: Scan):
        self.__subScans.append(scan)
        self.subScanAdded.emit(scan)

    def subScans(self) -> list[Scan]:
        return list(self.__subScans)


class DeviceType(enum.Enum):
    """Enumerate the kind of devices"""

    NONE = 0
    """Default type"""

    UNKNOWN = -1
    """Unknown value specified in the scan_info"""

    LIMA = 1
    LIMA2 = 10
    """Lima device as specified by the scan_info"""

    MCA = 2
    """MCA device as specified by the scan_info"""

    MOSCA = 20
    """Mosca device as specified by the scan_info"""

    VIRTUAL_ROI = 3
    """Device containing channel data from the same ROI.
    It is a GUI concept, there is no related device on the BLISS side.
    """

    VIRTUAL_MCA_DETECTOR = 4
    """Device containing channel data from a MCA detector.

    A MCA device can contain many detectors.
    """

    VIRTUAL_MOSCA_STATS = 5
    """Device containing statistics channel data from a MCA detector.

    A MCA device can contain many detectors.
    """

    LIMA_SUB_DEVICE = 11
    """Sub device of Lima."""

    VIRTUAL_CHAIN = 100
    """Virtual device which represents the chain

    It is the only device without master
    """


class DeviceMetadata(NamedTuple):
    info: dict[str, object]
    """raw metadata as stored by the scan_info"""

    roi: object | None
    """Define a ROI geometry, is one"""


class Device(qt.QObject, _Sealable):
    """
    Description of a device.

    In the GUI side, a device is an named object which can contain other devices
    and channels. This could not exactly match the Bliss API.
    """

    _noneMetadata = DeviceMetadata({}, None)

    def __init__(self, parent: Scan):
        qt.QObject.__init__(self, parent=parent)
        _Sealable.__init__(self)
        self.__name: str = ""
        self.__metadata: DeviceMetadata = self._noneMetadata
        self.__type: DeviceType = DeviceType.NONE
        self.__channels: list[Channel] = []
        self.__master: Device | None = None
        self.__topMaster: Device | None = None
        self.__isMaster: bool = False
        parent.addDevice(self)

    def scan(self) -> Scan:
        return self.parent()

    def devices(self) -> Iterator[Device]:
        """List sub devices from this device"""
        for d in self.scan().devices():
            if d.isChildOf(self):
                yield d

    def seal(self):
        for channel in self.__channels:
            channel.seal()
        super(Device, self).seal()

    def setName(self, name: str):
        if self.isSealed():
            raise SealedError()
        self.__name = name

    def name(self) -> str:
        return self.__name

    def stableName(self):
        """Device name which stays the same between 2 scans.

        This name is a guess, which is aimed to be stable also when the
        acquisition chain structure change.

        Each short name is separated by ":".
        """
        elements = [self.name()]
        parent = self.__master
        while parent is not None:
            elements.append(parent.name())
            if parent.type() not in [
                DeviceType.VIRTUAL_MCA_DETECTOR,
                DeviceType.VIRTUAL_MOSCA_STATS,
                DeviceType.VIRTUAL_ROI,
                DeviceType.LIMA_SUB_DEVICE,
            ]:
                break
            parent = parent.__master
        return ":".join(reversed(elements))

    def fullName(self):
        """Path name from top master to this device.

        Each short name is separated by ":".
        """
        elements = [self.name()]
        parent = self.__master
        while parent is not None:
            elements.append(parent.name())
            parent = parent.__master
        return ":".join(reversed(elements))

    def setMetadata(self, metadata: DeviceMetadata):
        if self.isSealed():
            raise SealedError()
        self.__metadata = metadata

    def metadata(self) -> DeviceMetadata:
        """
        Returns a bunch of metadata stored within the channel.
        """
        return self.__metadata

    def addChannel(self, channel: Channel):
        if self.isSealed():
            raise SealedError()
        if channel in self.__channels:
            raise ValueError("Already in the channel list")
        self.__channels.append(channel)

    def channels(self) -> Iterator[Channel]:
        return iter(self.__channels)

    def setMaster(self, master: Device | None):
        if self.isSealed():
            raise SealedError()
        self.__master = master
        self.__topMaster = None

    def master(self) -> Device | None:
        """
        FIXME: This have to be renamed, because here it is about parent
               structure, while master is about triggers
        """
        return self.__master

    def topMaster(self) -> Device:
        """
        FIXME: Rename it as chain, the top master is the first master of
               the chain, which is not the same
        """
        if self.__topMaster is None:
            topMaster = self
            while topMaster:
                m = topMaster.master()
                if m is None:
                    break
                topMaster = m
            self.__topMaster = topMaster
        return self.__topMaster

    def setIsMaster(self, isMaster: bool):
        if self.isSealed():
            raise SealedError()
        self.__isMaster = isMaster

    def isMaster(self) -> bool:
        """
        True if the device is a master device.
        """
        return self.__isMaster

    def isChildOf(self, master: Device) -> bool:
        """Returns true if this device is the child of `master` device."""
        parent = self.__master
        while parent is not None:
            if parent is master:
                return True
            parent = parent.__master
        return False

    def setType(self, deviceType: DeviceType):
        if self.isSealed():
            raise SealedError()
        self.__type = deviceType

    def type(self) -> DeviceType:
        """
        Returns the kind of this channel.
        """
        return self.__type


class ChannelTypeMeta(NamedTuple):
    dim: int
    """Data dim stored in this channel"""

    def __eq__(self, other):
        return self is other

    def __ne__(self, other):
        return self is not other


class ChannelType(enum.Enum):
    """Enumerate the kind of channels"""

    COUNTER = ChannelTypeMeta(dim=1)
    """Type of channel which store a single data per trigger.
    The sequence of acquisition is stored."""

    SPECTRUM = ChannelTypeMeta(dim=1)
    """Type of channel which store a list of data per trigger.

    Only the latest data is stored."""

    SPECTRUM_D_C = ChannelTypeMeta(dim=2)
    """Type of channel which store a stack of spectrum.

    Axis order is the following: `detector, channel`

    Only the latest data is stored."""

    VECTOR = ChannelTypeMeta(dim=1)
    """Type of channel which store a 1d data per trigger.

    Only the latest data is stored."""

    IMAGE = ChannelTypeMeta(dim=2)
    """Type of channel which store a 2d image per trigger.

    Only the latest data is stored."""

    IMAGE_C_Y_X = ChannelTypeMeta(dim=3)
    """Type of channel which store a 2d image per channel per trigger.

    Only the latest data is stored."""

    UNKNOWN = ChannelTypeMeta(dim=False)
    """Unknown type of channel.
    """


class AxisKind(enum.Enum):
    FORTH = "forth"
    BACKNFORTH = "backnforth"
    STEP = "step"

    # Deprecated code from user scripts from BLISS 1.4
    FAST = "fast"
    # Deprecated code from user scripts from BLISS 1.4
    FAST_BACKNFORTH = "fast-backnforth"
    # Deprecated code from user scripts from BLISS 1.4
    SLOW = "slow"
    # Deprecated code from user scripts from BLISS 1.4
    SLOW_BACKNFORTH = "slow-backnforth"


class ChannelMetadata(NamedTuple):
    start: float | None
    stop: float | None
    min: float | None
    max: float | None
    points: int | None
    axisId: int | None
    axisPoints: int | None
    axisKind: AxisKind | None
    group: str | None
    axisPointsHint: int | None
    dim: int | None
    decimals: int | None


class ScatterData(_Sealable):
    """Data structure of a scatter"""

    def __init__(self):
        super(ScatterData, self).__init__()
        self.__channels: list[list[Channel]] = []
        self.__noIndexes: list[Channel] = []
        self.__contains: set[Channel] = set([])
        self.__values: list[Channel] = []

    def maxDim(self):
        return len(self.__channels)

    def channelsAt(self, axisId: int) -> list[Channel]:
        """Returns the list of channels stored at this axisId"""
        return self.__channels[axisId]

    def findGroupableAt(self, axisId: int) -> Channel | None:
        """Returns a channel which can be grouped at a specific axisId"""
        for channel in self.channelsAt(axisId):
            if channel.metadata().axisKind == AxisKind.STEP:
                return channel
        return None

    def channelAxis(self, channel: Channel):
        for i in range(len(self.__channels)):
            if channel in self.__channels[i]:
                return i
        raise IndexError()

    def counterChannels(self):
        return list(self.__values)

    def addAxisChannel(self, channel: Channel, axisId: int):
        """Add channel as an axis of the scatter"""
        if self.isSealed():
            raise SealedError()
        if axisId is None:
            self.__noIndexes.append(channel)
        else:
            while len(self.__channels) <= axisId:
                self.__channels.append([])
            self.__channels[axisId].append(channel)
        self.__contains.add(channel)

    def addCounterChannel(self, channel: Channel):
        """Add channel used as a counter"""
        self.__values.append(channel)

    def contains(self, channel: Channel) -> bool:
        return channel in self.__contains

    def seal(self):
        for channel in self.__noIndexes:
            self.__channels.append([channel])
        del self.__noIndexes
        super(ScatterData, self).seal()

    def shape(self):
        """Returns the theorical ndim shape based on channels metadata.

        It is supported by numpy arrays. If a channel do not have `axisPoints`
        specified, -1 is used.
        """
        result = []
        for axisId in range(self.maxDim()):
            size = None
            for channel in self.__channels[axisId]:
                size = channel.metadata().axisPoints
                if size is not None:
                    break
            result.append(size)
        return tuple(reversed(result))


class Channel(qt.QObject, _Sealable):
    """
    Description of a channel.

    In the GUI side, a channel is leaf of the scan tree, which contain the raw
    data from Bliss through Redis.

    A channel have a specific data kind which can't change during the scan.
    It will only be feed with this kind of data.
    """

    dataUpdated = qt.Signal(object)
    """Emitted when setData is invoked.
    """

    _noneMetadata = ChannelMetadata(
        None, None, None, None, None, None, None, None, None, None, None, None
    )

    _dimToType = {
        0: ChannelType.COUNTER,
        1: ChannelType.VECTOR,
        2: ChannelType.IMAGE,
        3: ChannelType.IMAGE_C_Y_X,
    }

    def __init__(self, parent: Device):
        qt.QObject.__init__(self, parent=parent)
        _Sealable.__init__(self)
        self.__data: Data | None = None
        self.__metadata: ChannelMetadata = self._noneMetadata
        self.__name: str = ""
        self.__type: ChannelType | None = None
        self.__displayName: str | None = None
        self.__displayDecimals: int | None = None
        self.__unit: str | None = None
        self.__refreshRates: dict[str, int] = {}
        self.__updatedCount = 0
        parent.addChannel(self)

    def setType(self, channelType: ChannelType):
        if self.isSealed():
            raise SealedError()
        self.__type = channelType

    def type(self) -> ChannelType:
        """
        Returns the kind of this channel.

        FIXME this have to be property checked before remove (use device type instead or not)
        """
        if self.__type is None:
            dim = self.__metadata.dim
            if dim is None:
                dim = 0
            return self._dimToType.get(dim, ChannelType.UNKNOWN)
        return self.__type

    def setMetadata(self, metadata: ChannelMetadata):
        if self.isSealed():
            raise SealedError()
        self.__metadata = metadata

    def metadata(self) -> ChannelMetadata:
        """
        Returns a bunch of metadata stored within the channel.
        """
        return self.__metadata

    def setDisplayName(self, displayName: str):
        if self.isSealed():
            raise SealedError()
        self.__displayName = displayName

    def displayName(self) -> str | None:
        """
        Returns the preferred display name of this channel.
        """
        return self.__displayName

    def setUnit(self, unit: str):
        if self.isSealed():
            raise SealedError()
        self.__unit = unit

    def unit(self) -> str | None:
        """
        Returns the unit of this channel.
        """
        return self.__unit

    def device(self) -> Device:
        """
        Returns the device containing this channel.
        """
        return self.parent()

    def master(self) -> Device:
        """
        Returns the first master containing this channel.
        """
        parent = self.device()
        if parent.isMaster():
            return parent
        else:
            m = parent.master()
            assert m is not None
            return m

    def name(self) -> str:
        """
        Returns the full name of the channel.

        It is a unique identifier during a scan.
        """
        return self.__name

    def baseName(self) -> str:
        """
        Returns the trail sequence of the channel name.
        """
        return self.__name.split(":")[-1]

    @property
    def ndim(self) -> int:
        """
        Returns the amount of dimensions of the data, before reaching the data.

        Mimics numpy arrays."""
        dim = self.__metadata.dim
        if dim is not None:
            if dim == 0:
                # scalar are stored with an extra "time/step" dimension
                return dim + 1
            return dim

        if self.__type is None:
            return False

        return self.__type.value.dim

    def setName(self, name: str):
        if self.isSealed():
            raise SealedError()
        self.__name = name

    def hasData(self) -> bool:
        """
        True if a data is set to this channel.

        A channel can contain nothing during a scan.
        """
        return self.__data is not None

    def data(self) -> Data | None:
        """
        Returns the data associated to this channel.

        It is the only one attribute which can be updated during a scan.
        """
        return self.__data

    def array(self) -> numpy.ndarray | None:
        """
        Returns the array associated to this channel.

        This method is a shortcut to `.data().array()`.
        """
        if self.__data is None:
            return None
        return self.__data.array()

    def isDataCompatible(self, data: Data) -> bool:
        """
        True if this `data` is compatible with this channel.
        """
        if data is None:
            return True
        array = data.array()
        if array is None:
            return True
        if self.ndim == array.ndim:
            return True
        if self.type() == ChannelType.IMAGE:
            if array.ndim == 3:
                if array.shape[2] in [3, 4]:
                    return True
        return False

    def setData(self, data: Data):
        """
        Set the data associated to this channel.

        If the data is updated the signal `dataUpdated` is invoked.
        """
        if not self.isDataCompatible(data):
            raise ValueError("Data do not fit the channel requirements")
        if self.__data is data:
            return
        self.__updatedCount += 1
        self.__data = data
        self.dataUpdated.emit(data)

    def setPreferedRefreshRate(self, key: str, rate: int | None):
        """Allow to specify the prefered refresh rate.

        It have to be specified in millisecond.
        """
        if rate is None:
            if key in self.__refreshRates:
                del self.__refreshRates[key]
        else:
            self.__refreshRates[key] = rate

    def preferedRefreshRate(self) -> int | None:
        if len(self.__refreshRates) == 0:
            return None
        return min(self.__refreshRates.values())

    def updatedCount(self) -> int:
        """Amount of time the data was updated."""
        return self.__updatedCount


class Data(qt.QObject):
    """
    Store a `numpy.array` associated to a channel.

    This object was designed to be non-mutable in order to allow fast comparison,
    and to store metadata relative to the measurement (like unit, error) or
    helper to deal with the data (like hash). Could be renamed into `Quantity`.
    """

    def __init__(
        self,
        parent=None,
        array: numpy.ndarray | None = None,
        frameId: int | None = None,
        source: str | None = None,
        receivedTime: float | None = None,
    ):
        qt.QObject.__init__(self, parent=parent)
        self.__array = array
        self.__frameId = frameId
        self.__source = source
        self.__receivedTime = receivedTime

    def array(self) -> numpy.ndarray | None:
        return self.__array

    def frameId(self) -> int | None:
        """Frame number, only valid for images"""
        return self.__frameId

    def source(self) -> str | None:
        """Source of the image, only valid for images"""
        return self.__source

    def receivedTime(self) -> float | None:
        """Timestamp in second when the application received this data"""
        return self.__receivedTime
