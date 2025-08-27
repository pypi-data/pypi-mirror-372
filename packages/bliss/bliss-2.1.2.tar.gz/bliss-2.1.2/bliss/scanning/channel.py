# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

from __future__ import annotations
import functools
import weakref
import numpy
from typing import Any
from abc import ABC, abstractmethod

from bliss.common.event import dispatcher
from bliss.common.axis import Axis
from bliss import global_map

from blissdata.redis_engine.encoding.json import JsonStreamEncoder
from blissdata.redis_engine.encoding.numeric import NumericStreamEncoder


class AcquisitionChannelList(list):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._chan_names_cache = weakref.WeakKeyDictionary()

    def update(self, values_dict):
        """Update all channels and emit the new_data event

        Input:

           values_dict - { channel_name: value, ... }
        """
        if not self._chan_names_cache:
            for channel in self:
                self._chan_names_cache[channel] = (channel.short_name, channel.fullname)

        for channel in self:
            sn, fn = self._chan_names_cache[channel]
            if sn in values_dict:
                channel.emit(values_dict[sn])
            elif fn in values_dict:
                channel.emit(values_dict[fn])

    def update_from_iterable(self, iterable):
        for channel, data in zip(self, iterable):
            channel.emit(data)

    def update_from_array(self, array):
        for i, channel in enumerate(self):
            channel.emit(array[:, i])


class BaseAcquisitionChannel(ABC):
    def __init__(self, name):
        self._name = name

    @property
    @abstractmethod
    def shape(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def dtype(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def info_dict(self):
        raise NotImplementedError

    @property
    def scan_info_dict(self) -> dict[str, Any]:
        """Returns metadata which are stored in the `scan_info["channels"]` field."""
        meta = {}
        short_name = self.short_name
        file_only = self.file_only
        if short_name is not None:
            meta["display_name"] = short_name
        if self.shape is not None:
            meta["dim"] = len(self.shape)
        if file_only is not None:
            meta["file_only"] = file_only
        return meta

    @property
    def encoder(self):
        return self._encoder

    @property
    def file_only(self) -> bool | None:
        """True if the channel is only accessible by file."""
        return None

    @property
    def name(self):
        """If the `name` from the constructor is "A:B" this returns:
        - "A:B"  (when B has no alias)
        - "C"    (when B has alias "C" and A != "axis")
        - "A:C"  (when B has alias "C" and A == "axis")
        """
        prefix, _, last_part = self._name.rpartition(":")
        alias = global_map.aliases.get(last_part)
        if alias:
            if prefix == "axis":
                return f"{prefix}:{alias.name}"
            else:
                return alias.name
        else:
            return self._name

    @property
    def short_name(self):
        """If the `name` from the constructor is "A:B" this returns:
        - "B"   (when B has no alias)
        - "C"   (when B has alias "C")
        """
        _, _, last_part = self.name.rpartition(":")
        return last_part

    @property
    def fullname(self):
        """If the `name` from the constructor is "A:B" this returns:
        - "A:B"     (when B has no alias)
        - "A:C"     (when B has alias "C")
        """
        prefix, _, last_part = self._name.rpartition(":")
        alias = global_map.aliases.get(last_part)
        if alias:
            return f"{prefix}:{alias.name}"
        else:
            return self._name

    def set_stream_writer(self, stream_writer):
        self._stream_writer = stream_writer

    def emit(self, data):
        self._stream_writer.send(data)
        dispatcher.send("new_data", self, data)


class LimaAcquisitionChannel(BaseAcquisitionChannel):
    def __init__(self, name, dtype=None, shape=(-1, -1)):
        super().__init__(name)
        self._dtype = dtype
        self._shape = shape
        self._encoder = JsonStreamEncoder()
        self._lima_info = {}

    @property
    def shape(self):
        return self._shape

    @property
    def dtype(self):
        return self._dtype

    @property
    def info_dict(self):
        return {
            "format": "lima_v1",
            "dtype": numpy.dtype(self._dtype).name,
            "shape": self._shape,
            "lima_info": self._lima_info,
        }


class Lima2AcquisitionChannel(BaseAcquisitionChannel):
    def __init__(self, name, server_urls, dtype, shape, saving_spec, file_only=False):
        super().__init__(name)
        # self._server_url = json.dumps(server_urls)
        self._server_urls = server_urls
        self._dtype = dtype
        self._shape = shape
        self._encoder = JsonStreamEncoder()
        self._saving_spec = saving_spec
        self._file_only = file_only
        self._lima_info = {
            "name": self.short_name,
            "server_urls": self._server_urls,
        }

    @property
    def shape(self):
        return self._shape

    @property
    def dtype(self):
        return self._dtype

    @property
    def file_only(self):
        return self._file_only

    @property
    def saving_spec(self):
        return self._saving_spec

    @property
    def info_dict(self):
        # Stream info for Redis
        return {
            "format": "lima_v2",
            "dtype": numpy.dtype(self._dtype).name,
            "shape": self._shape,
            "lima_info": self._lima_info,
        }


class AcquisitionChannel(BaseAcquisitionChannel):
    def __init__(
        self,
        name: str,
        dtype: numpy.type,
        shape: tuple[int, ...],
        unit: str | None = None,
    ):
        super().__init__(name)
        self._dtype = dtype
        self._shape = shape
        self._encoder = NumericStreamEncoder(dtype, shape)
        self._unit = unit

    @property
    def shape(self):
        return self._shape

    @property
    def dtype(self):
        return self._dtype

    @property
    def unit(self):
        return self._unit

    @property
    def info_dict(self) -> dict[str, Any]:
        """Returns metadata which are stored in the `info` of the redis channels."""
        return {
            "dtype": numpy.dtype(self.dtype).name,
            "shape": self.shape,
            "unit": self.unit,
        }

    @property
    def scan_info_dict(self):
        """Returns metadata which are stored in the `scan_info["channels"]` field."""
        meta = BaseAcquisitionChannel.scan_info_dict.fget(self)
        if self._unit is not None:
            meta["unit"] = self._unit
        return meta

    def emit(self, data):
        data = self._check_and_reshape(data)
        if data.size == 0:
            return
        super().emit(data)

    def _check_and_reshape(self, data):
        # TODO this is actually copied from NumericStreamEncoder, thus the check runs twice...
        data = numpy.asarray(data)

        # ensure data has one more dimension than the point shape
        if data.ndim == len(self.shape) + 1:
            batch = data
        elif data.ndim == len(self.shape):
            batch = data[numpy.newaxis, ...]
        else:
            raise ValueError(
                f"Expected shape {self.shape} or {(-1,) + self.shape}, but received {data.shape}"
            )

        # match shape components, except for free ones (-1 values)
        for expected, actual in zip(self.shape, batch.shape[1:]):
            if expected not in [-1, actual]:
                raise ValueError(
                    f"Expected shape {self.shape} or {(-1,) + self.shape}, but received {data.shape}"
                )

        return batch


class AxisAcquisitionChannel(AcquisitionChannel):
    """An AcquisitionChannel created from a bliss axis.

    It is an helper to simplify extraction of metadata from axis.
    """

    def __init__(self, axis: Axis):
        AcquisitionChannel.__init__(
            self, f"axis:{axis.name}", numpy.double, (), unit=axis.unit
        )
        self._decimals = axis.display_digits

    @property
    def decimals(self) -> int:
        return self._decimals

    @property
    def scan_info_dict(self):
        meta = AcquisitionChannel.scan_info_dict.fget(self)
        if self._decimals is not None:
            meta["decimals"] = self._decimals
        return meta


class SubscanAcquisitionChannel(BaseAcquisitionChannel):
    def __init__(self, name):
        super().__init__(name)
        self._encoder = JsonStreamEncoder()

    @property
    def shape(self):
        return ()

    @property
    def dtype(self):
        return None

    @property
    def info_dict(self):
        return {"format": "subscan"}


def duplicate_channel(source, name=None, conversion=None, dtype=None):
    name = source.name if name is None else name
    dtype = source.dtype if dtype is None else dtype
    dest = AcquisitionChannel(name, dtype, source.shape, unit=source.unit)

    def callback(data, sender=None, signal=None):
        if conversion is not None:
            data = conversion(data)
        dest.emit(data)

    # Louie does not seem to like closure...
    dest._callback = callback

    def connect():
        return dispatcher.connect(callback, "new_data", source)

    connect.__name__ = "connect_" + name

    def cleanup():
        return dispatcher.disconnect(callback, "new_data", source)

    cleanup.__name__ = "cleanup_" + name

    return dest, connect, cleanup


def attach_channels(channels_source, emitter_channel):
    """
    Attaching a channel means that channel data
    is captured by the destination channel, which will re-emit it
    together with its own channel data.
    """

    def new_emitter(data, channel_source=None):
        channel_source._current_data = data

    for channel_source in channels_source:
        if hasattr(channel_source, "_final_emit"):
            raise RuntimeError("Channel %s is already attached to another channel")
        # replaced the final emit data with one which store
        # the current data
        channel_source._final_emit = channel_source.emit
        channel_source.emit = functools.partial(
            new_emitter, channel_source=channel_source
        )
        channel_source._current_data = None

    emitter_method = emitter_channel.emit

    def dual_emiter(data):
        for channel_source in channels_source:
            source_data = channel_source._current_data
            if len(data) > 1:
                try:
                    iter(source_data)
                except TypeError:
                    lst = [source_data]
                else:
                    lst = list(source_data)
                source_data = numpy.array(lst * len(data), dtype=channel_source.dtype)
            channel_source._final_emit(source_data)
        emitter_method(data)

    emitter_channel.emit = dual_emiter
