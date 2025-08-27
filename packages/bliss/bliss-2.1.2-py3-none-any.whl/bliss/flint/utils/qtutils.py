# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

from silx.gui import qt
from silx.gui import icons


getQIcon = icons.getQIcon


def getOnOffQIcon(nameOn: str, nameOff: str) -> qt.QIcon:
    on = icons.getQPixmap(nameOn)
    off = icons.getQPixmap(nameOff)
    icon = qt.QIcon()
    icon.addPixmap(on, qt.QIcon.Normal, qt.QIcon.Off)
    icon.addPixmap(off, qt.QIcon.Normal, qt.QIcon.On)
    return icon
