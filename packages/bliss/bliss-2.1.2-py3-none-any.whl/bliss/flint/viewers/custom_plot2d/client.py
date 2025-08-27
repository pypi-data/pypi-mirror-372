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

import numpy
import logging

from bliss.flint.client.data_plot import DataPlot


_logger = logging.getLogger(__name__)


class Plot2D(DataPlot):

    # Name of the corresponding silx widget
    WIDGET = "bliss.flint.viewers.custom_plot2d.viewer.Plot2D"

    # Available name to identify this plot
    ALIASES = ["plot2d"]

    def _init_plot(self):
        super(Plot2D, self)._init_plot()
        self.submit("setKeepDataAspectRatio", True)
        self.submit("setDisplayedIntensityHistogram", True)

    @property
    def yaxis_direction(self) -> str:
        """Direction of the y-axis.

        One of "up", "down"
        """
        return self.submit("getYaxisDirection")

    @yaxis_direction.setter
    def yaxis_direction(self, direction: str):
        self.submit("setYaxisDirection", direction)

    def add_image(
        self,
        image,
        origin=None,
        scale=None,
        colormap=None,
        legend="image",
        resetzoom=True,
    ):
        """Add an image item.

        Arguments:
            image: Image to display
            legend: Unique name of the item
        """
        self.submit(
            "addImage",
            image,
            origin=origin,
            scale=scale,
            colormap=colormap,
            legend=legend,
            resetzoom=resetzoom,
        )

    def add_scatter(
        self,
        x,
        y,
        value,
        colormap=None,
        legend="image",
        resetzoom=True,
    ):
        """Add a scatter item.

        Arguments:
            x: X-axis values
            y: Y-axis values
            value: Intensity values
            legend: Unique name of the item
        """
        self.submit(
            "addScatter",
            x=x,
            y=y,
            value=value,
            colormap=colormap,
            legend=legend,
            resetzoom=resetzoom,
        )

    def add_image_with_normalization(
        self,
        image: numpy.ndarray,
        x_axis: numpy.ndarray,
        y_axis: numpy.ndarray,
        colormap=None,
        legend: str | None = None,
    ):
        """Add an image item with axis normalization.

        Arguments:
            image: Image to display
            x_axis: Axis to use for the x-axis
            y_axis: Axis to use for the y-axis
            legend: Unique name of the item
        """
        self.submit(
            "addImageWithNormalization",
            image,
            x_axis,
            y_axis,
            colormap=colormap,
            legend=legend,
        )

    def add_colormap(
        self,
        name: str,
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
            name: Name for this colormap item
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
        self.submit(
            "addColormap",
            name=name,
            lut=lut,
            vmin=vmin,
            vmax=vmax,
            normalization=normalization,
            gammaNormalization=gamma_normalization,
            autoscale=autoscale,
            autoscaleMode=autoscale_mode,
        )

    def select_mask(
        self, initial_mask: numpy.ndarray | None = None, directory: str | None = None
    ):
        """Request a mask image from user selection.

        Argument:
            initial_mask: An initial mask image, else None
            directory: Directory used to import/export masks

        Return:
            A numpy array containing the user mask image
        """
        flint = self._flint
        request_id = flint.request_select_mask_image(
            self._plot_id, initial_mask, directory=directory
        )
        return self._wait_for_user_selection(request_id)
