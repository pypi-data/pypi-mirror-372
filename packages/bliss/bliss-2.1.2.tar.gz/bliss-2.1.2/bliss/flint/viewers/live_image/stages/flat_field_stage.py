# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

from __future__ import annotations
from typing import NamedTuple

import numpy
import numexpr
import functools
import logging
from silx.gui import qt
from bliss.flint.helper import scan_info_helper
from bliss.flint.model import scan_model
from .info import ImageLayer
from .info import ImageCorrections
from .base_stage import BaseStage


_logger = logging.getLogger(__name__)


def extract_exposure_time(scan_info: dict) -> tuple[ImageLayer, float]:
    technique = scan_info.get("technique", {})

    def read_exposure_time_in_second(meta):
        value = meta["exposure_time"]
        unit = scan.get("exposure_time@units", "s")
        coefs = {"s": 1, "ms": 0.001}
        if unit not in coefs:
            raise RuntimeError(f"Unsupported exposure_time unit '{unit}' in scan")
        return value * coefs[unit]

    if "dark" in technique:
        scan = technique["dark"]
        tomo_scan = ImageLayer.DARK
        exposure_time = read_exposure_time_in_second(scan)
    elif "flat" in technique:
        scan = technique["flat"]
        tomo_scan = ImageLayer.FLAT
        exposure_time = read_exposure_time_in_second(scan)
    elif "proj" in technique:
        scan = technique["proj"]
        tomo_scan = ImageLayer.RAW
        exposure_time = read_exposure_time_in_second(scan)
    elif "scan" in technique and "tomo_n" in technique["scan"]:
        scan = technique["scan"]
        tomo_scan = ImageLayer.RAW
        exposure_time = scan["exposure_time"] / 1000
    else:
        tomo_scan = None
        # NOTE: BLISS 1.9 expose mesh scan npoints as numpy int64
        # cast it to avoid further json serialization fail
        exposure_time = scan_info.get("count_time")
    return tomo_scan, exposure_time


class Layer(NamedTuple):
    array: numpy.ndarray
    exposureTime: float
    scanId: str
    scanTitle: str
    kind: ImageLayer

    def __hash__(self):
        """Needed to use the lru cache decorator"""
        return id(self)

    @functools.lru_cache(1)
    def normalized(self, shape, exposureTime: float):
        if self.array.shape != shape:
            return None
        tdark = exposureTime / self.exposureTime
        return numpy.asarray(self.array, float) * tdark


class FlatFieldStage(BaseStage):

    USE_NUMEXPR = True

    def __init__(self, parent: qt.QObject | None = None):
        BaseStage.__init__(self, parent=parent)
        self.__dark: Layer | None = None
        self.__flat: Layer | None = None

    def captureRawDetector(self, scan, raw):
        scanInfo = scan.scanInfo()
        layerKind, exposureTime = extract_exposure_time(scanInfo)
        if layerKind == ImageLayer.DARK:
            self.setDark(raw, exposureTime, scan)
        elif layerKind == ImageLayer.FLAT:
            self.setFlat(raw, exposureTime, scan)

    def dark(self) -> Layer | None:
        return self.__dark

    def setDark(
        self, image: numpy.ndarray, exposureTime: float, scan: scan_model.Scan = None
    ):
        if scan:
            scanInfo = scan.scanInfo()
            title = scan_info_helper.get_full_title(scan)
            scanId = scanInfo.get("scan_nb", None)
        else:
            title = None
            scanId = None
        self.__dark = Layer(image, exposureTime, scanId, title, ImageLayer.DARK)
        self.configUpdated.emit()

    def flat(self) -> Layer | None:
        return self.__flat

    def setFlat(
        self, image: numpy.ndarray, exposureTime: float, scan: scan_model.Scan = None
    ):
        if scan:
            scanInfo = scan.scanInfo()
            title = scan_info_helper.get_full_title(scan)
            scanId = scanInfo.get("scan_nb", None)
        else:
            title = None
            scanId = None
        self.__flat = Layer(image, exposureTime, scanId, title, ImageLayer.FLAT)
        self.configUpdated.emit()

    def correction(self, array: numpy.ndarray, exposureTime: float, use_flat=True):
        self._resetApplyedCorrections()
        if not use_flat:
            return self._dark_correction(array, exposureTime)

        if self.__dark is None and self.__flat is None:
            self._setApplyedCorrections([])
            return array

        def normalized(layer: Layer):
            if layer is None:
                return None
            shape = tuple(array.shape)
            return layer.normalized(shape, exposureTime)

        flat = normalized(self.__flat)
        dark = normalized(self.__dark)
        if dark is None and flat is None:
            self._setApplyedCorrections([])
            return array

        if dark is None:
            if self.USE_NUMEXPR:
                data = numexpr.evaluate("where(flat==0,0,array/flat)")
            else:
                with numpy.errstate(divide="ignore"):
                    data = array / flat
                data[numpy.logical_not(numpy.isfinite(data))] = 0
            self._setApplyedCorrections([ImageCorrections.FLAT_CORRECTION])
            return data

        if flat is None:
            self._setApplyedCorrections([ImageCorrections.DARK_CORRECTION])
            return array - dark

        if self.USE_NUMEXPR:
            data = numexpr.evaluate(
                "where(flat-dark>0,where((array-dark)<0,0,(array-dark))/where((flat-dark)<0,0,(flat-dark)),0)"
            )
        else:
            with numpy.errstate(divide="ignore"):
                data = (array - dark) / (flat - dark)
            data[numpy.logical_not(numpy.isfinite(data))] = 0

        self._setApplyedCorrections([ImageCorrections.FLATFIELD_CORRECTION])
        return data

    def _dark_correction(self, array: numpy.ndarray, exposureTime: float):
        if self.__dark is None:
            self._setApplyedCorrections([])
            return array

        def normalized(layer: Layer):
            if layer is None:
                return None
            shape = tuple(array.shape)
            return layer.normalized(shape, exposureTime)

        dark = normalized(self.__dark)
        if dark is None:
            self._setApplyedCorrections([])
            return array

        if self.USE_NUMEXPR:
            data = numexpr.evaluate("where((array-dark)<0,0,array-dark)")
        else:
            with numpy.errstate(divide="ignore"):
                data = array - dark
            data[numpy.logical_not(numpy.isfinite(data))] = 0

        self._setApplyedCorrections([ImageCorrections.DARK_CORRECTION])
        return data
