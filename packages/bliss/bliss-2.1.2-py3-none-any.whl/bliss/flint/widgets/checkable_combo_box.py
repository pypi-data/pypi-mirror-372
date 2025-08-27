# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

"""Combobox which allow to select multiple items"""

from __future__ import annotations

from silx.gui import qt


class CheckableComboBox(qt.QComboBox):
    """Combobox which allow to select multiple items

    Code from https://gis.stackexchange.com/questions/350148/qcombobox-multiple-selection-pyqt5
    """

    class Delegate(qt.QStyledItemDelegate):
        """Subclass Delegate to increase item height"""

        def sizeHint(self, option, index):
            size = super().sizeHint(option, index)
            size.setHeight(20)
            return size

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Make the combo editable to set a custom text, but readonly
        self.setEditable(True)
        lineEdit = self.lineEdit()
        lineEdit.setReadOnly(True)
        # Make the lineedit the same color as QPushButton
        palette = self.palette()
        palette.setBrush(qt.QPalette.Base, palette.button())
        lineEdit.setPalette(palette)

        # Use custom delegate
        self.setItemDelegate(CheckableComboBox.Delegate())

        # Update the text when an item is toggled
        model = self.model()
        model.dataChanged.connect(self.updateText)

        # Hide and show popup when clicking the line edit
        lineEdit.installEventFilter(self)
        self.closeOnLineEditClick = False

        # Prevent popup from closing when clicking on an item
        self.view().viewport().installEventFilter(self)

    def resizeEvent(self, event):
        # Recompute text to elide as needed
        self.updateText()
        super().resizeEvent(event)

    def eventFilter(self, obj: qt.QObject, event: qt.QEvent):

        if obj is self.lineEdit():
            if event.type() == qt.QEvent.MouseButtonRelease:
                if self.closeOnLineEditClick:
                    self.hidePopup()
                else:
                    self.showPopup()
                return True
            return False

        if obj is self.view().viewport():
            if event.type() == qt.QEvent.MouseButtonRelease:
                model = self.model()
                index = self.view().indexAt(event.pos())
                item = model.item(index.row())
                if item.checkState() == qt.Qt.Checked:
                    item.setCheckState(qt.Qt.Unchecked)
                else:
                    item.setCheckState(qt.Qt.Checked)
                return True
        return False

    def showPopup(self):
        super().showPopup()
        # When the popup is displayed, a click on the lineedit should close it
        self.closeOnLineEditClick = True

    def hidePopup(self):
        super().hidePopup()
        # Used to prevent immediate reopening when clicking on the lineEdit
        self.startTimer(100)
        # Refresh the display text when closing
        self.updateText()

    def timerEvent(self, event):
        # After timeout, kill timer, and reenable click on line edit
        self.killTimer(event.timerId())
        self.closeOnLineEditClick = False

    def updateText(self):
        texts = []
        model = self.model()
        for i in range(self.model().rowCount()):
            item = model.item(i)
            if item.checkState() == qt.Qt.Checked:
                texts.append(item.text())
        text = ", ".join(texts)

        # Compute elided text (with "...")
        lineEdit = self.lineEdit()
        metrics = qt.QFontMetrics(lineEdit.font())
        elidedText = metrics.elidedText(text, qt.Qt.ElideRight, lineEdit.width())
        lineEdit.setText(elidedText)

    def addItem(self, text: str, userData: object | None = None):
        item = qt.QStandardItem()
        item.setText(text)
        if userData is None:
            item.setData(text)
        else:
            item.setData(userData)
        item.setFlags(qt.Qt.ItemIsEnabled | qt.Qt.ItemIsUserCheckable)
        item.setData(qt.Qt.Unchecked, qt.Qt.CheckStateRole)
        model = self.model()
        model.appendRow(item)

    def setCurrentData(self, userData: list[object]):
        """Set the checked userData"""
        model = self.model()
        userDataSet = set(userData)
        for i in range(self.model().rowCount()):
            item = model.item(i)
            if item.data() in userDataSet:
                item.setCheckState(qt.Qt.Checked)
            else:
                item.setCheckState(qt.Qt.Unchecked)
        self.updateText()

    def currentData(self) -> list[object]:
        """Return the list of selected items data"""
        res = []
        model = self.model()
        for i in range(self.model().rowCount()):
            item = model.item(i)
            if item.checkState() == qt.Qt.Checked:
                res.append(item.data())
        return res
