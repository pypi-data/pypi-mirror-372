# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

from __future__ import annotations

import logging

from bliss.flint.widgets.extended_dock_widget import ExtendedDockWidget
from bliss.flint.widgets.custom_plot import CustomPlot
from silx.gui import qt


_logger = logging.getLogger(__name__)


class _EmptyWidget(qt.QLabel):
    """Widget used to display the property widget when it is empty"""

    def __init__(self, parent=None):
        super(_EmptyWidget, self).__init__(parent=parent)
        html = """<html>
<head/><body>
<p><span style=" font-size:14pt; font-weight:600; color:#939393;">No plot</span></p>
</body></html>"""
        self.setWordWrap(True)
        self.setText(html)
        self.setAlignment(qt.Qt.AlignHCenter | qt.Qt.AlignVCenter)


class InliveCustomPlot(ExtendedDockWidget):
    def __init__(self, parent=None):
        super(InliveCustomPlot, self).__init__(parent=parent)
        self.__expectedPlotId: str | None = None
        self.__dummy: _EmptyWidget | None = _EmptyWidget(self)
        self.setWidget(self.__dummy)

    def configuration(self):
        result = {"expected_plot_id": self.__expectedPlotId}
        return result

    def setConfiguration(self, config):
        self.__expectedPlotId = config.get("expected_plot_id")

    def isAnonymousPlotId(self) -> bool:
        """If true, the plot was generated on the fly without unique name"""
        if self.__expectedPlotId is None:
            return False
        return self.__expectedPlotId.startswith("custom_plot:")

    def setExpectedPlotId(self, expectedPlotId: str):
        self.__expectedPlotId = expectedPlotId

    def expectedPlotId(self) -> str:
        assert self.__expectedPlotId is not None
        return self.__expectedPlotId

    def setCustomPlot(self, customPlot: CustomPlot | None):
        if customPlot is None:
            if self.__dummy is not None:
                return
            self.__dummy = _EmptyWidget(self)
            self.setWidget(self.__dummy)
            return
        if self.__dummy is not None:
            self.__dummy.deleteLater()
            self.__dummy = None
        self.setWidget(customPlot)

    def customPlot(self) -> CustomPlot | None:
        if self.__dummy is not None:
            return None
        return self.widget()
