# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.
"""
Provides plot interface exposed inside BLISS shell.
"""

from __future__ import annotations

import typing
import logging
import gevent

from bliss.flint.client.base_plot import BasePlot

if typing.TYPE_CHECKING:
    from bliss.scanning.scan import Scan


_logger = logging.getLogger(__name__)


class LiveOneDimPlot(BasePlot):

    ALIASES = ["onedim"]

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
