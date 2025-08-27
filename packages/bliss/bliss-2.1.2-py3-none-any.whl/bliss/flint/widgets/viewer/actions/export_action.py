# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

from __future__ import annotations

import os
import tempfile
import logging
import weakref
import functools

from silx.gui import qt
from silx.gui import icons
from silx.gui.plot import PlotWindow
from silx.gui.plot.actions import PlotAction
from silx.gui.plot.actions import io
from bliss.flint.model import flint_model
from bliss.flint.model import plot_model
from bliss.flint.model import plot_item_model
from bliss.flint.model import scan_model
from bliss.flint.utils.error_utils import exceptionAsMessageBox
from bliss.flint.widgets.viewer.viewer_dock import ViewerDock


_logger = logging.getLogger(__name__)


class SwitchAction(qt.QWidgetAction):
    """This action provides a default action from a list of actions.

    The default action can be selected from a drop down list. The last one used
    became the default one.

    The default action is directly usable without using the drop down list.
    """

    def __init__(self, parent=None):
        assert isinstance(parent, qt.QWidget)
        qt.QWidgetAction.__init__(self, parent)
        button = qt.QToolButton(parent)
        button.setPopupMode(qt.QToolButton.MenuButtonPopup)
        self.setDefaultWidget(button)
        self.__button = button
        # In case of action enabled/disabled twice, this attribute can restore
        # a stable state
        self.__lastUserDefault = None

    def getMenu(self):
        """Returns the menu.

        :rtype: qt.QMenu
        """
        button = self.__button
        menu = button.menu()
        if menu is None:
            menu = qt.QMenu(button)
            button.setMenu(menu)
        return menu

    def addAction(self, action):
        """Add a new action to the list.

        :param qt.QAction action: New action
        """
        menu = self.getMenu()
        button = self.__button
        menu.addAction(action)
        if button.defaultAction() is None and action.isEnabled():
            self._setUserDefault(action)
        action.triggered.connect(self._trigger)
        action.changed.connect(self._changed)

    def _changed(self):
        action: qt.QAction = self.sender()
        if action.isEnabled():
            if action is self._userDefault():
                # If it was used as default action
                button = self.__button
                defaultAcction = button.defaultAction()
                if defaultAcction is action:
                    return
                # Select it back as the default
                button.setDefaultAction(action)
        else:
            button = self.__button
            defaultAcction = button.defaultAction()
            if defaultAcction is not action:
                return
            # If the action was the default one and is not enabled anymore
            menu = button.menu()
            for action in menu.actions():
                if action.isEnabled():
                    button.setDefaultAction(action)
                    break

    def _trigger(self):
        action = self.sender()
        self._setUserDefault(action)

    def _userDefault(self):
        if self.__lastUserDefault is None:
            return None
        userDefault = self.__lastUserDefault()
        return userDefault

    def _setUserDefault(self, action):
        self.__lastUserDefault = weakref.ref(action)
        button = self.__button
        button.setDefaultAction(action)


def export_plot_as_csv(plotModel: plot_model.Plot, scan: scan_model.Scan, filename):
    """
    Export the plotModel from this scan into a CVS formatat this filename.
    """
    xnames = []
    ynames = []
    for item in plotModel.items():
        print(item)
        if isinstance(item, plot_item_model.CurveItem):
            xchannel = item.xChannel()
            if xchannel is not None:
                name = xchannel.name()
                if name not in xnames and name not in ynames:
                    xnames.append(name)
            ychannel = item.yChannel()
            if ychannel is not None:
                name = ychannel.name()
                if name not in xnames and name not in ynames:
                    ynames.append(name)
    names = [] + xnames + ynames
    channels = [scan.getChannelByName(n) for n in names]
    data2 = [c.array() for c in channels if c is not None]
    data = [d for d in data2 if d is not None]
    if len(data) == 0:
        raise RuntimeError("No data to export")
    imax = max([len(d) for d in data])
    imin = min([len(d) for d in data])
    if imin != imax:
        _logger.warning("During the export to '%s' data was truncated", filename)

    with open(filename, "wt") as f:
        header = "\t".join([str(n) for n in names])
        f.write(header + "\n")
        for i in range(imin):
            dline = [str(d[i]) for d in data]
            line = "\t".join(dline)
            f.write(line + "\n")


class ExportAction(SwitchAction):
    def __init__(self, plot: PlotWindow, parent=None):
        super(ExportAction, self).__init__(parent)
        self._logbookAction = ExportToLogBookAction(plot, parent)
        self.addAction(self._logbookAction)
        self.addAction(io.CopyAction(plot, self))
        self.addAction(io.PrintAction(plot, self))

        def _export_model_as_csv(flintPlot: ViewerDock, plot, filename, nameFilter):
            with exceptionAsMessageBox(plot):
                plotModel = flintPlot.plotModel()
                if plotModel is None:
                    raise RuntimeError("No plot selection to export")
                scanModel = flintPlot.scan()
                if scanModel is None:
                    raise RuntimeError("No scan data to export")
                export_plot_as_csv(plotModel, scanModel, filename)

        silxSave = io.SaveAction(plot, self)
        if parent:
            silxSave.setFileFilter(
                "curves",
                "Curves as tab-separated CSV (*.csv)",
                functools.partial(_export_model_as_csv, parent),
            )
        self.addAction(silxSave)

    def setFlintModel(self, state: flint_model.FlintState):
        self._logbookAction.setFlintModel(state)

    def logbookAction(self):
        return self._logbookAction


class ExportToLogBookAction(PlotAction):
    """QAction managing the behavior of saving a current plot into the tango
    metadata logbook.
    """

    def __init__(self, plot: PlotWindow, parent: qt.QWidget):
        super(ExportToLogBookAction, self).__init__(
            plot,
            icon="flint:icons/export-logbook",
            text="Export to logbook",
            tooltip="Export this plot to the logbook",
            triggered=self._actionTriggered,
            parent=parent,
        )
        self.__state: flint_model.FlintState | None = None

    def setFlintModel(self, state: flint_model.FlintState):
        if self.__state is not None:
            self.__state.icatClientChanged.disconnect(self.__icatClientChanged)
        self.__state = state
        if self.__state is not None:
            self.__state.icatClientChanged.connect(self.__icatClientChanged)
        self.__icatClientChanged()

    def __icatClientChanged(self):
        if self.__state is not None:
            client = self.__state.icatClient()
        else:
            client = None

        if client is None:
            self.setEnabled(False)
            self.setToolTip("No ICAT client specified")
        elif not hasattr(client, "send_binary_data"):
            self.setEnabled(False)
            self.setToolTip(
                "The ICAT client is created but it does not provide API to upload image"
            )
        else:
            self.setEnabled(True)
            self.setToolTip("Export this plot to the logbook")

    def _actionTriggered(self):
        with exceptionAsMessageBox(parent=self.plot):
            self._processSave()

    def _processSave(self):
        plot: PlotWindow = self.plot

        try:
            f = tempfile.NamedTemporaryFile(delete=False)
            filename = f.name
            f.close()
            os.unlink(filename)
            plot.saveGraph(filename, fileFormat="png")
            with open(filename, "rb") as f2:
                data = f2.read()
            os.unlink(filename)
        except Exception:
            _logger.error("Error while creating the screenshot", exc_info=True)
            raise Exception("Error while creating the screenshot")
        try:
            assert self.__state is not None
            icatClient = self.__state.icatClient()
            icatClient.send_binary_data(data=data, mimetype="image/png")
        except Exception:
            _logger.error("Error while sending the screenshot", exc_info=True)
            raise Exception("Error while sending the screenshot")


class ExportOthersAction(qt.QWidgetAction):
    def __init__(self, plot, parent):
        super(ExportOthersAction, self).__init__(parent)

        menu = qt.QMenu(parent)
        menu.addAction(io.CopyAction(plot, self))
        menu.addAction(io.PrintAction(plot, self))
        menu.addAction(io.SaveAction(plot, self))

        icon = icons.getQIcon("flint:icons/export-others")
        toolButton = qt.QToolButton(parent)
        toolButton.setText("Other exports")
        toolButton.setToolTip("Various exports")
        toolButton.setIcon(icon)
        toolButton.setMenu(menu)
        toolButton.setPopupMode(qt.QToolButton.InstantPopup)
        self.setDefaultWidget(toolButton)
