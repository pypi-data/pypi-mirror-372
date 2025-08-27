# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

from __future__ import annotations

import os
import logging
import weakref

from silx.gui import qt
from silx.gui import icons
from silx.gui.widgets.FormGridLayout import FormGridLayout
from bliss.flint.model import flint_model
from bliss.flint.model import plot_model
from bliss.flint.model import plot_item_model
from bliss.flint.model import scan_model
from bliss.flint.widgets.image_plot import ImagePlotWidget
from bliss.flint.widgets.eye_check_box import EyeCheckBox
from bliss.flint.widgets.cog_check_box import CogCheckBox
from bliss.flint.widgets.icon_widget import IconWidget
from bliss.flint.widgets.viewer import refresh_manager
from bliss.flint.widgets.viewer import viewer_events
from silx.gui.plot.PlotWindow import Plot2D
from .stages.flat_field_stage import Layer
from .stages.flat_field_stage import extract_exposure_time
from .stages.selection_stage import SelectionStage
from bliss.flint.widgets import interfaces
from bliss.flint.widgets.checkable_combo_box import CheckableComboBox
from bliss.flint.utils import error_utils


_logger = logging.getLogger(__name__)


class _DeviceField(qt.QLabel):
    def plotItem(self):
        plotItem = self.__plotItem
        if plotItem is None:
            return None
        return plotItem()

    def setPlotItem(self, plotItem: plot_item_model.ImageItem):
        if plotItem is None:
            self.setText("")
            self.setEnabled(False)
            return

        dataChannel = plotItem.imageChannel()
        if dataChannel is None:
            self.setText("")
            self.setEnabled(False)
            return

        # FIXME: We have to access to the Device object instead
        elems = dataChannel.name().rsplit(":", 1)
        if len(elems) == 1:
            deviceName = "?"
        else:
            deviceName, _channelName = elems

        self.setEnabled(True)
        self.setText(deviceName)


class _ImageField(qt.QWidget):
    def __init__(self, parent):
        super(_ImageField, self).__init__(parent=parent)
        self.__plotItem = None

        self.__label = qt.QLabel(self)
        self.__display = EyeCheckBox(self)
        self.__display.toggled.connect(self.__checked)
        layout = qt.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.__label)
        layout.addStretch(1)
        layout.addWidget(self.__display)

    def plotItem(self):
        plotItem = self.__plotItem
        if plotItem is None:
            return None
        return plotItem()

    def __checked(self, isChecked):
        plotItem = self.plotItem()
        if plotItem is None:
            return
        plotItem.setVisible(isChecked)

    def setPlotItem(self, plotItem: plot_item_model.ImageItem):
        if plotItem is None:
            self.__plotItem = None
            self.__label.setText("")
            self.setEnabled(False)
            return

        self.__plotItem = weakref.ref(plotItem)

        self.__display.setChecked(plotItem.isVisible())

        dataChannel = plotItem.imageChannel()
        if dataChannel is None:
            self.__label.setText("")
            self.setEnabled(False)
            return

        self.setEnabled(True)
        channelName = dataChannel.name()
        self.__label.setText(channelName)


class _ImageSizeField(qt.QWidget):
    def __init__(self, parent):
        super(_ImageSizeField, self).__init__(parent=parent)
        self.__plotItem = None
        self.__scan = None

        self.__label = qt.QLabel(self)
        layout = qt.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.__label)

    def plotItem(self):
        plotItem = self.__plotItem
        if plotItem is None:
            return None
        return plotItem()

    def setPlotItem(self, plotItem: plot_item_model.ImageItem):
        self.__plotItem = weakref.ref(plotItem)
        self.updateData()

    def scan(self):
        return self.__scan

    def setScan(self, scan: scan_model.Scan):
        self.__scan = scan
        self.updateData()

    def updateData(self):
        scan = self.__scan
        plotItem = self.plotItem()
        if scan is None or plotItem is None:
            self.__label.setText("-")
            self.__label.setToolTip("")
            return

        imageChannelRef = plotItem.imageChannel()
        if imageChannelRef is None:
            self.__label.setText("")
            self.__label.setToolTip("")
            return

        imageChannel = imageChannelRef.channel(self.__scan)
        if imageChannel is None:
            self.__label.setText("")
            self.__label.setToolTip("")
            return

        data = imageChannel.data()
        if data is None:
            self.__label.setText("")
            self.__label.setToolTip("")
            return

        array = data.array()
        if array is None:
            self.__label.setText("")
            self.__label.setToolTip("")
            return

        t = imageChannel.type()
        if t == scan_model.ChannelType.IMAGE:
            shape = array.shape[0:2]
        elif t == scan_model.ChannelType.IMAGE_C_Y_X:
            shape = array.shape[1:3]
        else:
            self.__label.setText("?")
            self.__label.setToolTip(f"Unknown channel type {t}")

        title = " × ".join(reversed([str(x) for x in shape]))
        self.__label.setText(title)
        self.__label.setToolTip(f"Channel data shape: {array.shape}")


class _ImageDTypeField(qt.QWidget):
    def __init__(self, parent):
        super(_ImageDTypeField, self).__init__(parent=parent)
        self.__plotItem = None
        self.__scan = None

        self.__label = qt.QLabel(self)
        layout = qt.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.__label)

    def plotItem(self):
        plotItem = self.__plotItem
        if plotItem is None:
            return None
        return plotItem()

    def setPlotItem(self, plotItem: plot_item_model.ImageItem):
        self.__plotItem = weakref.ref(plotItem)
        self.updateData()

    def scan(self):
        return self.__scan

    def setScan(self, scan: scan_model.Scan):
        self.__scan = scan
        self.updateData()

    def updateData(self):
        scan = self.__scan
        plotItem = self.plotItem()
        if scan is None or plotItem is None:
            self.__label.setText("-")
            return

        imageChannel = plotItem.imageChannel()
        if imageChannel is None:
            self.__label.setText("")
            return

        data = imageChannel.data(self.__scan)
        if data is None:
            self.__label.setText("")
            return

        array = data.array()
        if array is None:
            self.__label.setText("")
            return

        dtype = array.dtype
        self.__label.setText(str(dtype))


class _LayerField(qt.QLabel):

    doubleClicked = qt.Signal()

    def __init__(self, parent=None):
        qt.QLabel.__init__(self, parent=parent)
        self.setToolTip("mock")
        self.doubleClicked.connect(self.__doubleClicked)
        self.__layer: Layer = None

    def mouseDoubleClickEvent(self, event: qt.QEvent):
        "Generates the doubleClicked signal"
        if event.button() == qt.Qt.LeftButton:
            self.doubleClicked.emit()
            event.accept()

    def setLayer(self, layer):
        self.__layer = layer
        if layer is None:
            self.setText("No data")
            self.setToolTip("")
        else:
            if layer.scanId:
                text = f"Scan #{layer.scanId}"
            else:
                text = " × ".join(reversed([str(s) for s in layer.array.shape]))
            self.setText(text)

            msg = ""
            if layer.scanId:
                msg += f"<li><b>Scan id</b>: #{layer.scanId}</li>"
            if layer.scanTitle:
                msg += f"<li><b>Scan title</b>: {layer.scanTitle}</li>"
            msg += f"<li><b>Exposure time</b>: {layer.exposureTime}s</li>"
            self.setToolTip(f"<ul>{msg}</ul>")

    def __doubleClicked(self):
        layer = self.__layer
        if layer is None:
            return

        window = Plot2D(parent=self)
        window.addImage(layer.array, legend=layer.kind)
        window.setKeepDataAspectRatio(True)
        window.getIntensityHistogramAction().setVisible(True)
        if self.__layer.scanTitle:
            window.setGraphTitle(self.__layer.scanTitle)
            window.setWindowTitle(self.__layer.scanTitle)
        window.setWindowFlags(qt.Qt.Window)
        window.show()


class _StagePanel(qt.QWidget):
    def __init__(self, parent):
        super(_StagePanel, self).__init__(parent=parent)
        self.__titleName = None
        self.__stage = None
        self.__enable = None

    def setupTitleName(self, name):
        self.__titleName = name

    def createTitle(self, parent):
        widget = qt.QWidget(parent)
        title = qt.QLabel(parent)
        title.setText(self.__titleName)
        enable = CogCheckBox(parent)
        enable.toggled.connect(self.__changeEnabled)
        enable.setToolTip("Enable/disable the processing")
        layout = qt.QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(enable)
        layout.addWidget(title)
        layout.addStretch()
        self.__enable = enable
        return widget

    def __changeEnabled(self, enable):
        stage = self.stage()
        if stage:
            stage.setEnabled(enable)

    def stage(self):
        stage = self.__stage
        if stage:
            return stage()
        self.__stage = None
        return None

    def setStage(self, stage):
        prevStage = self.stage()
        if stage is prevStage:
            return
        if prevStage:
            prevStage.configUpdated.disconnect(self._stageConfigUpdated)
            prevStage.sinkResultUpdated.disconnect(self._stageSinkResultUpdated)
        if stage is None:
            self.__stage = None
        else:
            self.__stage = weakref.ref(stage)
            stage.configUpdated.connect(self._stageConfigUpdated)
            stage.sinkResultUpdated.connect(self._stageSinkResultUpdated)
        self._stageConfigUpdated()
        self._stageSinkResultUpdated()

    def _stageConfigUpdated(self):
        stage = self.stage()
        if self.__enable is not None:
            self.__enable.setChecked(stage.isEnabled())

    def _stageSinkResultUpdated(self):
        pass


class _StatisticsStagePanel(_StagePanel):
    def __init__(self, parent):
        super(_StatisticsStagePanel, self).__init__(parent=parent)
        self.setupTitleName("Statistics")

        self.__min = qt.QLabel(self)
        self.__max = qt.QLabel(self)
        self.__mean = qt.QLabel(self)
        self.__std = qt.QLabel(self)

        layout = qt.QFormLayout(self)
        layout.addRow("Min", self.__min)
        layout.addRow("Max", self.__max)
        layout.addRow("Mean", self.__mean)
        layout.addRow("Std", self.__std)
        layout.setContentsMargins(0, 0, 0, 0)
        self._clearDisplay()

    def _clearDisplay(self):
        self.__min.setText("-")
        self.__max.setText("-")
        self.__mean.setText("-")
        self.__std.setText("-")

    def setFocusWidget(self, widget):
        stage = widget.imageProcessing().statisticsStage()
        self.setStage(stage)

    def _stageSinkResultUpdated(self):
        stage = self.stage()
        if stage is None:
            self._clearDisplay()
            return
        if not stage.isEnabled():
            self._clearDisplay()
            return

        def formatter(v):
            import numbers

            if v is None:
                return "-"
            if isinstance(v, numbers.Integral):
                return str(v)
            else:
                return f"{v:.3f}"

        self.__min.setText(formatter(stage.minimum()))
        self.__max.setText(formatter(stage.maximum()))
        self.__mean.setText(formatter(stage.nanmean()))
        self.__std.setText(formatter(stage.nanstd()))


class _FlatFieldStagePanel(_StagePanel):
    def __init__(self, parent):
        super(_FlatFieldStagePanel, self).__init__(parent=parent)
        self.setupTitleName("Flat field")
        self.__flat = _LayerField(self)
        self.__dark = _LayerField(self)
        layout = qt.QFormLayout(self)
        layout.addRow("Flat", self.__flat)
        layout.addRow("Dark", self.__dark)
        layout.setContentsMargins(0, 0, 0, 0)

    def setFocusWidget(self, widget):
        stage = widget.imageProcessing().flatFieldStage()
        self.setStage(stage)

    def _stageConfigUpdated(self):
        super()._stageConfigUpdated()
        stage = self.stage()
        self.__flat.setLayer(stage.flat())
        self.__dark.setLayer(stage.dark())


class _ExposureTimeStagePanel(_StagePanel):
    def __init__(self, parent):
        super(_ExposureTimeStagePanel, self).__init__(parent=parent)
        self.setupTitleName("Exposure time")
        self.__unit = qt.QLabel(self)
        self.__unit.setText("s")
        self.__unit.setToolTip("Exposure time in seconds")
        self.__expo = qt.QLabel(self)
        self.__expo.setText("-")
        layout = qt.QFormLayout(self)
        layout.addRow(self.__expo, self.__unit)
        layout.setContentsMargins(0, 0, 0, 0)

    def setScan(self, scan: scan_model.Scan):
        _layerKind, exposureTime = extract_exposure_time(scan.scanInfo())
        if exposureTime is not None:
            self.__expo.setText(f"{exposureTime:.3f}")
        else:
            self.__expo.setText("-")

    def setFocusWidget(self, widget):
        stage = widget.imageProcessing().exposureTimeStage()
        self.setStage(stage)


class _SaturationStagePanel(_StagePanel):
    def __init__(self, parent):
        super(_SaturationStagePanel, self).__init__(parent=parent)
        self.setupTitleName("Saturation")
        self.__edit = qt.QLineEdit(self)
        self.__edit.returnPressed.connect(self.__returnPressed)
        layout = qt.QVBoxLayout(self)
        layout.addWidget(self.__edit)
        layout.setContentsMargins(0, 0, 0, 0)

    def __returnPressed(self):
        stage = self.stage()
        if stage is None:
            return
        text = self.__edit.text()
        value = None if text == "" else float(text)
        stage.setValue(value)

    def setFocusWidget(self, widget):
        stage = widget.imageProcessing().saturationStage()
        self.setStage(stage)

    def _stageConfigUpdated(self):
        super()._stageConfigUpdated()
        stage = self.stage()
        value = stage.value()
        self.__edit.setText("" if value is None else str(value))


class _MaskField(qt.QWidget):
    def __init__(self, parent):
        super(_MaskField, self).__init__(parent=parent)
        self.__stage = None
        self.__label = qt.QLabel(self)
        self.__display = EyeCheckBox(self)
        self.__display.setToolTip("Display the mask as an overlay")
        self.__display.toggled.connect(self.__checked)

        self.__load = qt.QToolButton(self)
        self.__load.setAutoRaise(True)
        self.__load.setToolTip("Load a mask from a file")
        icon = icons.getQIcon("flint:icons/roi-load")
        self.__load.setIcon(icon)
        self.__load.clicked.connect(self.__loadMask)

        self.__remove = qt.QToolButton(self)
        self.__remove.setAutoRaise(True)
        self.__remove.setToolTip("Remove the actual mask")
        icon = icons.getQIcon("flint:icons/remove-item-small")
        self.__remove.setIcon(icon)
        self.__remove.clicked.connect(self.__removeMask)

        layout = qt.QHBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.__label)
        layout.addSpacing(4)
        layout.addStretch(1)
        layout.addWidget(self.__remove)
        layout.addWidget(self.__load)
        layout.addWidget(self.__display)

    def __removeMask(self):
        stage = self.stage()
        stage.setMask(None)

    def __loadMask(self):
        stage = self.stage()
        stage.requestMaskFile()

    def stage(self):
        stage = self.__stage
        if stage:
            return stage()
        self.__stage = None
        return None

    def stageWasUpdated(self, stage):
        self.__stage = weakref.ref(stage)
        self.__updateWidget()

    def __updateWidget(self):
        stage = self.stage()
        mask = stage.mask()
        if mask is not None:
            maskShape = " × ".join(reversed([str(s) for s in mask.shape]))
        self.__label.setText(maskShape if mask is not None else "No data")
        self.__remove.setVisible(stage.mask() is not None)

    def __checked(self, isChecked):
        stage = self.stage()
        stage.setMaskDisplayedAsLayer(isChecked)


class _MaskStagePanel(_StagePanel):
    def __init__(self, parent):
        super(_MaskStagePanel, self).__init__(parent=parent)
        self.setupTitleName("Mask")
        self.__mask = _MaskField(self)
        layout = qt.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.__mask)

    def setFocusWidget(self, widget):
        stage = widget.imageProcessing().maskStage()
        self.setStage(stage)

    def _stageConfigUpdated(self):
        super()._stageConfigUpdated()
        stage = self.stage()
        self.__mask.stageWasUpdated(stage)


class _RoiField(qt.QLabel):
    def __init__(self, parent):
        super(_RoiField, self).__init__(parent=parent)
        self.__plotItem = None

        self.__label = qt.QLabel(self)
        self.__icon = IconWidget(self)
        self.__display = EyeCheckBox(self)
        self.__display.toggled.connect(self.__checked)
        layout = qt.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.__icon.setIconSize(16, 16)
        self.__icon.setIconName("flint:icons/device-image-roi")

        layout.addWidget(self.__icon)
        layout.addWidget(self.__label)
        layout.addStretch(1)
        layout.addWidget(self.__display)

    def plotItem(self):
        plotItem = self.__plotItem
        if plotItem is None:
            return None
        return plotItem()

    def __checked(self, isChecked):
        plotItem = self.plotItem()
        if plotItem is None:
            return
        plotItem.setVisible(isChecked)

    def setPlotItem(self, plotItem: plot_item_model.RoiItem):
        if plotItem is None:
            self.__label.setText("")
            self.setEnabled(False)
            return

        roiName = plotItem.name()
        if roiName is None:
            self.__label.setText("")
            self.setEnabled(False)
            return

        self.__plotItem = weakref.ref(plotItem)

        self.__display.setChecked(plotItem.isVisible())

        self.setEnabled(True)
        self.__label.setText(roiName)


class _DiffractionUnits(CheckableComboBox):
    def __init__(self, parent=None):
        CheckableComboBox.__init__(self, parent=parent)
        from .stages.diffraction_stage import UNITS

        for code, desc in UNITS.items():
            label = desc[1]
            self.addItem(label, code)


class _DiffractionStagePanel(_StagePanel):
    def __init__(self, parent):
        super(_DiffractionStagePanel, self).__init__(parent=parent)
        self.setupTitleName("Diffraction")
        layout = qt.QGridLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.__calibrantDir = None
        self.__poniDir = None

        self.__pyfaiAvailable = True
        try:
            self.__feedPyFaiWidgets(layout)
        except ImportError as e:
            self.__pyfaiAvailable = False
            text = qt.QLabel(self)
            text.setText("pyFAI is not properly installed")
            text.setStyleSheet("QLabel { color: red; }")
            text.setToolTip(str(e))
            layout.addWidget(text)

    def __feedPyFaiWidgets(self, layout):
        from pyFAI.resources import silx_integration
        from pyFAI.gui.model.CalibrantModel import CalibrantModel
        from pyFAI.gui.model.GeometryModel import GeometryModel
        from pyFAI.gui.widgets.DetectorLabel import DetectorLabel
        from pyFAI.gui.widgets.CalibrantSelector import CalibrantSelector
        from pyFAI.gui.widgets.GeometryLabel import GeometryLabel

        silx_integration()

        self.__calibrantModel = CalibrantModel(self)
        self.__calibrantModel.changed.connect(self.__calibrantUpdated)
        self.__geometryModel = GeometryModel(self)
        self.__detectorLabel = DetectorLabel(self)
        self.__geometryLabel = GeometryLabel(self)
        self.__calibrantSelector = CalibrantSelector(self)
        self.__calibrantSelector.setStyleSheet("QComboBox {combobox-popup: 0;}")
        self.__calibrantSelector.setFileLoadable(True)
        self.__calibrantSelector.sigLoadFileRequested.connect(
            self.loadCalibrantRequested
        )
        self.__ringVisibility = EyeCheckBox(self)
        self.__ringVisibility.toggled.connect(self.__ringVisibilityChecked)

        poniAction = qt.QAction(self)
        poniAction.setToolTip("Load from a PONI file")
        poniAction.setText("...")
        poniAction.triggered.connect(self.loadPoniRequested)
        poniAction.setIcon(icons.getQIcon("flint:icons/roi-load"))
        self.__poniFileSelector = qt.QToolButton(self)
        self.__poniFileSelector.setDefaultAction(poniAction)
        self.__poniFileSelector.setAutoRaise(True)
        self.__units = _DiffractionUnits(self)
        self.__units.editTextChanged.connect(self.__tooltipUnitsUpdated)
        self.__units.setToolTip("Set of units displayed over the plot")

        self.__calibrantSelector.view().setVerticalScrollBarPolicy(
            qt.Qt.ScrollBarAsNeeded
        )

        self.__calibrantSelector.setModel(self.__calibrantModel)
        self.__geometryLabel.setGeometryModel(self.__geometryModel)

        layout.addWidget(self.__geometryLabel, 0, 0)
        layout.addWidget(self.__poniFileSelector, 0, 1, qt.Qt.AlignRight)
        layout.addWidget(self.__detectorLabel, 1, 0, 1, 2)
        layout.addWidget(self.__calibrantSelector, 2, 0)
        layout.addWidget(self.__ringVisibility, 2, 1, qt.Qt.AlignRight)
        layout.addWidget(self.__units, 3, 0)
        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 0)

    def createPoniDialog(self, title):
        """Create the poni file dialog"""
        dialog = qt.QFileDialog(self)
        dialog.setWindowTitle(title)
        dialog.setModal(True)
        filters = [
            "PONI files (*.poni)",
            "All files (*)",
        ]
        dialog.setNameFilters(filters)
        dialog.setFileMode(qt.QFileDialog.ExistingFile)
        return dialog

    def loadPoniRequested(self):
        """Display a file dialog to open a poni file"""
        dialog = self.createPoniDialog("Load PONI file")
        if self.__poniDir is not None and os.path.exists(self.__poniDir):
            dialog.setDirectory(self.__poniDir)

        result = dialog.exec_()
        if not result:
            return
        self.__poniDir = str(dialog.directory())
        if len(dialog.selectedFiles()) == 0:
            return

        from .stages.diffraction_stage import DiffractionStage

        stage: DiffractionStage = self.stage()

        fileName = dialog.selectedFiles()[0]
        with error_utils.exceptionAsMessageBox(self):
            stage.setGeometry(fileName)

    def createCalibrantDialog(self, title):
        """Create the calibrant file dialog"""
        dialog = qt.QFileDialog(self)
        dialog.setWindowTitle(title)
        dialog.setModal(True)
        filters = [
            "Calibrant files (*.D *.d *.DS *.ds)",
            "All files (*)",
        ]
        dialog.setNameFilters(filters)
        dialog.setFileMode(qt.QFileDialog.ExistingFile)
        return dialog

    def loadCalibrantRequested(self):
        """Display a file dialog to open a calibrant file"""
        dialog = self.createCalibrantDialog("Load calibrant file")
        if self.__calibrantDir is not None and os.path.exists(self.__calibrantDir):
            dialog.setDirectory(self.__calibrantDir)

        result = dialog.exec_()
        if not result:
            return
        self.__calibrantDir = str(dialog.directory())
        if len(dialog.selectedFiles()) == 0:
            return

        from .stages.diffraction_stage import DiffractionStage
        from pyFAI.calibrant import Calibrant

        stage: DiffractionStage = self.stage()

        filename = dialog.selectedFiles()[0]
        with error_utils.exceptionAsMessageBox(self):
            calibrant = Calibrant()
            try:
                calibrant.load_file(filename)
            except BaseException:
                calibrant = None
                raise
        if calibrant is None:
            return
        stage.setCalibrant(calibrant)

    def __calibrantUpdated(self):
        """Triggered when a calibrant is selected from the UI by the user"""
        from .stages.diffraction_stage import DiffractionStage

        stage: DiffractionStage = self.stage()
        stage.setCalibrant(self.__calibrantModel.calibrant())

    def __tooltipUnitsUpdated(self):
        """Triggered when the tooltip units was changed by the user"""
        from .stages.diffraction_stage import DiffractionStage

        stage: DiffractionStage = self.stage()
        stage.setTooltipUnits(self.__units.currentData())

    def __ringVisibilityChecked(self):
        from .stages.diffraction_stage import DiffractionStage

        stage: DiffractionStage = self.stage()
        stage.setRingsVisible(self.__ringVisibility.isChecked())

    def _stageConfigUpdated(self):
        super()._stageConfigUpdated()
        if self.__pyfaiAvailable:
            from .stages.diffraction_stage import DiffractionStage

            stage: DiffractionStage = self.stage()
            self.__detectorLabel.setDetector(stage.detector())
            self.__calibrantModel.setCalibrant(stage.calibrant())
            geometry = stage.geometry()
            self.__geometryModel.distance().setValue(geometry.dist)
            self.__geometryModel.poni1().setValue(geometry.poni1)
            self.__geometryModel.poni2().setValue(geometry.poni2)
            self.__geometryModel.rotation1().setValue(geometry.rot1)
            self.__geometryModel.rotation2().setValue(geometry.rot2)
            self.__geometryModel.rotation3().setValue(geometry.rot3)
            self.__geometryModel.wavelength().setValue(geometry.wavelength)
            self.__ringVisibility.setChecked(stage.isRingsVisible())
            self.__units.setCurrentData(stage.tooltipUnits())

    def setFocusWidget(self, widget):
        stage = widget.imageProcessing().diffractionStage()
        self.setStage(stage)


class _ImageChannelIndexField(_StagePanel):

    sigMeaningChanged = qt.Signal(bool)
    """True if the value received from  the stage have to be displayed."""

    def __init__(self, parent):
        super(_ImageChannelIndexField, self).__init__(parent=parent)
        self.setupTitleName("Channels")
        self.__spin = qt.QSpinBox(self)
        layout = qt.QVBoxLayout(self)
        layout.addWidget(self.__spin)
        layout.setContentsMargins(0, 0, 0, 0)

    def setFocusWidget(self, widget):
        stage = widget.imageProcessing().selectionStage()
        self.setStage(stage)

    def _stageConfigUpdated(self):
        super()._stageConfigUpdated()
        stage: SelectionStage = self.stage()
        if stage is None:
            self.__spin.setValue(0)
            self.__spin.setRange(0, 0)
            self.sigMeaningChanged.emit(False)
        else:
            maxIndex = stage.maxChannelIndex()
            if maxIndex in [None, 0]:
                self.__spin.setValue(0)
                self.__spin.setRange(0, 0)
                self.__spin.setToolTip("No channels")
                self.sigMeaningChanged.emit(False)
            else:
                index = stage.channelIndex()
                if index is not None:
                    self.__spin.setValue(index)
                self.__spin.setRange(0, maxIndex - 1)
                self.__spin.setToolTip(f"Nb channels: {maxIndex}")
                self.sigMeaningChanged.emit(True)


class ImagePlotProperty2Widget(qt.QWidget, interfaces.HasPlotModel, interfaces.HasScan):
    def __init__(self, parent=None):
        super(ImagePlotProperty2Widget, self).__init__(parent=parent)
        self.__scan: scan_model.Scan | None = None
        self.__flintModel: flint_model.FlintState | None = None
        self.__plotModel: plot_model.Plot | None = None

        self.__focusWidget = None

        self.__aggregator = viewer_events.PlotEventAggregator(self)
        self.__refreshManager = refresh_manager.RefreshManager(self)
        # self.__refreshManager.refreshModeChanged.connect(self.__refreshModeChanged)
        self.__refreshManager.setAggregator(self.__aggregator)

        self.__content = self.__createLayout(self)
        toolBar = self.__createToolBar()

        self.setAutoFillBackground(True)
        line = qt.QFrame(self)
        line.setFrameShape(qt.QFrame.HLine)
        line.setFrameShadow(qt.QFrame.Sunken)

        scroll = qt.QScrollArea(self)
        scroll.setBackgroundRole(qt.QPalette.Light)
        scroll.setFrameShape(qt.QFrame.NoFrame)
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.__content)

        layout = qt.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(toolBar)
        layout.addWidget(line)
        layout.addWidget(scroll)

    def __createLayout(self, parent):
        content = qt.QWidget(parent)
        layout = FormGridLayout(content)
        layout.setColumnStretch(0, 0)
        layout.setColumnStretch(1, 1)

        self.__deviceName = _DeviceField(content)
        self.__channelName = _ImageField(content)
        self.__imageSize = _ImageSizeField(content)
        self.__imageDType = _ImageDTypeField(content)
        self.__imageChannelIndexTitle = qt.QLabel(content)
        self.__imageChannelIndexTitle.setText("Channel index")
        self.__imageChannelIndexTitle.setToolTip(
            "Selection of the channel acquired per pixels"
        )
        self.__imageChannelIndex = _ImageChannelIndexField(content)
        self.__imageChannelIndex.sigMeaningChanged.connect(
            self.__imageChannelIndexMeaningChanged
        )
        self.__imageState = _StatisticsStagePanel(content)
        self.__imageFFC = _FlatFieldStagePanel(content)
        self.__imageExpo = _ExposureTimeStagePanel(content)
        self.__imageMask = _MaskStagePanel(content)
        self.__imageSaturation = _SaturationStagePanel(content)
        self.__imageDiffraction = _DiffractionStagePanel(content)
        self.__rois = qt.QWidget(content)
        roiLayout = qt.QVBoxLayout(self.__rois)
        roiLayout.setContentsMargins(0, 0, 0, 0)

        layout.addRow("Device", self.__deviceName)
        layout.addRow("Channel", self.__channelName)
        layout.addRow("Image size", self.__imageSize)
        layout.addRow("Image dtype", self.__imageDType)
        layout.addRow(self.__imageChannelIndexTitle, self.__imageChannelIndex)

        self.__roiSeparator = qt.QFrame(self)
        self.__roiSeparator.setFrameShape(qt.QFrame.HLine)
        self.__roiSeparator.setFrameShadow(qt.QFrame.Sunken)
        layout.addRow(self.__roiSeparator)
        self.__roiTitle = qt.QLabel(self)
        self.__roiTitle.setText("ROIs")
        layout.addRow(self.__roiTitle, self.__rois)

        self.__saturationSeparator = qt.QFrame(self)
        self.__saturationSeparator.setFrameShape(qt.QFrame.HLine)
        self.__saturationSeparator.setFrameShadow(qt.QFrame.Sunken)
        layout.addRow(self.__saturationSeparator)
        self.__saturationTitle = self.__imageSaturation.createTitle(self)
        layout.addRow(self.__saturationTitle, self.__imageSaturation)
        self.__toggleSaturationAction(False)

        self.__maskSeparator = qt.QFrame(self)
        self.__maskSeparator.setFrameShape(qt.QFrame.HLine)
        self.__maskSeparator.setFrameShadow(qt.QFrame.Sunken)
        layout.addRow(self.__maskSeparator)
        self.__maskTitle = self.__imageMask.createTitle(self)
        layout.addRow(self.__maskTitle, self.__imageMask)
        self.__toggleMaskAction(False)

        self.__statisticsSeparator = qt.QFrame(self)
        self.__statisticsSeparator.setFrameShape(qt.QFrame.HLine)
        self.__statisticsSeparator.setFrameShadow(qt.QFrame.Sunken)
        layout.addRow(self.__statisticsSeparator)
        self.__statisticsTitle = self.__imageState.createTitle(self)
        layout.addRow(self.__statisticsTitle, self.__imageState)
        self.__toggleStatisticsAction(False)

        self.__ffcSeparator = qt.QFrame(self)
        self.__ffcSeparator.setFrameShape(qt.QFrame.HLine)
        self.__ffcSeparator.setFrameShadow(qt.QFrame.Sunken)
        layout.addRow(self.__ffcSeparator)
        self.__ffcTitle = self.__imageFFC.createTitle(self)
        layout.addRow(self.__ffcTitle, self.__imageFFC)
        self.__toggleFlatFieldAction(False)

        self.__expoSeparator = qt.QFrame(self)
        self.__expoSeparator.setFrameShape(qt.QFrame.HLine)
        self.__expoSeparator.setFrameShadow(qt.QFrame.Sunken)
        layout.addRow(self.__expoSeparator)
        self.__expoTitle = self.__imageExpo.createTitle(self)
        layout.addRow(self.__expoTitle, self.__imageExpo)
        self.__toggleExpoTimeAction(False)

        self.__diffractionSeparator = qt.QFrame(self)
        self.__diffractionSeparator.setFrameShape(qt.QFrame.HLine)
        self.__diffractionSeparator.setFrameShadow(qt.QFrame.Sunken)
        layout.addRow(self.__diffractionSeparator)
        self.__diffractionTitle = self.__imageDiffraction.createTitle(self)
        layout.addRow(self.__diffractionTitle, self.__imageDiffraction)
        self.__toggleDiffractionAction(False)

        vstretch = qt.QSpacerItem(
            0, 0, qt.QSizePolicy.Minimum, qt.QSizePolicy.Expanding
        )
        layout.addItem(vstretch)
        return content

    def __imageChannelIndexMeaningChanged(self, hasMeaning):
        self.__imageChannelIndex.setVisible(hasMeaning)
        self.__imageChannelIndexTitle.setVisible(hasMeaning)

    def __createToolBar(self):
        toolBar = qt.QToolBar(self)
        toolBar.setMovable(False)

        saturationAction = qt.QAction(self)
        saturationAction.setCheckable(True)
        saturationAction.setText("Enable mask stage")
        saturationAction.toggled.connect(self.__toggleSaturationAction)
        icon = icons.getQIcon("flint:icons/data-saturation")
        saturationAction.setIcon(icon)
        toolBar.addAction(saturationAction)
        self.__saturationAction = saturationAction

        maskAction = qt.QAction(self)
        maskAction.setCheckable(True)
        maskAction.setText("Enable mask stage")
        maskAction.toggled.connect(self.__toggleMaskAction)
        icon = icons.getQIcon("flint:icons/data-mask")
        maskAction.setIcon(icon)
        toolBar.addAction(maskAction)
        self.__maskAction = maskAction

        statisticsAction = qt.QAction(self)
        statisticsAction.setCheckable(True)
        statisticsAction.setText("Enable mask stage")
        statisticsAction.toggled.connect(self.__toggleStatisticsAction)
        icon = icons.getQIcon("flint:icons/data-statistics")
        statisticsAction.setIcon(icon)
        toolBar.addAction(statisticsAction)
        self.__statisticsAction = statisticsAction

        flatFieldAction = qt.QAction(self)
        flatFieldAction.setCheckable(True)
        flatFieldAction.setText("Enable flat field stage")
        flatFieldAction.toggled.connect(self.__toggleFlatFieldAction)
        icon = icons.getQIcon("flint:icons/data-flat-field")
        flatFieldAction.setIcon(icon)
        toolBar.addAction(flatFieldAction)
        self.__flatFieldAction = flatFieldAction

        expoAction = qt.QAction(self)
        expoAction.setCheckable(True)
        expoAction.setText("Enable exposure time normalization")
        expoAction.toggled.connect(self.__toggleExpoTimeAction)
        icon = icons.getQIcon("flint:icons/data-expotime")
        expoAction.setIcon(icon)
        toolBar.addAction(expoAction)
        self.__expoAction = expoAction

        diffractionAction = qt.QAction(self)
        diffractionAction.setCheckable(True)
        diffractionAction.setText("Show diffraction ring overlay")
        diffractionAction.toggled.connect(self.__toggleDiffractionAction)
        icon = icons.getQIcon("flint:icons/data-diffraction")
        diffractionAction.setIcon(icon)
        toolBar.addAction(diffractionAction)
        self.__diffractionAction = diffractionAction

        return toolBar

    def __toggleFlatFieldAction(self, checked):
        if self.__focusWidget:
            self.__focusWidget.imageProcessing().flatFieldStage().setEnabled(checked)
        self.__imageFFC.setVisible(checked)
        self.__ffcSeparator.setVisible(checked)
        self.__ffcTitle.setVisible(checked)

    def __toggleExpoTimeAction(self, checked):
        if self.__focusWidget:
            self.__focusWidget.imageProcessing().exposureTimeStage().setEnabled(checked)
        self.__imageExpo.setVisible(checked)
        self.__expoSeparator.setVisible(checked)
        self.__expoTitle.setVisible(checked)

    def __toggleMaskAction(self, checked):
        if self.__focusWidget:
            self.__focusWidget.imageProcessing().maskStage().setEnabled(checked)
        self.__imageMask.setVisible(checked)
        self.__maskSeparator.setVisible(checked)
        self.__maskTitle.setVisible(checked)

    def __toggleSaturationAction(self, checked):
        if self.__focusWidget:
            self.__focusWidget.imageProcessing().saturationStage().setEnabled(checked)
        self.__imageSaturation.setVisible(checked)
        self.__saturationSeparator.setVisible(checked)
        self.__saturationTitle.setVisible(checked)

    def __toggleStatisticsAction(self, checked):
        if self.__focusWidget:
            self.__focusWidget.imageProcessing().statisticsStage().setEnabled(checked)
        self.__imageState.setVisible(checked)
        self.__statisticsSeparator.setVisible(checked)
        self.__statisticsTitle.setVisible(checked)

    def __toggleDiffractionAction(self, checked):
        if self.__focusWidget:
            self.__focusWidget.imageProcessing().diffractionStage().setEnabled(checked)
        self.__imageDiffraction.setVisible(checked)
        self.__diffractionSeparator.setVisible(checked)
        self.__diffractionTitle.setVisible(checked)

    def setFlintModel(self, flintModel: flint_model.FlintState = None):
        self.__flintModel = flintModel

    def focusWidget(self):
        return self.__focusWidget

    def setFocusWidget(self, widget: ImagePlotWidget):
        if self.__focusWidget is not None:
            widget.plotModelUpdated.disconnect(self.__plotModelUpdated)
            widget.scanModelUpdated.disconnect(self.__currentScanChanged)
        self.__focusWidget = widget
        if self.__focusWidget is not None:
            widget.plotModelUpdated.connect(self.__plotModelUpdated)
            widget.scanModelUpdated.connect(self.__currentScanChanged)
            plotModel = widget.plotModel()
            scanModel = widget.scan()
        else:
            plotModel = None
            scanModel = None
        self.__plotModelUpdated(plotModel)
        self.__currentScanChanged(scanModel)
        self.__imageState.setFocusWidget(widget)
        self.__imageFFC.setFocusWidget(widget)
        self.__imageChannelIndex.setFocusWidget(widget)
        self.__imageExpo.setFocusWidget(widget)
        self.__imageMask.setFocusWidget(widget)
        self.__imageSaturation.setFocusWidget(widget)
        self.__imageDiffraction.setFocusWidget(widget)
        if self.__focusWidget is not None:
            processing = widget.imageProcessing()
            self.__flatFieldAction.setChecked(processing.flatFieldStage().isEnabled())
            self.__maskAction.setChecked(processing.maskStage().isEnabled())
            self.__expoAction.setChecked(processing.exposureTimeStage().isEnabled())
            self.__saturationAction.setChecked(processing.saturationStage().isEnabled())
            self.__statisticsAction.setChecked(processing.statisticsStage().isEnabled())
            self.__diffractionAction.setChecked(
                processing.diffractionStage().isEnabled()
            )

    def __plotModelUpdated(self, plotModel):
        self.setPlotModel(plotModel)

    def setPlotModel(self, plotModel: plot_model.Plot):
        if self.__plotModel is not None:
            self.__plotModel.structureChanged.disconnect(self.__structureChanged)
            self.__plotModel.itemValueChanged.disconnect(self.__itemValueChanged)
        self.__plotModel = plotModel
        if self.__plotModel is not None:
            self.__plotModel.structureChanged.connect(self.__structureChanged)
            self.__plotModel.itemValueChanged.connect(self.__itemValueChanged)
        self.__updateDisplay()

    def __currentScanChanged(self, scanModel):
        self.__setScan(scanModel)

    def __structureChanged(self):
        self.__updateDisplay()

    def __itemValueChanged(
        self, item: plot_model.Item, eventType: plot_model.ChangeEventType
    ):
        pass

    def plotModel(self) -> plot_model.Plot | None:
        return self.__plotModel

    def __setScan(self, scan: scan_model.Scan = None):
        if self.__scan is scan:
            return
        if self.__scan is not None:
            self.__scan.scanDataUpdated[object].disconnect(
                self.__aggregator.callbackTo(self.__scanDataUpdated)
            )
            self.__scan.scanStarted.disconnect(
                self.__aggregator.callbackTo(self.__scanStarted)
            )
            self.__scan.scanFinished.disconnect(
                self.__aggregator.callbackTo(self.__scanFinished)
            )
        self.__scan = scan
        # As the scan was updated, clear the previous cached events
        self.__aggregator.clear()
        self.__imageSize.setScan(scan)
        self.__imageDType.setScan(scan)
        self.__imageExpo.setScan(scan)
        if self.__scan is not None:
            self.__scan.scanDataUpdated[object].connect(
                self.__aggregator.callbackTo(self.__scanDataUpdated)
            )
            self.__scan.scanStarted.connect(
                self.__aggregator.callbackTo(self.__scanStarted)
            )
            self.__scan.scanFinished.connect(
                self.__aggregator.callbackTo(self.__scanFinished)
            )
        self.__updateDisplay()

    def __scanStarted(self):
        pass

    def __scanFinished(self):
        pass

    def __scanDataUpdated(self, event: scan_model.ScanDataUpdateEvent):
        plotModel = self.__plotModel
        if plotModel is None:
            return
        self.__imageSize.updateData()
        self.__imageDType.updateData()

    def __updateDisplay(self):
        if self.__plotModel is None:
            return

        roisLayout = self.__rois.layout()
        for i in reversed(range(roisLayout.count())):
            roisLayout.itemAt(i).widget().deleteLater()

        countImages = 0
        countRois = 0
        for plotItem in self.__plotModel.items():
            if isinstance(plotItem, plot_item_model.ImageItem):
                countImages += 1
                self.__channelName.setPlotItem(plotItem)
                self.__deviceName.setPlotItem(plotItem)
                self.__imageSize.setPlotItem(plotItem)
                self.__imageDType.setPlotItem(plotItem)

            elif isinstance(plotItem, plot_item_model.RoiItem):
                countRois += 1
                roi = _RoiField(self.__rois)
                roisLayout.addWidget(roi)
                roi.setPlotItem(plotItem)

        self.__rois.setVisible(countRois > 0)
        self.__roiSeparator.setVisible(countRois > 0)
        self.__roiTitle.setVisible(countRois > 0)

        if countImages == 0:
            self.__channelName.setPlotItem(None)
            self.__deviceName.setPlotItem(None)
        elif countImages >= 2:
            _logger.warning(
                "More than one image is provided by this plot. A single image is supported, others will be ignored."
            )
