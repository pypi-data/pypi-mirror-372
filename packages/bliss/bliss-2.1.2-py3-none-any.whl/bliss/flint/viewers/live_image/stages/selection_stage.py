# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

from __future__ import annotations

import numpy
import logging
from silx.gui import qt
from .base_stage import BaseStage
from bliss.flint.model import scan_model


_logger = logging.getLogger(__name__)


class SelectionStage(BaseStage):
    """
    This stage features a selection of a channel from a multi channel data.

    For non multi channels data the stage is a pass through.
    """

    def __init__(self, parent: qt.QObject | None = None):
        BaseStage.__init__(self, parent=parent)
        self.__channelIndex: int | None = None
        self.__maxChannelIndex: int = 0

    def setupFromChannel(self, dataChannel: scan_model.Channel):
        image = dataChannel.array()
        assert image is not None

        if dataChannel.type() == scan_model.ChannelType.IMAGE_C_Y_X:
            nbChannels = image.shape[0]
            self.setMaxChannelIndex(nbChannels)
            if nbChannels == 0:
                self.setChannelIndex(None)
            if self.__channelIndex is None:
                self.setChannelIndex(0)
            elif self.__channelIndex >= image.shape[0]:
                self.setChannelIndex(0)

        elif dataChannel.type() == scan_model.ChannelType.IMAGE:
            self.setChannelIndex(None)
            self.setMaxChannelIndex(0)

        else:
            raise ValueError(f"Channel type {dataChannel.type()} unsupported")

    def process(self, array: numpy.ndarray):
        if self.__channelIndex is not None:
            return array[self.__channelIndex]
        return array

    def channelIndex(self) -> int | None:
        return self.__channelIndex

    def maxChannelIndex(self) -> int:
        return self.__maxChannelIndex

    def setChannelIndex(self, index: int | None):
        if self.__channelIndex == index:
            return
        self.__channelIndex = index
        self.configUpdated.emit()

    def setMaxChannelIndex(self, maxIndex: int):
        if self.__maxChannelIndex == maxIndex:
            return
        self.__maxChannelIndex = maxIndex
        self.configUpdated.emit()
