# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

"""Dialog to change the geometry to an ArcROI"""

from __future__ import annotations

import logging
import numpy
from silx.gui import qt
from silx.gui.widgets.FloatEdit import FloatEdit
from silx.gui.plot.items.roi import ArcROI
from bliss.flint.viewers.live_image.stages.diffraction_stage import (
    DiffractionStage,
    ArcGeometryDict,
)
from bliss.flint.utils import error_utils

try:
    import pyFAI
    import pyFAI.units
    from pyFAI.gui.utils.unitutils import tthToRad, from2ThRad
except ImportError:
    pyFAI = None

_logger = logging.getLogger(__name__)


class ArcRoiGeometryDialog(qt.QDialog):
    def __init__(self, parent=None):
        qt.QDialog.__init__(self, parent=parent)
        self.setWindowTitle("ArcRoi description")

        self.__diffractionStage: DiffractionStage | None = None
        self.__roi: ArcROI = None
        self.__selected: ArcGeometryDict | None = None

        self.__chiFrom = FloatEdit(self)
        self.__chiTo = FloatEdit(self)
        self.__q = FloatEdit(self)

        chiTitle = qt.QLabel(self)
        chiTitle.setText("χ")
        chiTitle.setToolTip("Radial chi as an oriented range")

        qTitle = qt.QLabel(self)
        qTitle.setText("q")
        qTitle.setToolTip("Azimuthal q")

        chiUnit = qt.QLabel(self)
        chiUnit.setText("deg")
        chiUnit.setToolTip("Degree")

        qUnit = qt.QLabel(self)
        qUnit.setText("Å⁻¹")
        qUnit.setToolTip("Inverse Ångström")

        buttons = qt.QDialogButtonBox(self)
        types = qt.QDialogButtonBox.Ok | qt.QDialogButtonBox.Cancel
        buttons.setStandardButtons(types)
        buttons.accepted.connect(self.__tryAccept)
        buttons.rejected.connect(self.reject)

        layout = qt.QGridLayout(self)
        layout.addWidget(chiTitle, 0, 0)
        layout.addWidget(self.__chiFrom, 0, 1)
        layout.addWidget(self.__chiTo, 0, 2)
        layout.addWidget(chiUnit, 0, 3)
        layout.addWidget(qTitle, 1, 0)
        layout.addWidget(self.__q, 1, 1, 1, 2)
        layout.addWidget(qUnit, 1, 3)
        layout.addWidget(buttons, 2, 1, 1, 4)

    def setDiffractionStage(self, diffractionStage: DiffractionStage):
        self.__diffractionStage = diffractionStage
        self.__updateInputs()

    def setRoi(self, roi: ArcROI):
        self.__roi = roi
        self.__updateInputs()

    def __tryAccept(self):
        def updateValidity(w):
            text = w.text()
            _value, validated = w.validator().locale().toDouble(text)
            if validated:
                w.setStyleSheet("QLineEdit {background-color: none}")
            else:
                w.setStyleSheet("QLineEdit {background-color: #FFFFA0}")
            return validated

        valid = True
        valid = updateValidity(self.__chiFrom) and valid
        valid = updateValidity(self.__chiTo) and valid
        valid = updateValidity(self.__q) and valid
        if not valid:
            return

        self.__selected = None
        with error_utils.exceptionAsMessageBox(self):
            self.__selected = self.__computeGeometry()
        if self.__selected is None:
            return

        self.accept()

    def __updateInputs(self):
        roi = self.__roi
        diffractionStage = self.__diffractionStage
        if diffractionStage is None:
            return
        if roi is None:
            return

        wavelength = diffractionStage.geometry().wavelength

        x0, y0 = roi._handleStart.getPosition()
        x1, y1 = roi._handleEnd.getPosition()
        chi0, tth0 = diffractionStage.getChiTth(x0, y0)
        chi1, tth1 = diffractionStage.getChiTth(x1, y1)

        q0 = from2ThRad(tth0, pyFAI.units.Q_A, wavelength)
        q1 = from2ThRad(tth1, pyFAI.units.Q_A, wavelength)

        # Try to normalize the angle direction
        expected = roi.getEndAngle() - roi.getStartAngle()
        posibilities = numpy.array([chi1, chi1 + numpy.pi * 2, chi1 - numpy.pi * 2])
        i = numpy.argmin(numpy.abs(posibilities - chi0 - expected))
        chi1 = posibilities[i]

        chi0 = numpy.rad2deg(chi0)
        chi1 = numpy.rad2deg(chi1)

        if abs(q0 - q1) < 0.1:
            self.__q.setValue((q0 + q1) * 0.5)
        else:
            # Else the input stay empty
            pass

        self.__chiFrom.setValue(chi0)
        self.__chiTo.setValue(chi1)

    def selectedGeometry(self) -> ArcGeometryDict | None:
        """Returns the parameters used by the ArcRoi geometry.

        This only can be `None` if the dialog was cancelled.
        """
        return self.__selected

    def __computeGeometry(self) -> ArcGeometryDict | None:
        """Returns the parameters used by the ArcRoi geometry.

        The resulting dictionary contains `center`, `innerRadius`, `outerRadius`, `startAngle`, `endAngle`

        raises:
            RuntimeError: If there is no way to fix an ArcRoi geometry
        """
        roi = self.__roi
        width = roi.getOuterRadius() - roi.getInnerRadius()
        assert self.__diffractionStage is not None
        geometry = self.__diffractionStage.geometry()

        chiRadStart = numpy.deg2rad(self.__chiFrom.value())
        chiRadStop = numpy.deg2rad(self.__chiTo.value())
        q = self.__q.value()
        tthRad = tthToRad(
            q,
            unit=pyFAI.units.Q_A,
            wavelength=geometry.wavelength,
        )
        arc = self.__diffractionStage.guessArcRoiGeometry(
            tthRad, chiRadStart, chiRadStop, width
        )
        return arc
