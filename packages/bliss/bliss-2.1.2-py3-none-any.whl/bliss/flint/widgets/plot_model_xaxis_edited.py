# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

import enum
import logging

from silx.gui import qt
from silx.gui import icons

from bliss.flint.model import plot_model
from bliss.flint.model import plot_item_model

_logger = logging.getLogger(__name__)


class PlotModelXaxisEditAction(qt.QAction):
    """Action displaying the state of the edition of a plot model and allow to
    lock or unlock it"""

    class _State(enum.Enum):
        LOCK = "lock"
        UNLOCK = "unlock"

    def __init__(self, parent=None):
        super(PlotModelXaxisEditAction, self).__init__(parent=parent)
        self.triggered.connect(self.__triggered)
        self.__state = None
        self.__plotModel = None
        self.setEnabled(False)
        self.__setState(self._State.UNLOCK)

    def __triggered(self):
        plotModel = self.__plotModel
        if plotModel is None:
            return
        editSource = plotModel.xaxisEditSource()
        if editSource is None:
            plotModel.tagXaxisUserEditTime()
        elif editSource == "user":
            plotModel.tagXaxisRawEdit()

    def setPlotModel(self, plotModel: plot_model.Plot):
        if self.__plotModel is not None:
            self.__plotModel.valueChanged.disconnect(self.__valueChanged)
        if isinstance(plotModel, plot_item_model.CurvePlot):
            self.__plotModel = plotModel
        if self.__plotModel is not None:
            self.__plotModel.valueChanged.connect(self.__valueChanged)
        self.__updateSelectionState()

    def __valueChanged(self, eventType):
        if eventType == plot_model.ChangeEventType.XAXIS_USER_EDIT_TIME:
            self.__updateSelectionState()

    def __updateSelectionState(self):
        plotModel = self.__plotModel
        if plotModel is None:
            self.setEnabled(False)
            self.__setState(self._State.UNLOCK)
        else:
            editSource = plotModel.xaxisEditSource()
            self.setEnabled(True)
            if editSource is None:
                self.__setState(self._State.UNLOCK)
            elif editSource == "user":
                self.__setState(self._State.LOCK)
            else:
                assert False

    def __setState(self, state: _State):
        if self.__state == state:
            return
        self.__state = state

        if self.__state == self._State.LOCK:
            name = "flint:icons/lock-xaxis-closed"
            self.setToolTip(
                "The actual x-axis GUI selection will be reused for new scans"
            )
        elif self.__state == self._State.UNLOCK:
            name = "flint:icons/lock-xaxis-open"
            self.setToolTip("The actual selected x-axis could be updated by a new scan")
        else:
            assert False
        icon = icons.getQIcon(name)
        self.setIcon(icon)
