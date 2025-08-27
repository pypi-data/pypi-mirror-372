# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

from __future__ import annotations

from silx.gui import qt
from silx.gui import icons


class StaticIcon(qt.QLabel):

    clicked = qt.Signal()

    def __init__(self, parent=None):
        super(StaticIcon, self).__init__(parent=parent)
        self.__targetAction = None

    def setIcon(self, icon: str | qt.QIcon):
        """Set an icon

        Arguments:
            icon: This can be a QIcon or a silx resource name.
        """
        if isinstance(icon, str):
            icon = icons.getQIcon(icon)
        # FIXME: Maybe the icon size could be read from the parent
        pixmap = icon.pixmap(qt.QSize(24, 24))
        self.setPixmap(pixmap)

    def event(self, event: qt.QEvent):
        if event.type() == qt.QEvent.MouseButtonRelease:
            self.__redirectClick()
            self.clicked.emit()
        return qt.QLabel.event(self, event)

    def __redirectClick(self):
        if self.__targetAction is None:
            return
        action = self.__targetAction
        menu = action.menu()
        if menu:
            action = menu.menuAction()
            # pos like it is drop by the next widget in the toolbar
            # this is obviously not always the case
            pos = self.mapToGlobal(qt.QPoint(self.width(), self.height()))
            menu.popup(pos)
        else:
            action.trigger()

    def redirectClickTo(self, action):
        """Define the action which will be triggered when the icon is clicked."""
        self.__targetAction = action
