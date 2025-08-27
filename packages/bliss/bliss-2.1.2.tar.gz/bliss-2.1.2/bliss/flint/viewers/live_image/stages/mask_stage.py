# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

from __future__ import annotations

import os
import numpy
import logging
from silx.gui import qt
from silx.gui.dialog.ImageFileDialog import ImageFileDialog
from .info import ImageCorrections
from .base_stage import BaseStage


_logger = logging.getLogger(__name__)


class MaskStage(BaseStage):
    def __init__(self, parent: qt.QObject | None = None):
        BaseStage.__init__(self, parent=parent)
        self.__maskDisplayedAsLayer = False
        self.__mask = None
        self.__maskDir: str | None = None
        self.__maskError = False

    def requestMaskFile(self):
        """Request user to load a mask"""
        dialog = ImageFileDialog(self._findRelatedWidget())
        if self.__maskDir is not None and os.path.exists(self.__maskDir):
            dialog.setDirectory(self.__maskDir)

        result = dialog.exec_()
        if not result:
            return
        try:
            mask = dialog.selectedImage()
            if mask is not None:
                self.setMask(mask)
        except Exception:
            _logger.error("Error while loading a mask", exc_info=True)
        directory = dialog.directory()
        self.__maskDir = None if directory is None else str(directory)

    def setMask(self, mask):
        """Set the actual mask"""
        if mask is None:
            self.__mask = None
        else:
            self.__mask = mask != 0
        self.configUpdated.emit()

    def mask(self):
        """Returns the mask used to filter the image"""
        return self.__mask

    def clear(self):
        self.__maskError = False

    def isValid(self):
        if self.__mask is None:
            return False
        return not self.__maskError

    def correction(self, image: numpy.ndarray):
        self._resetApplyedCorrections()
        if self.__mask is not None:
            if self.__mask.shape == image.shape[0:2]:
                self._setApplyedCorrections([ImageCorrections.MASK_CORRECTION])
                image = image.astype(float)
                image[self.__mask] = numpy.nan
            else:
                self._setApplyedCorrections([])
                if not self.__maskError:
                    _logger.error(
                        "Mask and image mismatch (%s != %s)",
                        self.__mask.shape,
                        image.shape,
                    )
                    self.__maskError = True
        else:
            self._setApplyedCorrections([])
        return image

    def setMaskDisplayedAsLayer(self, displayedAsLayer):
        if self.__maskDisplayedAsLayer == displayedAsLayer:
            return
        self.__maskDisplayedAsLayer = displayedAsLayer
        self.configUpdated.emit()

    def isMaskDisplayedAsLayer(self):
        return self.__maskDisplayedAsLayer
