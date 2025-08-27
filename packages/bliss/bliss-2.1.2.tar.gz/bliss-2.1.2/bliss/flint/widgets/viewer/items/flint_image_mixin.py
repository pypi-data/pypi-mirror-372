# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

from __future__ import annotations

# FIXME: This have to be refactored to avoid import in this direction
from bliss.flint.viewers.live_image.stages.info import ImageCorrections
from bliss.flint.helper.tooltip_factory import TooltipFactory
from .flint_item_mixin import FlintItemMixIn


class FlintImageMixIn(FlintItemMixIn):
    def __init__(self):
        FlintItemMixIn.__init__(self)
        self.__rawData = None
        self.__tags = []
        self.__channelIndex = None

    def setChannelIndex(self, index):
        self.__channelIndex = index

    def setRawData(self, rawData):
        """Define the raw data if there was corrections"""
        self.__rawData = rawData

    def getTags(self):
        return self.__tags

    def setTags(self, tags):
        self.__tags = tags

    def feedRawTooltip(self, tooltip: TooltipFactory, index):
        if self.__rawData is not None:
            if self.__channelIndex is not None:
                value = self.__rawData[:, index[0], index[1]]
            else:
                value = self.__rawData[index]
            tooltip.addQuantity("Input data", value)

    def feedFlintCorrectionTooltip(self, tooltip: TooltipFactory):
        if self.__tags:
            corrections = ", ".join([c.value for c in self.__tags])
            tooltip.addQuantity("Corrections", corrections)
        else:
            tooltip.addQuantity("Corrections", "None")

    def getUnit(self):
        unit = ""
        if ImageCorrections.EXPOTIME_CORRECTION in self.__tags:
            unit = "/s"
        return unit
