# coding: utf-8
# /*##########################################################################
#
# Copyright (c) European Synchrotron Radiation Facility
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# ###########################################################################*/
"""QWidget displaying a 2D image with histograms on its sides.

The :class:`ImageView` implements this widget, and
:class:`ImageViewMainWindow` provides a main window with additional toolbar
and status bar.

Basic usage of :class:`ImageView` is through the following methods:

- :meth:`ImageView.getColormap`, :meth:`ImageView.setColormap` to update the
  default colormap to use and update the currently displayed image.
- :meth:`ImageView.setImage` to update the displayed image.

For an example of use, see `imageview.py` in :ref:`sample-code`.
"""

from __future__ import annotations
from __future__ import division

__authors__ = ["T. Vincent"]
__license__ = "MIT"
__date__ = "26/04/2018"


from typing import NamedTuple
import logging
import numpy

from silx.gui import qt
from silx.gui import colors
from silx.gui.plot import PlotWidget
from silx.gui.plot import _utils
from silx.gui.plot.actions import PlotAction
from silx.gui.utils import blockSignals

_logger = logging.getLogger(__name__)


class ProfileSumResult(NamedTuple):
    dataXRange: tuple[int, int]
    dataYRange: tuple[int, int]
    histoH: int
    histoHRange: tuple[int, int]
    histoV: int
    histoVRange: tuple[int, int]
    xCoords: int
    xData: int
    yCoords: int
    yData: int


def computeProfileSumOnRange(imageItem, xRange, yRange, cache=None):
    """
    Compute a full vertical and horizontal profile on an image item using a
    a range in the plot referential.

    Optionally takes a previous computed result to be able to skip the
    computation.

    :rtype: ProfileSumResult
    """
    data = imageItem.getValueData(copy=False)
    origin = imageItem.getOrigin()
    scale = imageItem.getScale()
    height, width = data.shape

    xMin, xMax = xRange
    yMin, yMax = yRange

    # Convert plot area limits to image coordinates
    # and work in image coordinates (i.e., in pixels)
    xMin = int((xMin - origin[0]) / scale[0])
    xMax = int((xMax - origin[0]) / scale[0])
    yMin = int((yMin - origin[1]) / scale[1])
    yMax = int((yMax - origin[1]) / scale[1])

    if xMin >= width or xMax < 0 or yMin >= height or yMax < 0:
        return None

    # The image is at least partly in the plot area
    # Get the visible bounds in image coords (i.e., in pixels)
    subsetXMin = 0 if xMin < 0 else xMin
    subsetXMax = (width if xMax >= width else xMax) + 1
    subsetYMin = 0 if yMin < 0 else yMin
    subsetYMax = (height if yMax >= height else yMax) + 1

    if cache is not None:
        if (subsetXMin, subsetXMax) == cache.dataXRange and (
            subsetYMin,
            subsetYMax,
        ) == cache.dataYRange:
            # The visible area of data is the same
            return cache

    # Rebuild histograms for visible area
    visibleData = data[subsetYMin:subsetYMax, subsetXMin:subsetXMax]
    histoHVisibleData = numpy.nansum(visibleData, axis=0)
    histoVVisibleData = numpy.nansum(visibleData, axis=1)
    histoHMin = numpy.nanmin(histoHVisibleData)
    histoHMax = numpy.nanmax(histoHVisibleData)
    histoVMin = numpy.nanmin(histoVVisibleData)
    histoVMax = numpy.nanmax(histoVVisibleData)

    # Convert to histogram curve and update plots
    # Taking into account origin and scale
    coords = numpy.arange(2 * histoHVisibleData.size)
    xCoords = (coords + 1) // 2 + subsetXMin
    xCoords = origin[0] + scale[0] * xCoords
    xData = numpy.take(histoHVisibleData, coords // 2)
    coords = numpy.arange(2 * histoVVisibleData.size)
    yCoords = (coords + 1) // 2 + subsetYMin
    yCoords = origin[1] + scale[1] * yCoords
    yData = numpy.take(histoVVisibleData, coords // 2)

    result = ProfileSumResult(
        dataXRange=(subsetXMin, subsetXMax),
        dataYRange=(subsetYMin, subsetYMax),
        histoH=histoHVisibleData,
        histoHRange=(histoHMin, histoHMax),
        histoV=histoVVisibleData,
        histoVRange=(histoVMin, histoVMax),
        xCoords=xCoords,
        xData=xData,
        yCoords=yCoords,
        yData=yData,
    )

    return result


class SideHistogram(PlotWidget):
    """
    Widget displaying one of the side profile of the ImageView.

    Implement ProfileWindow
    """

    sigClose = qt.Signal()

    sigMouseMoved = qt.Signal(float, float)

    def __init__(self, parent=None, backend=None, direction=qt.Qt.Horizontal):
        super(SideHistogram, self).__init__(parent=parent, backend=backend)
        self._direction = direction
        self.sigPlotSignal.connect(self._plotEvents)
        self._color = "blue"
        self.__profile = None
        self.__profileSum = None

    def _plotEvents(self, eventDict):
        """Callback for horizontal histogram plot events."""
        if eventDict["event"] == "mouseMoved":
            self.sigMouseMoved.emit(eventDict["x"], eventDict["y"])

    def setProfileColor(self, color):
        self._color = color

    def setProfileSum(self, result):
        self.__profileSum = result
        if self.__profile is None:
            self.__drawProfileSum()

    def prepareWidget(self, roi):
        """Implements `ProfileWindow`"""
        pass

    def setRoiProfile(self, roi):
        """Implements `ProfileWindow`"""
        if roi is None:
            return
        self._roiColor = colors.rgba(roi.getColor())

    def getProfile(self):
        """Implements `ProfileWindow`"""
        return self.__profile

    def setProfile(self, data):
        """Implements `ProfileWindow`"""
        self.__profile = data
        if data is None:
            self.__drawProfileSum()
        else:
            self.__drawProfile()

    def __drawProfileSum(self):
        """Only draw the profile sum on the plot.

        Other elements are removed
        """
        profileSum = self.__profileSum

        try:
            self.removeCurve("profile")
        except Exception:
            pass

        if profileSum is None:
            try:
                self.removeCurve("profilesum")
            except Exception:
                pass
            return

        if self._direction == qt.Qt.Horizontal:
            xx, yy = profileSum.xCoords, profileSum.xData
        elif self._direction == qt.Qt.Vertical:
            xx, yy = profileSum.yData, profileSum.yCoords
        else:
            assert False

        self.addCurve(
            xx,
            yy,
            xlabel="",
            ylabel="",
            legend="profilesum",
            color=self._color,
            linestyle="-",
            selectable=False,
            resetzoom=False,
        )

        self.__updateLimits()

    def __drawProfile(self):
        """Only draw the profile on the plot.

        Other elements are removed
        """
        profile = self.__profile

        try:
            self.removeCurve("profilesum")
        except Exception:
            pass

        if profile is None:
            try:
                self.removeCurve("profile")
            except Exception:
                pass
            self.setProfileSum(self.__profileSum)
            return

        if self._direction == qt.Qt.Horizontal:
            xx, yy = profile.coords, profile.profile
        elif self._direction == qt.Qt.Vertical:
            xx, yy = profile.profile, profile.coords
        else:
            assert False

        self.addCurve(xx, yy, legend="profile", color=self._roiColor, resetzoom=False)

        self.__updateLimits()

    def __updateLimits(self):
        if self.__profile:
            data = self.__profile.profile
            vMin = numpy.nanmin(data)
            vMax = numpy.nanmax(data)
        elif self.__profileSum is not None:
            if self._direction == qt.Qt.Horizontal:
                vMin, vMax = self.__profileSum.histoHRange
            elif self._direction == qt.Qt.Vertical:
                vMin, vMax = self.__profileSum.histoVRange
            else:
                assert False
        else:
            vMin, vMax = 0, 0

        # Tune the result using the data margins
        margins = self.getDataMargins()
        if self._direction == qt.Qt.Horizontal:
            _, _, vMin, vMax = _utils.addMarginsToLimits(
                margins, False, False, 0, 0, vMin, vMax
            )
        elif self._direction == qt.Qt.Vertical:
            vMin, vMax, _, _ = _utils.addMarginsToLimits(
                margins, False, False, vMin, vMax, 0, 0
            )
        else:
            assert False

        if self._direction == qt.Qt.Horizontal:
            dataAxis = self.getYAxis()
        elif self._direction == qt.Qt.Vertical:
            dataAxis = self.getXAxis()
        else:
            assert False

        with blockSignals(dataAxis):
            dataAxis.setLimits(vMin, vMax)


class ShowSideHistogramsAction(PlotAction):
    """QAction to change visibility of side histogram of a :class:`.ImageView`.

    :param plot: :class:`.ImageView` instance on which to operate
    :param parent: See :class:`QAction`
    """

    def __init__(self, plot, parent=None):
        super(ShowSideHistogramsAction, self).__init__(
            plot,
            icon="side-histograms",
            text="Show/hide side histograms",
            tooltip="Show/hide side histogram",
            triggered=self._actionTriggered,
            checkable=True,
            parent=parent,
        )
        if self.plot.isSideHistogramDisplayed():
            self.setChecked(True)

    def _actionTriggered(self, checked=False):
        if self.plot.isSideHistogramDisplayed() != checked:
            self.plot.setSideHistogramDisplayed(checked)
