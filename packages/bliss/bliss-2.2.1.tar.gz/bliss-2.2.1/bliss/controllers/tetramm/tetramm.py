# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

"""Module to communicate with Tetramm picoammeter."""

import struct
import numpy as np

from bliss import global_map

# from bliss.comm.tcp import SocketTimeout
from bliss.comm.util import get_comm, TCP
from bliss.comm.exceptions import CommunicationTimeout
from bliss.common.tango import CommunicationFailed, DeviceProxy
from bliss.common.protocols import counter_namespace
from bliss.common.logtools import log_debug, log_warning, log_error
from bliss.common.utils import autocomplete_property

from bliss.controllers.bliss_controller import BlissController
from bliss.controllers.tetramm.tetramm_icc import TetrammICC
from bliss.controllers.tetramm.tetramm_icc import TetrammCounter  # noqa F401


class Tetramm(BlissController):
    def __init__(self, config):
        """Tetramm device.

        config -- controller configuration node
        """
        super().__init__(config)

        name = config["name"]
        log_debug(self, "Initialize Tetramm %s", name)

        if "tango" in config:
            tango = config.get("tango")
            self._hw = DeviceProxy(tango.get("name"))
            self._is_tango = True
        else:
            self._is_tango = False
            self._hw = TetrammHw(config)

        # Construct counter controller
        self._controller = TetrammICC(name, self)

        global_map.register("tetramm", parents_list=["global"])
        global_map.register(
            self,
            parents_list=["tetramm", "controllers", "counters"],
            children_list=[self._hw, self._controller],
        )

    def _init(self):
        """Called once the config has been loaded"""
        # Construct the declared counters
        for cfg in self.config.get("counters"):
            self._get_subitem(cfg["name"])

    @property
    def is_tango(self):
        return self._is_tango

    @property
    def name(self):
        return self._controller.name

    @autocomplete_property
    def counters(self):
        return self._controller.counters

    @property
    def trigger_mode(self):
        """Return the current trigger mode"""
        return self._controller.trigger_mode

    @property
    def counter_groups(self):
        groups = dict()
        groups["default"] = self._controller.counters
        return counter_namespace(groups)

    def __info__(self):
        lines = []
        if self._is_tango:
            lines.append(f"=== Tetramm: {self.name} (tango: {self._hw.name()}) ===")
        else:
            lines.append(f"=== Tetramm: {self.name}  ===")
        empty = "Absent" if self.empty_slot else f"Present ({self._hw.bias_range}V)"
        lines.append(f"  Bias Voltage Source:       {empty}")
        lines.append(f"  Nb. of channels (nch):     {self._hw.last_nch}")
        lines.append(f"  Averaged samples (nrsamp): {self._hw.last_nrsamp}")
        lines.append(f"  Data rate (data_rate):     {self._hw.last_data_rate}")
        ranges = self.get_range()
        all_ranges = self.get_supported_ranges()
        lines.append(f"  Supported ranges:          {all_ranges}")
        lines.append(f"  Channel ranges:            {ranges}")
        offsets = self.get_dark_offset()
        lines.append(f"  Dark correction is:        {self._hw.usercorr}")
        lines.append(f"  Channel dark offsets:      {offsets}")
        lines.append("")
        try:
            current = self._hw.get_current()
            for v, cnt in zip(current, self.counters):
                lines.append(f"  - {cnt.name}: {v:.3e} {cnt.unit}")
        except CommunicationFailed:
            lines.append("Measurements not available (is the device online?)")
        return "\n".join(lines)

    def _get_subitem_default_class_name(self, cfg, parent_key):
        return "TetrammCounter"

    def _create_subitem_from_config(
        self, name, cfg, parent_key, item_class, item_obj=None
    ):
        if parent_key == "counters":
            return item_class(cfg, self._controller)

    def _get_default_chain_counter_controller(self):
        """Return the default counter controller that should be used
        when this controller is used to customize the DEFAULT_CHAIN
        """
        return self._controller

    # ---------------------------------------------------------
    # Properties and functions to access the hardware features
    # just a mapping of the low level class TetrammHw

    @property
    def usercorr(self):
        return self._hw.usercorr

    @usercorr.setter
    def usercorr(self, value: str):
        self._hw.usercorr = value

    def calibrate_dark(self, nacq=5000):
        print(
            "Running Tetramm offset calibration procedure, please make sure to stop the beam...\n"
        )
        self._hw.calibrate_dark(nacq)
        print("=======> New dark offsets:")
        self.get_dark_offset()

        print(f"\nDark correction (usercorr) is {self.usercorr}")

    @property
    def data_rate(self):
        return self._hw.data_rate

    @data_rate.setter
    def data_rate(self, value):
        """Sampling rate (100 kHz) / number of averaged samples (nrsamp).

        The max data rate transfer is:
        - 100 Hz when ASCII format is enabled (NRSAMP=500)
        - 20 kHz when ASCII format is disabled (NRSAMP=5)

        """
        self._hw.data_rate = value

    @property
    def nrsamp(self):
        """Number of averaged samples"""
        return self._hw.nrsamp

    @nrsamp.setter
    def nrsamp(self, value):
        self._hw.nrsamp = value

    @property
    def trg_pol(self):
        return self._hw.trg_pol

    @trg_pol.setter
    def trg_pol(self, pol: str):
        self._hw.trg_pol = pol

    def get_supported_ranges(self):
        """Return the supported ranges"""
        return self._hw.get_supported_ranges()

    def get_range(self, channel="all"):
        """Return the range of the 4 channels"""
        return self._hw.get_range(channel)

    def set_range(self, value="auto"):
        """Set current range of all channels, default is auto"""
        self._hw.set_range(value)

    def set_range_ch1(self, value="auto"):
        """Set current range of channel 1, default is auto"""
        if self.is_tango:
            self._hw.set_range_ch1(value)
        else:
            self._hw.set_range(value, channel=1)

    def set_range_ch2(self, value="auto"):
        """Set current range of channel 2, default is auto"""
        if self.is_tango:
            self._hw.set_range_ch2(value)
        else:
            self._hw.set_range(value, channel=2)

    def set_range_ch3(self, value="auto"):
        """Set current range of channel 3, default is auto"""
        if self.is_tango:
            self._hw.set_range_ch3(value)
        else:
            self._hw.set_range(value, channel=3)

    def set_range_ch4(self, value="auto"):
        """Set current range of channel 4, default is auto"""
        if self.is_tango:
            self._hw.set_range_ch4(value)
        else:
            self._hw.set_range(value, channel=4)

    def get_dark_offset(self, channel="all"):
        """Return the dark offset of the 4 channels"""
        return self._hw.get_dark_offset(channel)

    @property
    def empty_slot(self):
        """True if there is no voltage source in this model"""
        return self._hw.empty_slot

    def bias_on(self):
        """Enable bias source and set voltage to zero"""
        self._hw.bias_on()

    def bias_off(self):
        """Disable bias source and set voltage to zero"""
        self._hw.bias_off()

    @property
    def bias(self):
        """Get bias voltage set point (V) or nan if OFF"""
        return self._hw.bias

    @bias.setter
    def bias(self, value):
        """Set bias voltage set point (V)"""
        self._hw.bias = value

    def get_bias_current(self):
        """Get measured bias current (A)"""
        return self._hw.get_bias_current()

    def get_bias_voltage(self):
        """Get measured bias voltage (V)"""
        return self._hw.get_bias_voltage()


class TetrammHw:
    def __init__(
        self,
        config=None,
        url="localhost",
        port=10001,
        timeout=0.005,
        debug=True,
    ):
        if config is not None:
            url = config.get("tcp")["url"]
            port = config.get("tcp")["port"]
            timeout = config.get("timeout", timeout)
            debug = config.get("debug", debug)
            trig_pol = config.get("trigger_polarity", "POS")

        log_debug(self, "comm: %s:%d", url, port)

        conf = {"tcp": ""}
        opts = {"url": url, "port": port, "eol": b"\r\n"}
        self.comm = get_comm(conf, ctype=TCP, **opts)

        self.url = url
        self.timeout = timeout
        self.debug = debug
        self.trigger_polarity = trig_pol

        # --- setup ---

        ans = self.write_readline(b"VER:?").split(b":")
        self._firmware_version = ans[2]
        ans3 = ans[3].split()
        self._nch = int(ans3[0].strip(b"IV"))
        rg0 = ans3[1][:-1].lower() + b"A"
        rg1 = ans3[2][:-1].lower() + b"A"
        self.all_ranges = {0: rg0.decode(), 1: rg1.decode()}

        # if BIAS option
        if ans[4] != b"EMPTY SLOT":
            # ans4 = b'HV 30V POS'
            ans4 = ans[4].split()
            if ans4[0] == b"HV":
                bias_max = "+" if ans4[2] == b"POS" else "-"
                bias_max += ans4[1][:-1].decode()
                bias_max = int(bias_max)
                bias_min = 0 if bias_max > 0 else bias_max
                bias_max = 0 if bias_max < 0 else bias_max
            # ans 4 = b'LV +/- 30 V'
            elif ans4[0] == b"LV":
                bias_max = int(ans4[2].decode())
                bias_min = -bias_max
            self._bias_range = (bias_min, bias_max)
            self.is_bias = False if self.bias == -1 else True
            self._empty_slot = False
        else:
            self._bias_range = (0, 0)
            self.is_bias = False
            self._empty_slot = True
        self.naq = 1
        self.ntrg = 1
        self.nrsamp = 100  # rate = 100e3/100
        self.trg_off()  # sets 'is_trg' to False
        self.trg_pol = trig_pol

        self.data = None  # scan data buffer
        self.acq_is_on = False

        self.last_data = np.array([], dtype=float)

        # Set ASCCI mode OFF
        self.command("ASCII:OFF")

        global_map.register(
            self,
            parents_list=["tetramm"],
            # children_list=[self.comm],
        )
        global_map.register(self.comm, parent_list=[self, "comms"])

    def command(self, cmd: str):
        """Send a command and check the answer status (ACK / NAK)"""
        cmd = cmd.encode()
        cmd += b"\r\n"
        ans = self.comm.write_readline(cmd)
        if ans != b"ACK":
            raise RuntimeError(f"Command {cmd} failed with error code {ans[:4]}")
        return ans

    def query(self, cmd: str):
        cmd = cmd.encode()
        cmd += b":?\r\n"
        ans = self.comm.write_readline(cmd)
        ans = ans.split(b":")[-1]
        return ans

    def write(self, cmd: bytes):
        cmd += b"\r\n"
        self.comm.write(cmd)

    def write_readline(self, cmd: bytes, eol=b"\r\n"):
        if not cmd.endswith(b"\r\n"):
            cmd += b"\r\n"
        ans = self.comm.write_readline(cmd, eol=eol)
        return ans

    def calibrate_dark(self, nacq=5000):
        print("Tetramm offset calibration procedure, please make sure to stop the beam")

        # save status
        is_correction_used = self.usercorr == "ON"
        self.trg_off()  # sets 'is_trg' to False

        data_rate = self.data_rate
        self.usercorr = "off"
        self.data_rate = 10
        for acq_range in (0, 1):
            self.set_range(acq_range)
            darks = [self.get_current() for i in range(nacq)]
            darks = np.asarray(darks)
            darks = darks.mean(axis=0)
            for channel in range(1, 5):
                dark = -darks[channel - 1]  # channel 1 is zero-th element ...
                cmd = f"USRCORR:RNG{acq_range}CH{channel}OFFS:{dark}"
                self.command(cmd)

        # put things back
        if is_correction_used:
            print("Tetramm: re-enabling user correction")
            self.usercorr = "on"
        self.data_rate = data_rate

    def get_dark_offset(self, channel):
        channels = ("all", "1", "2", "3", "4")
        if str(channel).lower() not in channels:
            raise ValueError("'channel' should be one of ", channels)

        ch_rawrng, ch_autorng = self.get_ranges()

        ch_offset = []
        for ch, rng in zip(range(1, 5), ch_rawrng):
            offset = float(self.query(f"USRCORR:RNG{rng}CH{ch}OFFS"))
            ch_offset.append(offset)

        if isinstance(channel, str) and channel.lower() == "all":
            return ch_offset
        else:
            return [ch_offset[int(channel) - 1]]

    @property
    def ifconfig(self):
        return (b"\n".join(self.comm.write_readlines(b"IFCONFIG\r\n", 7))).decode()

    @property
    def version(self):
        return self.write_readline(b"VER:?").decode()

    @property
    def nch(self):
        """Returns the number of active channels (1, 2 or 4)."""
        self._nch = int(self.query("CHN"))
        return self._nch

    @nch.setter
    def nch(self, value):
        """Set number of active channels (1, 2 or 4)."""
        value = int(value)
        if value not in [1, 2, 4]:
            raise ValueError("'value' must be 1, 2 or 4")
        self.write_readline(b"CHN:%d" % value)
        self._nch = value

    @property
    def last_nch(self):
        """Returns the number of active channels (1, 2 or 4)."""
        return self._nch

    @property
    def usercorr(self):
        return self.query("USRCORR").decode()

    @usercorr.setter
    def usercorr(self, value: str):
        if value.lower() not in ("off", "on"):
            raise ValueError("usercorr must be 'off' or 'on' (lower or uppercase)")
        value = value.upper()
        cmd = f"USRCORR:{value}"
        self.command(cmd)

    @property
    def naq(self):
        self._naq = int(self.query("NAQ"))
        return self._naq

    @naq.setter
    def naq(self, value: int):
        if not isinstance(value, (int, np.int64)):
            raise TypeError("'naq' must be int")
        self.write_readline(b"NAQ:%d" % value)
        self._naq = value

    @property
    def last_naq(self):
        return self._naq

    @property
    def nrsamp(self):
        """Number of averaged sampled data per single acquisition."""
        ans = self.query("NRSAMP")
        self._nrsamp = int(ans)
        self._data_rate = 100e3 / self._nrsamp
        return self._nrsamp

    @nrsamp.setter
    def nrsamp(self, value):
        """Set the number of averaged sampled data."""
        if not isinstance(value, int):
            raise TypeError("'nrsamp' must be int.")
        self.write_readline(b"NRSAMP:%d" % value)
        self._nrsamp = value
        self._data_rate = 100e3 / self._nrsamp

    @property
    def last_nrsamp(self):
        return self._nrsamp

    @property
    def data_rate(self):
        """Sampling rate (100 kHz) / number of averaged samples."""
        rate = 100e3 / self._nrsamp
        log_debug(self, "data_rate: 100e3 / %d = %f", self._nrsamp, rate)
        return rate

    @data_rate.setter
    def data_rate(self, value):
        """Sampling rate (100 kHz) / number of averaged samples.

        The max data rate transfer is:
        - 100 Hz when ASCII format is enabled (NRSAMP=500)
        - 20 kHz when ASCII format is disabled (NRSAMP=5)

        """
        self.nrsamp = int(100e3 / value) - 1

    @property
    def last_data_rate(self):
        return self._data_rate

    @property
    def ntrg(self):
        self._ntrg = int(self.query("NTRG"))
        return self._ntrg

    @ntrg.setter
    def ntrg(self, value):
        if not isinstance(value, (int, np.int64)):
            raise TypeError("'ntrg' must be int")
        self.write_readline(b"NTRG:%d" % value)
        self._ntrg = value

    @property
    def last_ntrg(self):
        return self._ntrg

    def trg_on(self):
        self.command("TRG:ON")
        self.is_trg = True

    def trg_off(self):
        self.command("TRG:OFF")
        self.is_trg = False

    @property
    def trg_pol(self):
        return self.query("TRGPOL")

    @trg_pol.setter
    def trg_pol(self, pol: str):
        if pol not in ["NEG", "POS"]:
            raise ValueError("Invalid polarity [NEG, POS]")
        self.command("TRGPOL:" + pol)

    # BIAS VOLTAGE SOURCE CONTROL
    @property
    def empty_slot(self):
        """True if there is no voltage source in this model"""
        return self._empty_slot

    def bias_on(self):
        """Enable bias source and set voltage to zero."""
        self.command("HVS:ON")
        self.is_bias = True

    def bias_off(self):
        """Disable bias source and set voltage to zero."""
        self.command("HVS:OFF")
        self.is_bias = False

    @property
    def bias(self):
        """Get bias voltage set point (V)"""
        ans = self.query("HVS").decode()
        return np.nan if ans == "OFF" else float(ans)

    @bias.setter
    def bias(self, value):
        """Set bias voltage set point (V)."""

        if not isinstance(value, (int, float)):
            raise TypeError("'Bias value' must int or float.")

        if not (self._bias_range[0] <= value <= self._bias_range[1]):
            raise ValueError(f"Bias range is  {self._bias_range}")
        elif not self.is_bias:
            self.bias_on()

        value = float(value)
        self.write_readline(b"HVS:%f" % value)

    @property
    def bias_range(self):
        return self._bias_range

    def get_bias_current(self):
        """Get measured bias current (A)."""
        return float(self.query("HVI"))

    def get_bias_voltage(self):
        """Get measured bias voltage (V)."""
        return float(self.query("HVV"))

    def get_register_status(self):
        """Get TetrAMM register status (48 bits)."""
        ans = self.query("STATUS")
        bits = bin(int(ans, 16))[2:]
        bits = bits[::-1]
        if len(bits) < 47:
            bits += (47 - len(bits)) * "0"
        return bits

    def get_supported_ranges(self):
        """Get all supported ranges"""
        return [r for r in self.all_ranges.values()]

    def get_ranges(self):
        """Get current range of all channels."""

        bits = self.get_register_status()
        ch_rawrng = [bits[24], bits[28], bits[32], bits[36]]
        ch_autorng = [bool(int(bit)) for bit in bits[16:20]]

        return ch_rawrng, ch_autorng

    def get_range(self, channel="all"):
        """Get current range of all channels or of a selected channel."""

        channels = ("all", "1", "2", "3", "4")
        if str(channel).lower() not in channels:
            raise ValueError("'channel' should be one of ", channels)

        ch_rawrng, ch_autorng = self.get_ranges()

        ch_rng = []
        for autorng, rawrng in zip(ch_autorng, ch_rawrng):
            rng = self.all_ranges[int(rawrng)]
            if autorng:
                ch_rng.append(f"{rng} (AUTO ON)")
            else:
                ch_rng.append(rng)

        if isinstance(channel, str) and channel.lower() == "all":
            return ch_rng
        else:
            return [ch_rng[int(channel) - 1]]

    def set_range(self, value="auto", channel="all"):
        """Set current range of all channels or of a selected channel."""

        if not isinstance(value, (str, int, float)):
            raise TypeError("'value' must be str, int or float.")

        channels = ("all", "1", "2", "3", "4")
        if str(channel).lower() not in channels:
            raise ValueError("'channel' should be one of ", channels)

        if isinstance(value, float):
            all_values = [r[:-2] for r in self.all_ranges.values()]
            all_units = [r[-2] for r in self.all_ranges.values()]
            unit = {"n": 1e-9, "u": 1e-6, "m": 1e-3}
            all_ranges = [float(v) * unit[u] for v, u in zip(all_values, all_units)]
            if not any(np.isclose(value, all_ranges, rtol=0.25)):
                raise ValueError("'value' must be close to one of", all_ranges)
            for k, r in enumerate(all_ranges):
                if np.isclose(value, r, rtol=0.25):
                    value = k
                    break

        if isinstance(value, int):
            if value not in [0, 1]:
                raise ValueError("'value' must be 0 or 1 if int.")

        if isinstance(value, str):
            all_ranges = [k for k in self.all_ranges.values()]
            all_ranges.append("0")
            all_ranges.append("1")
            if value not in all_ranges and value.lower() != "auto":
                raise ValueError("'value' must be 'auto' or one of ", all_ranges)
            if value == all_ranges[0] or value == "0":
                value = 0
            if value == all_ranges[1] or value == "1":
                value = 1
            else:
                value = "auto"

        # at this point 'value' can be only 'auto', 0 or 1
        value_bytes = str(value).upper().encode()

        if channel == "all":
            cmd = b"RNG:%s" % value_bytes
            self.write_readline(cmd)
        else:
            initial_ranges, auto_ranges = self.get_ranges()
            # if all channels are in "AUTO", they have to be set to manual
            # before a different setting for each channel can be used
            self.write_readline(b"RNG:0")
            # apply range to channel
            self.write_readline(b"RNG:CH%s:%s" % (channel.encode(), value_bytes))
            # restore all other channels
            for k, r in enumerate(initial_ranges):
                if (k + 1) != int(channel):
                    if auto_ranges[k]:
                        self.write_readline(b"RNG:CH%d:AUTO" % (k + 1))
                    else:
                        self.write_readline(b"RNG:CH%d:%s" % (k + 1, r.encode()))

    def acq_on(self):
        log_debug(self, "acq_on()")
        self.write(b"ACQ:ON")
        self.acq_is_on = True

    def acq_off(self):
        log_debug(self, "acq_off()")
        self.acq_is_on = False
        self.command("ACQ:OFF")

    def readout(self):
        log_debug(self, "readout(): Entering")

        # Run the readout loop and fill the output array
        try:
            data = []
            nb_header = 0
            nb_end_of_trig = 0
            nb_end_of_acq = 0
            previous_seq = 0

            # SIZEOF_FLOAT = 8
            # seq_len = SIZEOF_FLOAT * (
            #     (self._nch + 1) +  # header
            #     (self._nch + 1)  # data + footer
            #     (self._nch + 1)  # end of trigger
            # )
            if self._nrsamp >= 100:
                timeout = 3
            else:
                timeout = 1
            while True:
                # Acquistion been stopped, exit
                if not self.acq_is_on:
                    break
                try:
                    b = self.comm.read(8, timeout=timeout)
                except CommunicationTimeout as ex:
                    log_error(
                        self,
                        "readout(): Got a socket.read() exception (%s), stopping",
                        ex,
                    )
                    raise ex
                except Exception as ex:
                    log_warning(
                        self,
                        "readout(): Got a socket.read() exception (%s), continuing",
                        ex,
                    )
                    continue

                # if is sNaN
                if b[:3] == b"\xff\xf4\x00":
                    # log_debug(self, "readout(): sNaN: %s", b.hex())
                    if b[3:] == b"\00\xff\xff\xff\xff":
                        # log_debug(self, "readout(): End of header")
                        pass
                    elif b[3:] == b"\01\xff\xff\xff\xff":
                        nb_end_of_trig += 1
                        # log_debug(self, "readout(): End of trig #%d", nb_end_of_trig)

                        if nb_end_of_trig > self._nch:
                            if self.is_trg and self._naq > 1:
                                # In hardware single trigger mode, we can count time > 1s, so multiple acquisitions are used
                                # and need to be aggregated
                                data = np.mean(
                                    np.array(data).reshape((-1, self._nch)), axis=0
                                ).tolist()
                            # log_debug(self, "readout(): Append the available %d data", len(data))
                            if self.data is None:
                                self.data = data
                            else:
                                self.data.extend(data)

                            data = []
                            nb_end_of_trig = 0
                    elif b[3:] == b"\02\xff\xff\xff\xff":
                        # log_debug(self, "readout(): Got footer")
                        pass
                    elif b[3:] == b"\03\xff\xff\xff\xff":
                        nb_end_of_acq += 1
                        log_debug(self, "readout(): end of acq  #%d", nb_end_of_acq)
                        if nb_end_of_acq > self._nch:
                            # End of acquisition
                            if not self.is_trg and self._naq > 1:
                                # In software trigger mode, we can count time > 1s, so multiple acquisitions are used
                                # and need to be aggregated
                                data = np.mean(
                                    np.array(data).reshape((-1, self._nch)), axis=0
                                ).tolist()
                            # log_debug(self, "readout(): Append the available %d data", len(data))
                            if self.data is None:
                                self.data = data
                            else:
                                self.data.extend(data)

                            data = []
                            nb_end_of_acq = 0
                            break
                    else:
                        nb_header += 1

                        seq = struct.unpack(">i", b[4:])[0]
                        # log_debug(self, "readout(): header #%d", seq)

                        if nb_header >= self._nch:
                            log_debug(self, "readout(): Got all headers for #%d", seq)
                            if previous_seq == 0 or seq == previous_seq + 1:
                                previous_seq = seq
                            else:
                                log_warning(
                                    self,
                                    "readout(): Dropped data, seq. expected=%d, received=%d",
                                    previous_seq + 1,
                                    seq,
                                )
                                raise RuntimeError(
                                    self,
                                    "Dropped data: seq. expected=%d, received=%d"
                                    % (previous_seq + 1, seq),
                                )
                            nb_header = 0
                else:
                    val = struct.unpack(">d", b)[0]
                    # log_debug(self, "readout(): read %d", val)
                    data.append(val)

        except Exception as ex:
            log_warning(self, "readout():An exception occured %s", ex)
            raise

        log_debug(self, "readout(): Exiting")

    def empty_buffer(self):
        try:
            self.comm.flush()
        except Exception:
            pass

    def get_current(self):
        """Read back a single snapshot of the values for the active channels"""

        if self._nch != 4:
            self.nch = 4

        self.naq = 1

        if self._ntrg != 1:
            self.ntrg = 1

        self.comm.write("ACQ:ON\r\n".encode())
        eol = b"\xff\xf4\x00\x03\xff\xff\xff\xff" * 5
        buf = self.comm.readline(eol=eol)

        data = self.parse_binary_buffer(buf).flatten()

        ## Unpack
        # fmt = ">" + "d" * int(len(buf) / 8)
        # data = struct.unpack(fmt, buf)

        return data

    def parse_binary_buffer(self, buf):

        nbytes = 8 * (self._nch + 1)  # number of bytes in a single acquisition

        if buf[-5:] == b"ACK\r\n":
            buf = buf[:-5]

        if buf[-8:] == b"\xff\xf4\x00\x03\xff\xff\xff\xff":
            buf = buf[:-nbytes]

        fmt = ">" + "d" * (self._nch + 1)

        data = [
            struct.unpack(fmt, buf[k : k + nbytes])[:-1]
            for k in range(0, len(buf), nbytes)
        ]

        data = np.array(data)

        return data

    def get_temperature(self):
        ans = self.comm.write_readline(b"TEMP\r\n", timeout=1)
        if ans[:4] == b"TEMP":
            return int(ans[5:])
        raise RuntimeError("Failed to parse TEMP command response")

    def get_data(self, from_index):
        """Should be called by get_values() in counter controller."""
        if self.data is None:
            data = np.array([], dtype=float)
        else:
            from_index = from_index * self._nch
            self.last_data = np.array(self.data[-1 * self._nch :])
            data = np.array(self.data[from_index:])

        return data

    @property
    def last_acq_point_nb(self):
        if self.data:
            return int(len(self.data) / self._nch)
        else:
            return 0

    def prepare_acq_once(self, pars):
        """Should be called by _prepare_device() in acquisition slave."""
        naq, ntrg, nch = pars
        if nch != self.nch:
            self.nch = nch
        if naq != self.naq:
            self.naq = naq
        if ntrg != self.ntrg:
            self.ntrg = ntrg
        self.data = None
        self.ndata = 0

        log_debug(
            self,
            "prepare_acq_once(): NRSAMP=%d, NAQ=%d, NTRG=%d, NCH=%d, IS_TRIG=%r",
            self._nrsamp,
            self.naq,
            self.ntrg,
            self.nch,
            self.is_trg,
        )
