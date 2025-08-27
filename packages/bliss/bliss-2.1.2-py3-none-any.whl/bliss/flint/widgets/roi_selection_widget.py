# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

"""
Provide a RoiSelectionWidget
"""

from __future__ import annotations

import logging
import functools
import re
import os

from silx.gui import qt
from silx.gui import icons
from silx.gui import utils as qtutils
from silx.gui.dialog.DataFileDialog import DataFileDialog
from silx.gui.plot.tools.roi import RegionOfInterestManager
from silx.gui.plot.tools.roi import RegionOfInterestTableWidget
from silx.gui.plot.items.roi import RectangleROI
from silx.gui.plot.items.roi import ArcROI
from silx.gui.plot.items.roi import RegionOfInterest
from silx.gui.plot.tools.roi import RoiModeSelectorAction

from bliss.flint.utils import error_utils
from .viewer import roi_helper


_logger = logging.getLogger(__name__)


class _AutoHideToolBar(qt.QToolBar):
    """A toolbar which hide itself if no actions are visible"""

    def actionEvent(self, event):
        if event.type() == qt.QEvent.ActionChanged:
            self._updateVisibility()
        return qt.QToolBar.actionEvent(self, event)

    def _updateVisibility(self):
        visible = False
        for action in self.actions():
            if action.isVisible():
                visible = True
                break
        self.setVisible(visible)


class _RegionOfInterestManagerWithContextMenu(RegionOfInterestManager):

    sigRoiContextMenuRequested = qt.Signal(object, qt.QMenu)

    def _feedContextMenu(self, menu):
        RegionOfInterestManager._feedContextMenu(self, menu)
        roi = self.getCurrentRoi()
        if roi is not None:
            if roi.isEditable():
                self.sigRoiContextMenuRequested.emit(roi, menu)

        if hasattr(roi, "_feedContextMenu"):
            roi._feedContextMenu(menu)

    def getRoiByName(self, name):
        for r in self.getRois():
            if r.getName() == name:
                return r
        return None


class RoiSelectionWidget(qt.QWidget):

    selectionFinished = qt.Signal(object)

    selectionCancelled = qt.Signal()

    def __init__(
        self,
        plot,
        parent=None,
        kinds: list[RegionOfInterest] | None = None,
        loadFromDeviceName: str | None = None,
    ):
        qt.QWidget.__init__(self, parent)
        # TODO: destroy on close
        self.plot = plot

        mode = plot.getInteractiveMode()["mode"]
        self.__previousMode = mode
        self.__previousDir = None

        self.roiManager = _RegionOfInterestManagerWithContextMenu(plot)
        self.roiManager.setColor("pink")
        self.roiManager.sigRoiAdded.connect(self.__roiAdded)
        self.roiManager.sigRoiContextMenuRequested.connect(self.roiContextMenuRequested)
        self.roiManager.sigCurrentRoiChanged.connect(self.__currentRoiChanged)
        self.table = RegionOfInterestTableWidget(self)

        self.table.setSelectionBehavior(qt.QAbstractItemView.SelectRows)
        self.table.setSelectionMode(qt.QAbstractItemView.SingleSelection)
        selectionModel = self.table.selectionModel()
        selectionModel.currentRowChanged.connect(self.__currentRowChanged)

        # Hide coords
        horizontalHeader = self.table.horizontalHeader()
        horizontalHeader.setSectionResizeMode(0, qt.QHeaderView.Stretch)
        horizontalHeader.hideSection(1)  # is editable
        horizontalHeader.hideSection(3)  # coords
        self.table.setRegionOfInterestManager(self.roiManager)

        if kinds is None:
            kinds = [RectangleROI]

        self.roiToolbar = qt.QToolBar(self)

        cloneAction = qt.QAction(self.roiManager)
        cloneAction.setText("Duplicate")
        cloneAction.setToolTip("Duplicate selected ROI")
        icon = icons.getQIcon("flint:icons/roi-duplicate")
        cloneAction.setIcon(icon)
        cloneAction.setEnabled(False)
        cloneAction.triggered.connect(self.cloneCurrentRoiRequested)
        self.__cloneAction = cloneAction

        renameAction = qt.QAction(self.roiManager)
        renameAction.setText("Rename")
        renameAction.setToolTip("Rename selected ROI")
        icon = icons.getQIcon("flint:icons/roi-rename")
        renameAction.setIcon(icon)
        renameAction.setEnabled(False)
        renameAction.triggered.connect(self.renameCurrentRoiRequested)
        self.__renameAction = renameAction

        self.roiToolbar.addAction(cloneAction)
        self.roiToolbar.addAction(renameAction)
        self.roiToolbar.addSeparator()

        firstAction = None
        for roiKind in kinds:
            action = self.roiManager.getInteractionModeAction(roiKind)
            action.setSingleShot(True)
            self.roiToolbar.addAction(action)
            if firstAction is None:
                firstAction = action

        if loadFromDeviceName:
            self.roiToolbar.addSeparator()
            loadAction = qt.QAction(self.roiManager)
            loadAction.setText("Load from HDF5")
            loadAction.setToolTip(
                "Load a set of ROIs from a previous scan saved as HDF5"
            )
            icon = icons.getQIcon("flint:icons/roi-load")
            loadAction.setIcon(icon)
            loadAction.triggered.connect(
                functools.partial(self.__loadFromFile, loadFromDeviceName)
            )
            self.roiToolbar.addAction(loadAction)

        applyAction = qt.QAction(self.roiManager)
        applyAction.setText("Apply")
        applyAction.triggered.connect(self._onApply)
        applyAction.setObjectName("roi-apply-selection")
        self.addAction(applyAction)

        self.applyButton = qt.QPushButton(self)
        self.applyButton.setFixedHeight(40)
        self.applyButton.setText("Apply these ROIs")
        icon = icons.getQIcon("flint:icons/roi-save")
        self.applyButton.setIcon(icon)
        self.applyButton.clicked.connect(self._onApply)
        self.applyButton.setIconSize(qt.QSize(24, 24))

        self.cancelButton = qt.QPushButton(self)
        self.cancelButton.setFixedHeight(40)
        self.cancelButton.setToolTip("Cancel the edition")
        icon = icons.getQIcon("flint:icons/roi-cancel")
        self.cancelButton.setIcon(icon)
        self.cancelButton.clicked.connect(self._onCancel)
        self.cancelButton.setIconSize(qt.QSize(24, 24))

        roiEditToolbar = _AutoHideToolBar(self)
        modeSelectorAction = RoiModeSelectorAction(self)
        modeSelectorAction.setRoiManager(self.roiManager)
        roiEditToolbar.addAction(modeSelectorAction)
        self.roiEditToolbar = roiEditToolbar

        layout = qt.QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.roiToolbar)
        layout.addWidget(self.roiEditToolbar)
        layout.addWidget(self.table)

        blayout = qt.QHBoxLayout(self)
        blayout.addWidget(self.applyButton)
        blayout.addWidget(self.cancelButton)
        blayout.setContentsMargins(0, 0, 0, 0)
        blayout.setStretchFactor(self.applyButton, 1)
        layout.addLayout(blayout)

        if firstAction is not None:
            firstAction.trigger()

    def __loadFromFile(self, detectorName):
        def customFilter(obj):
            if "NX_class" in obj.attrs:
                return obj.attrs["NX_class"] in [b"NXentry", "NXentry"]
            return False

        dialog = DataFileDialog(self)
        if self.__previousDir and os.path.exists(self.__previousDir):
            dialog.setDirectory(self.__previousDir)
        dialog.setFilterMode(DataFileDialog.FilterMode.ExistingGroup)
        dialog.setFilterCallback(customFilter)
        result = dialog.exec_()
        self.__previousDir = dialog.directory()
        if not result:
            return
        dataUrl = dialog.selectedDataUrl()
        filePath = dataUrl.file_path()
        dataPath = dataUrl.data_path()
        try:
            rois = roi_helper.readRoisFromHdf5(filePath, dataPath, detectorName)
        except Exception as e:
            qt.QMessageBox.critical(self.plot, "Error", str(e.args[0]))
            return

        if len(rois) == 0:
            qt.QMessageBox.critical(
                self.plot, "Error", "No ROIs was found for this detector in this scan"
            )
            return

        self.roiManager.clear()
        for r in rois:
            r = roi_helper.roiToGui(r)
            if r is not None:
                self.roiManager.addRoi(r)

    def __currentRowChanged(self, current, previous):
        model = self.table.model()
        index = model.index(current.row(), 0)
        name = model.data(index)
        roi = self.roiManager.getRoiByName(name)
        self.roiManager.setCurrentRoi(roi)

    def __currentRoiChanged(self, roi):
        selectionModel = self.table.selectionModel()
        if roi is None:
            selectionModel.clear()
            enabled = False
        else:
            name = roi.getName()
            model = self.table.model()
            for row in range(model.rowCount()):
                index = model.index(row, 0)
                if model.data(index) == name:
                    selectionModel.reset()
                    mode = (
                        qt.QItemSelectionModel.Clear
                        | qt.QItemSelectionModel.Rows
                        | qt.QItemSelectionModel.Current
                        | qt.QItemSelectionModel.Select
                    )
                    selectionModel.select(index, mode)
                    enabled = True
                    break
            else:
                selectionModel.clear()
                enabled = False

        self.__cloneAction.setEnabled(enabled)
        self.__renameAction.setEnabled(enabled)

    def _onApply(self):
        self.selectionFinished.emit(self.roiManager.getRois())
        self.clear()

    def _onCancel(self):
        self.selectionCancelled.emit()
        self.clear()

    def roiContextMenuRequested(self, roi, menu: qt.QMenu):
        menu.addSeparator()

        cloneAction = qt.QAction(menu)
        cloneAction.setText("Duplicate %s" % roi.getName())
        callback = functools.partial(self.cloneRoiRequested, roi)
        cloneAction.triggered.connect(callback)
        menu.addAction(cloneAction)

        renameAction = qt.QAction(menu)
        renameAction.setText("Rename %s" % roi.getName())
        callback = functools.partial(self.renameRoiRequested, roi)
        renameAction.triggered.connect(callback)
        menu.addAction(renameAction)

        if isinstance(roi, ArcROI):
            from bliss.flint.widgets.image_plot import ImagePlotWidget

            def getImagePlotWidget() -> ImagePlotWidget | None:
                # FIXME: This is very fragile
                try:
                    w = self.plot.parent().parent().parent().parent()
                except Exception:
                    return None
                if not isinstance(w, ImagePlotWidget):
                    # raise RuntimeError(f"Unexpected class {type(w).__name__} found. Something have changed in the implementation")
                    return None
                return w

            imageWidget = getImagePlotWidget()
            if imageWidget is not None:
                diffractionStage = imageWidget.imageProcessing().diffractionStage()
                if diffractionStage is not None and diffractionStage.isEnabled():
                    diffMoveAction = qt.QAction(menu)
                    diffMoveAction.setText("Set %s location in χ/q" % roi.getName())
                    callback = functools.partial(
                        self.moveArcRoiInChiTthRequested, roi, diffractionStage
                    )
                    diffMoveAction.triggered.connect(callback)
                    menu.addAction(diffMoveAction)

    def renameRoiRequested(self, roi):
        name = roi.getName()
        result = qt.QInputDialog.getText(
            self, "Rename ROI name", "ROI name", qt.QLineEdit.Normal, name
        )
        if result[1]:
            newName = result[0]
            if newName == name:
                return
            if self.isAlreadyUsed(newName):
                qt.QMessageBox.warning(
                    self, "Action cancelled", f"ROI name '{newName}' already used."
                )
                return
            roi.setName(newName)

    def moveArcRoiInChiTthRequested(self, roi, diffractionStage):
        from bliss.flint.dialog.arcroi_geometry_dialog import ArcRoiGeometryDialog

        dialog = ArcRoiGeometryDialog(self)
        dialog.setDiffractionStage(diffractionStage)
        dialog.setRoi(roi)
        result = dialog.exec_()
        if result:
            with error_utils.exceptionAsMessageBox(self):
                roi.setGeometry(**dialog.selectedGeometry())

    def __splitTrailingNumber(self, name):
        m = re.search(r"^(.*?)(\d+)$", name)
        if m is None:
            return name, 1
        groups = m.groups()
        return groups[0], int(groups[1])

    def cloneRoiRequested(self, roi):
        name = roi.getName()
        basename, number = self.__splitTrailingNumber(name)
        for _ in range(50):
            number = number + 1
            name = f"{basename}{number}"
            if not self.isAlreadyUsed(name):
                break

        result = qt.QInputDialog.getText(
            self, "Clone ROI", "ROI name", qt.QLineEdit.Normal, name
        )
        if result[1]:
            if self.isAlreadyUsed(name):
                qt.QMessageBox.warning(
                    self, "Action cancelled", f"ROI name '{name}' already used."
                )
                return

            try:
                newRoi = roi.clone()
            except Exception:
                _logger.error("Error while cloning ROI", exc_info=True)
                return

            newName = result[0]
            newRoi.setName(newName)
            self.roiManager.addRoi(newRoi)

    def isAlreadyUsed(self, name):
        for r in self.roiManager.getRois():
            if r.getName() == name:
                return True
        return False

    def cloneCurrentRoiRequested(self):
        roi = self.roiManager.getCurrentRoi()
        if roi is None:
            return
        self.cloneRoiRequested(roi)

    def renameCurrentRoiRequested(self):
        roi = self.roiManager.getCurrentRoi()
        if roi is None:
            return
        self.renameRoiRequested(roi)

    def clear(self):
        roiManager = self.roiManager
        if len(roiManager.getRois()) > 0:
            # Weird: At this level self.table can be already deleted in C++ side
            # The if rois > 0 is a work around
            selectionModel = self.table.selectionModel()
            with qtutils.blockSignals(selectionModel):
                roiManager.clear()

        try:
            self.plot.setInteractiveMode(self.__previousMode)
        except Exception:
            # In case the mode is not supported
            pass

    def searchForFreeName(self, roi):
        """Returns a new name for a ROI.

        The name is picked in order to match roi_counters and
        roi2spectrum_counters. It was decided to allow to have the same sub
        names for both Lima devices.

        As this module is generic, it would be better to move this code in more
        specific place.
        """
        rois = self.roiManager.getRois()
        roiNames = set([r.getName() for r in rois])

        for i in range(1, 1000):
            name = f"roi{i}"
            if name not in roiNames:
                return name
        return "roi666.666"

    def __roiAdded(self, roi):
        roi.setSelectable(True)
        roi.setEditable(True)
        if not roi.getName():
            name = self.searchForFreeName(roi)
            roi.setName(name)

    def addRoi(self, roi):
        self.roiManager.addRoi(roi)
