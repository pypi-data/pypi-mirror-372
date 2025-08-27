# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

from __future__ import annotations
from typing import NamedTuple
from typing import TypedDict


import numpy
import logging
from silx.gui import qt
from .base_stage import BaseStage
from bliss.flint.widgets.viewer.tooltip_item_manager import TooltipExtension
from bliss.flint.widgets.viewer import flint_plot
from bliss.flint.helper.tooltip_factory import TooltipFactory
from bliss.flint.model import flint_model
from bliss.flint.model import scan_model
from bliss.flint.utils.mathutils import angular_dist

_CHI_DEG = object()

try:
    import pyFAI
    import pyFAI.units
    from pyFAI.geometry import Geometry as PyFaiGeometry
    from pyFAI.detectors import Detector, detector_factory
    from pyFAI.calibrant import get_calibrant, Calibrant
    from pyFAI.gui.utils.unitutils import from2ThRad
    from pyFAI.utils.ellipse import fit_ellipse
    from pyFAI.ext.invert_geometry import InvertGeometry

    _RecD2_A = pyFAI.units.RADIAL_UNITS.get("d*2_A^-2", object())
    _Q_A = pyFAI.units.Q_A
    _D_A = pyFAI.units.RADIAL_UNITS.get("d_A", object())
    _TTH_DEG = pyFAI.units.TTH_DEG

except ImportError as e:
    pyFAI = None
    pyFAIerror = e
    _RecD2_A = object()
    _Q_A = object()
    _D_A = object()
    _TTH_DEG = object()

    def raisePyFaiNotAvailable():
        global pyFAIerror
        raise pyFAIerror

    class Detector:
        def __init__(self, *args, **kwargs):
            raisePyFaiNotAvailable()

    class InvertGeometry:
        def __init__(self, *args, **kwargs):
            raisePyFaiNotAvailable()

    class PyFaiGeometry:
        def __init__(self, *args, **kwargs):
            raisePyFaiNotAvailable()

    class Calibrant:
        def __init__(self, *args, **kwargs):
            raisePyFaiNotAvailable()

    def detector_factory(*args, **kwargs):
        raisePyFaiNotAvailable()

    def get_calibrant(*args, **kwargs):
        raisePyFaiNotAvailable()

    def from2ThRad(*args, **kwargs):
        raisePyFaiNotAvailable()


_logger = logging.getLogger(__name__)


class Ring(NamedTuple):
    """Description of a ring including the data to display it"""

    nb: int
    tthRad: float
    q: float
    contour: numpy.ndarray


def toUnit(chi, tth, unit, wavelength=None, directDist=None, ai=None):
    """Convert chi/tth to another unit

    Arguments:
        chi: Chi in rad
        tth: Two theta in rad
    """
    if unit == _CHI_DEG:
        return numpy.rad2deg(chi)
    elif unit == pyFAI.units.RecD2_NM:
        # FIXME: This have to be backported to pyfai
        q_nm = (4.0e-9 * numpy.pi / wavelength) * numpy.sin(0.5 * tth)
        return (q_nm / (2.0 * numpy.pi)) ** 2
    elif unit == _RecD2_A:
        # FIXME: This have to be backported to pyfai
        q_A = (4.0e-10 * numpy.pi / wavelength) * numpy.sin(0.5 * tth)
        return (q_A / (2.0 * numpy.pi)) ** 2
    elif unit == _D_A:
        # FIXME: This have to be backported to pyfai
        q_m = (4.0 * numpy.pi / wavelength) * numpy.sin(0.5 * tth)
        return (2 * numpy.pi / q_m) * 1e10
    return from2ThRad(tth, unit, wavelength, directDist, ai)


UNITS = {
    "CHI_DEG": (_CHI_DEG, "χ", "deg", 2),
    "Q_A-1": (_Q_A, "q", "Å⁻¹", 3),
    "RecD2_A-2": (_RecD2_A, "d*²", "Å⁻²", 3),
    "D_A": (_D_A, "d", "Å", 3),
    "TTH_DEG": (_TTH_DEG, "2θ", "deg", 2),
}


def _concatenate_polygons_with_nan_separator(polygons: numpy.ndarray) -> numpy.ndarray:
    """Returns a single polygon shape, which use a NaN between each polygons"""
    npoints = 0
    for p in polygons:
        npoints += p.shape[0]
    if npoints > 0:
        npoints += len(polygons) - 1
    result = numpy.empty((npoints, 2), dtype=numpy.float32)
    cursor = 0
    for p in polygons:
        if cursor != 0:
            result[cursor, :] = numpy.nan
            cursor += 1
        result[cursor : cursor + p.shape[0], :] = p
        cursor += p.shape[0]
    return result


class Geometry(NamedTuple):
    """Abstract pyfai geometry"""

    dist: float | None = None
    poni1: float | None = None
    poni2: float | None = None
    rot1: float | None = None
    rot2: float | None = None
    rot3: float | None = None
    wavelength: float | None = None

    def isValid(self) -> bool:
        """Returns true if everything is set in this geometry"""
        if self.dist is None:
            return False
        if self.poni1 is None:
            return False
        if self.poni2 is None:
            return False
        if self.rot1 is None:
            return False
        if self.rot2 is None:
            return False
        if self.rot3 is None:
            return False
        if self.wavelength is None:
            return False
        return True


class ArcGeometryDict(TypedDict):
    center: tuple[float, float]
    innerRadius: float
    outerRadius: float
    startAngle: float
    endAngle: float


class DiffractionStage(BaseStage, TooltipExtension):

    sigBeamCenterChanged = qt.Signal(object)

    def __init__(self, parent: qt.QObject | None = None):
        BaseStage.__init__(self, parent=parent)
        self.__shape = None
        self.__rings: list[Ring] | None = None
        self.__geometry: Geometry = Geometry()
        self.__pyFaiGeometry: PyFaiGeometry | None = None
        self.__pyFaiInvertGeometry: InvertGeometry | None = None
        self.__detector: Detector | None = None
        self.__calibrant: Calibrant | None = None
        self.__ringsInvalidated: bool = False
        self.__beamCenter: tuple[float, float] | None = None
        self.__ringsVisible: bool = True
        self.__tooltipUnits = ["CHI_DEG", "D_A", "TTH_DEG"]

    def setDetector(self, detector: Detector | str):
        if self.__detector is detector:
            return
        if not isinstance(detector, Detector):
            detector = detector_factory(detector)
        self.__detector = detector
        self.__invalidateGeometry()
        self.configUpdated.emit()

    def detector(self) -> Detector | None:
        return self.__detector

    def setCalibrant(self, calibrant: Calibrant | str):
        if self.__calibrant == calibrant:
            return
        if not isinstance(calibrant, Calibrant):
            if calibrant.upper().endswith(".D") or calibrant.upper().endswith(".DS"):
                filename = calibrant
                calibrant = Calibrant()
                calibrant.load_file(filename)
            else:
                calibrant = get_calibrant(calibrant)
        self.__calibrant = calibrant
        self.__invalidateRings()
        self.configUpdated.emit()

    def calibrant(self) -> Calibrant | None:
        return self.__calibrant

    def setGeometry(
        self,
        fileName=None,
        dist=None,
        poni1=None,
        poni2=None,
        rot1=None,
        rot2=None,
        rot3=None,
        wavelength=None,
    ):
        if fileName is not None:
            g = pyFAI.load(fileName)
            dist = g.dist
            poni1 = g.poni1
            poni2 = g.poni2
            rot1 = g.rot1
            rot2 = g.rot2
            rot3 = g.rot3
            wavelength = g.wavelength
        geometry = Geometry(
            dist=dist,
            poni1=poni1,
            poni2=poni2,
            rot1=rot1,
            rot2=rot2,
            rot3=rot3,
            wavelength=wavelength,
        )
        if self.__geometry == geometry:
            return
        self.__geometry = geometry
        self.__invalidateGeometry()
        self.configUpdated.emit()

    def geometry(self) -> Geometry:
        return self.__geometry

    def setDataSize(self, data):
        """Set the actual data size"""
        if self.__shape == data.shape:
            return
        self.__shape = data.shape
        self.__invalidateRings()

    def __invalidateRings(self):
        self.__ringsInvalidated = True
        self.__rings = None

    def __invalidateGeometry(self):
        self.__pyFaiGeometry = None
        self.__pyFaiInvertGeometry = None
        self.__invalidateRings()

    def __getPyFaiGeometry(self) -> PyFaiGeometry | None:
        if pyFAI is None:
            raisePyFaiNotAvailable()

        if self.__pyFaiGeometry is not None:
            return self.__pyFaiGeometry

        geometry = self.__geometry
        if not geometry.isValid():
            return None

        if self.__detector is None:
            return None

        result = PyFaiGeometry(
            dist=geometry.dist,
            poni1=geometry.poni1,
            poni2=geometry.poni2,
            rot1=geometry.rot1,
            rot2=geometry.rot2,
            rot3=geometry.rot3,
            detector=self.__detector,
            wavelength=geometry.wavelength,
        )
        self.__pyFaiGeometry = result
        return result

    def __getPyFaiInvertGeometry(self) -> InvertGeometry:
        if pyFAI is None:
            raisePyFaiNotAvailable()

        if self.__pyFaiInvertGeometry is not None:
            return self.__pyFaiInvertGeometry

        geometry = self.__getPyFaiGeometry()
        assert geometry is not None
        invertGeometry = InvertGeometry(
            geometry.array_from_unit(
                typ="center", unit=pyFAI.units.TTH_RAD, scale=False
            ),
            geometry.chiArray(),
        )
        self.__pyFaiInvertGeometry = invertGeometry
        return invertGeometry

    def __updateRings(self):
        self._resetApplyedCorrections()

        calibrant = self.__calibrant
        if calibrant is None:
            self._setRings(None)
            self._setBeamCenter(None)
            return

        geometry = self.__getPyFaiGeometry()
        if geometry is None:
            self._setRings(None)
            self._setBeamCenter(None)
            return

        wavelength = self.__geometry.wavelength
        assert wavelength is not None

        tthArray = geometry.twoThetaArray()
        calibrant.set_wavelength(wavelength)
        tths = calibrant.get_2th()

        try:
            from silx.image.marchingsquares import MarchingSquaresMergeImpl

            # FIXME: Speedup with cached statistics
            algo = MarchingSquaresMergeImpl(tthArray)
            rings = []
            for i, tthRad in enumerate(tths):
                polygons = algo.find_contours(tthRad)
                polygon = _concatenate_polygons_with_nan_separator(polygons)
                q = from2ThRad(tthRad, pyFAI.units.Q_A, wavelength)
                rings.append(Ring(nb=i, tthRad=tthRad, q=q, contour=polygon))
            self._setRings(rings)
        except Exception:
            _logger.error("Error while computing diffraction rings", exc_info=True)
            self._setRings(None)

        try:
            f2d = geometry.getFit2D()
            coord = f2d["centerX"], f2d["centerY"]
            self._setBeamCenter(coord)
        except Exception:
            _logger.error("Error while computing beam center", exc_info=True)
            self._setBeamCenter(None)

    def setRingsVisible(self, visible: bool):
        if self.__ringsVisible == visible:
            return
        self.__ringsVisible = visible
        self.configUpdated.emit()

    def isRingsVisible(self) -> bool:
        return self.__ringsVisible

    def _setRings(self, rings):
        if self.__rings is rings:
            return
        self.__rings = rings
        self.sinkResultUpdated.emit()

    def beamCenter(self) -> tuple[float, float] | None:
        return self.__beamCenter

    def _setBeamCenter(self, coord: tuple[float, float] | None):
        if self.__beamCenter is coord:
            return
        self.__beamCenter = coord
        self.sigBeamCenterChanged.emit(coord)

    def isValid(self):
        return self.__detector is not None and self.__geometry.isValid()

    def rings(self) -> list[Ring] | None:
        return self.__rings

    def getChiTth(self, x: float, y: float):
        """Returns chi and 2theta angles in radian from data coordinate

        Arguments:
            x: X-coord in data coords (pixel detector)
            y: Y-coord in data coords (pixel detector)
        """

        geometry = self.__getPyFaiGeometry()
        assert geometry is not None
        ax, ay = numpy.array([x]), numpy.array([y])
        chi = geometry.chi(ay, ax)[0]
        tth = geometry.tth(ay, ax)[0]
        return chi, tth

    def getTTh(self, x: numpy.ndarray, y: numpy.ndarray):
        """Returns tth in radian for a list of pixels"""
        geometry = self.__getPyFaiGeometry()
        assert geometry is not None
        tth = geometry.tth(y, x)
        return tth

    def setTooltipUnits(self, units: list[str]):
        if self.__tooltipUnits == units:
            return
        self.__tooltipUnits = units
        self.configUpdated.emit()

    def tooltipUnits(self) -> list[str]:
        return self.__tooltipUnits

    def feedFlintTooltip(
        self,
        tooltip: TooltipFactory,
        plotModel: flint_plot.FlintPlot,
        flintModel: flint_model.FlintState,
        scan: scan_model.Scan,
        dx: float,
        dy: float,
    ):
        if not self.isValid():
            return None

        chi, tth = self.getChiTth(dx, dy)
        wavelength = self.__geometry.wavelength

        def feedQuantity(unitName):
            unitDef = UNITS.get(unitName)
            if unitDef is None:
                _logger.error("Unsupported unit %s", unitName)
                return
            code, label, unit, ndigits = unitDef
            value = toUnit(chi, tth, code, wavelength)
            tooltip.addQuantity(label, value, unit, ndigits=ndigits)

        if len(self.__tooltipUnits) == 0:
            return

        if not tooltip.isEmpty():
            tooltip.addSeparator()
        for n in self.__tooltipUnits:
            feedQuantity(n)

    def correction(self, image: numpy.ndarray):
        self.setDataSize(image)
        if self.__ringsInvalidated:
            self.__ringsInvalidated = False
            self.__updateRings()
        return None

    def guessArcRoiGeometry(
        self, tthRad: float, chiRadStart: float, chiRadStop: float, width: float
    ) -> ArcGeometryDict | None:
        """Guess an arc roi geometry from a tth/chi space.

        Returns the parameters which can be feed to a silx `ArcROI`.

        Arguments:
            tthRad: 2 theta location in radian
            chiRadStart: start chi location in radian
            chiRadStop: stop chi location in radian
            width: Width of the ROI in pixel
        """
        geometry = self.__getPyFaiGeometry()
        invertGeometry = self.__getPyFaiInvertGeometry()
        tthRads = numpy.empty(10)
        tthRads[:] = tthRad
        chiRads = numpy.linspace(chiRadStart, chiRadStop, 10)
        chiRads[chiRads > numpy.pi] -= 2 * numpy.pi
        pixels = invertGeometry.many(tthRads, chiRads, True)

        # Double check with the inverse transformation
        assert geometry is not None
        tthFromPixel = geometry.tth(pixels[:, 0], pixels[:, 1])
        chiFromPixel = geometry.chi(pixels[:, 0], pixels[:, 1])
        is_valid = (
            numpy.sqrt(
                angular_dist(tthRads, tthFromPixel) ** 2
                + angular_dist(chiRads, chiFromPixel) ** 2
            )
            <= 0.2
        )
        pixels = pixels[is_valid, :]
        ellipse = fit_ellipse(pixels[:, 1], pixels[:, 0])
        radius = (ellipse.half_long_axis + ellipse.half_short_axis) * 0.5

        def get_angle(pixels, index):
            return numpy.arctan2(
                pixels[index][0] - ellipse.center_2,
                pixels[index][1] - ellipse.center_1,
            )

        start = get_angle(pixels, 0)
        stop = get_angle(pixels, -1)

        # normalize the 'end' with the right oriented direction
        expected = abs(angular_dist(chiRads[-1], chiRads[0]))
        posibilities = numpy.array([stop, stop + numpy.pi * 2, stop - numpy.pi * 2])
        i = numpy.argmin(numpy.abs(numpy.abs(posibilities - start) - expected))
        stop = posibilities[i]

        return {
            "center": (ellipse.center_1, ellipse.center_2),
            "innerRadius": radius - width * 0.5,
            "outerRadius": radius + width * 0.5,
            "startAngle": get_angle(pixels, 0),
            "endAngle": stop,
        }
