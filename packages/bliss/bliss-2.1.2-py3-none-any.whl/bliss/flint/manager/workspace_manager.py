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
from typing import NamedTuple

import functools

import logging
from silx.gui import qt
from silx.gui import icons
from silx.gui.qt import inspect

from bliss.common import constants as bliss_constants
from bliss.config.settings import HashObjSetting
from . import manager
from ..model import flint_model
from bliss.flint import config
from bliss.flint.widgets.viewer.viewer_dock import ViewerDock


_logger = logging.getLogger(__name__)


class _WidgetDescriptionCompatibility(NamedTuple):
    """Allow to read the previous way to store the object.

    Was only stored this way before the restart, before 2020-02-26

    Could be remove in few months.
    """

    objectName: str
    windowTitle: str
    className: object
    modelId: int
    config: object


class WidgetDescription:
    def __init__(self):
        self.objectName = None
        self.windowTitle = None
        self.className = None
        # FIXME: We should store the full model, instead of a modelId
        #        (pickle can deal with)
        self.modelId = None
        self.config = None
        self.isVisible = None

    def __getstate__(self):
        """Inherit the serialization to make sure the object can grow up in the
        future"""
        state: dict[str, object] = {}
        state["objectName"] = self.objectName
        state["windowTitle"] = self.windowTitle
        state["className"] = self.className
        state["modelId"] = self.modelId
        state["config"] = self.config
        state["isVisible"] = self.isVisible
        return state

    def __setstate__(self, state):
        """Inherit the serialization to make sure the object can grow up in the
        future"""
        self.objectName = state.pop("objectName")
        self.windowTitle = state.pop("windowTitle")
        self.className = state.pop("className")
        self.modelId = state.pop("modelId")
        self.config = state.pop("config", None)
        self.isVisible = state.pop("isVisible", None)


class WorkspaceData(dict):
    def setWorkspace(
        self, workspace: flint_model.Workspace, includePlots: bool = False
    ):
        plots = {}
        if includePlots:
            for plot in workspace.plots():
                plots[id(plot)] = plot

        widgetDescriptions = []
        for widget in workspace.widgets():

            if not inspect.isValid(widget):
                continue

            if includePlots and isinstance(widget, ViewerDock):
                model = widget.plotModel()
                if model is not None:
                    modelId = id(model)
                else:
                    modelId = None
            else:
                modelId = None

            widgetDescription = WidgetDescription()
            widgetDescription.objectName = widget.objectName()
            widgetDescription.windowTitle = widget.windowTitle()
            widgetDescription.className = widget.__class__
            widgetDescription.modelId = modelId
            # The visibility of the floating windows are not restored
            # So we have to do it on our own
            widgetDescription.isVisible = widget.isVisibleTo(widget.parent())
            if hasattr(widget, "configuration"):
                config = widget.configuration()
                widgetDescription.config = config
            widgetDescriptions.append(widgetDescription)

        self["plots"] = plots
        self["widgets"] = widgetDescriptions
        self["version"] = 2
        self["auto-focus-on-new-scan"] = workspace.autoFocusOnNewScan()

    def widgetDescriptions(self) -> list[WidgetDescription]:
        return self["widgets"]

    def setLiveWindow(self, window: qt.QWidget):
        config = window.configuration()
        self["layout"] = window.saveState()
        self["window_config"] = config

    def initLiveWindow(self, window: qt.QWidget, workspace: flint_model.Workspace):

        # FIXME ugly hack to reach new widgets created by live window
        model = window.flintModel()
        currentWorkspace = model.workspace()
        if currentWorkspace is not None:
            previousWidgets = set(currentWorkspace.widgets())
        else:
            previousWidgets = set()

        version = self.get("version", 1)
        _logger.debug("WorkspaceData version %s", version)

        window.updateFromWorkspace(workspace)
        if "window_config" in self:
            config = self["window_config"]
            window.setConfiguration(config)

        if version == 1:
            # The first workspace storage was not saving property and status
            # widget by default. It was used from BLISS 1.0 to BLISS 1.6 included.
            # Workspace saved with BLISS 1.7 and later  to not relay on it.
            # FIXME: This could be removed in few version
            window.propertyWidget(create=True)
            window.scanStatusWidget(create=True)

        # FIXME ugly hack to reach new widgets created by live window
        if currentWorkspace is not None:
            currentWidgets = set(currentWorkspace.widgets())
        else:
            currentWidgets = set()

        newWidgets = currentWidgets - previousWidgets
        for widget in newWidgets:
            workspace.addWidget(widget)

        layout = self.get("layout")
        if layout is not None:
            _logger.debug("Restore layout state")
            window.restoreState(layout)

        # NOTE: window.restoreState does not restore properly visibility of floating
        # docks. We have to restore it manually
        widgetDescriptions = self["widgets"]
        descriptions = {}
        for data in widgetDescriptions:
            if isinstance(data, tuple):
                data = _WidgetDescriptionCompatibility(*data, None)
            descriptions[data.objectName] = data
        for widget in workspace.widgets():
            data = descriptions.get(widget.objectName())
            if data is not None:
                if data.isVisible is None:
                    # Compatibility with save files < BLISS 1.11
                    if widget.isFloating():
                        widget.setVisible(True)
                else:
                    widget.setVisible(data.isVisible)

    def feedWorkspace(
        self,
        workspace: flint_model.Workspace,
        remainingWidgets: list[qt.QWidget],
        parent: qt.QMainWindow,
    ):
        plots: dict = self["plots"]
        widgetDescriptions = self["widgets"]
        workspace.setAutoFocusOnNewScan(self.get("auto-focus-on-new-scan", True))

        descriptions = []
        for data in widgetDescriptions:
            if isinstance(data, tuple):
                data = _WidgetDescriptionCompatibility(*data, None)
            descriptions.append(data)

        objectNames = set([d.objectName for d in descriptions])

        existingWidgets = {w.objectName(): w for w in remainingWidgets}

        def pickUnusedObjectName():
            for i in range(100):
                name = "dock-%01d" % i
                if name not in objectNames:
                    objectNames.add(name)
                    return name
            return "dock-666-666"

        for data in descriptions:

            if data.objectName is None or data.objectName == "":
                _logger.warning(
                    "Widget %s from workspace configuration have no name. Generate one.",
                    data.className,
                )
                objectName = pickUnusedObjectName()
            else:
                objectName = data.objectName

            if objectName in existingWidgets:
                widget = existingWidgets[objectName]
                if parent is not None:
                    widget.setParent(parent)
            else:
                widget = data.className(parent)
                widget.setVisible(True)
            widget.setObjectName(objectName)
            widget.setWindowTitle(data.windowTitle)
            if hasattr(widget, "setConfiguration") and data.config is not None:
                widget.setConfiguration(data.config)

            # Looks needed to retrieve the right layout with restoreSate
            if parent is not None:
                parent.addDockWidget(qt.Qt.LeftDockWidgetArea, widget)
            if objectName not in existingWidgets:
                if data.modelId is not None:
                    plot = plots[data.modelId]
                    widget.setPlotModel(plot)
            workspace.addWidget(widget)


class WorkspaceManager(qt.QObject):
    """
    The WorkspaceManager provide an API to manage the workspaces.

    It provides 3 different scopes:

    - current scope: the current workspace
    - flint scope: The state of the workspaces as it was edited during this Flint
        execution
    - persistent scope: The state of the workspaces with persistent storage in
        Redis

    The name of the current workspace is saved in Redis inside each session
    in order to restart Flint with the last used workspace.

    A modified workspace is automatically stored in the flint scope, and can be
    reused while Flint is not closed.

    An explicit `save` action have to be triggered to save the current workspace
    in the persistent scope. It is stored in Redis independently of the current
    session: From any session, any workspace can be loaded and saved.

    A `reload` action is provided in order to reload the previous stored state
    from the persistent  scope of the current workspace. This is to prevent user
    mistakes: something done wrong can be reverted.
    """

    DEFAULT = "base"

    def __init__(self, parent=None):
        qt.QObject.__init__(self, parent=parent)
        self.__session: dict[str, WorkspaceData] = {}
        """Save workspace during flint life time"""

    def mainManager(self) -> manager.ManageMainBehaviours:
        return self.parent()

    def connectManagerActions(self, parent: qt.QObject, menu: qt.QMenu):
        """Create actions to interact with the manager"""
        menu.aboutToShow.connect(self.__feedWorkspaceMenu)

    def __feedWorkspaceMenu(self):
        menu: qt.QMenu = self.sender()
        menu.clear()

        flintModel = self.mainManager().flintModel()
        sessionName = flintModel.blissSessionName()
        if sessionName is None:
            action = qt.QAction(menu)
            action.setEnabled(False)
            action.setText("No BLISS session attached")
            menu.addAction(action)
            return

        workspace = flintModel.workspace()
        currentWorkspace = workspace.name()

        try:
            names = self.__getAvailableNames()
        except IOError:
            action = qt.QAction(menu)
            action.setEnabled(False)
            action.setText("Error while loading names")
            menu.addAction(action)
            names = []

        names = list(sorted(names))

        menu.addSection("Active workspace")
        group = qt.QActionGroup(menu)
        if len(names) > 0:
            for name in names:
                action = qt.QAction(menu)
                action.setText(f"{name}")
                action.setCheckable(True)
                if name == currentWorkspace:
                    action.setToolTip("The current workspace")
                    action.setChecked(True)
                    action.setEnabled(False)
                else:
                    action.triggered.connect(
                        functools.partial(self.switchToWorkspace, name)
                    )
                    action.setToolTip("Switch to '%s' workspace" % name)
                menu.addAction(action)
                group.addAction(action)
        else:
            action = qt.QAction(menu)
            action.setEnabled(False)
            action.setText("No workspace")
            menu.addAction(action)

        menu.addSeparator()

        action = qt.QAction(menu)
        action.setText("Reload")
        action.setToolTip("Reload the last saved state of the active workspace")
        action.triggered.connect(self.reloadCurrentWorkspace)
        iconName = qt.QStyle.SP_FileDialogBack
        icon = menu.style().standardIcon(iconName)
        action.setIcon(icon)
        menu.addAction(action)

        action = qt.QAction(menu)
        action.setText("Save")
        action.setToolTip("Save the active workspace")
        action.triggered.connect(self.saveCurrentWorkspace)
        menu.addAction(action)

        action = qt.QAction(menu)
        action.setText("Save as...")
        action.setToolTip("Save the active workspace into another name")
        action.triggered.connect(self.saveCurrentWorkspaceAs)
        menu.addAction(action)

        action = qt.QAction(menu)
        action.setText("Rename as...")
        action.setToolTip("Rename the active workspace to another name")
        action.triggered.connect(self.renameCurrentWorkspaceAs)
        menu.addAction(action)

        action = qt.QAction(menu)
        action.setText("Remove")
        action.setToolTip(
            "Remove the active workspace (after switching to the default workspace)"
        )
        action.triggered.connect(
            functools.partial(self.removeWorkspace, currentWorkspace)
        )
        icon = icons.getQIcon("flint:icons/remove-item")
        action.setIcon(icon)
        menu.addAction(action)

    def __saveAvailableNames(self, names: list[str]):
        settings = self.__getSettings()
        settings["@names"] = names

    def __getAvailableNames(self) -> list[str]:
        settings = self.__getSettings()
        names = settings.get("@names", [])
        return names

    def renameCurrentWorkspaceAs(self):
        """
        Rename the current workspace and stay in this workspace.
        """
        flintModel = self.mainManager().flintModel()
        workspace = flintModel.workspace()
        workspace.name()

        name, ok = qt.QInputDialog.getText(
            flintModel.liveWindow(),
            "Rename as",
            "New workspace name:",
            text=workspace.name(),
        )
        if not ok:
            return
        if name == workspace.name():
            return
        self.renameWorkspaceAs(workspace, name)

    def saveCurrentWorkspaceAs(self):
        """
        Save the current workspace as another name and switch to this new
        workspace.
        """
        flintModel = self.mainManager().flintModel()
        workspace = flintModel.workspace()
        workspace.name()

        name, ok = qt.QInputDialog.getText(
            flintModel.liveWindow(),
            "Save as",
            "New workspace name:",
            text=workspace.name(),
        )
        if not ok:
            return
        if name == workspace.name():
            return
        self.saveWorkspaceAs(workspace, name)

    def __saveCurrentWorkspaceName(self, name: str):
        settings = self.__getSessionSettings()
        settings["@lastname"] = name

    def __getLastWorkspaceName(self):
        settings = self.__getSessionSettings()
        name = settings.get("@lastname", None)
        if name == "":
            return None
        return name

    def loadLastWorkspace(self):
        """
        Load the last used workspace.

        Raises:
            ValueError: If there was no previous workspace defined
        """
        name = self.__getLastWorkspaceName()
        if name is None:
            raise ValueError("No previous workspace defined")
        self.loadWorkspace(name)

    def loadDefaultWorkspace(self):
        """
        Load the default workspace according to the current session configuration.
        """
        flintModel = self.mainManager().flintModel()
        sessionName = flintModel.blissSessionName()
        if sessionName in [None, "", bliss_constants.DEFAULT_SESSION_NAME]:
            workspaceName = self.DEFAULT
        else:
            workspaceName = self.DEFAULT + "_" + sessionName
        self.loadWorkspace(workspaceName)

    def __closeWorkspace(self):
        flintModel = self.mainManager().flintModel()
        workspace = flintModel.workspace()
        if workspace is None:
            return
        widgets = workspace.popWidgets()
        for w in widgets:
            # Make sure we can create object name without collision
            if isinstance(w, ViewerDock):
                w.setPlotModel(None)
                w.setScan(None)
            if hasattr(w, "setFlintModel"):
                w.setFlintModel(None)
            w.setObjectName(None)
            if hasattr(w, "windowClosed"):
                w.windowClosed.emit()
            w.deleteLater()

    def __closeUnusedWidget(self, data: WorkspaceData):
        flintModel = self.mainManager().flintModel()
        workspace = flintModel.workspace()
        if workspace is None:
            return
        widgets = workspace.popWidgets()
        names = set([desc.objectName for desc in data.widgetDescriptions()])
        for w in list(widgets):
            if w.objectName() in names:
                continue
            # Make sure we can create object name without collision
            widgets.remove(w)
            if isinstance(w, ViewerDock):
                w.setPlotModel(None)
                w.setScan(None)
            if hasattr(w, "setFlintModel"):
                w.setFlintModel(None)
            w.setObjectName(None)
            if hasattr(w, "windowClosed"):
                w.windowClosed.emit()
            w.deleteLater()
        return widgets

    def __getSessionSettings(self) -> HashObjSetting:
        """Returns the settings storing workspaces in this bliss session."""
        flintModel = self.mainManager().flintModel()
        redis = flintModel.redisConnection()
        sessionName = flintModel.blissSessionName()
        if sessionName is None:
            raise ValueError("No session defined")

        key = config.get_workspace_key(sessionName)
        setting = HashObjSetting(key, connection=redis)

        return setting

    def __getSettings(self) -> HashObjSetting:
        """Returns the settings storing workspaces in this bliss session."""
        flintModel = self.mainManager().flintModel()
        redis = flintModel.redisConnection()

        key = config.get_workspace_key(None)
        setting = HashObjSetting(key, connection=redis)

        if len(setting) == 0:
            # FIXME: Move settings from BLISS <= 1.7dev to BLISS 1.7
            sessionName = flintModel.blissSessionName()
            if sessionName is None:
                raise ValueError("No session defined")

            key = config.get_workspace_key(sessionName)
            oldSetting = HashObjSetting(key, connection=redis)
            setting.update(oldSetting.get_all())

        return setting

    def reloadCurrentWorkspace(self):
        """Reload the current workspace from the persistent storage"""
        flintModel = self.mainManager().flintModel()
        workspace = flintModel.workspace()
        name = workspace.name()
        self.loadWorkspace(name, flintScope=False)

    def isWorkspace(self, name: str) -> bool:
        """Returns true if the name is a workspace name"""
        if name in self.__session:
            return True
        settings = self.__getSettings()
        return name in settings

    def loadWorkspace(
        self, name: str, flintScope: bool = True, persistence: bool = True
    ):
        """Load a workspace name and switch to it.

        The current workspace is lost.
        """
        _logger.debug("Load workspace '%s'", name)
        manager = self.mainManager()
        flintModel = manager.flintModel()

        data = None

        if flintScope:
            workspace = flintModel.workspace()
            if workspace is not None and name == workspace.name():
                # It's already the current workspace
                _logger.debug("Workspace already loaded. Skipped.")
                return False
            if name in self.__session:
                data = self.__session[name]
        else:
            if name in self.__session:
                del self.__session[name]

        newWorkspace = flint_model.Workspace()
        newWorkspace.setName(name)
        manager.setNextWorkspace(newWorkspace)
        liveWindow = flintModel.liveWindow()
        scan = flintModel.currentScan()

        if data is None and persistence:
            try:
                settings = self.__getSettings()
                data = settings.get(newWorkspace.name(), None)
            except Exception:
                _logger.error(
                    "Problem to load workspace data. Information will be lost.",
                    exc_info=True,
                )

        if data is not None and not isinstance(data, WorkspaceData):
            _logger.error(
                "Problem to load workspace data. Unexpected type %s. Information will be lost.",
                type(data),
                exc_info=True,
            )
            data = None

        # Make sure there is no changes during the switch
        workspace = flintModel.workspace()
        workspace.setLocked(True)

        if data is None:
            # It have to be done before creating widgets
            self.__closeWorkspace()
            liveWindow.feedDefaultWorkspace(flintModel, newWorkspace)
            liveWindow.updateFromWorkspace(newWorkspace)
        else:
            # It have to be done before creating widgets
            remainingWidgets = self.__closeUnusedWidget(data)
            flintModel = self.mainManager().flintModel()
            data.feedWorkspace(
                newWorkspace, remainingWidgets=remainingWidgets, parent=liveWindow
            )

            # FIXME: Could be done in the manager callback event
            for plot in newWorkspace.plots():
                # FIXME: That's a hack while there is no better solution
                style = plot.styleStrategy()
                if hasattr(style, "setFlintModel"):
                    style.setFlintModel(flintModel)

            # FIXME: Could be done in the manager callback event
            for widget in newWorkspace.widgets():
                if isinstance(widget, ViewerDock):
                    widget.setScan(scan)

            data.initLiveWindow(liveWindow, newWorkspace)

        sessionName = flintModel.blissSessionName()
        if persistence:
            if sessionName is not None:
                self.__saveCurrentWorkspaceName(newWorkspace.name())

        manager.setNextWorkspace(None)
        flintModel.setWorkspace(newWorkspace)
        _logger.debug(
            "Available widgets: %s", [w.objectName() for w in newWorkspace.widgets()]
        )
        _logger.debug("Load workspace '%s': done", name)

    def removeWorkspace(self, name: str):
        """Remove a workspace from all the storage.

        If it's the default workspace, the action is cancelled.

        If the current workspace is the one to remove, switch first to the
        default workspace and then remove the requested workspace.
        """
        if name == self.DEFAULT or name.startswith(self.DEFAULT + "_"):
            _logger.warning("The base workspace can't be removed", self.DEFAULT)
            return

        flintModel = self.mainManager().flintModel()
        workspace = flintModel.workspace()
        currentWorkspace = workspace.name()
        if name == currentWorkspace:
            _logger.info("Switch to default workspace before removing '%s'", name)
            self.loadDefaultWorkspace()

        names = self.__getAvailableNames()
        if name in names:
            names.remove(name)
        self.__saveAvailableNames(names)

        if name in self.__session:
            del self.__session[name]

        key = "flint.workspace.%s" % name
        flintModel = self.mainManager().flintModel()
        redis = flintModel.redisConnection()
        redis.delete(key)

    def switchToWorkspace(self, name: str):
        """Save the current workspace the load the requested one"""
        flintModel = self.mainManager().flintModel()
        workspace = flintModel.workspace()
        self.saveWorkspace(workspace, flintScope=True)
        self.loadWorkspace(name)

    def saveCurrentWorkspace(self) -> bool:
        """Save the current workspace to the persistent storage

        Returns:
            True if the action is a success
        """
        flintModel = self.mainManager().flintModel()
        workspace = flintModel.workspace()
        return self.saveWorkspace(workspace, flintScope=False)

    def saveWorkspace(
        self, workspace: flint_model.Workspace, last=False, flintScope: bool = False
    ) -> bool:
        """Save this workspace

        Arguments:
            last: If true, save that this workspace was used
            flintScope: If true, the workspace is save at flint scope, else
                        the flint scope is cleaned up and the workspace is
                        saved in Redis
        Returns:
            True if the action is a success
        """
        flintModel = self.mainManager().flintModel()
        sessionName = flintModel.blissSessionName()
        if sessionName is None:
            _logger.error("No BLISS session. Save of workspace aborted")
            return False

        name = workspace.name()
        names = self.__getAvailableNames()
        if name not in names:
            names.append(name)
            self.__saveAvailableNames(names)

        workspace = flintModel.workspace()

        redis = flintModel.redisConnection()
        if redis is None:
            _logger.error("No Redis connection. Save of workspace aborted")
            return False

        data = WorkspaceData()
        window = flintModel.liveWindow()
        data.setWorkspace(workspace)

        data.setLiveWindow(window)

        if flintScope:
            self.__session[name] = data
        else:
            if name in self.__session:
                del self.__session[name]
            settings = self.__getSettings()
            try:
                settings[name] = data
            except Exception:
                _logger.error("Error while serializing the settings", exc_info=True)
                return False

        if last:
            self.__saveCurrentWorkspaceName(name)
        return True

    def saveWorkspaceAs(self, workspace: flint_model.Workspace, name: str) -> bool:
        """Save a workspace as a new name

        Returns:
            True if the action is a success
        """
        previous = workspace.name()
        if previous == name:
            return False
        workspace.setName(name)
        result = self.saveWorkspace(workspace, last=True)
        flintModel = self.mainManager().flintModel()
        flintModel.setWorkspace(workspace)
        return result

    def renameWorkspaceAs(self, workspace: flint_model.Workspace, name: str):
        """Rename a workspace as a new name"""
        previous = workspace.name()
        if previous == name:
            return
        workspace.setName(name)
        self.removeWorkspace(previous)
        self.saveWorkspace(workspace, last=True)
        flintModel = self.mainManager().flintModel()
        flintModel.setWorkspace(workspace)
