# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

"""Helper relative to QSettings"""

from __future__ import annotations
import logging
import enum
from silx.gui import qt

_logger = logging.getLogger(__name__)


def setNamedTuple(settings: qt.QSettings, data):
    """Write a named tuple into this settings"""
    for key, value in data._asdict().items():
        if isinstance(value, enum.Enum):
            # Unpack the enums to store a resilient object
            if hasattr(value, "code"):
                value = value.code
            elif hasattr(value, "value"):
                value = value.value
        settings.setValue(key, value)


def namedTuple(settings: qt.QSettings, datatype, defaultData=None):
    """Read a named tuple from the requested type using this settings"""
    content = {}
    for key in datatype._fields:
        if not settings.contains(key):
            continue
        try:
            # FIXME: Dirty hack cause int are read as string
            for dt in datatype.__mro__:
                # With python < 3.10 there is no need to iter the MRO
                if key not in dt.__annotations__:
                    continue
                keytype = dt.__annotations__[key]
                introspect = str(keytype)
                readtype: type | None
                if "Optional[int]" in introspect or "int | None" in introspect:
                    readtype = int
                elif "Optional[float]" in introspect or "float | None" in introspect:
                    readtype = float
                else:
                    readtype = None
                # Note: we can't use type= here, cause optional can be both the right type or None
                value = settings.value(key)
                if value is not None and readtype is not None:
                    value = readtype(value)
                content[key] = value
                break
        except Exception:
            _logger.error(
                "Error while reading key [%s] %s from settings",
                settings.group(),
                key,
                exc_info=True,
            )

    if len(content) == 0:
        return defaultData

    try:
        return datatype(**content)
    except Exception:
        _logger.debug(
            "Error while reading key [%s] %s from settings",
            settings.group(),
            key,
            exc_info=True,
        )
        return defaultData
