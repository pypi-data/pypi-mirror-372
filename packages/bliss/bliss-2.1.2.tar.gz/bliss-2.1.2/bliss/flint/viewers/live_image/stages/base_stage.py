# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

from __future__ import annotations

import logging
from silx.gui import qt


_logger = logging.getLogger(__name__)


class BaseStage(qt.QObject):
    """
    Processing managing a filter on an image.

    This can handle `Sink` or `Link` tasks, like a Lima1 server.
    """

    configUpdated = qt.Signal()
    """
    Emitted when the stage configuration was changed.

    Basically the the processing have to be redone.
    """

    sinkResultUpdated = qt.Signal()
    """
    Emitted when a sink result was updated.

    This means the stage hold processed data.
    """

    def __init__(self, parent: qt.QObject | None = None):
        qt.QObject.__init__(self, parent=parent)
        self.__isEnabled = False
        self.__applyedCorrections: list = []

    def _findRelatedWidget(self):
        """Returns the first known QWidget, else None"""
        p = self.parent()
        while p is not None:
            if isinstance(p, qt.QWidget):
                return p
            p = p.parent()
        return None

    def setEnabled(self, enabled: bool):
        if self.__isEnabled == enabled:
            return
        self.__isEnabled = enabled
        self.configUpdated.emit()

    def isEnabled(self):
        return self.__isEnabled

    def lastApplyedCorrections(self):
        """Returns the last used corrections during the last use of `correction`"""
        return self.__applyedCorrections

    def _resetApplyedCorrections(self):
        self.__applyedCorrections = []

    def _setApplyedCorrections(self, corrections):
        self.__applyedCorrections = corrections
