# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

"""
Helper class to manage the state of the model
"""

from __future__ import annotations
from typing import Any

import tracemalloc
import gevent.event
from bliss.config.conductor.client import get_redis_proxy
from bliss.config import get_sessions_list
from bliss.flint.helper import pickle
from bliss.flint import config
from bliss.common import constants as bliss_constants
from bliss.icat.client import icat_client_from_config, is_null_client
from bliss.flint.scan_info_parser.plots import create_plot_model

import logging
from silx.gui import qt

from bliss.flint.model import flint_model
from bliss.flint.model import plot_model
from bliss.flint.model import plot_item_model
from bliss.flint.model import scan_model
from bliss.flint.helper import model_helper
from bliss.flint.helper.style_helper import DefaultStyleStrategy
from bliss.flint.widgets.viewer.viewer_dock import ViewerDock
from bliss.flint.utils import memutils
from bliss.flint.widgets.inlive_custom_plot import InliveCustomPlot
from bliss.flint.widgets import interfaces

from ..helper import scan_info_helper
from . import workspace_manager
from . import monitoring
from . import curve_plot_update

_logger = logging.getLogger(__name__)


class BlissLogServerHandler(logging.handlers.SocketHandler):
    """
    Add 'session' field to emitted records

    The session field allow the log server to dispatch log records to
    the appropriate files
    """

    def __init__(self, host, port):
        logging.handlers.SocketHandler.__init__(self, host, port)
        self.session = None

    def emit(self, record):
        if self.session is None:
            return
        record.session = self.session
        record.application = "flint"
        return super().emit(record)


class MemoryMonitoring(qt.QObject):
    def __init__(self, parent=None):
        qt.QObject.__init__(self, parent=parent)
        self.__timer = qt.QTimer(self)
        self.__timer.setInterval(30000)
        self.__timer.timeout.connect(self.logMoritoring)

    def start(self):
        memutils.patch_count_qobject_instance(scan_model.Scan)
        memutils.patch_count_qobject_instance(scan_model.Data)
        memutils.patch_count_qobject_instance(plot_model.Plot)
        memutils.patch_count_qobject_instance(plot_model.Item)
        tracemalloc.start()
        self.__snapshot: Any | None = tracemalloc.take_snapshot()
        self.__timer.start()

    def stop(self):
        self.__timer.stop()
        tracemalloc.stop()
        self.__snapshot = None

    def flintModel(self) -> flint_model.FlintState:
        return self.parent().flintModel()

    def logMoritoring(self):
        app = qt.QApplication.instance()
        _logger.info("== Memory monitoring ==")
        _logger.info("GUI")
        _logger.info("- Nb widgets: %s", len(app.allWidgets()))
        _logger.info("Scans processed: %s", scan_model.Scan.SUM_INSTANCE)
        _logger.info("- Nb scan ref: %s", scan_model.Scan.ALIVE_INSTANCE)
        _logger.info("- Nb data ref: %s", scan_model.Data.ALIVE_INSTANCE)
        _logger.info("Plot created: %s", plot_model.Plot.SUM_INSTANCE)
        _logger.info("- Nb plot ref: %s", plot_model.Plot.ALIVE_INSTANCE)
        _logger.info("- Nb item ref: %s", plot_model.Item.ALIVE_INSTANCE)

        _logger.info("Tracemalloc")
        snapshot = tracemalloc.take_snapshot()
        assert self.__snapshot is not None
        stats = snapshot.compare_to(self.__snapshot, "lineno")
        for stat in stats[:10]:
            _logger.info("- %s", stat)

        flintModel = self.flintModel()
        scanManager = flintModel.scanManager()
        _logger.info("Scan manager")
        _logger.info("- Cache size: %s", len(scanManager._cache()))


class ManageMainBehaviours(qt.QObject):
    def __init__(self, parent=None):
        super(ManageMainBehaviours, self).__init__(parent=parent)
        self.__flintModel: flint_model.FlintState | None = None
        self.__activeDock = None
        self.__classMapping = {}
        self.__flintStarted = gevent.event.Event()
        self.__flintStarted.clear()
        self.__workspaceManager = workspace_manager.WorkspaceManager(self)
        self.__beaconLogHandler = None
        self.__memMonitoring = MemoryMonitoring(self)
        self.__nextWorkspace = None

    def memoryMonitoring(self) -> MemoryMonitoring:
        """Provide an helper to monitor the memory.

        By default it is not used.

        Can be started by calling:

        .. code-block::

            manager.memoryMonitoring().start()
        """
        return self.__memMonitoring

    def setNextWorkspace(self, workspace: flint_model.Workspace | None):
        """If not None, redirect registration into this workspace"""
        self.__nextWorkspace = workspace

    def setFlintModel(self, flintModel: flint_model.FlintState):
        if self.__flintModel is not None:
            self.__flintModel.workspaceChanged.disconnect(self.__workspaceChanged)
            self.__flintModel.currentScanChanged.disconnect(self.__currentScanChanged)
            self.__flintModel.aliveScanAdded.disconnect(self.__aliveScanDiscovered)
        self.__flintModel = flintModel
        if self.__flintModel is not None:
            self.__flintModel.workspaceChanged.connect(self.__workspaceChanged)
            self.__flintModel.currentScanChanged.connect(self.__currentScanChanged)
            self.__flintModel.aliveScanAdded.connect(self.__aliveScanDiscovered)

    def setIcatClientConfig(self, config: dict | None):
        assert self.__flintModel is not None
        if config is not None:
            client = icat_client_from_config(config)
            if is_null_client(client):
                client = None
        else:
            client = None
        self.__flintModel.setIcatClient(client)

    def flintModel(self) -> flint_model.FlintState:
        flintModel = self.__flintModel
        assert flintModel is not None
        return flintModel

    def initRedis(self):
        redis = get_redis_proxy()
        flintModel = self.flintModel()
        flintModel.setRedisConnection(redis)

    def tryToCreateBeaconLogServer(self, sessionName: str):
        rootLogger = logging.getLogger()
        if self.__beaconLogHandler is not None:
            _logger.info("Beacon logger about to be disconnected")
            rootLogger.removeHandler(self.__beaconLogHandler)
            self.__beaconLogHandler = None

        try:
            from bliss.config.conductor.client import get_log_server_address

            host, port = get_log_server_address()
        except Exception:
            _logger.error("Beacon server is not available", exc_info=True)
            return

        try:
            _logger.debug("About to create Beacon logger handler")
            handler = BlissLogServerHandler(host, port)
            handler.setLevel(logging.INFO)
            handler.session = sessionName
        except Exception:
            _logger.error("Can't create BlissLogServerHandler", exc_info=True)
        else:
            rootLogger.addHandler(handler)
            self.__beaconLogHandler = handler
            _logger.info("Beacon logger connected")

    def updateBlissSessionName(
        self,
        sessionName: str,
    ):
        flintModel = self.flintModel()
        previousSessionName = flintModel.blissSessionName()
        if previousSessionName == sessionName:
            # FIXME: In case of a restart of bliss, is it safe?
            return False

        if sessionName != bliss_constants.DEFAULT_SESSION_NAME:
            try:
                sessions = get_sessions_list()
                if sessionName not in list(sessions):
                    return False
            except RuntimeError as e:
                # In case beacon is not used
                if "Beacon port is missing" not in e.args[0]:
                    raise e

        # Early update of the beacon logger if possible
        beaconLogHandler = self.__beaconLogHandler
        if beaconLogHandler is not None:
            beaconLogHandler.session = sessionName

        redis = flintModel.redisConnection()
        if redis is not None:
            # Update redis with the RPC client
            key = config.get_flint_key()
            current_value = redis.lindex(key, 0).decode()
            value = sessionName + " " + current_value.split()[-1]
            redis.lpush(key, value)
            redis.rpop(key)

        flintModel.setBlissSessionName(sessionName)

        if beaconLogHandler is None:
            self.tryToCreateBeaconLogServer(sessionName)

        workspaceManager = self.workspaceManager()

        if redis is not None:
            try:
                workspaceManager.loadLastWorkspace()
            except ValueError:
                # No last workspace for now
                workspaceManager.loadDefaultWorkspace()
        else:
            _logger.warning("No persistence: No workspace loaded")
            workspaceManager.loadWorkspace("dummy", persistence=False)

        return True

    def __workspaceChanged(
        self,
        previousWorkspace: flint_model.Workspace,
        newWorkspace: flint_model.Workspace,
    ):
        if self.__flintModel is None:
            return
        scan = self.__flintModel.currentScan()
        if scan is not None:
            self.__storeScanIfNeeded(scan)

        if previousWorkspace is not None:
            for widget in previousWorkspace.widgets():
                self.__widgetRemoved(widget)
            previousWorkspace.widgetAdded.disconnect(self.__widgetAdded)
            previousWorkspace.widgetRemoved.disconnect(self.__widgetRemoved)
        if newWorkspace is not None:
            for widget in newWorkspace.widgets():
                self.__widgetAdded(widget)
            newWorkspace.widgetAdded.connect(self.__widgetAdded)
            newWorkspace.widgetRemoved.connect(self.__widgetRemoved)
            for widget in newWorkspace.widgets():
                self.__widgetAdded(widget)
        self.__updateLiveScanTitle()

    def __widgetAdded(self, widget: qt.QWidget):
        _logger.debug("Widget added %s", widget.objectName())
        if hasattr(widget, "setFlintModel"):
            # FIXME: This should be done outside
            widget.setFlintModel(self.__flintModel)
        if hasattr(widget, "widgetActivated"):
            widget.widgetActivated.connect(self.__widgetActivated)
        if hasattr(widget, "windowClosed"):
            widget.windowClosed.connect(self.__dockClosed)

    def __widgetRemoved(self, widget: qt.QWidget):
        _logger.debug("Widget removed %s", widget.objectName())
        if hasattr(widget, "widgetActivated"):
            widget.widgetActivated.disconnect(self.__widgetActivated)
        if hasattr(widget, "windowClosed"):
            widget.windowClosed.disconnect(self.__dockClosed)

    def __widgetActivated(self, widget: qt.QWidget):
        """Callback on widget activation.

        It synchronize the property widget with the active widget.
        """
        if self.__activeDock is widget:
            # Filter double selection
            return
        self.__activeDock = widget

        if hasattr(widget, "createPropertyWidget"):
            flintModel = self.flintModel()
            liveWindow = flintModel.liveWindow()
            if liveWindow is not None:
                propertyWidget = liveWindow.propertyWidget()
                if propertyWidget is not None:
                    propertyWidget.setFocusWidget(widget)

    def __currentScanChanged(
        self, previousScan: scan_model.Scan | None, newScan: scan_model.Scan | None
    ):
        self.__storeScanIfNeeded(newScan)

    def __updateLiveScanTitle(self):
        window = self.flintModel().liveWindow()
        # FIXME: Not nice to reach the tabWidget. It is implementation dependent
        tabWidget: qt.QTabWidget = window.parent().parent()
        liveScanIndex = tabWidget.indexOf(window)
        tabWidget.setCurrentIndex(liveScanIndex)

        flintModel = self.flintModel()
        workspace = flintModel.workspace()
        if workspace is not None:
            workspaceName = workspace.name()
        else:
            workspaceName = None

        title = "Live scan"
        if workspaceName != "" and workspaceName is not None:
            title += f" [{workspaceName}]"

        tabWidget.setTabText(liveScanIndex, title)

    def __storeScanIfNeeded(self, scan: scan_model.Scan | None):
        flintModel = self.__flintModel
        if flintModel is None:
            return None
        workspace = flintModel.workspace()
        if workspace is None:
            return None
        for plot in workspace.plots():
            if isinstance(plot, plot_item_model.CurvePlot):
                if plot.isScansStored():
                    item = plot_item_model.ScanItem(plot, scan)
                    plot.addItem(item)

    def saveBeforeClosing(self):
        assert self.__flintModel is not None
        redis = self.__flintModel.redisConnection()
        if redis is not None:
            flintModel = self.flintModel()
            workspace = flintModel.workspace()
            self.workspaceManager().saveWorkspace(workspace, last=True)
            _logger.info("Workspace saved")
        else:
            _logger.warning("No persistence: Workspace not saved")

    def registerDock(self, widget: qt.QWidget):
        """Register a new dock to the application

        As the dock is added to the workspace. If the current workspace is feed,
        it will trigger `__widgetAdded`.
        """
        assert self.__flintModel is not None
        if self.__nextWorkspace is not None:
            workspace = self.__nextWorkspace
        else:
            workspace = self.__flintModel.workspace()
        workspace.addWidget(widget)

    def __initClassMapping(self):
        if len(self.__classMapping) > 0:
            return
        from bliss.flint.viewers.live_curve.viewer import CurvePlotWidget
        from bliss.flint.viewers.live_mca.viewer import McaPlotWidget
        from bliss.flint.viewers.live_image.viewer import ImagePlotWidget
        from bliss.flint.viewers.live_scatter.viewer import ScatterPlotWidget
        from bliss.flint.viewers.live_onedim.viewer import OneDimDataPlotWidget
        from bliss.flint.widgets.ct_widget import CtWidget
        from bliss.flint.widgets.table_plot import TablePlotWidget

        mapping = [
            (CurvePlotWidget, plot_item_model.CurvePlot),
            (McaPlotWidget, plot_item_model.McaPlot),
            (ImagePlotWidget, plot_item_model.ImagePlot),
            (ScatterPlotWidget, plot_item_model.ScatterPlot),
            (CtWidget, plot_item_model.ScalarPlot),
            (TablePlotWidget, plot_item_model.TablePlot),
            (OneDimDataPlotWidget, plot_item_model.OneDimDataPlot),
        ]

        for k, v in mapping:
            self.__classMapping[k] = v
            self.__classMapping[v] = k

    def getWidgetClassFromPlotClass(
        self, plotClass: type[plot_model.Plot]
    ) -> type[qt.QDockWidget]:
        self.__initClassMapping()
        return self.__classMapping.get(plotClass, None)

    def __getPlotClassFromWidgetClass(
        self, widgetClass: type[qt.QDockWidget]
    ) -> type[plot_model.Plot]:
        self.__initClassMapping()
        return self.__classMapping.get(widgetClass, None)

    def moveWidgetToWorkspace(self, workspace: flint_model.Workspace):
        flintModel = self.flintModel()
        widgets = flintModel.workspace().popWidgets()
        availablePlots = list(workspace.plots())
        for widget in widgets:
            widget.setFlintModel(self.__flintModel)

            compatibleModel = self.__getPlotClassFromWidgetClass(type(widget))
            if compatibleModel is None:
                _logger.error("No compatible class model")
                plotModel = None
            else:
                plots = [p for p in availablePlots if isinstance(p, compatibleModel)]
                if len(plots) > 0:
                    plotModel = plots[0]
                    availablePlots.remove(plotModel)
                else:
                    _logger.error("No compatible model")
                    plotModel = compatibleModel()
                    plotModel.setStyleStrategy(DefaultStyleStrategy(self.__flintModel))

            widget.setPlotModel(plotModel)
            workspace.addWidget(widget)

    def __aliveScanDiscovered(self, scan: scan_model.Scan):
        _logger.info("Scan %s discovered", scan.scanId())
        currentScan = self.flintModel().currentScan()
        parentPlots = []
        scanInfo = scan.scanInfo()
        force_display_in_flint = scanInfo.get("force_display_in_flint", False)
        if currentScan is not None:
            group = scan.group()
            while group:
                ps = create_plot_model(currentScan.scanInfo(), group)
                parentPlots.append(ps)
                group = group.group()

            if not force_display_in_flint and len(parentPlots) == 0:
                if currentScan.state() != scan_model.ScanState.FINISHED:
                    # Update the current scan only if the previous one is finished
                    _logger.info(
                        "Scan %s ignored. Another scan is still running", scan.scanId()
                    )
                    return

        plots = create_plot_model(scanInfo, scan)
        for ps in parentPlots:
            plots = scan_info_helper.removed_same_plots(plots, ps)
        self.updateScanAndPlots(scan, plots)

    def __closePreviousScan(self, scan: scan_model.Scan):
        if isinstance(scan, monitoring.MonitoringScan):
            if scan.isMonitoring():
                scan.stopMonitoring()

    def getCompatiblePlots(
        self, widget: qt.QWidget, availablePlots: list[plot_model.Plot]
    ) -> list[plot_model.Plot]:
        """Returns a list of supported plots for a specific widget.

        This should returns an empty list or a single result.
        """
        compatibleModel = self.__getPlotClassFromWidgetClass(type(widget))
        if compatibleModel is None:
            return []
        plots = [p for p in availablePlots if isinstance(p, compatibleModel)]
        windowTitle = widget.windowTitle()

        if isinstance(widget, interfaces.HasDeviceName):
            deviceName = widget.deviceName()
        else:
            deviceName = None

        if issubclass(compatibleModel, plot_item_model.PLOTS_WITH_DEVICENAME):
            plots = [p for p in plots if p.deviceName() == deviceName]

        # plot with names will use dedicated widgets
        plots = [p for p in plots if p.name() is None or p.name() == windowTitle]
        return plots

    def updateScanAndPlots(self, scan: scan_model.Scan, plots: list[plot_model.Plot]):
        flintModel = self.flintModel()
        previousScan = flintModel.currentScan()
        if previousScan is not None:
            useDefaultPlot = (
                scan.scanInfo().get("display_extra", {}).get("displayed_channels", None)
                is not None
            )
        else:
            useDefaultPlot = True

        if len(plots) > 0:
            defaultPlot = plots[0]
        else:
            defaultPlot = None

        # Set the new scan
        if scan.group() is None:
            flintModel.setCurrentScan(scan)

        # Reuse/create and connect the widgets
        self.updateWidgetsWithPlots(scan, plots, useDefaultPlot, defaultPlot)

    def updateWidgetsWithPlots(
        self,
        scan: scan_model.Scan | None,
        plots,
        useDefaultPlot: bool,
        defaultPlot: scan_model.Plot | None,
    ):
        """Update the widgets with a set of plots"""
        flintModel = self.flintModel()
        workspace = flintModel.workspace()
        availablePlots = list(plots)
        widgets = flintModel.workspace().widgets()
        defaultWidget = None
        usedWidgets = []
        usedPlots = []
        for widget in widgets:
            plots = self.getCompatiblePlots(widget, availablePlots)
            if len(plots) == 0:
                # Do not update the widget (scan and plot stays as previous state)
                continue

            plotModel = plots[0]
            if plotModel is defaultPlot:
                defaultWidget = widget

            # Plot for devices can be reused multiple times
            if (
                isinstance(plotModel, plot_item_model.PLOTS_WITH_DEVICENAME)
                and plotModel.deviceName() is not None
            ):
                usedPlots.append(plotModel)
                # Clone to have independent plots in different widgets
                plotModel = plotModel.clone()
                plotModel.setStyleStrategy(DefaultStyleStrategy(flintModel))
            else:
                availablePlots.remove(plotModel)

            self.updateWidgetWithPlot(widget, scan, plotModel, useDefaultPlot)
            usedWidgets.append(widget)

        availablePlots = [p for p in availablePlots if p not in usedPlots]

        # There is no way in Qt to tabify a widget to a new floating widget
        # Then this code tabify the new widgets on an existing widget
        # FIXME: This behavior is not really convenient
        widgets = workspace.widgets()
        if len(widgets) == 0:
            lastTab = None
        else:
            lastTab = widgets[0]

        # Create widgets for unused plots
        window = flintModel.liveWindow()
        for plotModel in availablePlots:
            if plotModel.styleStrategy() is None:
                plotModel.setStyleStrategy(DefaultStyleStrategy(flintModel))
            widget = self.__createWidgetFromPlot(window, plotModel)
            if widget is None:
                continue
            if plotModel is defaultPlot:
                defaultWidget = widget

            previousScan = widget.scan()
            self.__closePreviousScan(previousScan)
            widget.setScan(scan)
            usedWidgets.append(widget)

            if lastTab is None:
                window.addDockWidget(qt.Qt.RightDockWidgetArea, widget)
                widget.setVisible(True)
            else:
                window.tabifyDockWidget(lastTab, widget)
            lastTab = widget

        if workspace.autoFocusOnNewScan():
            if scan and scan.group() is None:
                self.__updateFocus(defaultWidget, usedWidgets)

    def updateWidgetWithPlot(
        self,
        widget: qt.QWidget,
        scan: scan_model.Scan | None,
        plotModel,
        useDefaultPlot,
    ):
        # FIXME: useDefaultPlot is probably not much useful
        def reusePreviousPlotItems(previousWidgetPlot, plotModel, scan):
            with previousWidgetPlot.transaction():
                # Clean up temporary items
                for item in list(previousWidgetPlot.items()):
                    if isinstance(item, plot_model.NotReused):
                        try:
                            previousWidgetPlot.removeItem(item)
                        except Exception:
                            pass

                # Reuse only available values
                # FIXME: Make it work first for curves, that's the main use case
                if isinstance(previousWidgetPlot, plot_item_model.CurvePlot):
                    model_helper.copyItemsFromChannelNames(
                        previousWidgetPlot, plotModel, scan
                    )

        # FIXME: This looks to became business model
        # This have to be refactored in order to answer to each cases the way
        # people expect to retrieve the selection
        if isinstance(plotModel, plot_item_model.CurvePlot):
            assert scan is not None
            originalPlot = pickle.dumps(plotModel)
            previousPlotModel = widget.plotModel()
            previousScan = widget.scan()
            plotModel = curve_plot_update.resolveCurvePlotUpdate(
                previousScan, previousPlotModel, scan, plotModel
            )
            if plotModel.styleStrategy() is None:
                plotModel.setStyleStrategy(DefaultStyleStrategy(self.__flintModel))
            plotModel.setSerializedOriginalPlot(originalPlot)
            widget.setPlotModel(plotModel)
        elif isinstance(plotModel, plot_item_model.ImagePlot):
            previousPlotModel = widget.plotModel()
            if previousPlotModel is not None:
                model_helper.copyItemsFromRoiNames(previousPlotModel, plotModel)
            if plotModel.styleStrategy() is None:
                plotModel.setStyleStrategy(DefaultStyleStrategy(self.__flintModel))
            widget.setPlotModel(plotModel)
        else:
            assert scan is not None
            previousPlotModel = widget.plotModel()
            previousScan = widget.scan()
            if previousPlotModel is not None:
                equivalentPlots = model_helper.isSame(scan, previousScan)
                editedByUser = previousPlotModel.userEditTime() is not None
            else:
                editedByUser = False
                equivalentPlots = False

            # Try to reuse the previous plot
            if not useDefaultPlot and previousPlotModel is not None:
                reusePreviousPlotItems(previousPlotModel, plotModel, scan=scan)

            # Note: equivalentPlots assume that if the scanned axis are not the same
            # It's a totally different scan, and then it is better to reset anyway
            # the plot

            if editedByUser and equivalentPlots:
                model_helper.removeNotAvailableChannels(
                    previousPlotModel, plotModel, scan
                )
            else:
                if plotModel.styleStrategy() is None:
                    plotModel.setStyleStrategy(DefaultStyleStrategy(self.__flintModel))
                widget.setPlotModel(plotModel)

        previousScan = widget.scan()
        self.__closePreviousScan(previousScan)
        widget.setScan(scan)

    def __updateFocus(self, defaultWidget: qt.QWidget, usedWidgets: list[qt.QWidget]):
        """
        Set the focus on a widget which was used as part of the scan.

        If one of the widget was already shown nothing is updated.
        """
        for widget in usedWidgets:
            if hasattr(widget, "_silxPlot"):
                content = widget._silxPlot().getWidgetHandle()
            elif isinstance(widget, qt.QDockWidget):
                content = widget.widget()
            else:
                content = widget

            flintModel = self.flintModel()
            liveWindow = flintModel.liveWindow()
            if liveWindow is not None:
                propertyWidget = liveWindow.propertyWidget()
                propertyIsEmpty = (
                    propertyWidget is not None and propertyWidget.isEmpty()
                )
            else:
                propertyIsEmpty = False

            reallyVisible = not content.visibleRegion().isEmpty()
            if not propertyIsEmpty and reallyVisible:
                # One of the used widget is already visible
                # Nothing to do
                return

        # Select a widget part of the scan
        widget = defaultWidget
        if widget is None and len(usedWidgets) > 0:
            widget = usedWidgets[0]

        if widget is not None:
            widget.show()
            widget.raise_()
            widget.setFocus(qt.Qt.OtherFocusReason)
            self.__widgetActivated(widget)

    def __dockClosed(self):
        dock = self.sender()

        flintModel = self.flintModel()
        liveWindow = flintModel.liveWindow()

        propertyWidget = liveWindow.propertyWidget(create=False)
        if propertyWidget is not None and propertyWidget.focusWidget() is dock:
            propertyWidget.setFocusWidget(None)

        if isinstance(dock, ViewerDock):
            dock.setPlotModel(None)
        if hasattr(dock, "setFlintModel"):
            dock.setFlintModel(None)

        workspace = flintModel.workspace()
        if not workspace.locked():
            workspace.removeWidget(dock)

        if isinstance(dock, InliveCustomPlot):
            plot = dock.customPlot()
            if plot is not None:
                mainWindow = flintModel.mainWindow()
                mainWindow.removeCustomPlot(plot.plotId())

    def __createWidgetFromPlot(
        self, parent: qt.QWidget, plotModel: plot_model.Plot
    ) -> qt.QDockWidget:
        widgetClass = self.getWidgetClassFromPlotClass(type(plotModel))
        if widgetClass is None:
            _logger.error(
                "No compatible widget for plot model %s. Plot not displayed.",
                type(plotModel),
            )
            return None

        if isinstance(plotModel, plot_item_model.ScalarPlot):
            assert self.__flintModel is not None
            liveWindow = self.__flintModel.liveWindow()
            ctWidget = liveWindow.ctWidget()
            return ctWidget

        flintModel = self.flintModel()
        workspace = flintModel.workspace()
        widget: qt.QDockWidget = widgetClass(parent)
        widget.setPlotModel(plotModel)
        widget.setAttribute(qt.Qt.WA_DeleteOnClose)

        title = plotModel.name()
        if title is None:
            if hasattr(plotModel, "plotTitle"):
                title = plotModel.plotTitle()
            else:
                prefix = str(widgetClass.__name__).replace("PlotWidget", "")
                title = self.__getUnusedTitle(prefix, workspace)

        name = type(plotModel).__name__ + "-" + title
        name = name.replace(":", "--")
        name = name.replace(".", "--")
        name = name.replace(" ", "--")
        name = name.lower() + "-dock"

        widget.setWindowTitle(title)
        if isinstance(plotModel, plot_item_model.PLOTS_WITH_DEVICENAME):
            widget.setDeviceName(plotModel.deviceName())
        widget.setObjectName(name)
        self.registerDock(widget)
        return widget

    def __getUnusedTitle(self, prefix, workspace) -> str:
        for num in range(1, 100):
            title = prefix + str(num)
            for widget in workspace.widgets():
                if widget.windowTitle() == title:
                    break
            else:
                return title
        return title

    def allocateProfileDock(self):
        from bliss.flint.widgets import profile_holder_widget

        flintModel = self.flintModel()
        workspace = flintModel.workspace()

        # Search for an existing profile
        otherProfiles = [
            w
            for w in workspace.widgets()
            if isinstance(w, profile_holder_widget.ProfileHolderWidget)
        ]
        for w in otherProfiles:
            if w.isUsed():
                continue
            w.setVisible(True)
            w.setUsed(True)
            return w

        # Create the profile widget
        window = flintModel.liveWindow()
        widget = profile_holder_widget.ProfileHolderWidget(parent=window)
        widget.setAttribute(qt.Qt.WA_DeleteOnClose)

        # Search for another profile
        lastTab = None if len(otherProfiles) == 0 else otherProfiles[-1]

        def findFreeName(widget, template, others):
            for i in range(1, 100):
                name = template % i
                for w in others:
                    if w.objectName() == name:
                        break
                else:
                    return name
            # That's a dup name
            return template % abs(id(widget))

        widget.setVisible(True)
        name = findFreeName(widget, "profile-%s", otherProfiles)
        widget.setObjectName(name)
        widget.setWindowTitle(name.capitalize().replace("-", " "))
        widget.setUsed(True)

        if lastTab is not None:
            window.tabifyDockWidget(lastTab, widget)
        else:
            window.addDockWidget(qt.Qt.RightDockWidgetArea, widget)
            widget.setFloating(True)

        self.registerDock(widget)
        return widget

    def setFlintStarted(self):
        self.__flintStarted.set()

    def waitFlintStarted(self):
        self.__flintStarted.wait()

    def workspaceManager(self) -> workspace_manager.WorkspaceManager:
        return self.__workspaceManager

    def __findUniqueName(self) -> str:
        """Pick a unique object name for a live widget"""
        assert self.__flintModel is not None
        liveWindow = self.__flintModel.liveWindow()
        for i in range(1000):
            name = f"livewidget-{i}-dock"
            obj = liveWindow.findChild(qt.QWidget, name, qt.Qt.FindDirectChildrenOnly)
            if obj is None:
                return name
        return "livewidget-666.666-dock"

    def cloneLiveWidget(self, liveWidget):
        """
        Clone a live widget.

        Raises:
            TypeError: If the clone is not supported for this widget
        """
        from bliss.flint.widgets.mca_plot import McaPlotWidget
        from bliss.flint.widgets.image_plot import ImagePlotWidget

        flintModel = self.__flintModel
        assert flintModel is not None
        liveWindow = flintModel.liveWindow()
        if isinstance(liveWidget, ImagePlotWidget):
            newWidget = ImagePlotWidget(parent=liveWindow)
            newWidget.setDeviceName(liveWidget.deviceName())
        elif isinstance(liveWidget, McaPlotWidget):
            newWidget = McaPlotWidget(parent=liveWindow)
            newWidget.setDeviceName(liveWidget.deviceName())
        else:
            raise TypeError(
                "Cloning widget '%s' of type %s is not support"
                % (liveWidget.objectName(), type(liveWidget).__name__)
            )

        newWidget.setAttribute(qt.Qt.WA_DeleteOnClose)
        newWidget.setWindowTitle(liveWidget.windowTitle())
        newWidget.setFlintModel(flintModel)
        newWidget.setObjectName(self.__findUniqueName())
        newWidget.setVisible(True)
        scanModel = liveWidget.scan()
        if scanModel:
            newWidget.setScan(scanModel)
        plotModel = liveWidget.plotModel()
        if plotModel:
            # Clone to have independent plots in different widgets
            newPlotModel = plotModel.clone()
            newPlotModel.setStyleStrategy(DefaultStyleStrategy(flintModel))
            newWidget.setPlotModel(newPlotModel)
        self.registerDock(newWidget)
        liveWindow.tabifyDockWidget(liveWidget, newWidget)
        return newWidget
