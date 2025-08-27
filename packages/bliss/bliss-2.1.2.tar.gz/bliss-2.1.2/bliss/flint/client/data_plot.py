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

from bliss.common import deprecation
from .base_plot import BasePlot


_logger = logging.getLogger(__name__)


class DataPlot(BasePlot):
    """
    Plot providing a common API to store data

    This was introduced for baward compatibility with BLISS <= 1.8

    FIXME: This have to be deprecated and removed. Plots should be updated using
    another API
    """

    # Data handling

    def upload_data(self, field, data):
        """
        Update data as an identifier into the server side

        Argument:
            field: Identifier in the targeted plot
            data: Data to upload
        """
        deprecation.deprecated_warning(
            "Method", "upload_data", replacement="set_data", since_version="1.9"
        )
        return self.submit("updateStoredData", field, data)

    def upload_data_if_needed(self, field, data):
        """Upload data only if it is a numpy array or a list"""
        deprecation.deprecated_warning(
            "Method",
            "upload_data_if_needed",
            replacement="set_data",
            since_version="1.9",
        )
        if isinstance(data, (numpy.ndarray, list)):
            self.submit("updateStoredData", field, data)
            return field
        else:
            return data

    def add_data(self, data, field="default"):
        # Get fields
        deprecation.deprecated_warning(
            "Method", "add_data", replacement="set_data", since_version="1.9"
        )
        if isinstance(data, dict):
            fields = list(data)
        else:
            fields = numpy.array(data).dtype.fields
        # Single data
        if fields is None:
            data_dict = dict([(field, data)])
        # Multiple data
        else:
            data_dict = dict((field, data[field]) for field in fields)
        # Send data
        for field, value in data_dict.items():
            self.upload_data(field, value)
        # Return data dict
        return data_dict

    def remove_data(self, field):
        self.submit("removeStoredData", field)

    def select_data(self, *names, **kwargs):
        deprecation.deprecated_warning(
            "Method",
            "select_data",
            replacement="set_data/add_curve/add_curve_item/set_data",
            since_version="1.9",
        )
        self.submit("selectStoredData", *names, **kwargs)

    def deselect_data(self, *names):
        deprecation.deprecated_warning(
            "Method",
            "deselect_data",
            replacement="set_data/add_curve/add_curve_item",
            since_version="1.9",
        )
        self.submit("deselectStoredData", *names)

    def clear_data(self):
        self.submit("clear")

    def get_data(self, field=None):
        return self.submit("getStoredData", field=field)
