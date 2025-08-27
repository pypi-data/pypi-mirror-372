# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.
"""Contains implementation of concrete objects used to model plots.

It exists 4 kinds of plots: curves, scatter, image, MCAs. Each plot contains
specific items. But it is not a constraint from the architecture.

Here is a list of plot and item inheritance.

.. image:: _static/flint/model/plot_model_item.png
    :alt: Scan model
    :align: center
"""

from __future__ import annotations

import numpy
import logging
import time

from . import scan_model
from . import plot_model
from . import style_model

_logger = logging.getLogger(__name__)


class ScalarPlot(plot_model.Plot):
    """Define that the relative scan contains data which have to be displayed
    with scalar view (ct widget)."""


class CurvePlot(plot_model.Plot):
    """Define a plot which mostly draw curves."""

    def __init__(self, parent=None):
        super(CurvePlot, self).__init__(parent=parent)
        self.__scansStored = False
        self.__xaxisEditSource = None
        self.__xaxisUserEditTime = None

    def tagXaxisRawEdit(self):
        """Tag the x-axis of the model as not edited by any source"""
        self.__xaxisEditSource = None
        self.__xaxisUserEditTime = None
        self.valueChanged.emit(plot_model.ChangeEventType.XAXIS_USER_EDIT_TIME)

    def tagXaxisUserEditTime(self):
        """Tag the x-axis of the model as edited by the user now"""
        self.setXaxisUserEditTime(time.time())

    def setXaxisUserEditTime(self, userEditTime: float):
        """Set a specific user edit time"""
        self.__xaxisEditSource = "user"
        self.__xaxisUserEditTime = userEditTime
        self.valueChanged.emit(plot_model.ChangeEventType.XAXIS_USER_EDIT_TIME)

    def xaxisEditSource(self) -> str | None:
        """Returns the actual source of the x-axis edition of this model"""
        return self.__xaxisEditSource

    def _setEditTags(self, edit):
        super()._setEditTags(edit[0])
        self.__xaxisEditSource = edit[1][0]
        self.__xaxisUserEditTime = edit[1][1]

    def _editTags(self):
        return (super()._editTags(), (self.__xaxisEditSource, self.__xaxisUserEditTime))

    def setScansStored(self, enableStoring: bool):
        self.__scansStored = enableStoring
        self.valueChanged.emit(plot_model.ChangeEventType.SCANS_STORED)

    def isScansStored(self) -> bool:
        return self.__scansStored

    def __getstate__(self):
        state = super(CurvePlot, self).__getstate__()
        assert "scan_stored" not in state
        state["scan_stored"] = self.__scansStored
        return state

    def __setstate__(self, state):
        super(CurvePlot, self).__setstate__(state)
        self.__scansStored = state.pop("scan_stored")


class ScanItem(plot_model.Item, plot_model.NotStored):
    """Define a specific scan which have to be displayed by the plot."""

    def __init__(self, parent=None, scan: scan_model.Scan | None = None):
        super(ScanItem, self).__init__(parent=parent)
        assert scan is not None
        self.__scan = scan

    def scan(self) -> scan_model.Scan:
        return self.__scan


class CurveMixIn:
    """Define what have to be provide a curve in order to manage curves from a
    scan and computed curves in the same way."""

    def __init__(self):
        self.__yAxis = "left"

    def __getstate__(self):
        state = {}
        state["y_axis"] = self.yAxis()
        return state

    def __setstate__(self, state):
        self.setYAxis(state.pop("y_axis"))

    def yAxis(self) -> str:
        return self.__yAxis

    def setYAxis(self, yAxis: str):
        if self.__yAxis == yAxis:
            return
        self.__yAxis = yAxis
        self._emitValueChanged(plot_model.ChangeEventType.YAXIS)

    def xData(self, scan: scan_model.Scan) -> scan_model.Data | None:
        raise NotImplementedError()

    def yData(self, scan: scan_model.Scan) -> scan_model.Data | None:
        raise NotImplementedError()

    def xArray(self, scan: scan_model.Scan) -> numpy.ndarray | None:
        data = self.xData(scan)
        if data is None:
            return None
        return data.array()

    def yArray(self, scan: scan_model.Scan) -> numpy.ndarray | None:
        data = self.yData(scan)
        if data is None:
            return None
        return data.array()

    def displayName(self, axisName, scan: scan_model.Scan) -> str:
        """Helper to reach the axis display name"""
        raise NotImplementedError()


class CurveItem(plot_model.Item, CurveMixIn):
    """Define a curve as part of a plot.

    X and Y values are defined by a `ChannelRef`.
    """

    def __init__(self, parent: plot_model.Plot | None = None):
        plot_model.Item.__init__(self, parent=parent)
        CurveMixIn.__init__(self)
        self.__x: plot_model.ChannelRef | None = None
        self.__y: plot_model.ChannelRef | None = None

    def __getstate__(self):
        state: dict[str, object] = {}
        state.update(plot_model.Item.__getstate__(self))
        state.update(CurveMixIn.__getstate__(self))
        assert "x" not in state
        assert "y" not in state
        state["x"] = self.__x
        state["y"] = self.__y
        return state

    def __setstate__(self, state):
        plot_model.Item.__setstate__(self, state)
        CurveMixIn.__setstate__(self, state)
        self.__x = state.pop("x")
        self.__y = state.pop("y")

    def isValid(self):
        return self.__x is not None and self.__y is not None

    def isAvailableInScan(self, scan: scan_model.Scan) -> bool:
        """Returns true if this item is available in this scan.

        This only imply that the data source is available.
        """
        if not self.isValid():
            return False
        xchannel = self.xChannel()
        assert xchannel is not None
        if not isinstance(xchannel, plot_model.XIndexChannelRef):
            if xchannel.channel(scan) is None:
                return False
        ychannel = self.yChannel()
        assert ychannel is not None
        if ychannel.channel(scan) is None:
            return False
        return True

    def getScanValidation(self, scan: scan_model.Scan) -> str | None:
        """
        Returns None if everything is fine, else a message to explain the problem.
        """
        xx = self.xArray(scan)
        yy = self.yArray(scan)
        if xx is None and yy is None:
            return "No data available for X and Y data"
        elif xx is None:
            return "No data available for X data"
        elif yy is None:
            return "No data available for Y data"
        elif xx.ndim != 1:
            return "Dimension of X data do not match"
        elif yy.ndim != 1:
            return "Dimension of Y data do not match"
        elif len(xx) != len(yy):
            return "Size of X and Y data do not match"
        # It's fine
        return None

    def xChannel(self) -> plot_model.ChannelRef | None:
        return self.__x

    def setXChannel(self, channel: plot_model.ChannelRef | None):
        self.__x = channel
        self._emitValueChanged(plot_model.ChangeEventType.X_CHANNEL)

    def yChannel(self) -> plot_model.ChannelRef | None:
        return self.__y

    def setYChannel(self, channel: plot_model.ChannelRef | None):
        self.__y = channel
        self._emitValueChanged(plot_model.ChangeEventType.Y_CHANNEL)

    def xData(self, scan: scan_model.Scan) -> scan_model.Data | None:
        channel = self.xChannel()
        if isinstance(channel, plot_model.XIndexChannelRef):
            y = self.yArray(scan)
            if y is None:
                return None
            array = numpy.arange(len(y))
            return scan_model.Data(array=array)

        if channel is None:
            return None
        data = channel.data(scan)
        if data is None:
            return None
        return data

    def yData(self, scan: scan_model.Scan) -> scan_model.Data | None:
        channel = self.yChannel()
        if channel is None:
            return None
        data = channel.data(scan)
        if data is None:
            return None
        return data

    def displayName(self, axisName, scan: scan_model.Scan) -> str:
        """Helper to reach the axis display name"""
        if axisName == "x":
            xChannel = self.xChannel()
            if isinstance(xChannel, plot_model.XIndexChannelRef):
                return "index"
            assert xChannel is not None
            return xChannel.displayName(scan)
        elif axisName == "y":
            yChannel = self.yChannel()
            assert yChannel is not None
            return yChannel.displayName(scan)
        else:
            assert False

    def __str__(self):
        return "<%s x=%s y=%s yaxis=%s />" % (
            type(self).__name__,
            self.__x,
            self.__y,
            self.yAxis(),
        )


class XIndexCurveItem(CurveItem):
    """Define a curve as part of a plot.

    X is fixed as an index and Y value is defined by a `ChannelRef`.
    """

    def __init__(self, parent):
        super(XIndexCurveItem, self).__init__(parent)
        xchannel = plot_model.XIndexChannelRef(parent, None)
        self.setXChannel(xchannel)


class McaPlot(plot_model.Plot):
    """Define a plot which is specific for MCAs."""

    def __init__(self, parent=None):
        plot_model.Plot.__init__(self, parent=parent)
        self.__deviceName: str | None = None
        self.__xAxisInEnergy = False

    def setXaxisInEnergy(self, inEnergy: bool):
        if self.__xAxisInEnergy == inEnergy:
            return
        self.__xAxisInEnergy = inEnergy
        self.valueChanged.emit(plot_model.ChangeEventType.MCA_X_AXIS)

    def xAxisInEnergy(self) -> bool:
        return self.__xAxisInEnergy

    def deviceName(self) -> str | None:
        return self.__deviceName

    def setDeviceName(self, name: str):
        self.__deviceName = name

    def plotTitle(self) -> str:
        return self.__deviceName

    def hasSameTarget(self, other: plot_model.Plot) -> bool:
        if type(self) is not type(other):
            return False
        if self.__deviceName != other.deviceName():
            return False
        return True


class TablePlot(plot_model.Plot):
    """Define a plot which is displayed by a table."""

    def __init__(self, parent=None):
        plot_model.Plot.__init__(self, parent=parent)
        self.__plotTitle = "%s"

    def setPlotTitle(self, title):
        self.__plotTitle = title

    def plotTitle(self) -> str:
        return self.__plotTitle


class OneDimDataPlot(plot_model.Plot):
    """Define a plot which is specific for one dim data.

    It is not the same as `CurvePlot` as the content of the channels is 1D for
    each steps of the scan.
    """

    def __init__(self, parent=None):
        plot_model.Plot.__init__(self, parent=parent)
        self.__deviceName: str | None = None
        self.__plotTitle = "%s"

    def setPlotTitle(self, title):
        self.__plotTitle = title

    def deviceName(self) -> str | None:
        return self.__deviceName

    def plotTitle(self) -> str:
        return self.__plotTitle

    def setDeviceName(self, name: str):
        self.__deviceName = name

    def hasSameTarget(self, other: plot_model.Plot) -> bool:
        if type(self) is not type(other):
            return False
        if self.__deviceName != other.deviceName():
            return False
        return True


class McaItem(plot_model.Item):
    """Define a MCA as part of a plot.

    The MCA data is defined by a `ChannelRef`.
    """

    def __init__(self, parent: plot_model.Plot | None = None):
        super(McaItem, self).__init__(parent=parent)
        self.__mca: plot_model.ChannelRef | None = None

    def __reduce__(self):
        return (self.__class__, (), self.__getstate__())

    def __getstate__(self):
        state = super(McaItem, self).__getstate__()
        assert "mca" not in state
        state["mca"] = self.__mca
        return state

    def __setstate__(self, state):
        super(McaItem, self).__setstate__(state)
        self.__mca = state.pop("mca")

    def isValid(self):
        return self.__mca is not None

    def mcaChannel(self) -> plot_model.ChannelRef | None:
        return self.__mca

    def setMcaChannel(self, channel: plot_model.ChannelRef):
        self.__mca = channel
        self._emitValueChanged(plot_model.ChangeEventType.MCA_CHANNEL)


class ImagePlot(plot_model.Plot):
    """Define a plot which displays images."""

    def __init__(self, parent=None):
        plot_model.Plot.__init__(self, parent=parent)
        self.__deviceName: str | None = None

    def deviceName(self) -> str | None:
        return self.__deviceName

    def plotTitle(self) -> str:
        return self.__deviceName

    def setDeviceName(self, name: str):
        self.__deviceName = name

    def hasSameTarget(self, other: plot_model.Plot) -> bool:
        if type(self) is not type(other):
            return False
        if self.__deviceName != other.deviceName():
            return False
        return True


class ImageItem(plot_model.Item):
    """Define an image as part of a plot.

    The image is defined by a `ChannelRef`.
    """

    def __init__(self, parent: plot_model.Plot | None = None):
        super(ImageItem, self).__init__(parent=parent)
        self.__image: plot_model.ChannelRef | None = None
        self.__colormap = None

    def __reduce__(self):
        return (self.__class__, (), self.__getstate__())

    def __getstate__(self):
        state = super(ImageItem, self).__getstate__()
        assert "image" not in state
        state["image"] = self.__image
        return state

    def __setstate__(self, state):
        super(ImageItem, self).__setstate__(state)
        self.__image = state.pop("image")

    def isValid(self):
        return self.__image is not None

    def imageChannel(self) -> plot_model.ChannelRef | None:
        return self.__image

    def setImageChannel(self, channel: plot_model.ChannelRef):
        self.__image = channel
        self._emitValueChanged(plot_model.ChangeEventType.IMAGE_CHANNEL)

    def setCustomStyle(self, style: style_model.Style):
        result = super(ImageItem, self).setCustomStyle(style)
        if self.__colormap is not None:
            # Make sure the cache is updated
            if style.colormapLut is not None:
                self.__colormap.setName(style.colormapLut)
        return result

    def colormap(self):
        return self.__colormap

    def setColormap(self, colormap):
        self.__colormap = colormap


class RoiItem(plot_model.Item):
    """Define a ROI as part of a plot."""

    def __init__(self, parent: plot_model.Plot | None = None):
        super(RoiItem, self).__init__(parent=parent)
        self.__deviceName: str | None = None

    def __reduce__(self):
        return (self.__class__, (), self.__getstate__())

    def __getstate__(self):
        state = super(RoiItem, self).__getstate__()
        assert "deviceName" not in state
        state["deviceName"] = self.__deviceName
        return state

    def __setstate__(self, state):
        super(RoiItem, self).__setstate__(state)
        self.__deviceName = state.pop("deviceName")

    def name(self) -> str:
        """Returns the name displayed for this item"""
        return self.roiName()

    def roiName(self) -> str:
        """Returns the name of the ROI"""
        return self.__deviceName.split(":")[-1]

    def deviceName(self):
        """Returns the device name defining this ROI.

        The device name is the full device name prefixed by the top master name
        """
        return self.__deviceName

    def setDeviceName(self, name: str):
        """Set the device name containing the ROI.

        The device name is the full device name prefixed by the top master name
        """
        self.__deviceName = name

    def roi(self, scan):
        device = scan.getDeviceByName(self.__deviceName)
        return device.metadata().roi


class ScatterPlot(plot_model.Plot):
    """Define a plot which displays scatters."""


class ScatterItem(plot_model.Item):
    """Define a MCA as part of a plot.

    The X, Y, and Value data are each defined by a `ChannelRef`.
    """

    def __init__(self, parent: plot_model.Plot | None = None):
        super(ScatterItem, self).__init__(parent=parent)
        self.__x: plot_model.ChannelRef | None = None
        self.__y: plot_model.ChannelRef | None = None
        self.__value: plot_model.ChannelRef | None = None
        self.__groupBy: list[plot_model.ChannelRef] | None = None
        self.__colormap = None

    def __reduce__(self):
        return (self.__class__, (), self.__getstate__())

    def __getstate__(self):
        state = super(ScatterItem, self).__getstate__()
        assert "x" not in state
        assert "y" not in state
        assert "value" not in state
        state["x"] = self.__x
        state["y"] = self.__y
        state["value"] = self.__value
        return state

    def __setstate__(self, state):
        super(ScatterItem, self).__setstate__(state)
        self.__x = state.pop("x")
        self.__y = state.pop("y")
        self.__value = state.pop("value")

    def isValid(self):
        return (
            self.__x is not None and self.__y is not None and self.__value is not None
        )

    def getScanValidation(self, scan: scan_model.Scan) -> str | None:
        """
        Returns None if everything is fine, else a message to explain the problem.
        """
        xx = self.xArray(scan)
        yy = self.yArray(scan)
        value = self.valueArray(scan)

        if xx is None or yy is None or value is None:
            return "No data available for X or Y or Value data"
        elif self.xChannel().name() == self.yChannel().name():
            return "X and Y axis must differ"
        elif xx.ndim != 1:
            return "Dimension of X data do not match"
        elif yy.ndim != 1:
            return "Dimension of Y data do not match"
        elif value.ndim != 1:
            return "Dimension of Value data do not match"
        elif len(xx) != len(yy):
            return "Size of X and Y data do not match"
        elif len(xx) != len(value):
            return "Size of X and Value data do not match"
        # It's fine
        return None

    def xChannel(self) -> plot_model.ChannelRef | None:
        return self.__x

    def setXChannel(self, channel: plot_model.ChannelRef | None):
        self.__x = channel
        self._emitValueChanged(plot_model.ChangeEventType.X_CHANNEL)

    def xArray(self, scan: scan_model.Scan) -> numpy.ndarray | None:
        channel = self.__x
        if channel is None:
            return None
        array = channel.array(scan)
        return array

    def yChannel(self) -> plot_model.ChannelRef | None:
        return self.__y

    def setYChannel(self, channel: plot_model.ChannelRef | None):
        self.__y = channel
        self._emitValueChanged(plot_model.ChangeEventType.Y_CHANNEL)

    def yArray(self, scan: scan_model.Scan) -> numpy.ndarray | None:
        channel = self.__y
        if channel is None:
            return None
        array = channel.array(scan)
        return array

    def valueChannel(self) -> plot_model.ChannelRef | None:
        return self.__value

    def setValueChannel(self, channel: plot_model.ChannelRef | None):
        self.__value = channel
        self._emitValueChanged(plot_model.ChangeEventType.VALUE_CHANNEL)

    def groupByChannels(self) -> list[plot_model.ChannelRef] | None:
        return self.__groupBy

    def setGroupByChannels(self, channels: list[plot_model.ChannelRef] | None):
        self.__groupBy = channels
        self._emitValueChanged(plot_model.ChangeEventType.GROUP_BY_CHANNELS)

    def valueArray(self, scan: scan_model.Scan) -> numpy.ndarray | None:
        channel = self.__value
        if channel is None:
            return None
        array = channel.array(scan)
        return array

    def setCustomStyle(self, style: style_model.Style):
        result = super(ScatterItem, self).setCustomStyle(style)
        if self.__colormap is not None:
            # Make sure the cache is updated
            if style.colormapLut is not None:
                self.__colormap.setName(style.colormapLut)
        return result

    def colormap(self):
        return self.__colormap

    def setColormap(self, colormap):
        self.__colormap = colormap

    def __str__(self):
        return "<%s x=%s y=%s value=%s />" % (
            type(self).__name__,
            self.__x,
            self.__y,
            self.__value,
        )


class AxisPositionMarker(plot_model.Item, plot_model.NotReused):
    """Define a location of a motor in a plot.

    This item is only displayable when the plot uses its motor
    axis as the plot axis
    """

    def __init__(self, parent: plot_model.Plot = None):
        super(AxisPositionMarker, self).__init__(parent=parent)
        self.__motor: plot_model.ChannelRef | None = None
        self.__position: float | None = None
        self.__text: str | None = None

    def isValid(self):
        return (
            self.__motor is not None
            and self.__position is not None
            and self.__text is not None
        )

    def initProperties(
        self, unique_name: str, ref: plot_model.ChannelRef, position: float, text: str
    ):
        """Define object properties just after construction

        This object is not supposed to be mutable. This avoid to define boilerplat and events
        """
        assert self.__motor is None
        self.__unique_name = unique_name
        self.__motor = ref
        self.__position = position
        self.__text = text

    def motorChannel(self) -> plot_model.ChannelRef | None:
        """Returns the channel reference identifying this motor"""
        return self.__motor

    def position(self) -> float | None:
        """Returns the position of the y-axis in which the statistic have to be displayed"""
        return self.__position

    def text(self) -> str | None:
        """Returns the name of the y-axis in which the statistic have to be displayed"""
        return self.__text

    def unique_name(self) -> str:
        """Returns the name of the y-axis in which the statistic have to be displayed"""
        return self.__unique_name


class MotorPositionMarker(AxisPositionMarker):
    """Deprecated object.

    Created for compatibility since bliss 1.3
    """


def getHashableSource(obj: plot_model.Item | None):
    if obj is None:
        return tuple()
    while isinstance(obj, plot_model.ChildItem):
        obj = obj.source()
    if obj is None:
        return tuple()
    if isinstance(obj, plot_model.ChannelRef):
        return (obj.name(),)
    if isinstance(obj, CurveItem):
        x = obj.xChannel()
        y = obj.yChannel()
        xName = None if x is None else x.name()
        yName = None if y is None else y.name()
        return (xName, yName)
    else:
        _logger.error("Source list not implemented for %s" % type(obj))
        return tuple()


class CurveStatisticItem(plot_model.ChildItem):
    """Statistic displayed on a source item, depending on it y-axis."""

    def inputData(self):
        return getHashableSource(self.source())

    def yAxis(self) -> str:
        """Returns the name of the y-axis in which the statistic have to be displayed"""
        source = self.source()
        return source.yAxis()

    def setSource(self, source: plot_model.Item):
        previousSource = self.source()
        if previousSource is not None:
            previousSource.valueChanged.disconnect(self.__sourceChanged)
        plot_model.ChildItem.setSource(self, source)
        if source is not None:
            source.valueChanged.connect(self.__sourceChanged)
            self.__sourceChanged(plot_model.ChangeEventType.YAXIS)
            self.__sourceChanged(plot_model.ChangeEventType.X_CHANNEL)
            self.__sourceChanged(plot_model.ChangeEventType.Y_CHANNEL)

    def __sourceChanged(self, eventType):
        if eventType == plot_model.ChangeEventType.YAXIS:
            self._emitValueChanged(plot_model.ChangeEventType.YAXIS)
        if eventType == plot_model.ChangeEventType.Y_CHANNEL:
            self._emitValueChanged(plot_model.ChangeEventType.Y_CHANNEL)
        if eventType == plot_model.ChangeEventType.X_CHANNEL:
            self._emitValueChanged(plot_model.ChangeEventType.X_CHANNEL)


class ComputedCurveItem(plot_model.ChildItem, CurveMixIn):
    def __init__(self, parent=None):
        plot_model.ChildItem.__init__(self, parent)
        CurveMixIn.__init__(self)

    def inputData(self):
        return getHashableSource(self.source())

    def isResultValid(self, result) -> bool:
        return result is not None

    def xData(self, scan: scan_model.Scan) -> scan_model.Data | None:
        result = self.reachResult(scan)
        if not self.isResultValid(result):
            return None
        data = result.xx
        return scan_model.Data(None, data)

    def yData(self, scan: scan_model.Scan) -> scan_model.Data | None:
        result = self.reachResult(scan)
        if not self.isResultValid(result):
            return None
        data = result.yy
        return scan_model.Data(None, data)

    def setSource(self, source: plot_model.Item):
        previousSource = self.source()
        if previousSource is not None:
            previousSource.valueChanged.disconnect(self.__sourceChanged)
        plot_model.ChildItem.setSource(self, source)
        if source is not None:
            source.valueChanged.connect(self.__sourceChanged)
            self.__sourceChanged(plot_model.ChangeEventType.X_CHANNEL)
            self.__sourceChanged(plot_model.ChangeEventType.Y_CHANNEL)

    def __sourceChanged(self, eventType):
        if eventType == plot_model.ChangeEventType.Y_CHANNEL:
            self._emitValueChanged(plot_model.ChangeEventType.Y_CHANNEL)
        if eventType == plot_model.ChangeEventType.X_CHANNEL:
            self._emitValueChanged(plot_model.ChangeEventType.X_CHANNEL)


class UserValueItem(plot_model.ChildItem, CurveMixIn, plot_model.NotReused):
    """This item is used to add to the plot data provided by the user.

    The y-data is custom and the x-data is provided by the linked item.
    """

    def __init__(self, parent=None):
        plot_model.ChildItem.__init__(self, parent=parent)
        CurveMixIn.__init__(self)
        self.__name = "userdata"
        self.__y = None

    def setName(self, name):
        self.__name = name

    def name(self) -> str:
        return self.__name

    def displayName(self, axisName, scan: scan_model.Scan) -> str:
        if axisName == "x":
            sourceItem = self.source()
            return sourceItem.displayName("x", scan)
        elif axisName == "y":
            return self.__name

    def isValid(self):
        return self.source() is not None and self.__y is not None

    def inputData(self):
        return getHashableSource(self.source())

    def xData(self, scan: scan_model.Scan) -> scan_model.Data | None:
        source = self.source()
        if source is None:
            return None
        return source.xData(scan)

    def setYArray(self, array):
        self.__y = array
        self._emitValueChanged(plot_model.ChangeEventType.Y_CHANNEL)

    def yData(self, scan: scan_model.Scan) -> scan_model.Data | None:
        return scan_model.Data(None, self.__y)

    def getScanValidation(self, scan: scan_model.Scan) -> str | None:
        """
        Returns None if everything is fine, else a message to explain the problem.
        """
        xx = self.xArray(scan)
        yy = self.yArray(scan)
        if xx is None and yy is None:
            return "No data available for X and Y data"
        elif xx is None:
            return "No data available for X data"
        elif yy is None:
            return "No data available for Y data"
        elif xx.ndim != 1:
            return "Dimension of X data do not match"
        elif yy.ndim != 1:
            return "Dimension of Y data do not match"
        elif len(xx) != len(yy):
            return "Size of X and Y data do not match"
        # It's fine
        return None

    def setSource(self, source: plot_model.Item):
        previousSource = self.source()
        if previousSource is not None:
            previousSource.valueChanged.disconnect(self.__sourceChanged)
        plot_model.ChildItem.setSource(self, source)
        if source is not None:
            source.valueChanged.connect(self.__sourceChanged)
            self.__sourceChanged(plot_model.ChangeEventType.X_CHANNEL)

    def __sourceChanged(self, eventType):
        if eventType == plot_model.ChangeEventType.X_CHANNEL:
            self._emitValueChanged(plot_model.ChangeEventType.X_CHANNEL)


PLOTS_WITH_DEVICENAME = (
    ImagePlot,
    McaPlot,
    OneDimDataPlot,
)
