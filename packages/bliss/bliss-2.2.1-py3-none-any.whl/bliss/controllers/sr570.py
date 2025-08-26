# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

"""
Stanford Research's SR570 Low-Noise Current Preamplifier.
Communicate with the devices through a serial line.

The SR570 serial parameters are:
- 9600 bauds
- 8 bits
- no parity
- 2 stop bits

"""

import re
import math
import enum

from bliss.comm.util import get_comm
from bliss.config.beacon_object import BeaconObject
from bliss.common.logtools import log_debug
from bliss.common.protocols import HasMetadataForScan


_SR570_UNITS = ["p", "n", "u", "m"]  # pico, nano, ...

_SENS_MIN_PAV = 1  # minimum range in pA/v
_SENS_MAX_PAV = 1e9  # maximum range in pA/v

_OFST_MIN_PAV = 1  # minimum range in pA/v
_OFST_MAX_PAV = 5e9  # maximum range in pA/v


def _command_to_unit(command):
    assert command in range(0, 30)
    return _SR570_UNITS[command // 9]


def _amps_to_command(value, minv=_SENS_MIN_PAV, maxv=_SENS_MAX_PAV, clip=True):
    """
    Converts ampers to a command that can be sent to the amplifier.
    See the doc : command is a value between 0 and 27 (sensitivity) or 29 (offset).

    Args:
        value: can either be a string value[unit] or a number.
            If value is a string, the unit (optional) can be either p, n, u or m.
            If unit is not provided, pA/V is assumed.
            If value is a number, the unit is assumed to be pA/V.
    """

    if isinstance(value, (str,)):
        m = re.match("(?P<amps>[^pnum]*)(?P<unit>[pnum]{0,1})", value)
        if not m:
            return -1
        gd = m.groupdict()
        amps = gd["amps"]
        unit = gd["unit"]

        # exception to be caught by caller
        amps = float(amps)

        # no negative value
        if amps <= 0:
            return -2

        if unit:
            # converting to pA/V
            amps = amps * 10 ** (3 * _SR570_UNITS.index(unit))
    else:
        amps = float(value)

    # minimum value: 1pA/v
    if amps < minv or amps > maxv:
        if not clip:
            return -2
        amps = max(min(amps, maxv), minv)

    # x is 0, 3, 6, ...
    x = int(math.log10(amps))
    # y can be 0, 1 or 2
    y = int(amps / 10**x)

    # out of supported range
    if x > 9:
        return -2
    if y >= 5:
        y = 2
    elif y >= 2:
        y = 1
    else:
        y = 0
    command = 3 * x + y
    return command


class SR570Commands(enum.Enum):
    SENS = ("Sensitivity", 0, 27)
    SUCM = ("Sensitivity calibration mode (1=uncalibrated)", 0, 1)
    SUCV = ("", 0, 100)
    IOON = ("Input offset curent (1=ON)", 0, 1)
    IOLV = ("Calibrated input offset current", 0, 29)
    IOSN = ("Input offset current sign (1=negative)", 0, 1)
    IOUC = ("Input offset calibration mode (1=uncalibrated", 0, 1)
    IOUV = ("Input offset vernier (in 1/10 %)", -1000, 1000)
    BSON = ("Bias voltage on/off (1=ON)", 0, 1)
    BSLV = ("Bias voltage level, in mV (-5V to 5V)", -5000, 5000)
    FLTT = ("Filter type", 0, 5)
    LFRQ = ("Low pass filter 3dB point", 0, 15)
    HFRQ = ("Highpass filtr 3dB", 0, 15)
    ROLD = ("Resets filter capacitors to clear an overload condition", None, None)
    GNMD = ("Amplifier gain mode", 0, 2)
    INVT = ("Signal invert sense (1=inverted)", 0, 1)
    BLNK = ("Blanks the front-end output (1=blank)", 0, 1)


class SR570(BeaconObject, HasMetadataForScan):
    """
    Stanford SR570 preamplifier.
    """

    def __init__(self, name, config):
        BeaconObject.__init__(self, config)
        HasMetadataForScan.__init__(self)
        self._comm = get_comm(config, eol="\r\n")
        self._sr570_settings = {}
        # self._force_init = self.config.get('force_init', False)
        # if self._force_init:
        self._init()
        log_debug(self, "__init__ done.")

    @BeaconObject.lazy_init
    def __info__(self):
        msg = "============\n"
        msg += "== SR 570 ==\n"
        msg += f" - name {self.name}\n"
        msg += f" - range: {self.sensitivity}"
        return msg

    @BeaconObject.lazy_init
    def _init(self):
        """
        QAD, only way to force setting params
        at initialization? i.e: disable lazy init
        """
        pass

    def _send_command(self, command, value):
        """
        WARNING: no check done on the command.
        """
        self._check_value(command, value)
        command_str = f"{command.name} {value}\r\n".encode("utf-8")
        log_debug(self, f"Sending: {command_str}.")
        self._comm.write(command_str)
        self._save_last_command_value(command, value)

    def _save_last_command_value(self, command, value):
        log_debug(self, f"Saving last know value for {command}: {value}.")
        self._sr570_settings[command.name] = value

    def _last_command_value(self, command):
        value = self._sr570_settings.get(command)
        if value is None:
            value = "UNKNOWN"
        log_debug(self, f"Last set {command.name}: {value}.")

    def _check_value(self, command, value):
        """
        Check if the value is within allowed range.
        """
        minval, maxval = command.value[1:3]
        if minval is None:
            if value is not None:
                raise ValueError(
                    f"The command {command.name} doesnt take any arguments."
                )
            return True
        if value not in range(minval, maxval + 1):
            raise ValueError(
                f"Value for command {command.name} must "
                f"be in range [{minval} .. {maxval}] "
                f"(got {value})."
            )

    @BeaconObject.property(default=27)
    def sensitivity(self):
        return self._last_command_value(SR570Commands.SENS)

    @sensitivity.setter
    def sensitivity(self, sensitivity):
        log_debug(self, f"User setting sensitivity to {sensitivity}.")
        value = _amps_to_command(sensitivity, _SENS_MIN_PAV, _SENS_MAX_PAV)
        print(f"User setting sensitivity to {sensitivity} ({value}).")
        self._send_command(SR570Commands.SENS, value)

    @BeaconObject.property(default=0)
    def bias(self):
        """
        Bias voltage, in mV
        """
        return self._last_command_value(SR570Commands.BSLV)

    @bias.setter
    def bias(self, bias):
        """
        Bias voltage, in mV
        Args:
            bias (integer): value between -5000 and 5000
        """
        bslv = int(bias)
        self._send_command(SR570Commands.BSLV, bslv)

    def scan_metadata(self):
        meta_dict = {"@NX_class": "NXcollection"}
        meta_dict["sensitivity"] = self.sensitivity
        meta_dict["bias"] = self.bias
        return meta_dict
