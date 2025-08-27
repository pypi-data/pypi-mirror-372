# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.
"""This module contains a shared dialog to edit colormap"""

from __future__ import annotations

import weakref
import logging

from silx.gui import qt
from silx.gui.qt import inspect
from silx.gui.dialog.ColormapDialog import ColormapDialog, DisplayMode
from bliss.flint.model import scan_model
from .extended_dock_widget import ExtendedDockWidget

_logger = logging.getLogger(__name__)


class ColormapWidget(ExtendedDockWidget):
    def __init__(self, parent=None):
        super(ColormapWidget, self).__init__(parent=parent)

        dialog = ColormapDialog(parent=self)
        dialog.setWindowFlags(qt.Qt.Widget)
        dialog.setVisible(True)
        dialog.installEventFilter(self)
        self.__dialog: weakref.ReferenceType[ColormapDialog] = weakref.ref(dialog)

        # FIXME: This should be done with stylesheet
        mainWidget = qt.QFrame(self)
        mainWidget.setFrameShape(qt.QFrame.StyledPanel)
        mainWidget.setAutoFillBackground(True)
        layout = qt.QVBoxLayout(mainWidget)
        layout.addWidget(dialog)
        layout.setContentsMargins(0, 0, 0, 0)

        # FIXME: This should be done with stylesheet
        widget = qt.QFrame(self)
        layout = qt.QVBoxLayout(widget)
        layout.addWidget(mainWidget)
        layout.setContentsMargins(0, 1, 0, 0)
        self.setWidget(widget)

        self.__owner = None
        self.__channelName: str | None = None
        self.__scan: scan_model.Scan | None = None

    def setShowHistogram(self, show: bool):
        dialog = self._dialog()
        if dialog is None:
            _logger.error("The C++ dialog was already release")
            return
        histo = dialog.getHistogramWidget()
        if show:
            histo.setDisplayMode(DisplayMode.HISTOGRAM)
        else:
            histo.setDisplayMode(DisplayMode.RANGE)

    def showHistogram(self) -> bool:
        dialog = self._dialog()
        if dialog is None:
            _logger.error("The C++ dialog was already release")
            return False
        histo = dialog.getHistogramWidget()
        # FIXME: Typo in method name have to be fixed in silx > 2.1.0
        return histo.getDsiplayMode() == DisplayMode.HISTOGRAM

    def eventFilter(self, widget, event):
        if event.type() == qt.QEvent.HideToParent:
            self.windowClosed.emit()
            self.deleteLater()
        return widget.eventFilter(widget, event)

    def setOwner(self, widget):
        """Widget owning the colormap widget"""
        self.__owner = weakref.ref(widget)

    def owner(self):
        """Widget owning the colormap widget"""
        owner = self.__owner
        if owner is not None:
            owner = owner()
        return owner

    def _dialog(self) -> ColormapDialog | None:
        d = self.__dialog()
        if d is not None:
            # https://github.com/silx-kit/silx/issues/3885
            if not inspect.isValid(d):
                _logger.debug("The C++ dialog was already release")
                return None
        return d

    def setItem(self, item):
        """Display data and colormap from a silx item"""
        dialog = self._dialog()
        if dialog is None:
            return
        dialog.setItem(item)
        if hasattr(item, "getColormap"):
            dialog.setColormap(item.getColormap())
        else:
            dialog.setColormap(None)

    def setColormap(self, colormap):
        """Display only a colormap in the editor"""
        dialog = self._dialog()
        if dialog is None:
            return
        dialog.setItem(None)
        dialog.setColormap(colormap)
