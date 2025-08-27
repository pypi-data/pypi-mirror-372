# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

from __future__ import annotations

import numpy

from silx.gui import qt
import silx.gui.plot.items.roi as silx_rois
from bliss.flint.model import scan_model


class MoscaRangeRoi(silx_rois.HorizontalRangeROI):
    """ROI selection for mosca.

    It have to hold a name, with a detector channel,
    and a range of spectrum bins.
    """

    def __init__(self, parent=None):
        silx_rois.HorizontalRangeROI.__init__(self, parent=parent)
        self.__channel: int | None = None
        self.__energy: numpy.ndarray | None = None
        self.__range: tuple[int, int] | None = None

    def setFirstShapePoints(self, points):
        # Normalize the ROI position to the pixel
        points = points.astype(int)
        silx_rois.HorizontalRangeROI.setFirstShapePoints(self, points)

    def __clampChannelRange(self, vmin: int, vmax: int) -> tuple[int, int]:
        if self.__range is not None:
            if vmin < self.__range[0]:
                vmin = self.__range[0]
            if vmin >= self.__range[1]:
                vmin = self.__range[1] - 1
            if vmax >= self.__range[1]:
                vmax = self.__range[1] - 1
            if vmax < vmin:
                vmax = vmin
        else:
            if vmin < 0:
                vmin = 0
            if vmax < vmin:
                vmax = vmin
        return vmin, vmax

    def _updatePos(self, vmin, vmax, force=False):
        if self.__energy is None:
            vmin = int(vmin + 0.5)
            vmax = int(vmax - 0.5)
            vmin, vmax = self.__clampChannelRange(vmin, vmax)
            # FIXME: Fix max channel
            vmin = vmin - 0.5
            vmax = vmax + 0.5
        else:
            if vmin < self.__energy[0]:
                vmin = self.__energy[0]
            if vmin > self.__energy[-1]:
                vmin = self.__energy[-1]
            if vmax > self.__energy[-1]:
                vmax = self.__energy[-1]
            if vmax < vmin:
                vmax = vmin

        silx_rois.HorizontalRangeROI._updatePos(self, vmin, vmax, force=force)

    def setMcaChannel(self, channel: int | None):
        self.__channel = channel

    def getMcaChannel(self) -> int | None:
        return self.__channel

    def setMcaRange(self, vmin: int, vmax: int):
        if self.__energy is not None:
            fmin = self.__energy[vmin]
            fmax = self.__energy[vmax]
        else:
            fmin = vmin - 0.5
            fmax = vmax + 0.5
        self.setRange(fmin, fmax)

    def getMcaRange(self) -> tuple[int, int]:
        p0, p1 = self.getRange()
        if self.__energy is not None:
            norm = self.__energy
            p0 = numpy.argmin(numpy.abs(norm - p0))
            if p0 >= 1:
                p0 = p0 - 1
            p1 = numpy.argmin(numpy.abs(norm - p1))
            return p0, p1
        else:
            vmin = int(p0 + 0.5)
            vmax = int(p1 - 0.5)
            return vmin, vmax

    def setEnergy(self, energy: numpy.ndarray | None):
        vmin, vmax = self.getMcaRange()
        self.__energy = energy
        self.setMcaRange(vmin, vmax)

    def getEnergy(self) -> numpy.ndarray | None:
        return self.__energy

    def clone(self):
        newRoi = type(self)()
        newRoi.setRange(*self.getRange())
        return newRoi

    def setParent(self, parent):
        super(MoscaRangeRoi, self).setParent(parent)
        self.__parentUpdated()

    def __parentUpdated(self):
        self._setupWithEnergy()
        self.__range = self.getDetectorRange()

    def _getMcaPlot(self):
        manager = self.parent()
        if manager is None:
            return None
        plot = manager.parent()
        if plot is None:
            return None
        plot = plot.parent()
        if plot is None:
            return None
        plot = plot.parent()
        if plot is None:
            return None
        plot = plot.parent()
        if plot is None:
            return None
        from bliss.flint.viewers.live_mca.viewer import McaPlotWidget

        if not isinstance(plot, McaPlotWidget):
            return None
        return plot

    def _setupWithEnergy(self):
        from bliss.flint.viewers.live_mca.viewer import McaPlotWidget

        mcaPlot: McaPlotWidget | None = self._getMcaPlot()
        if mcaPlot is not None:
            mcaPlot.sigXAxisMode.connect(self.__xAxisModeChanged)
            self.__xAxisModeChanged()

    def __xAxisModeChanged(self):
        from bliss.flint.viewers.live_mca.viewer import McaPlotWidget

        mcaPlot: McaPlotWidget | None = self._getMcaPlot()
        if mcaPlot is None:
            return

        self.setEnergy(mcaPlot.getNormalization())

    def getDevice(self) -> scan_model.Device | None:
        from bliss.flint.viewers.live_mca.viewer import McaPlotWidget

        mcaPlot: McaPlotWidget | None = self._getMcaPlot()
        if mcaPlot is None:
            return None

        scan = mcaPlot.scan()
        if scan is None:
            return None

        deviceName = mcaPlot.deviceName()
        return scan.findDeviceByName(deviceName, devtype=scan_model.DeviceType.MOSCA)

    def getDetectorRange(self) -> tuple[int, int] | None:
        """Returns the available channel range for the ROIs.

        It's min-max range, min included, max excluded.
        """
        device = self.getDevice()
        if device is None:
            return None
        channelRange = None
        for channel in device.channels():
            data = channel.data()
            if data is None:
                continue
            array = data.array()
            if array is None:
                continue
            if channel.type() == scan_model.ChannelType.SPECTRUM:
                r = 0, array.shape[0]
            elif channel.type() == scan_model.ChannelType.SPECTRUM_D_C:
                r = 0, array.shape[-1]
            else:
                continue
            if channelRange is None or r[1] > channelRange[1]:
                channelRange = r
        return channelRange

    def getAvailableSpectrumNames(self) -> list[str] | None:
        device = self.getDevice()
        if device is None:
            return None
        names = []
        for channel in device.channels():
            if channel.type() not in (
                scan_model.ChannelType.SPECTRUM,
                scan_model.ChannelType.SPECTRUM_D_C,
            ):
                continue
            names.append(channel.name())

        names = sorted(names)
        return names

    def requestEdition(self):
        from bliss.flint.dialog.mosca_range_roi_dialog import MoscaRangeRoiDialog

        silxPlot = self.parent().parent()
        dialog = MoscaRangeRoiDialog(silxPlot)
        dialog.setRoi(self)
        result = dialog.exec_()
        if result:
            dialog.applySelectionToRoi(self)

    def _feedContextMenu(self, menu: qt.QMenu):
        action = qt.QAction(menu)
        action.setText(f"Edit {self.getName()}")
        action.triggered.connect(self.requestEdition)
        menu.addAction(action)
