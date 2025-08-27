# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

from __future__ import annotations

from .lima_profile_roi import LimaProfileRoi


class LimaHProfileRoi(LimaProfileRoi):
    """
    Lima ROI for horizontal profile.

    It displays a rectangle ROI with extra overlay to show that there is
    a vertical reduction of the data.
    """

    ICON = "flint:icons/add-vreduction"
    NAME = "vreduction"
    SHORT_NAME = "vertical reduction"

    def __init__(self, parent=None):
        LimaProfileRoi.__init__(self, parent=parent)
        self.setLimaKind(LimaProfileRoi.Directions.VERTICAL_REDUCTION)
