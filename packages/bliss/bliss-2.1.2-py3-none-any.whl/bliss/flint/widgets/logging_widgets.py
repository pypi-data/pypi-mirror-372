# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

"""
Provide a widget to display logs from `logging` Python module.
"""

from __future__ import annotations

import logging

from silx.gui import qt
from silx.gui import utils
from bliss.flint.model import logging_model


_levelToColor = {
    logging.CRITICAL: (199, 78, 129),
    logging.ERROR: (253, 113, 98),
    logging.WARNING: (251, 202, 88),
    logging.INFO: (122, 184, 240),
    logging.DEBUG: (127, 212, 142),
    logging.NOTSET: (150, 150, 150),
}


def colorFromLevel(levelno: int, alpha: int = 255) -> qt.QColor:
    """
    Returns a color from a logging level.

    The returned color is one from `_levelToColor`.

    Arguments:
        levelno: The level, which can be a value between names levels (for example 45)
        alpha: An optional alpha channel for the opacity.
    """
    if levelno >= logging.CRITICAL:
        norm = logging.CRITICAL
    elif levelno >= logging.ERROR:
        norm = logging.ERROR
    elif levelno >= logging.WARNING:
        norm = logging.WARNING
    elif levelno >= logging.INFO:
        norm = logging.INFO
    elif levelno >= logging.DEBUG:
        norm = logging.DEBUG
    else:
        norm = logging.NOTSET
    rgb = _levelToColor[norm]
    return qt.QColor(*rgb, alpha)


class LoggerNameComboBox(qt.QComboBox):
    def __init__(self, parent=None):
        super(LoggerNameComboBox, self).__init__(parent=parent)
        self.setInsertPolicy(qt.QComboBox.InsertAlphabetically)
        self.setEditable(True)
        self.setMinimumWidth(300)

        names = logging.Logger.manager.loggerDict.keys()
        completer = qt.QCompleter(names, self)
        completer.setCaseSensitivity(qt.Qt.CaseInsensitive)
        self.setCompleter(completer)

        self.refresh()

    def setLoggerName(self, name):
        self.setEditText(name)
        self.activated[str].emit(name)

    def setLogModel(self, model: logging_model.LoggingModel):
        self.__logModel = model
        model.levelsConfigHaveChanged.connect(self.refresh)

    def refresh(self):
        currentText = self.currentText()
        self.clear()
        names = sorted(logging.Logger.manager.loggerDict.keys())
        for name in sorted(names):
            logger = logging.getLogger(name)
            if logger.level != logging.NOTSET:
                self.addItem(name)
        self.insertItem(0, "ROOT")
        with utils.blockSignals(self):
            self.setEditText(currentText)

    def keyPressEvent(self, event: qt.QKeyEvent):
        super(LoggerNameComboBox, self).keyPressEvent(event)
        if event.key() in (qt.Qt.Key_Enter, qt.Qt.Key_Return):
            # Skip parent propagation
            event.accept()


class LoggerLevelEdit(qt.QWidget):
    def __init__(self, parent=None):
        super(LoggerLevelEdit, self).__init__(parent=parent)
        self.__group = qt.QButtonGroup()
        self.__group.setExclusive(False)
        layout = qt.QHBoxLayout(self)
        layout.setSpacing(1)
        layout.setContentsMargins(0, 0, 0, 0)
        self.__buttons = {}
        self.__loggerName = None

        for num, name in logging._levelToName.items():
            btn = qt.QPushButton(self)
            btn.setCheckable(True)
            btn.setText(f" {name} ")
            btn.setToolTip(f"Set the level to {name} (={num})")
            r, g, b = _levelToColor.get(num, [128, 128, 128])
            textcolor = "white" if name == "CRITICAL" else "black"
            btn.setStyleSheet(
                f"""
                .QPushButton {{
                    background-color: rgb(200,200,200);
                    border: 0px;
                    border-radius: 9px;
                    color: black;
                    padding: 1px;
                    font-size: 12px;
                }}
                .QPushButton:checked {{
                    background-color: rgb({r}, {g}, {b});
                    color: {textcolor};
                }}
                """
            )
            self.__buttons[num] = btn
            self.__group.addButton(btn)
            layout.addWidget(btn)

        self.__group.buttonClicked.connect(self.__levelSelected)

    def setLogModel(self, model: logging_model.LoggingModel):
        self.__logModel = model
        model.levelsConfigHaveChanged.connect(self.__updateDispay)

    def setLoggerName(self, name):
        if self.__loggerName == name:
            return
        self.__loggerName = name
        self.__updateDispay()

    def loggerName(self):
        return self.__loggerName

    def refresh(self):
        """
        Refresh the widget in case the logging was manually changed.
        """
        self.__updateDispay()

    def __updateDispay(self):
        name = self.__loggerName
        if name == "ROOT":
            name = None
        logger = logging.getLogger(name)
        level = logger.level
        with utils.blockSignals(self.__group):
            for buttonLevel, button in self.__buttons.items():
                with utils.blockSignals(button):
                    button.setEnabled(self.__loggerName is not None)
                    if level == logging.NOTSET:
                        button.setChecked(
                            buttonLevel == logging.NOTSET
                            or buttonLevel >= logging.WARNING
                        )
                    else:
                        button.setChecked(buttonLevel >= level)

    def __levelSelected(self, button):
        name = self.loggerName()
        if name is None:
            return
        for level, b in self.__buttons.items():
            if button is b:
                break
        else:
            return

        if name == "ROOT":
            name = None
        self.__logModel.setLevel(name, level)
        self.__updateDispay()


class LogProfileAction(qt.QAction):
    def __init__(self, parent):
        super(LogProfileAction, self).__init__(parent=parent)
        self.__loglevels = {}
        self.triggered.connect(self.__activate)

    def setLogLevels(self, loglevels):
        self.__loglevels = loglevels

    def __activate(self):
        logModel = self.parent().logModel()
        logModel.setLevels(self.__loglevels, reset=True)


class LogProfiles(qt.QToolButton):

    logChanged = qt.Signal()

    def __init__(self, parent=None):
        super(LogProfiles, self).__init__(parent=parent)
        self.setText("Profiles")
        self.setToolTip("Load predefined log levels")
        self.setPopupMode(qt.QToolButton.InstantPopup)
        menu = qt.QMenu(self)
        self.setMenu(menu)

        profile = LogProfileAction(self)
        profile.setText("Default levels")
        profile.setLogLevels({None: logging.WARNING, "bliss": logging.INFO})
        self.addProfileAction(profile)

        profile = LogProfileAction(self)
        profile.setText("Debug levels")
        profile.setLogLevels({None: logging.DEBUG, "matplotlib": logging.INFO})
        self.addProfileAction(profile)

        profile = LogProfileAction(self)
        profile.setText("Debug scan listener")
        profile.setLogLevels(
            {
                None: logging.WARNING,
                "bliss": logging.INFO,
                "bliss.flint.manager.scan_manager": logging.DEBUG,
            }
        )
        self.addProfileAction(profile)

        profile = LogProfileAction(self)
        profile.setText("Clear all levels")
        self.addProfileAction(profile)

    def setLogModel(self, model: logging_model.LoggingModel):
        self.__logModel = model

    def logModel(self):
        return self.__logModel

    def addProfileAction(self, action):
        menu = self.menu()
        action.triggered.connect(self.__logChanged)
        menu.addAction(action)

    def __logChanged(self):
        self.logChanged.emit()
