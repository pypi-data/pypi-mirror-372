# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

"""
BLISS controller for Bronkhorst Mass flow Controller.
"""

from bliss import global_map
from bliss.controllers.tango_attr_as_counter import (
    TangoCounterController,
    TangoAttrCounter,
)

from bliss.comm.util import get_tango_proxy
from bliss.common import tango
from bliss.common.protocols import CounterContainer, HasMetadataForScan
from bliss.common.utils import autocomplete_property
from bliss.common.logtools import log_warning
from bliss.controllers.counter import counter_namespace


class BronkhorstNode(TangoCounterController):
    """
    Bronkhorst SubDevice (Node) Controller
    """

    def __init__(self, name, tango_uri_or_proxy):
        super().__init__(name, tango_uri_or_proxy, global_map_register=False)

    @autocomplete_property
    def idn(self):
        return self._proxy.idn

    @autocomplete_property
    def type(self):
        return self._proxy.type

    @autocomplete_property
    def fluid(self):
        return self._proxy.fluid

    @autocomplete_property
    def measure(self):
        return self._proxy.measure

    @autocomplete_property
    def fmeasure(self):
        return self._proxy.fmeasure

    @autocomplete_property
    def setpoint(self):
        return self._proxy.setpoint

    @setpoint.setter
    def setpoint(self, value):
        self._proxy.setpoint = value

    @autocomplete_property
    def fsetpoint(self):
        return self._proxy.fsetpoint

    @fsetpoint.setter
    def fsetpoint(self, value):
        self._proxy.fsetpoint = value

    @autocomplete_property
    def fluid_temperature(self):
        return self._proxy.fluid_temperature

    @autocomplete_property
    def orifice(self):
        return self._proxy.orifice

    @autocomplete_property
    def pressure_inlet(self):
        return self._proxy.pressure_inlet

    @autocomplete_property
    def pressure_outlet(self):
        return self._proxy.pressure_outlet

    @autocomplete_property
    def capacity_unit(self):
        return self._proxy.capacity_unit

    def __info__(self):
        info = f"Fluid   : {self.fluid}\n"
        info += f"Setpoint: {self.fsetpoint:.2f} {self.capacity_unit}\n"
        info += f"Setpoint : {self.measure:.2f} %\n"
        info += f"Measure : {self.fmeasure:.2f} {self.capacity_unit}\n"
        info += f"Measure : {self.measure:.2f} %\n"
        # mystr += f"Flow    : {self.flow:.2f} ml/min\n"
        return info

    def scan_metadata(self):
        meta = {}
        meta["fluid"] = self.fluid
        meta["setpoint"] = self.setpoint
        return meta


class Bronkhorst(CounterContainer, HasMetadataForScan):
    """
    Bronkhorst Device Controller
    """

    def __init__(self, name, config):
        # super().__init__(config, share_hardware=False)
        global_map.register(self, tag=name)

        nodes_config = config.get("nodes")

        self._name = name
        self._proxy = get_tango_proxy(config)
        self._subdevices = self._proxy.subdevices
        self._nodes = []

        self.__counters = []

        for subdevice in self._subdevices:
            try:
                proxy = tango.DeviceProxy(subdevice)

                # Check if node is configured in bliss
                if proxy.idn not in nodes_config:
                    log_warning(self, "missing configuration for %s" % proxy.idn)
                    continue

                node_config = nodes_config.get(proxy.idn)

                node_name = node_config["name"]
                node = BronkhorstNode(node_name, proxy)
                self._nodes.append(node)
                setattr(self, node_name, node)

                counter_config = config.clone()
                counter_config["uri"] = config["tango_url"]
                counter_config["mode"] = "SINGLE"
                counter_config["format"] = node_config.get("format", "%6.2f")

                # fmeasure counter
                counter_config["attr_name"] = "fmeasure"
                cnt_measure = TangoAttrCounter(node_name, counter_config, node)

                # fsetpoint counter
                counter_config["attr_name"] = "fsetpoint"
                cnt_setpoint = TangoAttrCounter(
                    f"{node_name}_fsetpoint", counter_config, node
                )

                # NB: "cnt.allow_failure==True"
                #     means "the scan will crash if reading of cnt fails"
                cnt_measure.allow_failure = False
                self.__counters.extend((cnt_measure, cnt_setpoint))
            except Exception:
                global_map.unregister(self)  # issue 3029
                raise

    @property
    def name(self):
        return self._name

    @autocomplete_property
    def counters(self):
        return counter_namespace(self.__counters)

    def scan_metadata(self):
        """
        Return a dict to be put in HDF5 metadata.
        """
        meta_data = {}
        for node in self._nodes:
            meta_data[node.fullname] = node.scan_metadata()
        return meta_data
