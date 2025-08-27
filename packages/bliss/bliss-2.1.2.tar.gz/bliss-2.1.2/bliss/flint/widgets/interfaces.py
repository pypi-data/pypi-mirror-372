# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

"""Interface to flag some classes"""

from __future__ import annotations

from bliss.flint.model import scan_model
from bliss.flint.model import plot_model


class HasPlotModel:
    """Flag a class as a plot provider."""

    def plotModel(self) -> plot_model.Plot | None:
        """Returns a plot"""
        raise NotImplementedError


class HasScan:
    """Flag a class as a scan provider."""

    def scan(self) -> scan_model.Scan | None:
        """Returns a plot"""
        raise NotImplementedError


class HasDeviceName:
    """Flag a class as a device provider."""

    def deviceName(self) -> str | None:
        """Returns a plot"""
        raise NotImplementedError
