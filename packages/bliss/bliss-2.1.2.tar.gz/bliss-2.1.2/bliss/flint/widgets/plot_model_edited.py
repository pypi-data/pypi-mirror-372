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


class PlotModelEditAction(qt.QAction):
    """Action displaying the state of the edition of a plot model and allow to
    lock or unlock it"""

    class _State(enum.Enum):
        LOCK = "lock"
        UNLOCK = "unlock"
        UNLOCK_PLOTSELECT = "unlock-plotselect"

    def __init__(self, parent=None):
        super(PlotModelEditAction, self).__init__(parent=parent)
        self.triggered.connect(self.__triggered)
        self.__state = None
        self.__plotModel = None
        self.setEnabled(False)
        self.__setState(self._State.UNLOCK)

    def __triggered(self):
        plotModel = self.__plotModel
        if plotModel is None:
            return
        locked = plotModel.editSource() == "user"
        if locked:
            # Plot without name is set up with plotselect
            if plotModel.name() is None and isinstance(
                plotModel, plot_item_model.CurvePlot
            ):
                plotModel.tagPlotselectEdit()
            else:
                plotModel.tagRawEdit()
        else:
            plotModel.tagUserEditTime()

    def setPlotModel(self, plotModel: plot_model.Plot):
        if self.__plotModel is not None:
            self.__plotModel.valueChanged.disconnect(self.__valueChanged)
        self.__plotModel = plotModel
        if self.__plotModel is not None:
            self.__plotModel.valueChanged.connect(self.__valueChanged)
        self.__updateSelectionState()

    def __valueChanged(self, eventType):
        if eventType == plot_model.ChangeEventType.USER_EDIT_TIME:
            self.__updateSelectionState()

    def __updateSelectionState(self):
        plotModel = self.__plotModel
        if plotModel is None:
            self.setEnabled(False)
            self.__setState(self._State.UNLOCK)
        else:
            userEdited = plotModel.userEditTime() is not None
            editSource = plotModel.editSource()

            self.setEnabled(True)
            if editSource == "plotselect":
                self.__setState(self._State.UNLOCK_PLOTSELECT)
            elif userEdited:
                self.__setState(self._State.LOCK)
            else:
                self.__setState(self._State.UNLOCK)

    def __setState(self, state: _State):
        if self.__state == state:
            return
        self.__state = state

        if self.__state == self._State.LOCK:
            name = "flint:icons/lock-closed"
            self.setToolTip("The actual GUI selection will be reused for new scans")
        elif self.__state == self._State.UNLOCK:
            name = "flint:icons/lock-open"
            self.setToolTip(
                "The actual display selection will be replaced by a new scan"
            )
        elif self.__state == self._State.UNLOCK_PLOTSELECT:
            name = "flint:icons/lock-open-plotselect"
            self.setToolTip(
                "The actual plotselect selection will be used for new scans"
            )
        else:
            return
        icon = icons.getQIcon(name)
        self.setIcon(icon)
