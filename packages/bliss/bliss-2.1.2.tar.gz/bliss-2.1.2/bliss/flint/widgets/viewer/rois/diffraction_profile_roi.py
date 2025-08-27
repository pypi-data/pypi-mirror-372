# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

from __future__ import annotations

import numpy
import logging
import weakref

from silx.gui import qt
from silx.gui.plot import items
from silx.gui.plot.tools.profile.rois import ProfileImageDirectedLineROI
from silx.gui.plot.tools.profile import core

# FIXME: THis have to be refactored to avoid import in this direction
from bliss.flint.viewers.live_image.stages.diffraction_stage import DiffractionStage

try:
    import pyFAI
    import pyFAI.units
    from pyFAI.gui.utils.unitutils import from2ThRad
except ImportError as e:
    pyFAI = None
    pyFAIerror = e

    def raisePyFaiNotAvailable():
        global pyFAIerror
        raise pyFAIerror

    def from2ThRad(*args, **kwargs):
        raisePyFaiNotAvailable()


_logger = logging.getLogger(__name__)


class DiffractionImageProfileDirectedLineROI(ProfileImageDirectedLineROI):

    NAME = "diffraction line profile"
    ICON = "flint:icons/shape-diffraction-directed"

    _plotShape = "point"
    """Inform that the first interaction is done by a single click"""

    def __init__(self, parent=None):
        super(DiffractionImageProfileDirectedLineROI, self).__init__(parent=parent)
        self.__diffractionStage = None

    def _connectToPlot(self, plot):
        super(DiffractionImageProfileDirectedLineROI, self)._connectToPlot(plot)
        diffractionStage = self._findDiffractionStage(plot)
        if diffractionStage is not None:
            diffractionStage.sigBeamCenterChanged.connect(self.__beamCenterUpdated)
            self.__diffractionStage = weakref.ref(diffractionStage)
        else:
            self.__diffractionStage = None
        self.centerOriginToBeamCenter()

    def _disconnectFromPlot(self, plot):
        super(DiffractionImageProfileDirectedLineROI, self)._disconnectFromPlot(plot)
        diffractionStage = self._getDiffractionStage()
        if diffractionStage is not None:
            diffractionStage.sigBeamCenterChanged.disconnect(self.__beamCenterUpdated)
        self.__diffractionStage = None

    def __beamCenterUpdated(self, coord):
        if coord is not None:
            _p0, p1 = self.getEndPoints()
            self.setEndPoints(coord, p1)

    def setFirstShapePoints(self, points):
        assert len(points) == 1
        self.setEndPoints((0, 0), points[0])

    def _setProfileManager(self, profileManager):
        ProfileImageDirectedLineROI._setProfileManager(self, profileManager)

    def _getDiffractionStage(self) -> DiffractionStage:
        if self.__diffractionStage is None:
            return None
        return self.__diffractionStage()

    def _findDiffractionStage(self, plot=None) -> DiffractionStage:
        if plot is None:
            profileManager = self.getProfileManager()
            plot = profileManager.getPlotWidget()

        from bliss.flint.widgets.image_plot import ImagePlotWidget

        def getImagePlotWidget(plot) -> ImagePlotWidget:
            # FIXME: This is very fragile
            try:
                w = plot.parent().parent().parent().parent()
            except Exception:
                return None
            if not isinstance(w, ImagePlotWidget):
                raise RuntimeError(
                    f"Unexpected class {type(w).__name__} found. Something have changed in the implementation"
                )
            return w

        imagePlotWidget = getImagePlotWidget(plot)
        diffractionStage = imagePlotWidget.imageProcessing().diffractionStage()
        return diffractionStage

    def computeProfile(self, item):
        if not isinstance(item, items.ImageBase):
            raise TypeError("Unexpected class %s" % type(item))

        diffractionStage = self._getDiffractionStage()
        if not diffractionStage.isEnabled():
            return None
        if not diffractionStage.isValid():
            return None

        from silx.image.bilinear import BilinearImage

        origin = item.getOrigin()
        scale = item.getScale()
        method = self.getProfileMethod()
        lineWidth = self.getProfileLineWidth()
        currentData = item.getValueData(copy=False)

        roiInfo = self._getRoiInfo()
        roiStart, roiEnd, _lineProjectionMode = roiInfo

        startPt = (
            (roiStart[1] - origin[1]) / scale[1],
            (roiStart[0] - origin[0]) / scale[0],
        )
        endPt = ((roiEnd[1] - origin[1]) / scale[1], (roiEnd[0] - origin[0]) / scale[0])

        if numpy.array_equal(startPt, endPt):
            return None

        bilinear = BilinearImage(currentData)
        profile = bilinear.profile_line(
            (startPt[0] - 0.5, startPt[1] - 0.5),
            (endPt[0] - 0.5, endPt[1] - 0.5),
            lineWidth,
            method=method,
        )

        # Compute x-axis
        py = numpy.linspace(startPt[0] - 0.5, endPt[0] - 0.5, len(profile))
        px = numpy.linspace(startPt[1] - 0.5, endPt[1] - 0.5, len(profile))
        tthRads = diffractionStage.getTTh(px, py)
        chiRad, _tthRad = diffractionStage.getChiTth(px[-1], py[-1])
        geometry = diffractionStage.geometry()
        wavelength = geometry.wavelength
        qs = from2ThRad(tthRads, pyFAI.units.Q_A, wavelength)

        title = f"Diffraction pattern; width = {lineWidth} px; chi = {numpy.rad2deg(chiRad):0.2f} deg"
        xLabel = "q (in Å⁻¹)"
        yLabel = str(method).capitalize()

        data = core.CurveProfileData(
            coords=qs,
            profile=profile,
            title=title,
            xLabel=xLabel,
            yLabel=yLabel,
        )
        return data

    def centerOriginToBeamCenter(self):
        diffractionStage = self._getDiffractionStage()
        if diffractionStage is not None:
            _p0, p1 = self.getEndPoints()
            beamCenter = diffractionStage.beamCenter()
            if beamCenter is not None:
                self.setEndPoints(beamCenter, p1)

    def _feedContextMenu(self, menu: qt.QMenu):
        """Called by Flint to feed the context menu when the mouse is over the mouse"""
        centerAction = qt.QAction(menu)
        centerAction.setText(f"Center {self.getName()} origin to the beam center")
        centerAction.triggered.connect(self.centerOriginToBeamCenter)
        menu.addAction(centerAction)
