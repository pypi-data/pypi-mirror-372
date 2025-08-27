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

import typing
import logging
import numpy
import gevent

from bliss.flint.client.base_plot import BasePlot

if typing.TYPE_CHECKING:
    from bliss.scanning.scan import Scan


_logger = logging.getLogger(__name__)


class _LiveImageProcessing:
    def __init__(self, proxy):
        self.__proxy = proxy

    def _submit(self, cmd, *args, **kwargs):
        self.__proxy.submit(cmd, *args, **kwargs)

    def set_flat(self, array, expotime):
        """Specify a flat which will be used for the flatfield correction."""
        array = numpy.asarray(array)
        self._submit(
            "imageProcessing().flatFieldStage().setFlat", array, exposureTime=expotime
        )

    def set_dark(self, array, expotime):
        """Specify a dark which will be used for the flatfield correction."""
        array = numpy.asarray(array)
        self._submit(
            "imageProcessing().flatFieldStage().setDark", array, exposureTime=expotime
        )

    def set_mask(self, array):
        """Specify a mask which will be used to mask pixels."""
        array = numpy.asarray(array)
        self._submit("imageProcessing().maskStage().setMask", array)


class _LiveImageDiffractionStage:
    def __init__(self, proxy):
        self.__proxy = proxy

    def _submit(self, cmd, *args, **kwargs):
        self.__proxy.submit(cmd, *args, **kwargs)

    @property
    def enabled(self) -> bool:
        return self._submit("imageProcessing().diffractionStage().isEnabled()")

    @enabled.setter
    def enabled(self, enabled: bool):
        return self._submit("imageProcessing().diffractionStage().setEnabled", enabled)

    def set_calibrant(self, calibrant: str):
        """Specify the calibrant to be displayed by the diffraction processing.

        Arguments:
            calibrant: A pyFAI calibrant name or a pyFAI `.D` file
        """
        self._submit("imageProcessing().diffractionStage().setCalibrant", calibrant)

    def set_detector(self, detector: str):
        """Specify the detector to be used by the diffraction processing.

        Arguments:
            detector: A pyFAI detector name, or a hdf5 detector description
        """
        self._submit("imageProcessing().diffractionStage().setDetector", detector)

    def set_geometry(
        self,
        filename=None,
        dist=None,
        poni1=None,
        poni2=None,
        rot1=None,
        rot2=None,
        rot3=None,
        wavelength=None,
    ):
        """Specify the pyFAI geometry to be used by the diffraction processing.

        Arguments:
            filename: pyFAI poni-file containing the geometry
        """
        self._submit(
            "imageProcessing().diffractionStage().setGeometry",
            fileName=filename,
            dist=dist,
            poni1=poni1,
            poni2=poni2,
            rot1=rot1,
            rot2=rot2,
            rot3=rot3,
            wavelength=wavelength,
        )


class LiveImagePlot(BasePlot):

    ALIASES = ["image"]

    def _init(self):
        # Make it public
        self.set_colormap = self._set_colormap
        self.__processing = None
        self.__diffraction = None

    def wait_end_of_scan(self, scan: Scan, timeout=5):
        """Wait for the end of a scan in this widget.

        The implementation is based on a polling.
        """
        scan_key = scan._scan_data.key
        polling = 0.5
        for _ in range(max(1, int(timeout // polling))):
            gevent.sleep(polling)
            if self.submit("scanWasTerminated", scan_key):
                break
        else:
            raise TimeoutError(
                f"Timeout {timeout} seconds expired. Scan {scan_key} not yet termnated"
            )

    def update_marker(
        self,
        unique_name: str,
        position: tuple[float, float] | None = None,
        text: str | None = None,
        editable: bool | None = None,
        kind: str | None = None,
    ):
        """
        Create or update a marker into the image.

        Arguments:
            unique_name: Unique name identifying this marker
            position: X and Y position in the image, else None to remove the marker
            text: Text to display with the marker
            editable: If true, the marker can be moved with the mouse
            kind: Shape of the ROI. One of `point`, `cross`, `vline`, `hline`
        """
        self.submit(
            "updateMarker",
            uniqueName=unique_name,
            position=position,
            text=text,
            editable=editable,
            kind=kind,
        )

    def remove_marker(self, unique_name: str):
        """
        Remove a marker already existing.

        If the marker is not there, no feedback is returned.

        Arguments:
            unique_name: Unique name identifying this marker
        """
        self.submit("removeMarker", uniqueName=unique_name)

    def marker_position(self, unique_name: str) -> tuple[float, float] | None:
        """
        Create or update a marker into the image.

        Arguments:
            unique_name: Unique name identifying this marker

        Returns:
            The position of the marker, else None if the marker does not exist
        """
        p = self.submit("markerPosition", uniqueName=unique_name)
        if p is None:
            return None
        # FIXME: the RPC returns a list instead of a tuple
        return p[0], p[1]

    @property
    def processing(self):
        if self.__processing is None:
            self.__processing = _LiveImageProcessing(self)
        return self.__processing

    @property
    def diffraction(self):
        if self.__diffraction is None:
            self.__diffraction = _LiveImageDiffractionStage(self)
        return self.__diffraction
