# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

"""
The Celeroton Fast Chopper is using serial line binary protocol.
A command always consist of a request package and a reply package,
containing at least an acknowledgment or an error code. The format is:
Request:

.. code-block::

             |-------------------- length ---------------------|
    ------------------------------------------------------------
    | length | command | data[0] | ... | data [n-1] | checksum |
    ------------------------------------------------------------
    |------------------ checksum -------------------|

Reply:

.. code-block::

    -------------------------------------------------------
    | length | ~command | LSB Error | MSB error| checksum |
    -------------------------------------------------------

Each block is 1 byte. The length includes all the blocks, except the length one.
The checksum is calculated on all the blocks, using the formula

.. code-block:: python

    checksum = (~(length+command+sum(data[0]...data[n-1]))+1) & 0xff

The serial line configuration is 57600 baud, 1 stop bit and 8 data bits.

Example yml configuration example:

.. code-block::

    name: fast_chopper
    class: Celeroton
    serial:
       url: "rfc2217://lid293:28010"       #serial line name
    or
    tango:
       url: id29/chopper/fast
"""
import struct
from bliss.comm.util import get_comm, SERIAL
from bliss.comm.serial import Serial

ERROR_CODE = {
    0x4001: "Unknown command",
    0x4002: "Wrong checksum",
    0x4004: "Invalid format",
    0x4008: "Read only",
    0x4010: "Type mismatch",
    0x4020: "Unknown variable",
    0x4040: "Save is not possible",
}

VARIABLE_CODE = {
    "Reference speed": 0x00,
    "Actual speed": 0x01,
    "DC-Link current": 0x02,
    "DC-Link current reference": 0x03,
    "Converter temperature": 0x04,
    "DC-Link voltage": 0x05,
    "Output power": 0x06,
    "Motor temperature (THC)": 0x07,
    "Motor temperature (PTC)": 0x08,
    "Pole pairs": 0x09,
    "Max. phase current": 0x0A,
    "Max. rotational speed": 0x0B,
    "Synchronization current": 0x0C,
    "Axial moment of inertia": 0x0D,
    "PM flux linkage": 0x0E,
    "Phase inductance": 0x0F,
    "Phase resistance": 0x10,
    "Rotation direction": 0x11,
    "Acc. Ratio (above sync.)": 0x12,
    "Acc. Ratio (below sync.)": 0x13,
    "Speed controller rise time": 0x14,
    "User defined sync. Speed": 0x15,
    "Default sync speed (lower)": 0x16,
    "Default sync speed (upper)": 0x17,
    "User def. sync speed (lower)": 0x18,
    "User def. sync speed (upper)": 0x19,
    "User defined control parameter": 0x1A,
    "Proportional speed gain": 0x1B,
    "Integral speed gain": 0x1C,
}

VARIABLE_TYPE = {
    "Int16": 0x01,
    "Uint16": 0x02,
    "Int32": 0x03,
    "Uint32": 0x04,
    "Float": 0x05,
}


class Celeroton:
    """Commands"""

    def __init__(self, name, config):
        self.name = name
        try:
            self._serial = get_comm(config, ctype=SERIAL, baudrate=57600, timeout=2)
        except ValueError:
            port = config["serial"]["url"]
            self._serial = Serial(port=port, baudrate=57600, timeout=2)

    def start(self):
        """Start the motor with the currently set speed reference.

        Raises:
            RuntimeError: Error reported by the controller.
        """
        request = b"\x02\x02\xfc"
        reply = self._serial.write_read(request, size=16)
        if request != reply:
            err_str = f"Start not executed, {self._check_error(reply)}"
            raise RuntimeError(err_str)

    def stop(self):
        """Stop the motor.

        Raises:
            RuntimeError: Error reported by the controller.
        """
        request = b"\x02\x03\xfb"
        reply = self._serial.write_read(request, size=16)
        if request != reply:
            err_str = f"Stop not executed, {self._check_error(reply)}"
            raise RuntimeError(err_str)

    @property
    def reference_speed(self) -> int:
        """Read the reference speed.

        Returns:
            The reference speed [rpm]
        """
        speed = self._read_value(VARIABLE_CODE["Reference speed"])
        return speed

    @reference_speed.setter
    def reference_speed(self, value: int):
        """Set the actual speed.

        Args:
            value: The actual speed [rpm]
        """
        self._write_value(
            VARIABLE_CODE["Reference speed"], value, VARIABLE_TYPE["Int32"]
        )

    @property
    def actual_speed(self) -> int:
        """Read the actual speed.

        Returns:
            The actual speed [rpm]
        """
        speed = self._read_value(VARIABLE_CODE["Actual speed"])
        return speed

    def _read_value(self, code):
        """Read the value of a variable specified by its code.

        Args:
            code (int): Variable byte code.
        Returns:
            (int) or (float): Actual value.
        """
        req_length = 0x03
        asw_length = 0x07
        cmd = 0x04
        checksum = self._calc_checksum(code, req_length, cmd)

        request = struct.pack("<BBBB", req_length, cmd, code, checksum)
        reply = self._serial.write_read(request, size=16)

        if reply[0] != asw_length or reply[1] != cmd:
            raise RuntimeError("Incorrect answer")

        # get the value depending on the variable type
        conv_format = self._read_conversion_format(reply[2])
        answer = struct.unpack(conv_format, reply)

        return answer[3]

    def _write_value(self, code, value, value_type):
        """Write value to a variable specified by its code.

        Args:
            code (int): Variable byte code.
            value (int) or (float): Value to be set.
            value_type (int): Value type as in VARIABLE_TYPE.
        """
        req_length = 0x08
        asw_length = 0x02
        cmd = 0x05
        conv_format = self._write_conversion_format(value_type)

        request = struct.pack(conv_format, *(req_length, cmd, code, value_type, value))
        checksum = self._calc_checksum((request))
        request += struct.pack("<B", checksum)
        reply = self._serial.write_read(request, size=16)

        if reply[0] != asw_length or reply[1] != cmd or reply[2] != 0xF9:
            raise RuntimeError("Incorrect answer")

    def _calc_checksum(self, code, length=None, cmd=None):
        """Calculate the checksum for a given variable.

        Args:
            code (int): Variable byte code.
            length (int): Command length
            cmd (int): Command byte code
        Returns:
            (int): Calculated checksum [bytes].
        """
        if isinstance(code, bytes):
            _sum = ~sum(code)
        else:
            _sum = ~sum((length, cmd, code))
        return (_sum + 1) & 0xFF

    def _check_error(self, error):
        """Conver the error from the controller to be human readble.

        Args:
            error (byte string): The raw error
        Returns:
            (str): Error string.
        """
        err = struct.unpack("<BBHHB", error)

        # Conver to human readable message
        try:
            return ERROR_CODE[err[2]]
        except ValueError:
            return "Unknown error"

    def _read_conversion_format(self, var_type):
        """Choose the conversion format.

        Args:
            vat_type (int): Variable type. Accepted values as in VARIABLE_TYPE
        Returns:
            (str): String to be used as format by struct.unpack.
        Raises:
            RuntimeError: Unknown variable type.
        """

        if var_type in (VARIABLE_TYPE["Int16"], VARIABLE_TYPE["Int32"]):
            return "<BBBiB"
        if var_type in (VARIABLE_TYPE["Uint16"], VARIABLE_TYPE["Uint32"]):
            return "<BBBIB"
        if var_type == VARIABLE_TYPE["Float"]:
            return "<BBBfB"
        raise RuntimeError("Unknown variable type")

    def _write_conversion_format(self, var_type):
        """Choose the conversion format.

        Args:
            vat_type (int): Variable type. Accepted values as in VARIABLE_TYPE
        Returns:
            (str): String to be used as format by struct.pack.
        Raises:
            RuntimeError: Unknown variable type.
        """

        if var_type == VARIABLE_TYPE["Int16"]:
            return "<BBBBh"
        if var_type == VARIABLE_TYPE["Uint16"]:
            return "<BBBBH"
        if var_type == VARIABLE_TYPE["Int32"]:
            return "<BBBBi"
        if var_type == VARIABLE_TYPE["Uint32"]:
            return "<BBBBI"
        if var_type == VARIABLE_TYPE["Float"]:
            return "<BBBBf"
        raise RuntimeError("Unknown variable type")
