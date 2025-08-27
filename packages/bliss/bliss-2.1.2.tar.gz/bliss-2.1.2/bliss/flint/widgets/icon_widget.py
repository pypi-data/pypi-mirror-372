# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

from __future__ import annotations

import logging

from silx.gui import qt
from silx.gui import icons

_logger = logging.getLogger(__name__)


class IconWidget(qt.QLabel):
    """
    Widget to display a `QIcon`.

    It supports `setIconName` which use icon from silx resources.
    """

    def __init__(self, parent=None):
        super(IconWidget, self).__init__(parent=parent)
        self.__size = 16, 16
        self.__icon = None

    def setIconSize(self, width, height):
        self.__size = width, height
        self._updateDisplay()

    def setIconName(self, iconName):
        icon = icons.getQIcon(iconName)
        self.setIcon(icon)

    def setIcon(self, icon):
        self.__icon = icon
        self._updateDisplay()

    def _updateDisplay(self):
        icon = self.__icon
        if icon is None:
            return
        pixmap = icon.pixmap(*self.__size)
        self.setPixmap(pixmap)
