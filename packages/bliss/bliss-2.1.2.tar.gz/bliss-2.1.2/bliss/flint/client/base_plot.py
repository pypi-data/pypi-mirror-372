# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.
"""
Provides plot helper class to deal with flint proxy.
"""

from __future__ import annotations

import gevent
import gevent.queue
import logging

from bliss.common import event
from bliss.comm.rpc import RpcConnectionError


_logger = logging.getLogger(__name__)


class FlintWasDisconnected(RuntimeError):
    pass


class BasePlot(object):

    # Qualified classname of the corresponding Qt widget
    WIDGET: str = NotImplemented

    # Available name to identify this plot
    ALIASES: list[str] = []

    def __init__(self, flint, plot_id, register=False):
        """Describe a custom plot handled by Flint."""
        self._plot_id = plot_id
        self._flint = flint
        self._xlabel = None
        self._ylabel = None
        self._init()
        if flint is not None:
            if register:
                self._init_plot()

    def _init(self):
        """Allow to initialize extra attributes in a derived class, without
        redefining the constructor"""

    def _init_plot(self):
        """Inherits it to custom the plot initialization"""
        if self._xlabel is not None:
            self.submit("setGraphXLabel", self._xlabel)
        if self._ylabel is not None:
            self.submit("setGraphYLabel", self._ylabel)

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, txt):
        self._title = str(txt)
        self.submit("setGraphTitle", self._title)

    @property
    def xlabel(self):
        return self._xlabel

    @xlabel.setter
    def xlabel(self, txt):
        self._xlabel = str(txt)
        self.submit("setGraphXLabel", self._xlabel)

    @property
    def ylabel(self):
        return self._ylabel

    @ylabel.setter
    def ylabel(self, txt):
        self._ylabel = str(txt)
        self.submit("setGraphYLabel", self._ylabel)

    def __repr__(self):
        try:
            # Protect problems on RPC
            name = self._flint.get_plot_name(self._plot_id)
        except Exception:
            name = None
        return "{}(plot_id={!r}, flint_pid={!r}, name={!r})".format(
            self.__class__.__name__, self.plot_id, self.flint_pid, name
        )

    def submit(self, method, *args, **kwargs):
        try:
            return self._flint.run_method(self.plot_id, method, args, kwargs)
        except RpcConnectionError as e:
            if e.args[0].startswith("Disconnected"):
                raise FlintWasDisconnected(
                    f"Can't call '{method}' on plot '{self.plot_id}'"
                ) from e
            raise

    # Properties

    @property
    def flint_pid(self):
        return self._flint._pid

    @property
    def plot_id(self):
        return self._plot_id

    @property
    def name(self):
        return self._flint.get_plot_name(self._plot_id)

    def focus(self):
        """Set the focus on this plot"""
        self._flint.set_plot_focus(self._plot_id)

    def export_to_logbook(self):
        """Set the focus on this plot"""
        self._flint.export_to_logbook(self._plot_id)

    def get_data_range(self):
        """Returns the current data range used by this plot"""
        return self.submit("getDataRange")

    # Clean up

    def is_open(self) -> bool:
        """Returns true if the plot is still open in the linked Flint
        application"""
        try:
            return self._flint.plot_exists(self._plot_id)
        except Exception:
            # The proxy is maybe dead
            return False

    def close(self):
        self._flint.remove_plot(self.plot_id)

    # Interaction

    def _wait_for_user_selection(self, request_id):
        """Wait for a user selection and clean up result in case of error"""
        from . import proxy

        proxy.FLINT_LOGGER.warning("Waiting for selection in Flint window.")
        flint = self._flint
        results = gevent.queue.Queue()
        event.connect(flint._proxy, request_id, results.put)
        try:
            result = results.get()
            return result
        except Exception:
            try:
                flint.cancel_request(request_id)
            except Exception:
                proxy.FLINT_LOGGER.debug(
                    "Error while canceling the request", exc_info=True
                )
            proxy.FLINT_LOGGER.warning("Plot selection cancelled. An error occurred.")
            raise
        except KeyboardInterrupt:
            try:
                flint.cancel_request(request_id)
            except Exception:
                proxy.FLINT_LOGGER.debug(
                    "Error while canceling the request", exc_info=True
                )
            proxy.FLINT_LOGGER.warning("Plot selection cancelled by bliss user.")
            raise

    def select_shapes(
        self,
        initial_selection: list[object] | None = None,
        kinds: str | list[str] | None = "rectangle",
    ):
        """
        Request user selection of shapes.

        `initial_selection` is a list of ROIs from `bliss.controllers.lima.roi`.

        It also supports key-value dictionary for simple rectangle.
        In this case, the dictionary contains "kind" (which is "Rectangle"),
        and "label", "origin" and "size" which are tuples of 2 floats.

        Arguments:
            initial_selection: List of shapes already selected.
            kinds: List or ROI kind which can be created (for now, "rectangle"
                (described as a dict), "lima-rectangle", "lima-arc",
                "lima-vertical-profile",
                "lima-horizontal-profile", "mosca-range")

        Raises:
            RuntimeError: If the edition was cancelled in Flint
        """
        flint = self._flint
        request_id = flint.request_select_shapes(
            self._plot_id, initial_selection, kinds=kinds
        )
        result = self._wait_for_user_selection(request_id)
        if result is None:
            raise RuntimeError("Edition was cancelled")
        return result

    def select_points(self, nb):
        flint = self._flint
        request_id = flint.request_select_points(self._plot_id, nb)
        return self._wait_for_user_selection(request_id)

    def select_shape(
        self, shape: str, valid: bool = False, cancel: bool = False
    ) -> bool | list[tuple[float, float]]:
        """
        Request and wait for a user shape selection in Flint.

        Arguments:
            shape: The kind of shape requested ("rectangle", "line", "polygon",
                "hline", "vline")
            valid: If true, a validation button is including, returning `True` if clicked
            cancel: If true, a cancel button is including, returning `False` if clicked
        """
        flint = self._flint
        request_id = flint.request_select_shape(
            self._plot_id, shape, valid=valid, cancel=cancel
        )
        return self._wait_for_user_selection(request_id)

    def _set_colormap(
        self,
        lut: str | None = None,
        vmin: float | str | None = None,
        vmax: float | str | None = None,
        normalization: str | None = None,
        gamma_normalization: float | None = None,
        autoscale: bool | None = None,
        autoscale_mode: str | None = None,
    ):
        """
        Allows to setup the default colormap of this plot.

        Arguments:
            lut: A name of a LUT. At least the following names are supported:
                 `"gray"`, `"reversed gray"`, `"temperature"`, `"red"`, `"green"`,
                 `"blue"`, `"jet"`, `"viridis"`, `"magma"`, `"inferno"`, `"plasma"`.
            vmin: Can be a float or "`auto"` to set the min level value
            vmax: Can be a float or "`auto"` to set the max level value
            normalization: Can be on of `"linear"`, `"log"`, `"arcsinh"`,
                           `"sqrt"`, `"gamma"`.
            gamma_normalization: float defining the gamma normalization.
                                 If this argument is defined the `normalization`
                                 argument is ignored
            autoscale: If true, the auto scale is set for min and max
                       (vmin and vmax arguments are ignored)
            autoscale_mode: Can be one of `"minmax"` or `"3stddev"`
        """
        flint = self._flint
        flint.set_plot_colormap(
            self._plot_id,
            lut=lut,
            vmin=vmin,
            vmax=vmax,
            normalization=normalization,
            gammaNormalization=gamma_normalization,
            autoscale=autoscale,
            autoscaleMode=autoscale_mode,
        )
