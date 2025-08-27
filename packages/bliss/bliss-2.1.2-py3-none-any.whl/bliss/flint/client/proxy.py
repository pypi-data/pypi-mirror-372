# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

"""
Provide helper to create a Flint proxy.
"""

from __future__ import annotations
import typing

import os
import sys
import subprocess
import logging
import psutil
import gevent
import signal
import enum

import bliss
from bliss.comm import rpc

from bliss import current_session
from bliss.config.conductor.client import get_default_connection
from bliss.scanning.scan_display import ScanDisplay
from bliss.flint import config
from bliss.flint.client.base_plot import FlintWasDisconnected
from . import base_plot
from . import plots

if typing.TYPE_CHECKING:
    from bliss.controllers.lima.lima_base import Lima
    from bliss.controllers.mca.base import BaseMCA
    from bliss.controllers.mosca.base import McaController

try:
    from bliss.flint.patches import poll_patch
except ImportError:
    poll_patch = None


FLINT_LOGGER = logging.getLogger("flint")
FLINT_OUTPUT_LOGGER = logging.getLogger("flint.output")
# Disable the flint output
FLINT_OUTPUT_LOGGER.setLevel(logging.INFO)
FLINT_OUTPUT_LOGGER.disabled = True

FLINT = None


class _FlintState(enum.Enum):
    NO_PROXY = 0
    IS_AVAILABLE = 1
    IS_STUCKED = 2


class FlintClient:
    """
    Proxy on a optional Flint application.

    It provides API to create/connect/disconnect/ a Flint application.

    Arguments:
        process: A process object from (psutil) or an int
    """

    def __init__(self, process=None):
        self._pid: int | None = None
        self._proxy = None
        self._process = None
        self._shortcuts = set()
        self._on_new_pid = None

    @property
    def pid(self) -> int | None:
        """Returns the PID of the Flint application connected by this proxy, else None"""
        return self._pid

    def __getattr__(self, name):
        if self._proxy is None:
            raise AttributeError(
                "No Flint proxy created. Access to '%s' ignored." % name
            )
        attr = getattr(self._proxy, name)
        # Shortcut the lookup attribute
        self._shortcuts.add(name)
        setattr(self, name, attr)
        return attr

    def _proxy_get_flint_state(self, timeout=2) -> _FlintState:
        """Returns one of the state describing the life cycle of Flint"""
        pid = self._pid
        if pid is None:
            return _FlintState.NO_PROXY
        if not psutil.pid_exists(pid):
            return _FlintState.NO_PROXY
        proxy = self._proxy
        if proxy is None:
            return _FlintState.NO_PROXY
        try:
            with gevent.Timeout(seconds=timeout):
                proxy.get_bliss_version()
        except gevent.Timeout:
            return _FlintState.IS_STUCKED
        return _FlintState.IS_AVAILABLE

    def _proxy_create_flint(self) -> psutil.Process:
        """Start the flint application in a subprocess.

        Returns:
            The process object"""
        if sys.platform.startswith("linux") and not os.environ.get("DISPLAY", ""):
            FLINT_LOGGER.error(
                "DISPLAY environment variable have to be defined to launch Flint"
            )
            raise RuntimeError("DISPLAY environment variable is not defined")

        FLINT_LOGGER.warning("Flint starting...")
        env = dict(os.environ)
        env["BEACON_HOST"] = _get_beacon_address()
        # Do not use all the cores anyway used algorithms request it
        # NOTE:  Mitigate problem occurred with silx colormap computation
        env["OMP_NUM_THREADS"] = "4"
        if poll_patch is not None:
            poll_patch.set_ld_preload(env)

        session_name = current_session.name
        scan_display = ScanDisplay()

        python_bin = scan_display.flint_python_bin
        if python_bin == "":
            python_bin = sys.executable
        else:
            FLINT_LOGGER.warning(
                "Flint is executed with a custom python binary: %s", python_bin
            )

        args = [python_bin, "-m", "bliss.flint"]
        args.extend(["-s", session_name])
        args.extend(scan_display.extra_args)
        process = subprocess.Popen(
            args,
            env=env,
            start_new_session=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return process

    def _proxy_create_flint_proxy(self, process):
        """Attach a flint process, make a RPC proxy and bind Flint to the current
        session and return the FLINT proxy.
        """

        def raise_if_dead(process):
            if hasattr(process, "returncode"):
                if process.returncode is not None:
                    raise RuntimeError("Processus terminaded")

        pid = process.pid
        FLINT_LOGGER.debug("Attach flint PID: %d...", pid)
        beacon = get_default_connection()
        redis = beacon.get_redis_proxy()
        try:
            session_name = current_session.name
        except AttributeError:
            raise RuntimeError("No current session, cannot attach flint")

        # Current URL
        key = config.get_flint_key(pid)
        value = None
        for _ in range(3):
            raise_if_dead(process)
            value = redis.brpoplpush(key, key, timeout=5)

            if value is not None:
                break
        if value is None:
            raise ValueError(
                f"flint: cannot retrieve Flint RPC server address from pid '{pid}`"
            )
        url = value.decode().split()[-1]

        # Return flint proxy
        raise_if_dead(process)
        FLINT_LOGGER.debug("Creating flint proxy...")
        proxy = rpc.Client(url, timeout=3)

        # Check the Flint API version
        remote_flint_api_version = proxy.get_flint_api_version()
        if remote_flint_api_version != config.FLINT_API_VERSION:
            FLINT_LOGGER.debug("Flint used API: {config.FLINT_API_VERSION}")
            FLINT_LOGGER.debug("Flint provided API: {remote_flint_api_version}")
            # Display the BLISS version
            remote_bliss_version = proxy.get_bliss_version()
            FLINT_LOGGER.warning(
                "Bliss and Flint API does not match (bliss version %s, flint version: %s).",
                bliss.release.version,
                remote_bliss_version,
            )
            FLINT_LOGGER.warning("You should restart Flint.")

        proxy.set_session(session_name)
        self._set_new_proxy(proxy, process.pid)

        scan_saving = current_session.scan_saving
        if scan_saving is not None:
            if scan_saving.data_policy == "ESRF":
                try:
                    cfg = scan_saving.icat_client_config
                except Exception:
                    FLINT_LOGGER.error(
                        "Error while getting ICAT client information", exc_info=True
                    )
                    cfg = None
                if cfg is not None:
                    proxy.set_icat_client_config(cfg)
                else:
                    FLINT_LOGGER.warning("Elogbook for Flint is not available")

    def _proxy_close_proxy(self, timeout=5):
        proxy = self._proxy
        if proxy is not None:
            for i in range(4):
                if i == 0:
                    pid = self._pid
                    FLINT_LOGGER.debug("Close Flint %s", pid)
                    try:
                        with gevent.Timeout(seconds=timeout):
                            proxy.close_application()
                    except gevent.Timeout:
                        pass
                    self._wait_for_closed(pid, timeout=2)
                    if not psutil.pid_exists(pid):
                        # Already dead
                        break
                elif i == 1:
                    pid = self._pid
                    FLINT_LOGGER.debug("Request trace info from %s", pid)
                    assert pid is not None
                    if not psutil.pid_exists(pid):
                        # Already dead
                        break
                    os.kill(pid, signal.SIGUSR1)
                    gevent.sleep(2)
                elif i == 2:
                    pid = self._pid
                    FLINT_LOGGER.debug("Kill flint %s", pid)
                    assert pid is not None
                    if not psutil.pid_exists(pid):
                        # Already dead
                        break
                    os.kill(pid, signal.SIGTERM)
                    self._wait_for_closed(pid, timeout=2)
                    if not psutil.pid_exists(pid):
                        break
                elif i == 3:
                    pid = self._pid
                    FLINT_LOGGER.debug("Force kill flint %s", pid)
                    assert pid is not None
                    if not psutil.pid_exists(pid):
                        # Already dead
                        break
                    os.kill(pid, signal.SIGABRT)

        self._proxy_cleanup()
        # FIXME: here we should clean up redis keys

    def _proxy_cleanup(self):
        """Disconnect Flint if there is such connection.

        Flint application stay untouched.
        """
        for s in self._shortcuts:
            delattr(self, s)
        self._shortcuts = set()
        if self._proxy is not None:
            try:
                self._proxy.close()
            except Exception:
                pass
        self._proxy = None
        self._pid = None
        self._process = None

    def _set_new_proxy(self, proxy, pid):
        # Make sure no cached functions are used
        for s in self._shortcuts:
            delattr(self, s)
        self._shortcuts = set()
        # Setup the new proxy
        self._proxy = proxy
        self._pid = pid
        if self._on_new_pid is not None:
            self._on_new_pid(pid)

    def _proxy_attach_pid(self, pid):
        """Attach the proxy to another Flint PID.

        If a Flint application is already connected, it will stay untouched,
        but will not be connected anymore, anyway the new PID exists or is
        responsive.
        """
        self._proxy_cleanup()
        process = psutil.Process(pid)
        self._proxy_create_flint_proxy(process)

    @staticmethod
    def _wait_for_closed(pid, timeout=None):
        """Wait for the PID to be closed"""
        try:
            p = psutil.Process(pid)
        except psutil.NoSuchProcess:
            # process already closed
            return

        try:
            with gevent.Timeout(timeout):
                # gevent timeout have to be used here
                # See https://github.com/gevent/gevent/issues/622
                p.wait(timeout=None)
        except gevent.Timeout:
            pass

    def close(self, timeout=None):
        """Close Flint and clean up this proxy."""
        if self._proxy is None:
            raise RuntimeError("No proxy connected")
        with gevent.Timeout(timeout):
            self._proxy.close_application()
        self._wait_for_closed(self._pid, timeout=4.0)
        self._proxy_cleanup()

    def focus(self):
        """Set the focus to the Flint window."""
        if self._proxy is None:
            raise RuntimeError("No proxy connected")
        self._proxy.set_window_focus()

    def terminate(self):
        """Interrupt Flint with SIGTERM and clean up this proxy."""
        if self._pid is None:
            raise RuntimeError("No proxy connected")
        os.kill(self._pid, signal.SIGTERM)
        self._wait_for_closed(self._pid, timeout=4.0)
        self._proxy_cleanup()

    def kill(self):
        """Interrupt Flint with SIGKILL and clean up this proxy."""
        if self._pid is None:
            raise RuntimeError("No proxy connected")
        os.kill(self._pid, signal.SIGKILL)
        self._wait_for_closed(self._pid, timeout=4.0)
        self._proxy_cleanup()

    def kill9(self):
        """Deprecated. Provided for compatibility only"""
        self.kill()

    def _proxy_start_flint(self):
        """
        Start a new Flint application and connect a proxy to it.
        """
        process = self._proxy_create_flint()
        try:
            # Try 3 times
            for nb in range(4):
                try:
                    self._proxy_create_flint_proxy(process)
                    break
                except Exception:
                    # Is the process has terminated?
                    if process.returncode is not None:
                        if process.returncode != 0:
                            raise subprocess.CalledProcessError(
                                process.returncode, "flint"
                            )
                        # Else it is just a normal close
                        raise RuntimeError("Flint have been closed")
                    if nb == 3:
                        raise
        except subprocess.CalledProcessError as e:
            # The process have terminated with an error
            FLINT_LOGGER.error("Flint has terminated with an error.")
            out, err = process.communicate(timeout=1)

            def normalize(data):
                if data is None:
                    return "Not recorded"
                try:
                    return data.decode("utf-8")
                except UnicodeError:
                    return data.decode("latin1")

            out = normalize(out)
            err = normalize(err)
            FLINT_OUTPUT_LOGGER.error("---STDOUT---\n%s", out)
            FLINT_OUTPUT_LOGGER.error("---STDERR---\n%s", err)
            raise subprocess.CalledProcessError(e.returncode, e.cmd, out, err)
        except Exception:
            if hasattr(process, "stdout"):
                FLINT_LOGGER.error("Flint can't start.")
                FLINT_OUTPUT_LOGGER.error("---STDOUT---")
                self.__log_process_output_to_logger(
                    process, "stdout", FLINT_OUTPUT_LOGGER, logging.ERROR
                )
                FLINT_OUTPUT_LOGGER.error("---STDERR---")
                self.__log_process_output_to_logger(
                    process, "stderr", FLINT_OUTPUT_LOGGER, logging.ERROR
                )
            raise
        FLINT_LOGGER.debug("Flint proxy initialized")
        assert self._proxy is not None
        self._proxy.wait_started()
        FLINT_LOGGER.debug("Flint proxy ready")

    def __log_process_output_to_logger(self, process, stream_name, logger, level):
        """Log the stream output of a process into a logger until the stream is
        closed.

        Args:
            process: A process object from subprocess or from psutil modules.
            stream_name: One of "stdout" or "stderr".
            logger: A logger from logging module
            level: A value of logging
        """
        was_openned = False
        if hasattr(process, stream_name):
            # process come from subprocess, and was pipelined
            stream = getattr(process, stream_name)
        else:
            # process output was not pipelined.
            # Try to open a linux stream
            stream_id = 1 if stream_name == "stdout" else 2
            try:
                path = f"/proc/{process.pid}/fd/{stream_id}"
                stream = open(path, "r")
                was_openned = True
            except Exception:
                FLINT_LOGGER.debug("Error while opening path %s", path, exc_info=True)
                FLINT_LOGGER.warning("Flint %s can't be attached.", stream_name)
                return
        if stream is None:
            # Subprocess returns None attributes if the streams are not catch
            return
        try:
            while self._proxy is not None and not stream.closed:
                line = stream.readline()
                try:
                    line = line.decode()
                except UnicodeError:
                    pass
                if not line:
                    break
                if line[-1] == "\n":
                    line = line[:-1]
                logger.log(level, "%s", line)
        except RuntimeError:
            # Process was terminated
            pass
        if stream is not None and was_openned and not stream.closed:
            stream.close()

    def is_available(self, timeout=2):
        """Returns true if Flint is available and not stucked."""
        state = self._proxy_get_flint_state(timeout=timeout)
        return state == _FlintState.IS_AVAILABLE

    #
    # Helper on top of the proxy
    #

    @typing.overload
    def get_live_plot(
        self,
        kind: typing.Literal["curve", "default-curve"],
        name: str | None = None,
    ) -> plots.LiveCurvePlot:
        ...

    @typing.overload
    def get_live_plot(
        self,
        kind: typing.Literal["scatter", "default-scatter"],
        name: str | None = None,
    ) -> plots.LiveScatterPlot:
        ...

    @typing.overload
    def get_live_plot(
        self,
        kind: typing.Literal["onedim"],
        name: str | None = None,
    ) -> plots.LiveOneDimPlot:
        ...

    @typing.overload
    def get_live_plot(
        self,
        kind: Lima,
    ) -> plots.LiveImagePlot:
        ...

    @typing.overload
    def get_live_plot(
        self,
        kind: BaseMCA | McaController,
    ) -> plots.LiveMcaPlot:
        ...

    @typing.overload
    def get_live_plot(
        self,
        image_detector: str,
    ) -> plots.LiveImagePlot:
        ...

    @typing.overload
    def get_live_plot(
        self,
        mca_detector: str,
    ) -> plots.LiveMcaPlot:
        ...

    @typing.overload
    def get_live_plot(
        self,
        onedim_detector: str,
    ) -> plots.LiveOneDimPlot:
        ...

    def get_live_plot(  # type: ignore
        self,
        kind: str | Lima | BaseMCA | McaController | None = None,
        name: str | None = None,
        image_detector: str | None = None,
        mca_detector: str | None = None,
        onedim_detector: str | None = None,
    ) -> base_plot.BasePlot:
        """Retrieve a live plot.

        This is an helper to simplify access to the plots used to display scans
        from BLISS.

        Arguments:
            kind: Can be one of "default-curve", "default-scatter",
                  or a supported controller like Mosca or Lima
            image_detector: Name of the detector displaying image.
            mca_detector: Name of the detector displaying MCA data.
            onedim_detector: Name of the detector displaying one dim data.
        """
        from bliss.controllers.lima.lima_base import Lima
        from bliss.controllers.mca.base import BaseMCA
        from bliss.controllers.mosca.base import McaController

        plot_class: type
        if isinstance(kind, Lima):
            plot_class = plots.LiveImagePlot
            plot_id = self.get_live_plot_detector(kind.name, plot_type="image")
            return plot_class(plot_id=plot_id, flint=self)

        if isinstance(kind, (BaseMCA, McaController)):
            plot_class = plots.LiveMcaPlot
            plot_id = self.get_live_plot_detector(kind.name, plot_type="mca")
            return plot_class(plot_id=plot_id, flint=self)

        if kind is not None:
            if kind in ("curve", "default-curve"):
                plot_class = plots.LiveCurvePlot
                plot_type = "curve"
            elif kind in ("scatter", "default-scatter"):
                plot_class = plots.LiveScatterPlot
                plot_type = "scatter"
            elif kind == "onedim":
                plot_class = plots.LiveOneDimPlot
                plot_type = "onedim"
            else:
                raise ValueError(f"Unexpected plot kind '{kind}'.")

            if name is not None:
                plot_id = self.get_live_scan_plot_by_name(
                    plot_name=name, plot_type=plot_type
                )
            else:
                plot_id = self.get_default_live_scan_plot(plot_type)
            if plot_id is None:
                raise ValueError(f"No {plot_type} plot available or plot is empty")

            return plot_class(plot_id=plot_id, flint=self)

        elif image_detector is not None:
            plot_class = plots.LiveImagePlot
            plot_id = self.get_live_plot_detector(image_detector, plot_type="image")
            return plot_class(plot_id=plot_id, flint=self)

        elif mca_detector is not None:
            plot_class = plots.LiveMcaPlot
            plot_id = self.get_live_plot_detector(mca_detector, plot_type="mca")
            return plot_class(plot_id=plot_id, flint=self)

        elif onedim_detector is not None:
            plot_class = plots.LiveOneDimPlot
            plot_id = self.get_live_plot_detector(onedim_detector, plot_type="onedim")
            return plot_class(plot_id=plot_id, flint=self)

        raise ValueError("No plot requested")

    def get_plot(
        self,
        plot_class: str | object,
        name: str | None = None,
        unique_name: str | None = None,
        selected: bool = False,
        closeable: bool = True,
        parent_id: str | None = None,
        parent_layout_params=None,
        in_live_window: bool | None = None,
    ) -> base_plot.BasePlot:
        """Create or retrieve a plot from this flint instance.

        If the plot does not exists, it will be created in a new tab on Flint.

        Arguments:
            plot_class: A class defined in `bliss.flint.client.plot`, or a
                silx class name. Can be one of "Plot1D", "Plot2D", "ImageView",
                "StackView", "ScatterView".
            name: Name of the plot as displayed in the tab header. It is not a
                unique name.
            unique_name: If defined the plot can be retrieved from flint.
            selected: If true (not the default) the plot became the current
                displayed plot.
            closeable: If true (default), the tab can be closed manually
            in_live_window: If true, the plot will be displayed in the live window
                            Default is None for auto selection.
        """
        plot_class2 = self.__normalize_plot_class(plot_class)
        silx_class_name = plot_class2.WIDGET

        if unique_name is not None:
            if self.plot_exists(unique_name, silx_class_name):
                return plot_class2(flint=self, plot_id=unique_name)

        if self._proxy is None:
            raise FlintWasDisconnected

        plot_id = self._proxy.add_plot(
            silx_class_name,
            name=name,
            selected=selected,
            closeable=closeable,
            unique_name=unique_name,
            parent_id=parent_id,
            parent_layout_params=parent_layout_params,
            in_live_window=in_live_window,
        )
        return plot_class2(plot_id=plot_id, flint=self, register=True)

    def add_plot(
        self,
        plot_class: str | object,
        name: str | None = None,
        selected: bool = False,
        closeable: bool = True,
        parent_id: str | None = None,
        parent_layout_params=None,
        in_live_window: bool | None = None,
    ):
        """Create a new custom plot based on the `silx` API.

        The plot will be created in a new tab on Flint.

        Arguments:
            plot_class: A class defined in `bliss.flint.client.plot`, or a
                silx class name. Can be one of "PlotWidget",
                "PlotWindow", "Plot1D", "Plot2D", "ImageView", "StackView",
                "ScatterView".
            name: Name of the plot as displayed in the tab header. It is not a
                unique name.
            selected: If true (not the default) the plot became the current
                displayed plot.
            closeable: If true (default), the tab can be closed manually
            in_live_window: If true, the plot will be displayed in the live window.
                            Default is None for auto selection.
        """
        plot_class2 = self.__normalize_plot_class(plot_class)
        silx_class_name = plot_class2.WIDGET

        if self._proxy is None:
            raise FlintWasDisconnected

        plot_id = self._proxy.add_plot(
            silx_class_name,
            name=name,
            selected=selected,
            closeable=closeable,
            parent_id=parent_id,
            parent_layout_params=parent_layout_params,
            in_live_window=in_live_window,
        )
        return plot_class2(plot_id=plot_id, flint=self, register=True)

    def __normalize_plot_class(self, plot_class: str | object):
        """Returns a BLISS side plot class.

        Arguments:
            plot_class: A BLISS side plot class, or one of its alias
        """
        if isinstance(plot_class, str):
            plot_class = plot_class.lower()
            for cls in plots.CUSTOM_CLASSES:
                if plot_class in cls.ALIASES:
                    plot_class = cls
                    break
            else:
                raise ValueError(f"Name '{plot_class}' does not refer to a plot class")
        return plot_class


def _get_beacon_address() -> str:
    return get_default_connection().get_address()


def _get_flint_pid_from_redis(session_name) -> int | None:
    """Check if an existing Flint process is running and attached to session_name.

    Returns:
        The process object from psutil.
    """
    beacon = get_default_connection()
    redis = beacon.get_redis_proxy()

    # get existing flint, if any
    pattern = config.get_flint_key(pid="*")
    for key in redis.scan_iter(pattern):
        key = key.decode()
        pid = int(key.split(":")[-1])
        if not psutil.pid_exists(pid):
            redis.delete(key)
            continue

        ps = psutil.Process(pid)
        if "flint" not in " ".join(ps.cmdline()):
            redis.delete(key)
            continue

        value = redis.lindex(key, 0).split()[0]
        if value.decode() == session_name:
            return pid

    return None


def _get_singleton() -> FlintClient:
    """Returns the Flint client singleton managed by this module.

    This singleton can be connected or not to a Flint application.
    """
    global FLINT
    if FLINT is None:
        FLINT = FlintClient()
    return FLINT


def _get_available_proxy() -> FlintClient | None:
    """Returns the Flint proxy only if there is a working connected Flint
    application."""
    proxy = _get_singleton()
    if proxy.is_available():
        return proxy
    return None


@typing.overload
def get_flint() -> FlintClient:
    # Most of the time it is used without params
    # It's useful to know that FlintClient result is mandatory
    ...


@typing.overload
def get_flint(
    start_new: bool = False,
    creation_allowed: bool = True,
    mandatory: bool = True,
    restart_if_stucked: bool = False,
) -> FlintClient | None:
    ...


def get_flint(
    start_new: bool = False,
    creation_allowed: bool = True,
    mandatory: bool = True,
    restart_if_stucked: bool = False,
) -> FlintClient | None:
    """Get the running flint proxy or create one.

    Arguments:
        start_new: If true, force starting a new flint subprocess (which will be
            the new current one)
        creation_allowed: If false, a new application will not be created.
        mandatory: If True (default), a Flint proxy must be returned else
            an exception is raised.
            If False, try to return a Flint proxy, else None is returned.
        restart_if_stucked: If True, if Flint is detected as stucked it is
            restarted.
    """
    if not mandatory:
        # Protect call to flint
        try:
            return get_flint(
                start_new=start_new,
                creation_allowed=creation_allowed,
                restart_if_stucked=restart_if_stucked,
            )
        except KeyboardInterrupt:
            # A warning should already be displayed in case of problem
            return None
        except Exception:
            # A warning should already be displayed in case of problem
            return None

    try:
        session_name = current_session.name
    except AttributeError:
        raise RuntimeError("No current session, cannot get flint")

    if not start_new:
        check_redis = True

        proxy = _get_singleton()
        state = proxy._proxy_get_flint_state(timeout=2)
        if state == _FlintState.NO_PROXY:
            pass
        elif state == _FlintState.IS_AVAILABLE:
            remote_session_name = proxy.get_session_name()
            if session_name == remote_session_name:
                return proxy
            # Do not use this Redis PID if is is already this one
            pid_from_redis = _get_flint_pid_from_redis(session_name)
            check_redis = pid_from_redis != proxy._pid
        elif state == _FlintState.IS_STUCKED:
            if restart_if_stucked:
                return restart_flint()
            raise RuntimeError("Flint is stucked")
        else:
            assert False, f"Unexpected state {state}"

        if check_redis:
            pid = _get_flint_pid_from_redis(session_name)
            if pid is not None:
                try:
                    return attach_flint(pid)
                except BaseException:
                    FLINT_LOGGER.error(
                        "Impossible to attach Flint to the already existing PID %s", pid
                    )
                    raise

    if not creation_allowed:
        return None

    proxy = _get_singleton()
    proxy._proxy_start_flint()
    return proxy


def check_flint() -> bool:
    """
    Returns true if a Flint application from the current session is alive.
    """
    flint = _get_available_proxy()
    return flint is not None


def attach_flint(pid: int) -> FlintClient:
    """Attach to an external flint process, make a RPC proxy and bind Flint to
    the current session and return the FLINT proxy

    Argument:
        pid: Process identifier of Flint
    """
    flint = _get_singleton()
    flint._proxy_attach_pid(pid)
    return flint


def restart_flint(creation_allowed: bool = True):
    """Restart flint.

    Arguments:
        creation_allowed:  If true, if FLint was not started is will be created.
            Else, nothing will happen.
    """
    proxy = _get_singleton()
    state = proxy._proxy_get_flint_state(timeout=2)
    if state == _FlintState.NO_PROXY:
        if not creation_allowed:
            return
    elif state == _FlintState.IS_AVAILABLE:
        proxy._proxy_close_proxy()
    elif state == _FlintState.IS_STUCKED:
        proxy._proxy_close_proxy()
    else:
        assert False, f"Unexpected state {state}"
    flint = get_flint(start_new=True, mandatory=True)
    return flint


def close_flint():
    """Close the current flint proxy."""
    proxy = _get_singleton()
    state = proxy._proxy_get_flint_state(timeout=2)
    if state == _FlintState.NO_PROXY:
        pass
    elif state == _FlintState.IS_AVAILABLE:
        proxy._proxy_close_proxy()
    elif state == _FlintState.IS_STUCKED:
        proxy._proxy_close_proxy()
    else:
        assert False, f"Unexpected state {state}"


def reset_flint():
    """Close the current flint proxy."""
    close_flint()
