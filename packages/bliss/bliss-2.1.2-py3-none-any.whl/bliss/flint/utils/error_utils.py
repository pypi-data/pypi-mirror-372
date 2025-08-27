# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

from __future__ import annotations

import typing
import contextlib
import logging
import traceback
from silx.gui import qt

_logger = logging.getLogger(__name__)


@contextlib.contextmanager
def exceptionAsMessageBox(
    parent: qt.QWidget, title: str = "Error", onError: typing.Callbable | None = None
):
    try:
        yield
    except Exception as e:
        _logger.warning("Error catched by an message box", exc_info=True)
        try:
            msg = str(e.args[0])
        except Exception:
            msg = str(e)
        detail: str | None
        try:
            detail = traceback.format_exc()
        except Exception:
            _logger.error("Error while reaching traceback", exc_info=True)
            detail = None

        try:
            if onError is not None:
                onError()
        except Exception:
            _logger.error("Error while executing onError callback", exc_info=True)

        msgBox = qt.QMessageBox(parent)
        msgBox.setIcon(qt.QMessageBox.Critical)
        msgBox.setText(msg)
        msgBox.setWindowTitle(title)
        if detail is not None:
            msgBox.setDetailedText(detail)
        msgBox.exec_()
