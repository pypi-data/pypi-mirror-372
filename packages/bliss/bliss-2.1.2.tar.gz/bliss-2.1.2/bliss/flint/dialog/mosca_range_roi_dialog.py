# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

from __future__ import annotations

import logging
import numpy

from silx.gui import qt
from bliss.flint.widgets.viewer.rois.mosca_range_roi import MoscaRangeRoi
from bliss.flint.utils import error_utils


_logger = logging.getLogger(__name__)


class _ChannelValidator(qt.QValidator):
    def __init__(self, parent=None):
        qt.QValidator.__init__(self, parent=parent)
        self.__acceptNegOne = True

    def setNegOneAccepted(self, accepted: bool):
        self.__acceptNegOne = accepted

    def validate(
        self, inputText: str, pos: int
    ) -> tuple[qt.QValidator.State, str, int]:
        if len(inputText) > 0:
            if pos > 0:
                c = inputText[pos - 1]
                if c not in "-0123456789":
                    inputText = inputText[0 : pos - 1] + inputText[pos:]
                    pos = pos - 1

        try:
            channel = int(inputText)
        except ValueError:
            channel = None

        if channel is not None:
            if channel < -1:
                return qt.QValidator.Intermediate, inputText, pos
            if channel == -1 and not self.__acceptNegOne:
                return qt.QValidator.Intermediate, inputText, pos
            return qt.QValidator.Acceptable, inputText, pos

        inputSplit = inputText.split("-")
        if len(inputSplit) == 2:
            try:
                n = int(inputSplit[0])
            except ValueError:
                n = None
            try:
                m = int(inputSplit[1])
            except ValueError:
                m = None

            if n is not None and m is not None:
                if n > -1 and m > -1:
                    return qt.QValidator.Acceptable, inputText, pos

        return qt.QValidator.Intermediate, inputText, pos

    def fixup(self, inputText: str) -> str:
        try:
            channel = int(inputText)
        except ValueError:
            channel = None
        if channel is not None:
            # Remove leading '0'
            return f"{channel}"

        inputSplit = inputText.split("-")
        if len(inputSplit) == 2:
            try:
                n = int(inputSplit[0])
            except ValueError:
                n = None
            try:
                m = int(inputSplit[1])
            except ValueError:
                m = None

            if n is not None and m is not None:
                if n == m:
                    return f"{n}"
                if n > m:
                    return f"{m}-{n}"

        return inputText

    def toValue(self, inputText: str):
        """Convert a text to a valid channel value

        Raises:
            ValueError if the string is not valid
        """
        try:
            channel = int(inputText)
        except ValueError:
            channel = None

        if channel is not None and channel >= -1:
            return channel

        inputSplit = inputText.split("-")
        if len(inputSplit) == 2:
            try:
                n = int(inputSplit[0])
            except ValueError:
                n = None
            try:
                m = int(inputSplit[1])
            except ValueError:
                m = None

            if n is not None and m is not None:
                if n == m:
                    return n
                if n < m:
                    return n, m
                if n > m:
                    return m, n

        raise ValueError(f"'{inputText}' is not a valid channel description")


class MoscaRangeRoiDialog(qt.QDialog):
    """
    Dialog to edit a Mosca rage ROI
    """

    def __init__(self, parent=None):
        qt.QDialog.__init__(self, parent=parent)
        self.setWindowTitle("Mosca ROI description")

        self.__energy: None | numpy.ndarray
        self.__nbSpectrums: None | int

        self.__name = qt.QLineEdit(self)
        self.__name.setReadOnly(True)
        self.__name.setEnabled(False)

        rangeValidator = qt.QIntValidator(self)
        rangeValidator.setBottom(0)
        self.__start = qt.QLineEdit(self)
        self.__start.setValidator(rangeValidator)
        self.__stop = qt.QLineEdit(self)
        self.__stop.setValidator(rangeValidator)

        channelValidator = _ChannelValidator(self)
        self.__channel = qt.QLineEdit(self)
        self.__channel.setValidator(channelValidator)

        self.__allChannels = qt.QCheckBox(self)
        self.__allChannels.setText("Apply to every spectrums")

        nameTitle = qt.QLabel(self)
        nameTitle.setText("Name")
        nameTitle.setToolTip("Name of the ROI")

        rangeTitle = qt.QLabel(self)
        rangeTitle.setText("Range")
        rangeTitle.setToolTip("Start and stop (included) of the spectrum bins")

        channelTitle = qt.QLabel(self)
        channelTitle.setText("Spectrum id")
        channelTitle.setToolTip("Id of the spectrum in which to apply this ROI")

        energyValidator = qt.QDoubleValidator(self)
        energyValidator.setBottom(0)

        self.__startEnergy = qt.QLineEdit(self)
        self.__startEnergy.setValidator(energyValidator)
        self.__stopEnergy = qt.QLineEdit(self)
        self.__stopEnergy.setValidator(energyValidator)
        self.__unitEnergy = qt.QLabel(self)
        self.__unitEnergy.setText("keV")

        buttons = qt.QDialogButtonBox(self)
        types = qt.QDialogButtonBox.Ok | qt.QDialogButtonBox.Cancel
        buttons.setStandardButtons(types)
        buttons.accepted.connect(self.__tryAccept)
        buttons.rejected.connect(self.reject)

        layout = qt.QGridLayout(self)
        layout.addWidget(nameTitle, 0, 0)
        layout.addWidget(self.__name, 0, 1, 1, 2)
        layout.addWidget(rangeTitle, 1, 0)
        layout.addWidget(self.__start, 1, 1)
        layout.addWidget(self.__stop, 1, 2)
        layout.addWidget(self.__startEnergy, 2, 1)
        layout.addWidget(self.__stopEnergy, 2, 2)
        layout.addWidget(self.__unitEnergy, 2, 3)
        layout.addWidget(channelTitle, 3, 0)
        layout.addWidget(self.__channel, 3, 1, 1, 2)
        layout.addWidget(self.__allChannels, 4, 1, 1, 2)
        layout.addWidget(buttons, 5, 0, 1, 4)

        self.__allChannels.toggled.connect(self.__allChannelChanged)
        self.__start.editingFinished.connect(self.__startUpdated)
        self.__stop.editingFinished.connect(self.__stopUpdated)
        self.__startEnergy.editingFinished.connect(self.__startEnergyUpdated)
        self.__stopEnergy.editingFinished.connect(self.__stopEnergyUpdated)

    def __startUpdated(self):
        if self.__energy is None:
            return
        v = int(self.__start.text())
        if v < 0:
            v = 0
        if v >= len(self.__energy):
            v = len(self.__energy) - 1
        e = self.__energy[v]
        self.__startEnergy.setText(f"{e}")

    def __stopUpdated(self):
        if self.__energy is None:
            return
        v = int(self.__stop.text())
        if v < 0:
            v = 0
        if v >= len(self.__energy):
            v = len(self.__energy) - 1
        e = self.__energy[v]
        self.__stopEnergy.setText(f"{e}")

    def __startEnergyUpdated(self):
        if self.__energy is None:
            return
        try:
            e = float(self.__startEnergy.text())
        except ValueError:
            return
        if e < 0:
            e = 0
        ie = numpy.argmin(abs(self.__energy - e))
        if ie >= 1:
            ie - 1
        self.__start.setText(f"{ie}")

    def __stopEnergyUpdated(self):
        if self.__energy is None:
            return
        try:
            e = float(self.__stopEnergy.text())
        except ValueError:
            return
        if e < 0:
            e = 0
        ie = numpy.argmin(abs(self.__energy - e))
        if ie >= 1:
            ie - 1
        self.__stop.setText(f"{ie}")

    def __allChannelChanged(self):
        if self.__allChannels.isChecked():
            self.__channel.setEnabled(False)
        else:
            self.__channel.setEnabled(True)

    def setRoi(self, roi: MoscaRangeRoi):
        self.__energy = roi.getEnergy()
        names = roi.getAvailableSpectrumNames()
        if names is not None:
            self.__nbSpectrums = len(names)
        else:
            self.__nbSpectrums = None
        self.__updateInputs(roi)

    def __tryAccept(self):
        if not self.__allChannels.isChecked():
            channel = None
            with error_utils.exceptionAsMessageBox(self):
                v = self.__channel.validator()
                text = self.__channel.text()
                channel = v.toValue(text)
                if self.__nbSpectrums is not None:
                    try:
                        if isinstance(channel, int):
                            if channel >= self.__nbSpectrums:
                                raise ValueError(
                                    f"{channel} is too big. Only {self.__nbSpectrums} spectrums are available"
                                )
                        elif isinstance(channel, tuple):
                            if channel[0] >= self.__nbSpectrums:
                                raise ValueError(
                                    f"{channel[0]} is too big. Only {self.__nbSpectrums} spectrums are available"
                                )
                            if channel[1] >= self.__nbSpectrums:
                                raise ValueError(
                                    f"{channel[1]} is too big. Only {self.__nbSpectrums} spectrums are available"
                                )
                    except Exception:
                        channel = None
                        raise
            if channel is None:
                return
        self.accept()

    def __updateInputs(self, roi: MoscaRangeRoi):
        self.__name.setText(roi.getName())

        vmin, vmax = roi.getMcaRange()
        self.__start.setText(f"{vmin}")
        self.__stop.setText(f"{vmax}")

        channel = roi.getMcaChannel()
        if channel == -1:
            self.__allChannels.setChecked(False)
            self.__channel.setText("-1")
        elif channel is None:
            self.__allChannels.setChecked(True)
            self.__channel.setText("")
        elif isinstance(channel, int):
            self.__allChannels.setChecked(False)
            self.__channel.setText(f"{channel}")
        elif isinstance(channel, tuple):
            self.__allChannels.setChecked(False)
            self.__channel.setText(f"{channel[0]}-{channel[1]}")
        else:
            assert False
        self.__allChannelChanged()

        useEnergy = self.__energy is not None
        self.__startEnergy.setEnabled(useEnergy)
        self.__stopEnergy.setEnabled(useEnergy)
        self.__unitEnergy.setEnabled(useEnergy)
        self.__startUpdated()
        self.__stopUpdated()

    def applySelectionToRoi(self, roi: MoscaRangeRoi):
        """Apply the parameters to a ROI."""
        vmin = int(self.__start.text())
        vmax = int(self.__stop.text())
        if vmin > vmax:
            vmin, vmax = vmax, vmin
        channel = None
        if self.__allChannels.isChecked():
            channel = None
        else:
            v = self.__channel.validator()
            text = self.__channel.text()
            channel = v.toValue(text)
        roi.setMcaChannel(channel)
        roi.setMcaRange(vmin, vmax)
