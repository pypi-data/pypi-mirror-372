# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

from __future__ import annotations

from .lima_profile_roi import LimaProfileRoi


class LimaVProfileRoi(LimaProfileRoi):
    """
    Lima ROI for vertical profile.

    It displays a rectangle ROI with extra overlay to show that there is
    a horizontal reduction of the data.
    """

    ICON = "flint:icons/add-hreduction"
    NAME = "hreduction"
    SHORT_NAME = "horizontal reduction"

    def __init__(self, parent=None):
        LimaProfileRoi.__init__(self, parent=parent)
        self.setLimaKind(LimaProfileRoi.Directions.HORIZONTAL_REDUCTION)
