# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.
"""Module containing the description of the logging window provided by Flint"""

from __future__ import annotations

import logging
from silx.gui import qt

from bliss.flint.widgets.logging_list import LoggingList
from bliss.flint.model import flint_model
from bliss.flint.widgets import logging_widgets


class LoggingWindow(qt.QDialog):

    activated = qt.Signal()
    """Sent when the window get the focus"""

    def __init__(self, parent, model: flint_model.FlintState):
        qt.QDialog.__init__(self, parent=parent)
        self.setWindowTitle("Log messages")
        self.__flintState = model
        logModel = model.logModel()
        logLevelEdit = logging_widgets.LoggerLevelEdit(self)
        logLevelEdit.setLogModel(logModel)
        logCombo = logging_widgets.LoggerNameComboBox(self)
        logCombo.setLogModel(logModel)
        logProfile = logging_widgets.LogProfiles(self)
        logProfile.setLogModel(logModel)
        logWidget = LoggingList(self)
        logWidget.setLogModel(logModel)
        self.__logWidget = logWidget

        toolbar = qt.QToolBar(self)
        toolbar.addWidget(logCombo)
        toolbar.addWidget(logLevelEdit)
        toolbar.addSeparator()
        toolbar.addWidget(logProfile)

        logWidget.logSelected.connect(logCombo.setLoggerName)
        logWidget.doubleClicked.connect(self.__doubleClicked)
        logCombo.activated[str].connect(logLevelEdit.setLoggerName)
        # logProfile.logChanged.connect(logCombo.refresh)
        logCombo.setLoggerName("ROOT")

        layout = qt.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(1)
        layout.addWidget(toolbar)
        layout.addWidget(logWidget)

        self.rejected.connect(self.__saveLogWindowSettings)
        self.__initLogWindowFromSettings()

    def __doubleClicked(self, index):
        record = self.__logWidget.recordFromIndex(index)
        if record is None:
            return

        # _logger.error("%s %s %s", type_, value, ''.join(traceback.format_tb(trace)))
        msg = qt.QMessageBox()
        msg.setWindowTitle("Logging record")

        if record.levelno > logging.WARNING:
            icon = qt.QMessageBox.Critical
        elif record.levelno > logging.INFO:
            icon = qt.QMessageBox.Warning
        else:
            icon = qt.QMessageBox.Information
        msg.setIcon(icon)

        try:
            message = record.getMessage()
        except Exception as e:
            # In case there is a wrong call of logging methods
            message = "Error in logs: " + e.args[0]
            message += "\nMessage: %r" % record.msg
            message += "\nArguments: %s" % record.args

        cuts = message.split("\n", 1)

        msg.setInformativeText(cuts[0])
        msg.setDetailedText(message)
        msg.raise_()
        msg.exec()

    def focusInEvent(self, event):
        self.activated.emit()
        return super(LoggingWindow, self).focusInEvent(event)

    def __initLogWindowFromSettings(self):
        settings = self.__flintState.settings()
        # resize window to 70% of available screen space, if no settings
        settings.beginGroup("log-window")
        if settings.contains("size"):
            self.resize(settings.value("size"))
        if settings.contains("pos"):
            self.move(settings.value("pos"))
        settings.endGroup()

    def __saveLogWindowSettings(self):
        settings = self.__flintState.settings()
        settings.beginGroup("log-window")
        settings.setValue("size", self.size())
        settings.setValue("pos", self.pos())
        settings.endGroup()
