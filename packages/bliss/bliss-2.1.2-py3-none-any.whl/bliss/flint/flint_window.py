# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.
"""Module containing the description of the main window provided by Flint"""

from __future__ import annotations
from typing import NamedTuple, Any

import logging
import os
import functools

from silx.gui import qt

from bliss.flint.widgets.live_window import LiveWindow
from bliss.flint.widgets.custom_plot import CustomPlot
from bliss.flint.widgets.logging_window import LoggingWindow
from bliss.flint.widgets.state_indicator import StateIndicator
from bliss.flint.widgets.inlive_custom_plot import InliveCustomPlot
from bliss.flint.widgets.viewer.actions import app_actions
from bliss.flint.model import flint_model
from bliss.common import constants as bliss_constants
from bliss.flint.utils import error_utils

_logger = logging.getLogger(__name__)


class CustomPlotLocation(NamedTuple):
    customPlot: CustomPlot
    parentCustomPlot: CustomPlot | None
    inLive: bool


class FlintWindow(qt.QMainWindow):
    """Main Flint window"""

    aboutToClose = qt.Signal()

    def __init__(self, parent=None):
        qt.QMainWindow.__init__(self, parent=parent)
        self.setAttribute(qt.Qt.WA_QuitOnClose, True)

        self.__flintState: flint_model.FlintState | None = None
        self.__stateIndicator: StateIndicator | None = None
        self.__customPlots: dict[str, CustomPlotLocation] = {}

        central_widget = qt.QWidget(self)

        tabs = qt.QTabWidget(central_widget)
        tabs.setTabsClosable(True)
        tabs.tabCloseRequested[int].connect(self.__tabCloseRequested)
        self.__tabs = tabs

        self.setCentralWidget(tabs)

    def event(self, event: qt.QEvent):
        if event.type() == qt.QEvent.Close:
            self.aboutToClose.emit()
        return super(FlintWindow, self).event(event)

    def setFlintModel(self, flintState: flint_model.FlintState):
        if self.__flintState is not None:
            self.__flintState.blissSessionChanged.disconnect(self.__blissSessionChanged)
        self.__flintState = flintState
        if self.__flintState is not None:
            self.__flintState.blissSessionChanged.connect(self.__blissSessionChanged)
        self.__updateTitle()
        if self.__stateIndicator is not None:
            self.__stateIndicator.setFlintModel(flintState)

    def flintModel(self) -> flint_model.FlintState:
        assert self.__flintState is not None
        return self.__flintState

    def tabs(self):
        # FIXME: Have to be removed as it is not really an abstraction
        return self.__tabs

    def __tabCloseRequested(self, tabIndex: int):
        widget = self.__tabs.widget(tabIndex)
        if isinstance(widget, CustomPlot):
            plotId = widget.plotId()
            if plotId is None:
                _logger.debug("Unexpected plotId None")
                return
            self.removeCustomPlot(plotId)

    def __createLogWindow(self):
        assert self.__flintState is not None
        logWindow = LoggingWindow(self, self.__flintState)
        logWindow.setAttribute(qt.Qt.WA_DeleteOnClose)
        return logWindow

    def _createSettingsMenu(self, parent: qt.QWidget) -> qt.QMenu:
        assert self.__flintState is not None
        flintState = self.__flintState
        settingsMenu = qt.QMenu(parent)
        settingsMenu.setTitle("Settings")
        openGlAction = app_actions.OpenGLAction(self)
        useFlatImagePropertyAction = qt.QAction(self)
        useFlatImagePropertyAction.setCheckable(True)
        useFlatImagePropertyAction.setText("Use flat live image property")
        settingsMenu.addSection("Application settings")
        settingsMenu.addAction(openGlAction)
        settingsMenu.addAction(useFlatImagePropertyAction)
        settingsMenu.addSection("Workspace settings")
        autoFocusAction = app_actions.AutoFocusOnNewScanAction(
            settingsMenu, self.__flintState
        )
        settingsMenu.addAction(autoFocusAction)

        def updateFlatImageProperty(checked):
            flintState.setUseFlatImageProperty(checked)

        useFlatImagePropertyAction.triggered.connect(updateFlatImageProperty)

        def update():
            autoFocusAction.updateState()
            useFlatImagePropertyAction.setChecked(flintState.useFlatImageProperty())

        settingsMenu.aboutToShow.connect(update)
        return settingsMenu

    def initMenus(self):
        assert self.__flintState is not None
        flintModel = self.flintModel()
        liveWindow = flintModel.liveWindow()
        manager = flintModel.mainManager()

        exitAction = qt.QAction("&Exit", self)
        exitAction.setShortcut("Ctrl+Q")
        exitAction.setStatusTip("Exit flint")
        exitAction.triggered.connect(self.close)
        showLogAction = qt.QAction("Show &log", self)
        showLogAction.setStatusTip("Show log window")

        showLogAction.triggered.connect(self.showLogDialog)
        menubar = self.menuBar()
        fileMenu = menubar.addMenu("&File")
        fileMenu.addAction(exitAction)

        windowMenu: qt.QMenu = menubar.addMenu("&Windows")
        windowMenu.addSection("Live scans")
        liveWindow.createWindowActions(windowMenu)
        windowMenu.addSection("Live widgets")
        action = self.__createActionToCloneActiveLiveWidget()
        windowMenu.addAction(action)
        windowMenu.addSection("Custom plots")
        action = self.__createActionToMoveCustomPlotToLive()
        windowMenu.addAction(action)
        action = self.__createActionToMoveCustomPlotToTab()
        windowMenu.addAction(action)
        windowMenu.addSection("Helpers")
        windowMenu.addAction(showLogAction)
        action = qt.QAction("&IPython console", self)
        action.setStatusTip("Show a IPython console (for debug purpose)")
        action.triggered.connect(self.openDebugConsole)
        windowMenu.addAction(action)

        settingsMenu = self._createSettingsMenu(menubar)
        menubar.addMenu(settingsMenu)

        menubar = self.menuBar()
        layoutMenu = menubar.addMenu("&Layout")
        liveWindow.createLayoutActions(layoutMenu)

        menubar = self.menuBar()
        workspaceMenu = menubar.addMenu("&Workspace")
        workspaceManager = manager.workspaceManager()
        workspaceManager.connectManagerActions(self, workspaceMenu)

        BLISS_HELP_ROOT = "https://bliss.gitlab-pages.esrf.fr/bliss/master/"
        BLISS_HELP_URL = BLISS_HELP_ROOT
        FLINT_DEMO_URL = BLISS_HELP_ROOT + "bliss_flint.html"
        FLINT_HELP_URL = BLISS_HELP_ROOT + "flint/flint_scan_plotting.html"

        def openUrl(url):
            qt.QDesktopServices.openUrl(qt.QUrl(url))

        helpMenu = menubar.addMenu("&Help")

        action = qt.QAction("Flint online &demo", self)
        action.setStatusTip("Show the online demo about Flint")
        action.triggered.connect(lambda: openUrl(FLINT_DEMO_URL))
        helpMenu.addAction(action)

        helpMenu.addSeparator()

        action = qt.QAction("&BLISS online help", self)
        action.setStatusTip("Show the online help about BLISS")
        action.triggered.connect(lambda: openUrl(BLISS_HELP_URL))
        helpMenu.addAction(action)

        action = qt.QAction("&Flint online help", self)
        action.setStatusTip("Show the online help about Flint")
        action.triggered.connect(lambda: openUrl(FLINT_HELP_URL))
        helpMenu.addAction(action)

        helpMenu.addSeparator()

        action = qt.QAction("&About", self)
        action.setStatusTip("Show the application's About box")
        action.triggered.connect(self.showAboutBox)
        helpMenu.addAction(action)

        stateIndicator = StateIndicator(self)
        stateIndicator.setFlintModel(self.__flintState)
        stateIndicator.setLogModel(self.__flintState.logModel())
        # widgetAction = qt.QWidgetAction(menubar)
        # widgetAction.setDefaultWidget(stateIndicator)
        # menubar.addAction(widgetAction)
        self.__stateIndicator = stateIndicator
        menubar.setCornerWidget(stateIndicator, qt.Qt.TopLeftCorner)
        # self.__tabs.setCornerWidget(stateIndicator)

    def openDebugConsole(self):
        """Open a new debug console"""
        try:
            from silx.gui.console import IPythonDockWidget
        except ImportError:
            _logger.debug("Error while loading IPython console", exc_info=True)
            _logger.error("IPython not available")
            return

        available_vars = {"flintState": self.__flintState, "window": self}
        banner = (
            "The variable 'flintState' and 'window' are available.\n"
            "Use the 'whos' and 'help(flintState)' commands for more information.\n"
            "\n"
        )
        widget = IPythonDockWidget(
            parent=self, available_vars=available_vars, custom_banner=banner
        )
        widget.setAttribute(qt.Qt.WA_DeleteOnClose)
        self.addDockWidget(qt.Qt.RightDockWidgetArea, widget)
        widget.show()

    def showLogDialog(self):
        """Show the log dialog of Flint"""
        assert self.__flintState is not None
        logWindow = self.__flintState.logWindow()
        if logWindow is None:
            logWindow = self.__createLogWindow()
            self.__flintState.setLogWindow(logWindow)
        logWindow.finished.connect(self.__closeLogWindow)
        logWindow.show()

    def __createActionToCloneActiveLiveWidget(self):
        assert self.__flintState is not None
        flintState = self.__flintState
        action = qt.QAction(self)
        action.setText("Clone the active live widget")

        def executeAction():
            liveWindow = flintState.liveWindow()
            propertyWidget = liveWindow.propertyWidget()
            if propertyWidget is None:
                # Here we use propertyWidget but it's weird
                # FIXME: Create a slot if the global state for the active viewer
                qt.QMessageBox.critical(self, "Error", "No property windows found")
                return

            widget = propertyWidget.focusWidget()
            if widget is None:
                qt.QMessageBox.critical(self, "Error", "No viewer selected")
                return

            manager = flintState.mainManager()
            with error_utils.exceptionAsMessageBox(self):
                manager.cloneLiveWidget(widget)

        action.triggered.connect(executeAction)
        return action

    def __createActionToMoveCustomPlotToLive(self):
        mainAction = qt.QAction(self)
        mainAction.setText("Move to live tab")
        subMenu = qt.QMenu(self)
        mainAction.setMenu(subMenu)

        def feedActions():
            subMenu.clear()
            for location in self.__customPlots.values():
                if location.parentCustomPlot is not None:
                    continue
                if not location.inLive:
                    action = qt.QAction(self)
                    action.setText(f"Move {location.customPlot.plotId()}")
                    action.triggered.connect(
                        functools.partial(self.__moveToLive, location.customPlot)
                    )
                    subMenu.addAction(action)
            if subMenu.isEmpty():
                emptyAction = qt.QAction(self)
                emptyAction.setText("No plot")
                emptyAction.setEnabled(False)
                subMenu.addAction(emptyAction)

        subMenu.aboutToShow.connect(feedActions)
        return mainAction

    def __createActionToMoveCustomPlotToTab(self):
        mainAction = qt.QAction(self)
        mainAction.setText("Move to dedicated tab")
        subMenu = qt.QMenu(self)
        mainAction.setMenu(subMenu)

        def feedActions():
            subMenu.clear()
            for location in self.__customPlots.values():
                if location.parentCustomPlot is not None:
                    continue
                if location.inLive:
                    action = qt.QAction(self)
                    action.setText(f"Move {location.customPlot.plotId()}")
                    action.triggered.connect(
                        functools.partial(self.__moveToTab, location.customPlot)
                    )
                    subMenu.addAction(action)
            if subMenu.isEmpty():
                emptyAction = qt.QAction(self)
                emptyAction.setText("No plot")
                emptyAction.setEnabled(False)
                subMenu.addAction(emptyAction)

        subMenu.aboutToShow.connect(feedActions)
        return mainAction

    def __closeLogWindow(self):
        if self.__flintState is not None:
            self.__flintState.setLogWindow(None)

    def showAboutBox(self):
        """Show the about box of Flint"""
        from .widgets.about import About

        About.about(self, "Flint")

    def setFocusOnLiveScan(self):
        self.__tabs.setCurrentIndex(0)

    def setFocusOnPlot(self, plot: qt.QWidget):
        i = self.__tabs.indexOf(plot)
        if i >= 0:
            self.__tabs.setCurrentIndex(i)

    def __moveToLive(self, customPlot: CustomPlot):
        self.__removeTab(customPlot)
        self.__createLive(customPlot.plotId(), customPlot.name(), customPlot=customPlot)
        plotId = customPlot.plotId()
        assert plotId is not None
        self.__customPlots[plotId] = CustomPlotLocation(customPlot, None, True)

    def __moveToTab(self, customPlot: CustomPlot):
        inliveCustomPlot: InliveCustomPlot = customPlot.parent()
        inliveCustomPlot.setCustomPlot(None)
        inliveCustomPlot.windowClosed.emit()
        inliveCustomPlot.deleteLater()
        self.__createTab(
            customPlot.name(),
            widgetClass=None,
            closeable=True,
            selected=False,
            customPlot=customPlot,
        )
        plotId = customPlot.plotId()
        assert plotId is not None
        self.__customPlots[plotId] = CustomPlotLocation(customPlot, None, False)

    def __createTab(
        self,
        label,
        widgetClass=qt.QWidget,
        closeable=False,
        selected=False,
        customPlot=None,
    ):
        # FIXME: The parent have to be set
        if customPlot is not None:
            widget = customPlot
        else:
            widget = widgetClass()
        index = self.__tabs.addTab(widget, label)
        if selected:
            self.__tabs.setCurrentIndex(index)
        if not closeable:
            closeButton = self.__tabs.tabBar().tabButton(index, qt.QTabBar.RightSide)
            if closeButton is not None:
                closeButton.setVisible(False)
        return widget

    def __findInliveCustomPlot(self, plotId):
        assert self.__flintState is not None
        workspace = self.__flintState.workspace()
        for w in workspace.widgets():
            if isinstance(w, InliveCustomPlot):
                if w.expectedPlotId() == plotId:
                    return w
        return None

    def __createLive(self, plotId, label, customPlot=None):
        assert self.__flintState is not None
        liveWindow = self.__flintState.liveWindow()
        workspace = self.__flintState.workspace()
        w = self.__findInliveCustomPlot(plotId)
        newWidget = w is None

        if w is None:
            w = InliveCustomPlot(parent=liveWindow)
            liveWindow.addDockWidget(qt.Qt.LeftDockWidgetArea, w)
            w.setWindowTitle(label)
            w.setFloating(True)
            w.setExpectedPlotId(plotId)
            w.setObjectName(f"customplot-{plotId}-dock")
            w.setAttribute(qt.Qt.WA_DeleteOnClose)

        if customPlot is not None:
            widget = customPlot
        else:
            widget = CustomPlot(parent=w)
        w.setCustomPlot(widget)
        if newWidget:
            workspace.addWidget(w)

        # It is used, make sure it is visible
        w.setVisible(True)
        return widget

    def __removeTab(self, customPlot: CustomPlot):
        index = self.__tabs.indexOf(customPlot)
        self.__tabs.removeTab(index)

    def createLiveWindow(self):
        window: qt.QMainWindow = self.__createTab("Live scan", LiveWindow)
        window.setObjectName("scan-window")
        return window

    def __blissSessionChanged(self):
        self.__updateTitle()

    def __updateTitle(self):
        assert self.__flintState is not None
        sessionName = self.__flintState.blissSessionName()

        if sessionName is None:
            session = "no session attached"
        elif sessionName == bliss_constants.DEFAULT_SESSION_NAME:
            session = "attached to default"
        else:
            session = "attached to '%s'" % sessionName
        pid = os.getpid()

        title = f"Flint (PID={pid}) - {session}"
        self.setWindowTitle(title)

    def __screenId(self):
        """Try to return a kind of unique name to define the used screens.

        This allows to store different preferences for different environments,
        which is the case when we use SSH.
        """
        app = qt.QApplication.instance()
        desktop = app.desktop()
        size = desktop.size()
        return hash(size.width()) ^ hash(size.height())

    def initFromSettings(self):
        assert self.__flintState is not None
        settings = self.__flintState.settings()
        # resize window to 70% of available screen space, if no settings
        screenId = self.__screenId()
        groups = settings.childGroups()
        mainWindowGroup = "main-window-%s" % screenId
        if mainWindowGroup not in groups:
            mainWindowGroup = "main-window"
        settings.beginGroup(mainWindowGroup)
        pos = qt.QDesktopWidget().availableGeometry(self).size() * 0.7
        w = pos.width()
        h = pos.height()
        self.resize(settings.value("size", qt.QSize(w, h)))
        self.move(settings.value("pos", qt.QPoint(3 * w // 14, 3 * h // 14)))
        settings.endGroup()

    def saveToSettings(self):
        assert self.__flintState is not None
        settings = self.__flintState.settings()
        screenId = self.__screenId()
        settings.beginGroup("main-window-%s" % screenId)
        settings.setValue("size", self.size())
        settings.setValue("pos", self.pos())
        settings.endGroup()

    def createCustomPlot(
        self,
        plotWidget: qt.QWidget,
        name: str,
        plot_id: str,
        selected: bool,
        closeable: bool,
        parentId: str | None,
        parentLayoutParams: Any,
        inLiveWindow: bool | None,
    ):
        """Create a custom plot"""
        if parentId is not None:
            location = self.__customPlots[parentId]
            w = location.customPlot.widget()
            customPlot = w.createCustomPlot(
                plotWidget=plotWidget,
                name=name,
                plot_id=plot_id,
                selected=selected,
                closeable=closeable,
                parentLayoutParams=parentLayoutParams,
            )
            self.__customPlots[plot_id] = CustomPlotLocation(
                customPlot, location.customPlot, False
            )
            return

        if inLiveWindow is None:
            # Automatic tab/live location
            inLiveWindow = self.__findInliveCustomPlot(plot_id) is not None

        if inLiveWindow:
            customPlot = self.__createLive(
                plot_id,
                name,
            )
        else:
            customPlot = self.__createTab(
                name, widgetClass=CustomPlot, selected=selected, closeable=closeable
            )
        customPlot.setPlotId(plot_id)
        customPlot.setName(name)
        customPlot.setPlot(plotWidget)
        self.__customPlots[plot_id] = CustomPlotLocation(customPlot, None, inLiveWindow)
        plotWidget.show()

    def removeCustomPlot(self, plot_id: str):
        """Remove a custom plot by its id

        Raises:
            ValueError: If the plot id does not exist
        """
        location = self.__customPlots.pop(plot_id, None)
        if location is None:
            raise ValueError(f"Plot id '{plot_id}' does not exist")

        if location.customPlot.isPlotContainer():
            for subPlotId in location.customPlot.subPlotIds():
                del self.__customPlots[subPlotId]

        if location.parentCustomPlot is not None:
            parent = location.parentCustomPlot.widget()
            parent.removeCustomPlot(plot_id)
        else:
            self.__removeTab(location.customPlot)

    def customPlot(self, plot_id: str) -> CustomPlot | None:
        """If the plot does not exist, returns None"""
        location = self.__customPlots.get(plot_id)
        if location is None:
            return None
        return location.customPlot

    def countCustomPlots(self):
        return len(self.__customPlots)
