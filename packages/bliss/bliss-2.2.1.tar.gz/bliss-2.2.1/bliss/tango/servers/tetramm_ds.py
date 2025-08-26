# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.


import numpy as np
import logging

from tango import DevState, GreenMode, Except
from tango.server import Device, device_property, attribute, command, run

from bliss.config.static import get_config
from bliss.common.logtools import log_debug, log_warning
from bliss import global_log, global_map

from bliss.controllers.tetramm.tetramm import TetrammHw


def switch_state(tg_dev, state=None, status=None):
    """Helper to switch state and/or status and send event"""
    if state is not None:
        tg_dev.set_state(state)
        if state in (DevState.ALARM, DevState.UNKNOWN, DevState.FAULT):
            msg = "State changed to " + str(state)
            if status is not None:
                msg += ": " + status
    if status is not None:
        tg_dev.set_status(status)


class TetrammServer(Device):
    beacon_name = device_property(dtype=str, doc="Object name inside Beacon")
    debug_on = device_property(dtype=bool, default_value=False)

    def init_device(self, *args, **kwargs):
        super().init_device(*args, **kwargs)
        self.set_state(DevState.STANDBY)

        try:
            config = get_config()
            yml_config = config.get_config(self.beacon_name)
            if yml_config is None:
                raise RuntimeError(
                    f"Could not find a Beacon object with name {self.beacon_name}"
                )
            self.hw = TetrammHw(yml_config)

            switch_state(self, DevState.ON, "Ready!")
        except Exception as e:
            msg = "Exception initializing device: {0}".format(e)
            print(msg)
            self.error_stream(msg)
            switch_state(self, DevState.FAULT, msg)

        self._in_scan = False
        self._busy_outside_scan = False

        global_map.register(self, parents_list=["tetramm"])

        if self.debug_on:
            global_log.debugon(self)
            global_log.debugon(self.hw)
            global_log.debugoff(self.hw.comm)
        else:
            global_log.debugoff(self)
            global_log.debugoff(self.hw)

    def delete_device(self):
        if self.hw:
            self.hw = None

    @attribute(dtype=bool, doc="Enable/Disable log_debug")
    def debug(self):
        return self.debug_on

    @debug.setter
    def debug(self, value):
        self.debug_on = value
        if value:
            global_log.debugon(self)
            global_log.debugon(self.hw)
            global_log.debugoff(self.hw.comm)
            global_log._stdout_handler.setLevel(logging.DEBUG)
        else:
            global_log.debugoff(self)
            global_log.debugoff(self.hw)
            global_log._stdout_handler.setLevel(logging.NOTSET)  # set DEBUG level

    @attribute(dtype=bool, doc="Busy in scan")
    def in_scan(self):
        return self._in_scan

    @in_scan.setter
    def in_scan(self, value):
        self._in_scan = value

    @attribute(dtype=bool, doc="Busy outside scan")
    def busy_outside_scan(self):
        return self._busy_outside_scan

    @busy_outside_scan.setter
    def busy_outside_scan(self, value):
        self._busy_outside_scan = value

    @attribute(dtype=bool)
    def is_trg(self):
        return self.hw.is_trg

    @attribute(dtype=bool)
    def is_bias(self):
        return self.hw.is_bias

    @attribute(dtype=int, doc="Last programmed nb of active channels")
    def last_nch(self):
        return self.hw.last_nch

    @attribute(dtype=int, doc="Last programmed nb of acquisitions")
    def last_naq(self):
        return self.hw.last_naq

    @attribute(dtype=float, doc="Last programmed transfer rate", unit="Hz")
    def last_data_rate(self):
        return self.hw.last_data_rate

    @attribute(dtype=int, doc="Last programmed nb of triggers")
    def last_ntrg(self):
        return self.hw.last_ntrg

    @attribute(
        dtype=int, doc="Last number of averaged sampled data per single acquisition"
    )
    def last_nrsamp(self):
        return self.hw.last_nrsamp

    # --- SCAN COMMANDS/ATTRIBUTES (allowed during a scan) ---

    @command(
        dtype_in=str, dtype_out=str, doc_in="Query command", doc_out="Query answer"
    )
    def query(self, cmd):
        return self.hw.query(cmd)

    @attribute(dtype=str, doc="The model version")
    def version(self):
        return self.hw.version

    @command(dtype_in=(int,))
    def prepare_acq_once(self, pars):
        """Should be called by _prepare_device() in acquisition slave."""
        self.hw.prepare_acq_once(pars)

    @command
    def acq_on(self):
        """Should be called by start_device() in acquisition slave."""
        self.hw.acq_on()
        self.set_state(DevState.RUNNING)

    @command
    def acq_off(self):
        self.hw.acq_off()
        self.set_state(DevState.ON)

    @command
    def trg_off(self):
        self.hw.trg_off()

    @command
    def trg_on(self):
        self.hw.trg_on()

    @command(dtype_out=bool)
    def readout(self):
        log_debug(self, "DS readout(): Starting")
        try:
            self.hw.readout()
        except Exception as ex:
            log_warning(self, "DS readout(): Got an exception %s", ex)
            self.set_state(DevState.FAULT)
            Except.throw_exception("Got an exception", str(ex), "readout")

        log_debug(self, "DS readout(): Got %d  data", len(self.hw.data))
        log_debug(self, "DS readout(): Exiting")
        self.set_state(DevState.ON)
        # just for the async call reply
        return True

    @command(dtype_in=int, dtype_out=(float,))
    def get_data(self, from_index):
        """Should be called by get_values() in counter controller."""
        return self.hw.get_data(from_index)

    @attribute(dtype=int, doc="Las acquired point number")
    def last_acq_point_nb(self):
        return self.hw.last_acq_point_nb

    @command
    def empty_buffer(self):
        self.hw.empty_buffer()
        self._in_scan = False

    # --- OTHER COMMANDS/ATTRIBUTES (banned during a scan) ---

    @command(
        dtype_in=int,
        doc_in="number of acq. for the calibration procedure, please make sure to stop the beam",
    )
    def calibrate_dark(self, nacq):
        if not self._in_scan:
            self.hw.calibrate_dark(nacq)

    @command(dtype_in=str, dtype_out=(float,))
    def get_dark_offset(self, value):
        """Get current dark offset of all channels."""
        if not self._in_scan:
            self._busy_outside_scan = True
            ans = self.hw.get_dark_offset(value)
            self._busy_outside_scan = False
            return ans
        else:
            return self.hw._nch * [None]

    @attribute(dtype=str, doc="User correction on/off")
    def usercorr(self):
        if not self._in_scan:
            self._busy_outside_scan = True
            usercorr = self.hw.usercorr
            self._busy_outside_scan = False
            return usercorr
        else:
            return ""

    @usercorr.setter
    def usercorr(self, value):
        if not self._in_scan:
            self._busy_outside_scan = True
            self.hw.usercorr = value
            self._busy_outside_scan = False

    @attribute(dtype=int, doc="The number of active channels (1, 2 or 4")
    def nch(self):
        if not self._in_scan:
            self._busy_outside_scan = True
            nch = self.hw.nch
            self._busy_outside_scan = False
            return nch
        else:
            return 0

    @nch.setter
    def nch(self, value):
        if not self._in_scan:
            self._busy_outside_scan = True
            self.hw.nch = value
            self._busy_outside_scan = False

    @attribute(dtype=str, doc="Trigger polarity")
    def trg_pol(self):
        if not self._in_scan:
            self._busy_outside_scan = True
            trig_pol = self.hw.trg_pol
            self._busy_outside_scan = False
            return trig_pol
        else:
            return ""

    @trg_pol.setter
    def trg_pol(self, pol):
        if not self._in_scan:
            self._busy_outside_scan = True
            self.hw.trg_pol = pol
            self._busy_outside_scan = False

    @attribute(dtype=str, doc="interface configuration")
    def ifconfig(self):
        if not self._in_scan:
            self._busy_outside_scan = True
            ifconfig = self.hw.ifconfig
            self._busy_outside_scan = False
            return ifconfig
        else:
            return ""

    @command(dtype_in=float, dtype_out=str)
    def raw_read(self, timeout):
        # use only for debugging purposes
        if not self._in_scan:
            self._busy_outside_scan = True
            ans = self.hw.comm.read(size=8, timeout=timeout)
            self._busy_outside_scan = False
            return ans
        else:
            return ""

    @attribute(dtype=float, doc="The temperature")
    def temperature(self):
        if not self._in_scan:
            self._busy_outside_scan = True
            return self.hw.get_temperature()
            self._busy_outside_scan = False
        else:
            return 0

    @command(dtype_out=(float,))
    def get_current(self):
        self._busy_outside_scan = True
        data = []
        if not self._in_scan:
            try:
                data = self.hw.get_current()
                if len(data) != 4:
                    data = [0, 0, 0, 0]
            except Exception:
                data = [0, 0, 0, 0]
            finally:
                self._busy_outside_scan = False
        else:
            data = np.array(self.hw.last_data)

        self._busy_outside_scan = False
        return data

    @attribute(dtype=float, doc="Data transfer rate", unit="Hz")
    def data_rate(self):
        if not self._in_scan:
            self._busy_outside_scan = True
            ans = float(self.hw.data_rate)
            self._busy_outside_scan = False
            return ans
        else:
            return self.hw.last_data_rate

    @data_rate.setter
    def data_rate(self, value):
        if not self._in_scan:
            self._busy_outside_scan = True
            self.hw.data_rate = float(value)
            self._busy_outside_scan = False

    @attribute(dtype=int, doc="Averaged samples")
    def nrsamp(self):
        if not self._in_scan:
            self._busy_outside_scan = True
            ans = self.hw.nrsamp
            self._busy_outside_scan = False
            return ans
        else:
            return self.hw.last_nrsamp

    @nrsamp.setter
    def nrsamp(self, value):
        self._busy_outside_scan = True
        self.hw.nrsamp = value
        self._busy_outside_scan = False

    @attribute(dtype=bool, doc="True if there is no Bias voltage source in this model")
    def empty_slot(self):
        return self.hw.empty_slot

    @command
    def bias_on(self):
        self.hw.bias_on()

    @command
    def bias_off(self):
        self.hw.bias_off()

    @attribute(dtype=float, doc="Bias voltage set point", unit="V")
    def bias(self):
        # return -1 if OFF
        if not self._in_scan:
            self._busy_outside_scan = True
            ans = self.hw.bias
            self._busy_outside_scan = False
            return ans
        else:
            return 0

    @bias.setter
    def bias(self, value):
        if not self._in_scan:
            self._busy_outside_scan = True
            self.hw.bias = value
            self._busy_outside_scan = False

    @attribute(dtype=(float,), max_dim_x=2)
    def bias_range(self):
        return self.hw.bias_range

    @command(dtype_out=(str,))
    def get_supported_ranges(self):
        """Get all available current range"""
        if not self._in_scan:
            self._busy_outside_scan = True
            ans = [r for r in self.hw.all_ranges.values()]
            self._busy_outside_scan = False
            return ans
        else:
            return ["", "", "", ""]

    @command(dtype_out=float)
    def get_bias_current(self):
        if not self._in_scan:
            self._busy_outside_scan = True
            bias = self.hw.get_bias_current()
            self._busy_outside_scan = False
        else:
            bias = 0
        return bias

    @command(dtype_out=float)
    def get_bias_voltage(self):
        if not self._in_scan:
            self._busy_outside_scan = True
            bias = self.hw.get_bias_voltage()
            self._busy_outside_scan = False
        else:
            bias = 0
        return bias

    @command(dtype_in=str, dtype_out=(str,))
    def get_range(self, value):
        """Get current range status of all channels."""
        if not self._in_scan:
            self._busy_outside_scan = True
            ans = self.hw.get_range(value)
            self._busy_outside_scan = False
            return ans
        else:
            return self.hw._nch * [""]

    @command(dtype_in=str)
    def set_range(self, value):
        """Set current range of all channels."""
        if not self._in_scan:
            self._busy_outside_scan = True
            self.hw.set_range(value, channel="all")
            self._busy_outside_scan = False

    @command(dtype_in=str)
    def set_range_ch1(self, value):
        if not self._in_scan:
            self._busy_outside_scan = True
            self.hw.set_range(value, channel="1")
            self._busy_outside_scan = False

    @command(dtype_in=str)
    def set_range_ch2(self, value):
        if not self._in_scan:
            self._busy_outside_scan = True
            self.hw.set_range(value, channel="2")
            self._busy_outside_scan = False

    @command(dtype_in=str)
    def set_range_ch3(self, value):
        if not self._in_scan:
            self._busy_outside_scan = True
            self.hw.set_range(value, channel="3")
            self._busy_outside_scan = False

    @command(dtype_in=str)
    def set_range_ch4(self, value):
        if not self._in_scan:
            self._busy_outside_scan = True
            self.hw.set_range(value, channel="4")
            self._busy_outside_scan = False


def main():
    # prepare for debug logging
    global_log.start_stdout_handler()
    global_log._stdout_handler.setLevel(logging.DEBUG)
    format = "%(levelname)s %(asctime)-15s %(name)s: %(message)s"
    fmt = logging.Formatter(format)
    global_log._stdout_handler.setFormatter(fmt)

    run([TetrammServer], green_mode=GreenMode.Gevent)


if __name__ == "__main__":
    main()
