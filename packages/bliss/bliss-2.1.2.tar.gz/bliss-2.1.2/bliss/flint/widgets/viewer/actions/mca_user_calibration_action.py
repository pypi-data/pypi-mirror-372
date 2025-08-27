# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

from __future__ import annotations

import logging

from silx.gui import qt
from silx.gui import icons
from silx.gui.widgets.FloatEdit import FloatEdit


_logger = logging.getLogger(__name__)


class _ResponsiveFloatEdit(FloatEdit):
    """Make sure the numbers are visible, always"""

    QLinePrivateHorizontalMargin = 2

    def __init__(self, parent: qt.QWidget | None):
        FloatEdit.__init__(self, parent)
        self.textChanged.connect(self.__updateMinimumSizeHint)

    def setValue(self, value):
        FloatEdit.setValue(self, value)
        self.__updateMinimumSizeHint()

    def __minimumSizeHint(self) -> int:
        """Minimum size for the widget to properly read the actual number"""
        text = self.text()
        font = self.font()
        metrics = qt.QFontMetrics(font)
        margins = self.textMargins()
        width = (
            metrics.horizontalAdvance(text)
            + self.QLinePrivateHorizontalMargin * 2
            + margins.left()
            + margins.right()
        )
        width = max(30, width)
        self.setMinimumWidth(width)
        opt = qt.QStyleOptionFrame()
        self.initStyleOption(opt)
        s = self.style().sizeFromContents(
            qt.QStyle.CT_LineEdit, opt, qt.QSize(width, self.height())
        )
        return s.width()

    def sizeHint(self):
        sizeHint = FloatEdit.sizeHint(self)
        width = self.__minimumSizeHint()
        return qt.QSize(width, sizeHint.height())

    def __updateMinimumSizeHint(self, text=None):
        width = self.__minimumSizeHint()
        self.setMinimumWidth(width)
        self.updateGeometry()


class _McaUserCalibrationDialog(qt.QDialog):
    """Dialog to display and define an MCA calibration.

    It allows to edit the transfer function from channel id to energy based on
    polynomial function.
    """

    def __init__(
        self,
        parent: qt.QWidget | None = None,
    ) -> None:
        qt.QDialog.__init__(self, parent=parent)
        self.setWindowTitle("MCA calibration")

        self._calibrationResult: None | tuple[float, float, float] = None

        layout = qt.QVBoxLayout(self)
        self._buttons = qt.QDialogButtonBox(self)
        self._buttons.clicked.connect(self.__buttonClicked)
        self.__okButton = self._buttons.addButton(qt.QDialogButtonBox.Ok)
        self.__cancelButton = self._buttons.addButton(qt.QDialogButtonBox.Cancel)
        self.__resetButton = self._buttons.addButton(qt.QDialogButtonBox.Reset)

        self.__x2 = _ResponsiveFloatEdit(self)
        self.__x1 = _ResponsiveFloatEdit(self)
        self.__x0 = _ResponsiveFloatEdit(self)

        hlayout = qt.QHBoxLayout(self)
        hlayout.addWidget(qt.QLabel("energy = ", self))
        hlayout.addWidget(self.__x2)
        hlayout.addWidget(qt.QLabel("c<sup>2</sup> + ", self))
        hlayout.addWidget(self.__x1)
        hlayout.addWidget(qt.QLabel("c + ", self))
        hlayout.addWidget(self.__x0)
        hlayout.addWidget(qt.QLabel("keV", self))
        legend = qt.QLabel("c: index of the channel", self)
        legend.setAlignment(qt.Qt.AlignRight)
        layout.addLayout(hlayout)
        layout.addWidget(legend)
        layout.addSpacing(5)
        layout.addStretch()
        layout.addWidget(self._buttons)

    def __buttonClicked(self, button):
        if button is self.__resetButton:
            self._calibrationResult = None
            self.accept()
        elif button is self.__okButton:
            x0 = self.__x0.value()
            x1 = self.__x1.value()
            x2 = self.__x2.value()
            self._calibrationResult = (x0, x1, x2)
            self.accept()
        elif button is self.__cancelButton:
            self.reject()
        else:
            raise Exception("Unsupported clicked button")

    def setCalibration(self, calibration: tuple[float, float, float] | None):
        if calibration is None:
            self.__x0.setValue(0)
            self.__x1.setValue(1)
            self.__x2.setValue(0)
        else:
            self.__x0.setValue(calibration[0])
            self.__x1.setValue(calibration[1])
            self.__x2.setValue(calibration[2])

    def calibration(self) -> tuple[float, float, float] | None:
        return self._calibrationResult


class McaUserCalibrationAction(qt.QAction):
    """Action to enable and edit MCA calibration.

    It allows to edit the transfer function from channel id to energy based on
    polynomial function.
    """

    def __init__(self, parent):
        super(McaUserCalibrationAction, self).__init__(parent)
        self.setCheckable(True)
        icon = icons.getQIcon("flint:icons/mca-calibration")
        self.setIcon(icon)
        self.setText("Calibration")
        self.setToolTip("Define a user calibration for the MCA")
        self.triggered.connect(self.__triggered)
        self._lastCalibration = None

    def __triggered(self):
        if self.isChecked():
            dialog = _McaUserCalibrationDialog(self.parent())
            calibration = self.parent().userCalibration()
            if calibration is None:
                calibration = self._lastCalibration
            dialog.setCalibration(calibration)
            result = dialog.exec_()
            if result:
                calibration = dialog.calibration()
                if calibration:
                    self._lastCalibration = calibration
                self.parent().setUserCalibration(calibration)
                self.setChecked(calibration is not None)
            else:
                self.setChecked(False)
        else:
            self.parent().setUserCalibration(None)
            self.setChecked(False)
