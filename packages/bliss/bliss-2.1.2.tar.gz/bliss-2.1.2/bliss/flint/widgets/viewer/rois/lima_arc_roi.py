# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

from __future__ import annotations

import logging

import silx.gui.plot.items.roi as silx_rois

_logger = logging.getLogger(__name__)


class LimaArcRoi(silx_rois.ArcROI):
    """Arc ROI used to configure Lima detector.

    It is used to count sum, avg, min, max
    """

    def clone(self):
        newRoi = type(self)()
        newRoi.setGeometry(
            center=self.getCenter(),
            innerRadius=self.getInnerRadius(),
            outerRadius=self.getOuterRadius(),
            startAngle=self.getStartAngle(),
            endAngle=self.getEndAngle(),
        )
        return newRoi
