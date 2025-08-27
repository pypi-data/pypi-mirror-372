# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

from __future__ import annotations

import logging

from silx.gui import qt
from bliss.flint.model import flint_model
from bliss.flint.model.logging_model import LoggingModel
from bliss.flint.widgets.logging_widgets import colorFromLevel


class StateIndicator(qt.QWidget):
    """
    Widget to display an indicator when a warning or an error was logged.

    The indicator is reset when the log window is consulted.
    """

    def __init__(self, parent=None):
        super(StateIndicator, self).__init__(parent=parent)
        self.__action = qt.QAction(self)

        self.__button = qt.QToolBar(self)
        self.__button.setIconSize(qt.QSize(10, 10))
        self.__button.addAction(self.__action)
        self.__action.triggered.connect(self.__clicked)
        self.__action.setEnabled(False)

        layout = qt.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.__button)
        self.__flintModel: flint_model.FlintState | None = None
        self.__logModel: LoggingModel | None = None
        self.__lastLevelNo: int = 0
        self.__logWindow = None

    def __clicked(self):
        assert self.__flintModel is not None
        flintWindow = self.__flintModel.mainWindow()
        flintWindow.showLogDialog()

    def setFlintModel(self, model: flint_model.FlintState):
        self.__flintModel = model
        self.__flintModel.logWindowChanged.connect(self.__logWindowChanged)
        self.__logWindowChanged()

    def __logWindowChanged(self):
        assert self.__flintModel is not None
        window = self.__flintModel.logWindow()
        self.setLogWindow(window)

    def setLogWindow(self, window):
        if self.__logWindow is not None:
            self.__logWindow.activated.disconnect(self.__logWindowActivated)
        self.__logWindow = window
        if self.__logWindow is not None:
            self.__logWindow.activated.connect(self.__logWindowActivated)

    def setLogModel(self, model: LoggingModel):
        model.recordReceived.connect(self.__recordReceived)
        self.__logModel = model

    def __createCircleIcon(self, color: qt.QColor):
        pixmap = qt.QPixmap(10, 10)
        pixmap.fill(qt.Qt.transparent)
        painter = qt.QPainter(pixmap)
        painter.setRenderHint(qt.QPainter.Antialiasing)
        painter.setPen(color)
        painter.setBrush(qt.QBrush(color))
        painter.drawEllipse(1, 1, 8, 8)
        painter.end()
        return qt.QIcon(pixmap)

    def __recordReceived(self, record):
        levelno = record.levelno
        if levelno <= self.__lastLevelNo:
            return
        if levelno < logging.WARNING:
            return
        if self.__logWindow and self.__logWindow.isActiveWindow():
            return
        self.__lastLevelNo = levelno
        color = colorFromLevel(levelno)
        icon = self.__createCircleIcon(color)
        self.__action.setIcon(icon)
        self.__action.setEnabled(True)
        self.__action.setToolTip("Unread logging messages")

    def __logWindowActivated(self):
        self.__lastLevelNo = 0
        self.__action.setIcon(qt.QIcon())
        self.__action.setEnabled(False)
        self.__action.setToolTip("")
