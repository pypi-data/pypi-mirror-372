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

import logging
from typing import NamedTuple

_logger = logging.getLogger(__name__)


class PositionerDescription(NamedTuple):
    name: str
    start: float | None
    end: float | None
    dial_start: float | None
    dial_end: float | None
    units: str | None


def get_all_positioners(scan_info: dict) -> list[PositionerDescription]:
    result: list[PositionerDescription] = []
    positioners = scan_info.get("positioners", None)
    if positioners is None:
        return result

    def zipdict(*args):
        keys = []
        for d in args:
            if d is not None:
                for k in d.keys():
                    #  Add keys in a conservative order
                    if k not in keys:
                        keys.append(k)
        for k in keys:
            result = [k]
            for d in args:
                if d is None:
                    v = None
                else:
                    v = d.get(k, None)
                result.append(v)
            yield result

    positioners_dial_start = positioners.get("positioners_dial_start", None)
    positioners_dial_end = positioners.get("positioners_dial_end", None)
    positioners_start = positioners.get("positioners_start", None)
    positioners_end = positioners.get("positioners_end", None)
    positioners_units = positioners.get("positioners_units", None)
    meta = [
        positioners_start,
        positioners_end,
        positioners_dial_start,
        positioners_dial_end,
        positioners_units,
    ]
    for key, start, end, dial_start, dial_end, units in zipdict(*meta):
        p = PositionerDescription(key, start, end, dial_start, dial_end, units)
        result.append(p)
    return result
