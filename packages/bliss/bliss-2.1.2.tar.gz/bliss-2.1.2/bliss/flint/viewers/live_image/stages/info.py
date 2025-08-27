# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

import enum


class ImageCorrections(enum.Enum):
    FLAT_CORRECTION = "flat"
    DARK_CORRECTION = "dark"
    FLATFIELD_CORRECTION = "flatfield"
    MASK_CORRECTION = "mask"
    EXPOTIME_CORRECTION = "expotime"


class ImageLayer(enum.Enum):
    RAW = "raw"
    FLAT = "flat"
    DARK = "dark"
    MASK = "mask"
    SATURATION = "saturation"
