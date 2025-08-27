# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

from __future__ import annotations

from silx.gui import qt
from silx.gui import icons


class DurationAction(qt.QAction):

    valueChanged = qt.Signal(float)

    DEFAULT_ICONS = {
        60 * 60: "flint:icons/duration-1h",
        30 * 60: "flint:icons/duration-30m",
        10 * 60: "flint:icons/duration-10m",
        5 * 60: "flint:icons/duration-5m",
        2 * 60: "flint:icons/duration-2m",
        1 * 60: "flint:icons/duration-1m",
        30: "flint:icons/duration-30s",
    }

    def __init__(self, parent=None):
        super(DurationAction, self).__init__(parent)
        self.__duration: int = 0
        self.__durations = {}

        self.__menu = qt.QMenu(parent)
        self.__menu.aboutToShow.connect(self.__menuAboutToShow)
        self.setMenu(self.__menu)

    def __menuAboutToShow(self):
        menu: qt.QMenu = self.sender()
        menu.clear()
        currentDuration = self.__duration
        currentWasFound = False
        group = qt.QActionGroup(menu)
        group.setExclusive(True)
        for value, (label, icon) in self.__durations.items():
            action = qt.QAction()
            action.setText(label)
            action.setData(value)
            action.setIcon(icon)
            action.setCheckable(True)
            if currentDuration == value:
                action.setChecked(True)
                currentWasFound = True
            group.addAction(action)
            menu.addAction(action)
        if currentDuration is not None and not currentWasFound:
            menu.addSeparator()
            action = qt.QAction()
            action.setText(f"{currentDuration}s")
            action.setData(currentDuration)
            action.setCheckable(True)
            action.setChecked(True)
            currentWasFound = True
            group.addAction(action)
            menu.addAction(action)
        group.triggered.connect(self.__actionSelected)

    def __actionSelected(self, action):
        duration = action.data()
        self.setDuration(duration)

    def setDuration(self, duration: int):
        if self.__duration == duration:
            return
        self.__duration = duration
        self.__updateLookAndFeel()
        self.valueChanged.emit(duration)

    def addDuration(self, label: str, value: int, icon: str | qt.QIcon | None = None):
        """Add a selectable duration in second

        Attributes:
            label: Text to display with the item
            value: Duration in second
            icon: silx icon id to display with the item, else a default icon is
                  loaded.
        """
        if icon is None:
            icon = self.DEFAULT_ICONS[value]
        if isinstance(icon, str):
            icon = icons.getQIcon(icon)
        self.__durations[value] = label, icon

    def duration(self) -> int:
        """Return a duration in second"""
        return self.__duration

    def __updateLookAndFeel(self):
        duration = self.__duration
        label, icon = self.__durations.get(duration, (None, None))
        if icon is None:
            icon = icons.getQIcon("flint:icons/duration-x")
        if label is None:
            label = f"{duration}s"
        self.setToolTip(f"Duration of {label} selected")
        self.setIcon(icon)
