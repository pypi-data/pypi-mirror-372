# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

from __future__ import annotations

import logging
import weakref

from silx.gui import qt
from .extended_dock_widget import ExtendedDockWidget

_logger = logging.getLogger(__name__)


class _Stack(qt.QStackedWidget):
    def setWidget(self, widget: qt.QWidget):
        count = self.count()
        if count >= 1:
            w = self.widget(0)
            self.removeWidget(w)
            w.setParent(None)
        self.addWidget(widget)

    def sizeHint(self):
        return qt.QSize(200, 500)


class _EmptyWidget(qt.QLabel):
    """Widget used to display the property widget when it is empty"""

    def __init__(self, parent=None):
        super(_EmptyWidget, self).__init__(parent=parent)
        html = """<html>
<head/><body>
<p><span style=" font-size:14pt; font-weight:600; color:#939393;">Click on a plot</span></p>
<p><span style=" font-size:14pt; font-weight:600; color:#939393;">to display here</span></p>
<p><span style=" font-size:14pt; font-weight:600; color:#939393;">its properties</span></p>
</body></html>"""
        self.setWordWrap(True)
        self.setText(html)
        self.setAlignment(qt.Qt.AlignHCenter | qt.Qt.AlignVCenter)


class _ErrorWidget(qt.QLabel):
    """Widget used to display the property widget when it is empty"""

    def __init__(self, parent=None):
        super(_ErrorWidget, self).__init__(parent=parent)
        html = """<html>
<head/><body>
<p><span style=" font-size:14pt; font-weight:600; color:#FF9393;">Property widget</span></p>
<p><span style=" font-size:14pt; font-weight:600; color:#FF9393;">can't be created</span></p>
<p><span style=" font-size:14pt; font-weight:600; color:#FF9393;">Check the logs</span></p>
</body></html>"""
        self.setWordWrap(True)
        self.setText(html)
        self.setAlignment(qt.Qt.AlignHCenter | qt.Qt.AlignVCenter)


class MainPropertyWidget(ExtendedDockWidget):

    widgetUpdated = qt.Signal()

    def __init__(self, parent: qt.QWidget | None = None):
        super(MainPropertyWidget, self).__init__(parent=parent)
        self.setWindowTitle("Plot properties")
        self.__view = None
        self.__viewSource: weakref.ReferenceType | None = None
        self.__stack = _Stack(self)
        self.__stack.setSizePolicy(qt.QSizePolicy.Preferred, qt.QSizePolicy.Expanding)

        # Try to improve the look and feel
        # FIXME: THis should be done with stylesheet
        frame = qt.QFrame(self)
        frame.setFrameShape(qt.QFrame.StyledPanel)
        layout = qt.QVBoxLayout(frame)
        layout.addWidget(self.__stack)
        layout.setContentsMargins(0, 0, 0, 0)
        widget = qt.QFrame(self)
        layout = qt.QVBoxLayout(widget)
        layout.addWidget(frame)
        layout.setContentsMargins(0, 1, 0, 0)
        self.setWidget(widget)

        self.__stack.setWidget(_EmptyWidget(self))

    def isEmpty(self):
        return self.focusWidget() is None

    def focusWidget(self):
        """Returns the widget which provides the actual content to the property
        view"""
        source = self.__viewSource
        if source is None:
            return None
        return source()

    def setFocusWidget(self, widget):

        viewSource = None
        if self.__viewSource is not None:
            viewSource = self.__viewSource()

        if widget is viewSource:
            # Skip if it is the same source
            if widget is None and self.__viewSource is None:
                # Make sure the view source ref is None
                # And not only invalidated
                return

        view: qt.QWidget
        if widget is None:
            view = _EmptyWidget(self)
            self.__viewSource = None
        else:
            try:
                view = widget.createPropertyWidget(self)
                self.__viewSource = weakref.ref(widget)
            except Exception:
                _logger.error("Error while creating property widget", exc_info=True)
                view = _ErrorWidget(self)
                self.__viewSource = None

        self.__view = view
        self.__stack.setWidget(view)
        self.widgetUpdated.emit()
