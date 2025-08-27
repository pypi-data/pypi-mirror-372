# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

from __future__ import annotations

import numpy
import logging
import tempfile
import os

from silx.gui import qt

_logger = logging.getLogger(__name__)


class DataWidget(qt.QWidget):
    def __init__(self, parent=None):
        super(DataWidget, self).__init__(parent=parent)
        self.__silxWidget = self._createSilxWidget(self)
        self.__dataDict = {}

        frame = qt.QFrame(self)
        frame.setFrameShape(qt.QFrame.StyledPanel)
        frame.setAutoFillBackground(True)
        layout = qt.QVBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.__silxWidget)
        widget = qt.QFrame(self)
        layout = qt.QVBoxLayout(widget)
        layout.addWidget(frame)
        layout.setContentsMargins(0, 1, 0, 0)

        layout = qt.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(widget)

    def dataDict(self):
        return self.__dataDict

    def silxWidget(self):
        return self.__silxWidget

    def silxPlot(self) -> qt.QWidget:
        """Used by the interactive API.

        This have to returns a PlotWidget, that's why it could be not always
        the same as the silx widget.
        """
        return self.__silxWidget

    def _createSilxWidget(self, parent):
        raise NotImplementedError

    def __getattr__(self, name: str):
        silxWidget = self.silxWidget()
        return getattr(silxWidget, name)

    def updateStoredData(self, field, data):
        data_dict = self.dataDict()

        # Data from the network is sometime not writable
        # This make it fail silx for some use cases
        if data is None:
            return None
        if isinstance(data, numpy.ndarray):
            if not data.flags.writeable:
                data = numpy.array(data)

        data_dict[field] = data

    def removeStoredData(self, field):
        data_dict = self.dataDict()
        del data_dict[field]

    def getStoredData(self, field=None):
        data_dict = self.dataDict()
        if field is None:
            return data_dict
        else:
            return data_dict.get(field, [])

    def clearStoredData(self):
        data_dict = self.dataDict()
        data_dict.clear()

    def clear(self):
        self.clearStoredData()
        self.silxWidget().clear()

    def selectStoredData(self, *names, **kwargs):
        # FIXME: This have to be moved per plot widget
        # FIXME: METHOD have to be removed
        method = self.METHOD
        if "legend" not in kwargs and method.startswith("add"):
            kwargs["legend"] = " -> ".join(names)
        data_dict = self.dataDict()
        args = tuple(data_dict[name] for name in names)
        widget_method = getattr(self, method)
        # Plot
        widget_method(*args, **kwargs)

    def deselectStoredData(self, *names):
        legend = " -> ".join(names)
        self.remove(legend)

    def exportToLogbook(self, icatClient):
        plot = self.silxPlot()
        try:
            f = tempfile.NamedTemporaryFile(delete=False)
            filename = f.name
            f.close()
            os.unlink(filename)
            plot.saveGraph(filename, fileFormat="png")
            with open(filename, "rb") as f2:
                data = f2.read()
            os.unlink(filename)
        except Exception:
            _logger.error("Error while creating the screenshot", exc_info=True)
            raise Exception("Error while creating the screenshot")
        try:
            icatClient.send_binary_data(data=data, mimetype="image/png")
        except Exception:
            _logger.error("Error while sending the screenshot", exc_info=True)
            raise Exception("Error while sending the screenshot")
