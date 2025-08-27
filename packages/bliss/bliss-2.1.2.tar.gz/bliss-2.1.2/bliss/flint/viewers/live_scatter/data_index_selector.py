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
from silx.gui.plot import PlotWidget
from silx.gui.plot.items.roi import PointROI
from silx.gui.plot.tools.roi import RegionOfInterestManager
from silx.gui.plot.items.scatter import Scatter
from bliss.flint.helper.plot_interaction import Selector

_logger = logging.getLogger(__name__)


class DataIndexSelector(Selector):
    """
    Selector for index data selection.
    """

    def __init__(self, parent):
        assert isinstance(parent, PlotWidget), f"Found {type(parent)}"
        super(DataIndexSelector, self).__init__(parent)

        self._manager = RegionOfInterestManager(parent)
        self._manager.sigRoiAdded.connect(self._roiAdded)
        self._manager.sigInteractiveRoiCreated.connect(self._roiCreated)
        self.__widget = None
        self._selection = None

    def selection(self):
        """Returns the selection"""
        if self._selection is not None:
            return self._selection

        selection = None
        if self._manager.isStarted():
            rois = [r for r in self._manager.getRois() if isinstance(r, PointROI)]
            pos = rois[0].getPosition()
            pos = [tuple(r.getPosition()) for r in rois]
            selection = pos

        if selection == [] or selection is None:
            return None

        pos = selection[0]
        x, y = pos

        plot = self.parent()

        def isScatter(item):
            return isinstance(item, Scatter)

        results = list(plot.pickItems(x, y, isScatter))
        for result in results:
            indices = result.getIndices(copy=False)
            return indices

        if len(results) == 0:
            selectedScatter = plot.getActiveScatter()
            # Pick on the active curve with a highter tolerence
            if selectedScatter is not None:
                index = self.__closest(selectedScatter, x, y)
                return index

        return None

    def __closest(self, scatter, x, y):
        """Returns the closest index from a scatter item"""
        xx = scatter.getXData()
        yy = scatter.getYData()
        if xx is None or len(xx) == 0:
            return None
        dist = ((xx - x)) ** 2 + ((yy - y)) ** 2
        index = numpy.nanargmin(dist)
        return index

    def _roiAdded(self):
        self._updateStatusBar()
        self.stop()

    def _roiCreated(self, roi):
        rois = self._manager.getRois()
        roi.setName("%d" % len(rois))
        roi.setColor("pink")

    def eventFilter(self, obj, event):
        """Event filter for plot hide and key event"""
        if event.type() == qt.QEvent.Hide:
            self.stop()

        elif event.type() == qt.QEvent.KeyPress:
            if event.key() in (qt.Qt.Key_Delete, qt.Qt.Key_Backspace) or (
                event.key() == qt.Qt.Key_Z and event.modifiers() & qt.Qt.ControlModifier
            ):
                self._removeLastInput()
                return True  # Stop further handling of those keys

            elif event.key() == qt.Qt.Key_Return:
                self.stop()
                return True  # Stop further handling of those keys

        return super(DataIndexSelector, self).eventFilter(obj, event)

    def _removeLastInput(self):
        rois = self._manager.getRois()
        if len(rois) == 0:
            return
        roi = rois[-1]
        self._manager.removeRoi(roi)
        self._updateStatusBar()
        self.selectionChanged.emit()

    def start(self):
        """Start interactive selection of points"""
        self.stop()
        self.reset()

        plot = self.parent()
        if plot is None:
            raise RuntimeError("No plot to perform selection")

        plot.installEventFilter(self)

        self.__widget = qt.QToolButton(plot)
        action = self._manager.getInteractionModeAction(PointROI)
        self.__widget.setDefaultAction(action)
        action.trigger()
        plot.statusBar().addPermanentWidget(self.__widget)

        self._updateStatusBar()

    def stop(self):
        """Stop interactive point selection"""
        if not self._manager.isStarted():
            return
        assert self.__widget is not None

        plot = self.parent()
        if plot is None:
            return

        # Save the current state
        self._selection = self.selection()

        self._manager.clear()
        self._manager.stop()
        plot.removeEventFilter(self)
        statusBar = plot.statusBar()
        statusBar.clearMessage()
        statusBar.removeWidget(self.__widget)
        self.__widget.deleteLater()
        self.__widget = None
        self.selectionFinished.emit()

    def reset(self):
        """Reset selected points"""
        plot = self.parent()
        if plot is None:
            return
        self._manager.clear()
        self._updateStatusBar()
        self.selectionChanged.emit()

    def _updateStatusBar(self):
        """Update status bar message"""
        pass
