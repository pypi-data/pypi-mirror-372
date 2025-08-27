# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.


__all__ = ["LocalSerial", "RFC2217", "SER2NET", "TangoSerial", "Serial"]

import os
import platform
import re
import struct
import weakref
from functools import wraps
import gevent
from gevent import socket, select, lock, event
from ..common.greenlet_utils import KillMask

from bliss.common.cleanup import capture_exceptions
from bliss.common.logtools import log_debug, log_debug_data
from bliss.common.tango import DeviceProxy
from bliss import global_map

from . import tcp
from .exceptions import CommunicationError, CommunicationTimeout

import serial
from serial import rfc2217
from serial.rfc2217 import TelnetOption, TelnetSubnegotiation


class SerialError(CommunicationError):
    pass


class SerialTimeout(CommunicationTimeout):
    pass


def try_open(fu):
    @wraps(fu)
    def rfunc(self, *args, **kwarg):
        try:
            with KillMask():
                self.open()
                return fu(self, *args, **kwarg)
        except gevent.Timeout:
            raise
        except BaseException:
            try:
                self.close()
            except BaseException:
                pass
            raise

    return rfunc


def _atomic(fu):
    @wraps(fu)
    def f(self, *args, **kwarg):
        with self.lock:
            return fu(self, *args, **kwarg)

    return f


class _BaseSerial:
    def __init__(self, cnt, port):
        self._cnt = weakref.ref(cnt)  # reference to the container
        self._port = port

        self._data = b""
        self._event = event.Event()
        self._rx_filter = None
        self._pipe = None
        self._pipe_lock = lock.Semaphore()
        self._raw_read_task = None

    def _init(self):
        with self._pipe_lock:
            self._pipe = os.pipe()
        self._raw_read_task = gevent.spawn(self._raw_read_loop, weakref.proxy(self))

    def _timeout_context(self, timeout):
        timeout_errmsg = "timeout on serial(%s)" % (self._port)
        return gevent.Timeout(timeout, SerialTimeout(timeout_errmsg))

    def _close(self):
        with self._pipe_lock:
            if self._pipe:
                os.write(self._pipe[1], b"|")
        if self._raw_read_task:
            self._raw_read_task.join()
            self._raw_read_task = None
        self._event.set()

    def readline(self, eol, timeout):
        with self._timeout_context(timeout):
            return self._readline(eol)

    def _readline(self, eol):
        if not isinstance(eol, bytes):
            eol = eol.encode()
        eol_pos = self._data.find(eol)
        with capture_exceptions() as capture:
            while eol_pos == -1:
                with capture():
                    self._event.wait()
                    self._event.clear()

                eol_pos = self._data.find(eol)

                if capture.failed:
                    other_exc = [
                        x
                        for _, x, _ in capture.failed
                        if not isinstance(x, gevent.Timeout)
                    ]
                    if not other_exc:
                        if eol_pos == -1:
                            continue
                    else:
                        break

            msg = self._data[:eol_pos]
            self._data = self._data[eol_pos + len(eol) :]
            log_debug_data(self._cnt(), "Rx:", msg)
            return msg

    def read(self, size, timeout):
        with self._timeout_context(timeout):
            return self._read(size)

    def _read(self, size):
        with capture_exceptions() as capture:
            while len(self._data) < size:
                with capture():
                    self._event.wait()
                    self._event.clear()
                if capture.failed:
                    other_exc = [
                        x
                        for _, x, _ in capture.failed
                        if not isinstance(x, gevent.Timeout)
                    ]
                    if not other_exc:
                        if len(self._data) < size:
                            continue
                    else:
                        break
            msg = self._data[:size]
            self._data = self._data[size:]
            log_debug_data(self._cnt(), "Rx:", msg)
            return msg

    def write(self, msg, timeout):
        with self._timeout_context(timeout):
            return self._write(msg)

    def _write(self, msg):
        log_debug_data(self._cnt(), "Tx:", msg)
        while msg:
            _, ready, _ = select.select([], [self.fd], [])
            size_send = os.write(self.fd, msg)
            msg = msg[size_send:]

    def raw_read(self, maxsize, timeout):
        with self._timeout_context(timeout):
            return self._raw_read(maxsize)

    def _raw_read(self, maxsize):
        while not self._data:
            self._event.wait()
            self._event.clear()
        if maxsize:
            msg = self._data[:maxsize]
            self._data = self._data[maxsize:]
        else:
            msg = self._data
            self._data = b""

        log_debug_data(self._cnt(), "Rx:", msg)
        return msg

    @staticmethod
    def _raw_read_loop(self_wk):
        """Use a staticmethod only holding a weakref on self: do not block
        garbage collection."""
        try:
            while True:
                ready, _, _ = select.select([self_wk.fd, self_wk._pipe[0]], [], [])
                if self_wk._pipe[0] in ready:
                    break
                raw_data = os.read(self_wk.fd, 4096)
                if raw_data:
                    if self_wk._rx_filter:
                        raw_data = self_wk._rx_filter(raw_data)
                    self_wk._data += raw_data
                    self_wk._event.set()
                else:
                    break
        finally:
            with self_wk._pipe_lock:
                os.close(self_wk._pipe[0])
                os.close(self_wk._pipe[1])
                self_wk._pipe = None
            try:
                cnt = self_wk._cnt()
                if cnt:
                    cnt._raw_handler = None
            except ReferenceError:
                pass


class LocalSerial(_BaseSerial):
    def __init__(self, cnt, **keys):
        _BaseSerial.__init__(self, cnt, keys.get("port"))
        try:
            # Use python serial module to communicate.
            self.__serial = serial.Serial(**keys)
        except BaseException:
            self.__serial = None
            raise
        self.fd = self.__serial.fd
        self._init()

    def __del__(self):
        self.close()

    def flushInput(self):
        self.__serial.flushInput()
        self._data = b""

    def close(self):
        self._close()
        if self.__serial:
            self.__serial.close()


class RFC2217Error(SerialError):
    pass


class RFC2217Timeout(SerialTimeout):
    pass


class RFC2217(_BaseSerial):
    """There is an existing implementation in pyserial but it's not gevent
    compatible."""

    class TelnetCmd:
        def __init__(self):
            self.data = b""

        def telnet_send_option(self, action, option):
            self.data += b"".join([rfc2217.IAC, action, option])

    class TelnetSubNego:
        def __init__(self):
            self.data = b""
            self.logger = None

        def rfc2217_send_subnegotiation(self, option, value):
            value = value.replace(rfc2217.IAC, rfc2217.IAC_DOUBLED)
            self.data += (
                rfc2217.IAC
                + rfc2217.SB
                + rfc2217.COM_PORT_OPTION
                + option
                + value
                + rfc2217.IAC
                + rfc2217.SE
            )

    def __init__(
        self,
        cnt,
        port,
        baudrate,
        bytesize,
        parity,
        stopbits,
        timeout,
        xonxoff,
        rtscts,
        writeTimeout,
        dsrdtr,
        interCharTimeout,
    ):
        _BaseSerial.__init__(self, cnt, port)
        self.baudrate = baudrate
        self.bytesize = bytesize
        self.parity = parity
        self.stopbits = stopbits
        self.xonxoff = xonxoff
        self.rtscts = rtscts
        self.dsrdtr = dsrdtr
        # cache for line and modem states that the server sends to us
        self._linestate = 0
        self._modemstate = None
        self._modemstate_expires = 0
        # RFC 2217 flow control between server and client
        self._remote_suspend_flow = False

        port_parse = re.compile(r"^(rfc2217://)?([^:/]+?):([0-9]+)$")
        match = port_parse.match(port)
        if match is None:
            raise RFC2217Error("port is not a valid url (%s)" % port)

        local_host, local_port = match.group(2), match.group(3)

        # use socket to communicate
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.connect((local_host, int(local_port)))
        self._socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

        if platform.system() != "Windows":
            self._socket.setsockopt(socket.SOL_IP, socket.IP_TOS, 0x10)

        self.fd = self._socket.fileno()
        self._init()

        telnet_cmd = self.TelnetCmd()
        # get code from rfc2217 in serial module
        # name the following separately so that, below, a check can be easily done
        mandatory_options = [
            TelnetOption(
                telnet_cmd,
                "we-BINARY",
                rfc2217.BINARY,
                rfc2217.WILL,
                rfc2217.WONT,
                rfc2217.DO,
                rfc2217.DONT,
                rfc2217.INACTIVE,
            ),
            TelnetOption(
                telnet_cmd,
                "we-RFC2217",
                rfc2217.COM_PORT_OPTION,
                rfc2217.WILL,
                rfc2217.WONT,
                rfc2217.DO,
                rfc2217.DONT,
                rfc2217.REQUESTED,
            ),
        ]
        # all supported telnet options
        self.telnet_options = [
            TelnetOption(
                telnet_cmd,
                "ECHO",
                rfc2217.ECHO,
                rfc2217.DO,
                rfc2217.DONT,
                rfc2217.WILL,
                rfc2217.WONT,
                rfc2217.REQUESTED,
            ),
            TelnetOption(
                telnet_cmd,
                "we-SGA",
                rfc2217.SGA,
                rfc2217.WILL,
                rfc2217.WONT,
                rfc2217.DO,
                rfc2217.DONT,
                rfc2217.REQUESTED,
            ),
            TelnetOption(
                telnet_cmd,
                "they-SGA",
                rfc2217.SGA,
                rfc2217.DO,
                rfc2217.DONT,
                rfc2217.WILL,
                rfc2217.WONT,
                rfc2217.REQUESTED,
            ),
            TelnetOption(
                telnet_cmd,
                "they-BINARY",
                rfc2217.BINARY,
                rfc2217.DO,
                rfc2217.DONT,
                rfc2217.WILL,
                rfc2217.WONT,
                rfc2217.INACTIVE,
            ),
            TelnetOption(
                telnet_cmd,
                "they-RFC2217",
                rfc2217.COM_PORT_OPTION,
                rfc2217.DO,
                rfc2217.DONT,
                rfc2217.WILL,
                rfc2217.WONT,
                rfc2217.REQUESTED,
            ),
        ] + mandatory_options

        telnet_sub_cmd = self.TelnetSubNego()
        self.rfc2217_port_settings = {
            "baudrate": TelnetSubnegotiation(
                telnet_sub_cmd,
                "baudrate",
                rfc2217.SET_BAUDRATE,
                rfc2217.SERVER_SET_BAUDRATE,
            ),
            "datasize": TelnetSubnegotiation(
                telnet_sub_cmd,
                "datasize",
                rfc2217.SET_DATASIZE,
                rfc2217.SERVER_SET_DATASIZE,
            ),
            "parity": TelnetSubnegotiation(
                telnet_sub_cmd, "parity", rfc2217.SET_PARITY, rfc2217.SERVER_SET_PARITY
            ),
            "stopsize": TelnetSubnegotiation(
                telnet_sub_cmd,
                "stopsize",
                rfc2217.SET_STOPSIZE,
                rfc2217.SERVER_SET_STOPSIZE,
            ),
        }
        self.rfc2217_options = {
            "purge": TelnetSubnegotiation(
                telnet_sub_cmd, "purge", rfc2217.PURGE_DATA, rfc2217.SERVER_PURGE_DATA
            ),
            "control": TelnetSubnegotiation(
                telnet_sub_cmd,
                "control",
                rfc2217.SET_CONTROL,
                rfc2217.SERVER_SET_CONTROL,
            ),
        }
        self.rfc2217_options.update(self.rfc2217_port_settings)

        # negotiate Telnet/RFC 2217 -> send initial requests
        for option in self.telnet_options:
            if option.state is rfc2217.REQUESTED:
                telnet_cmd.telnet_send_option(option.send_yes, option.option)

        self._socket.send(telnet_cmd.data)
        telnet_cmd.data = b""

        # Read telnet negotiation
        with gevent.Timeout(
            5.0, RFC2217Timeout("timeout on serial negotiation(%s)" % self._port)
        ):
            while 1:
                self._parse_nego(telnet_cmd)
                if sum(o.active for o in mandatory_options) == len(mandatory_options):
                    break

            # configure port
            self.rfc2217_port_settings["baudrate"].set(struct.pack("!I", self.baudrate))
            self.rfc2217_port_settings["datasize"].set(struct.pack("!B", self.bytesize))
            self.rfc2217_port_settings["parity"].set(
                struct.pack("!B", rfc2217.RFC2217_PARITY_MAP[self.parity])
            )
            self.rfc2217_port_settings["stopsize"].set(
                struct.pack("!B", rfc2217.RFC2217_STOPBIT_MAP[self.stopbits])
            )

            if self.rtscts and self.xonxoff:
                raise ValueError("xonxoff and rtscts together are not supported")
            elif self.rtscts:
                self.rfc2217_options["control"].set(
                    rfc2217.SET_CONTROL_USE_HW_FLOW_CONTROL
                )
            elif self.xonxoff:
                self.rfc2217_options["control"].set(
                    rfc2217.SET_CONTROL_USE_SW_FLOW_CONTROL
                )
            else:
                self.rfc2217_options["control"].set(
                    rfc2217.SET_CONTROL_USE_NO_FLOW_CONTROL
                )

            self._socket.send(telnet_sub_cmd.data)
            telnet_sub_cmd.data = b""
            items = self.rfc2217_port_settings.values()
            while 1:
                self._parse_nego(telnet_cmd)
                if sum(o.active for o in items) == len(items):
                    break

        # check rtscts,xonxoff or no flow control
        while not self.rfc2217_options["control"].is_ready():
            self._parse_nego(telnet_cmd)

        # plug the data filter
        self._rx_filter = self._rfc2217_filter
        self._pending_data = None

    def __del__(self):
        self.close()

    def write(self, msg, timeout):
        msg = msg.replace(rfc2217.IAC, rfc2217.IAC_DOUBLED)
        _BaseSerial.write(self, msg, timeout)

    def flushInput(self):
        telnet_cmd = self.telnet_options[0].connection
        purge = self.rfc2217_options["purge"]
        telnet_sub_cmd = purge.connection
        purge.set(rfc2217.PURGE_RECEIVE_BUFFER)
        self._data = b""
        self._rx_filter = None
        self._socket.send(telnet_sub_cmd.data)
        telnet_sub_cmd.data = b""

        while not purge.is_ready():
            self._parse_nego(telnet_cmd)
        self._rx_filter = self._rfc2217_filter
        self._data = b""

    def _rfc2217_filter(self, data):
        if bytes([data[-1]]) == rfc2217.IAC and bytes([data[-2]]) != rfc2217.IAC:
            self._pending_data = data
            return b""

        if self._pending_data:
            data = self._pending_data + data
            self._pending_data = None
        return data.replace(rfc2217.IAC_DOUBLED, rfc2217.IAC)

    def _parse_nego(self, telnet_cmd):
        iac_pos = -1
        while 1:
            while iac_pos == -1 or len(self._data[iac_pos:]) < 3:
                self._event.wait()
                self._event.clear()
                iac_pos = self._data.find(rfc2217.IAC)

            if (
                len(self._data[iac_pos:]) > 2
                and bytes([self._data[iac_pos + 1]]) == rfc2217.IAC
            ):  # ignore double rfc2217.IAC
                self._data = self._data[iac_pos + 2 :]
            else:
                _, command, option = serial.serialutil.iterbytes(
                    self._data[iac_pos : iac_pos + 3]
                )
                self._data = self._data[iac_pos + 3 :]
                if command != rfc2217.SB:
                    # ignore other command than
                    if command in (
                        rfc2217.DO,
                        rfc2217.DONT,
                        rfc2217.WILL,
                        rfc2217.WONT,
                    ):
                        known = False
                        for item in self.telnet_options:
                            if item.option == option:
                                item.process_incoming(command)
                                known = True

                        if not known:
                            if command == rfc2217.WILL:
                                telnet_cmd.telnet_send_option(rfc2217.DONT, option)
                            elif command == rfc2217.DO:
                                telnet_cmd.telnet_send_option(rfc2217.WONT, option)
                else:  # sub-negotiation
                    se_pos = self._data.find(rfc2217.IAC + rfc2217.SE)
                    while se_pos == -1:
                        self._event.wait()
                        self._event.clear()
                        se_pos = self._data.find(rfc2217.IAC + rfc2217.SE)
                    suboption, value = self._data[0:1], self._data[1:se_pos]
                    self._data = self._data[se_pos + 2 :]
                    if option == rfc2217.COM_PORT_OPTION:
                        if suboption == rfc2217.SERVER_NOTIFY_LINESTATE:
                            self._linestate = ord(value)
                        elif suboption == rfc2217.SERVER_NOTIFY_MODEMSTATE:
                            self._modemstate = ord(value)
                        elif suboption == rfc2217.FLOWCONTROL_SUSPEND:
                            self._remote_suspend_flow = True
                        elif suboption == rfc2217.FLOWCONTROL_RESUME:
                            self._remote_suspend_flow = False
                        else:
                            for item in self.rfc2217_options.values():
                                if item.ack_option == suboption:
                                    item.check_answer(value)
                                    break

            iac_pos = self._data.find(rfc2217.IAC)
            # check if we need to send extra command
            if iac_pos == -1:  # no more negotiation rx
                if telnet_cmd.data:
                    self._socket.send(telnet_cmd.data)
                    telnet_cmd.data = b""
                break

    def close(self):
        self._close()
        if self._socket:
            self._socket.close()


class SER2NETError(SerialError):
    pass


class SER2NET(RFC2217):
    """Keep a separate class to highlight how connection was established, but
    SER2NET is just a TCP negociation prior to connect RFC2217"""

    pass


def ser2net_request_rfc2217_url(ser2net_url: str) -> str:
    """Request an RFC2217 url from a ser2net server"""
    url_parse = re.compile(r"^(ser2net://)?([^:/]+?):([0-9]+)(.+)$")
    match = url_parse.match(ser2net_url)
    # print(f"### ### configured url='{ser2net_port}'")
    if match is None:
        raise SER2NETError(f"port is not a valid url ({ser2net_url})")
    comm_par1 = match.group(2)
    comm_par2 = int(match.group(3))
    # print(f"### ### comm_par1={comm_par1} comm_par2={comm_par2}")
    comm = tcp.Command(comm_par1, comm_par2, eol="->")

    # Send a request to get list of available ports.
    msg = b"showshortport\r\n"
    _, rx = comm.write_readlines(msg, 2)
    # print("### ### Raw answer to the request:",)
    # print(rx)

    # Answer should start with "showshortport" string; remove it.
    msg_pos = rx.find(msg)
    rx = rx[msg_pos + len(msg) :]
    rx = rx.decode()

    requested_device = match.group(4)
    # print(f"### ### look for device:'{requested_device}'")
    # Regexp to identify requested device from url.
    port_parse = re.compile(r"^([0-9]+).+%s" % requested_device)
    rfc2217_port = None

    # Search for requested device in received list of ports.
    for line in rx.split("\n"):
        line = line.strip()
        # print ("### ### LINE=%r" % line)
        g = port_parse.match(line)
        if g:
            rfc2217_port = int(g.group(1))
            break
    if rfc2217_port is None:
        raise SER2NETError(f"port {match.group(4)} is not found on server")
    return f"rfc2217://{match.group(2)}:{rfc2217_port}"


class TangoSerial(_BaseSerial):
    """Tango serial line"""

    SL_RAW = 0
    SL_NCHAR = 1
    SL_LINE = 2
    SL_RETRY = 3

    SL_NONE = 0
    SL_ODD = 1
    SL_EVEN = 3

    SL_STOP1 = 0
    SL_STOP15 = 1
    SL_STOP2 = 2

    SL_TIMEOUT = 3
    SL_PARITY = 4
    SL_CHARLENGTH = 5
    SL_STOPBITS = 6
    SL_BAUDRATE = 7
    SL_NEWLINE = 8

    FLUSH_INPUT = 0
    FLUSH_OUTPUT = 1
    FLUSH_BOTH = 2

    PARITY_MAP = {
        serial.PARITY_NONE: SL_NONE,
        serial.PARITY_ODD: SL_ODD,
        serial.PARITY_EVEN: SL_EVEN,
    }

    STOPBITS_MAP = {
        serial.STOPBITS_ONE: SL_STOP1,
        serial.STOPBITS_TWO: SL_STOP2,
        serial.STOPBITS_ONE_POINT_FIVE: SL_STOP15,
    }

    PAR_MAP = {
        SL_BAUDRATE: ("baudrate", lambda o, v: int(v)),
        SL_CHARLENGTH: ("bytesize", lambda o, v: int(v)),
        SL_PARITY: ("parity", lambda o, v: o.PARITY_MAP[v]),
        SL_STOPBITS: ("stopbits", lambda o, v: o.STOPBITS_MAP[v]),
        SL_TIMEOUT: ("timeout", lambda o, v: int(v * 1000)),
        SL_NEWLINE: ("eol", lambda o, v: ord(v[-1]) if type(v) is str else v[-1]),
    }

    def __init__(self, cnt, **kwargs):
        _BaseSerial.__init__(self, cnt, kwargs.get("port"))
        self._device = None
        self._pars = kwargs
        self._last_eol = kwargs["eol"] = cnt._eol
        del self._data
        del self._event
        device = DeviceProxy(kwargs["port"])
        timeout = kwargs.get("timeout")
        if timeout:
            device.set_timeout_millis(int(timeout * 1000))
        args = []
        kwargs["eol"] = cnt._eol
        for arg, (key, encode) in self.PAR_MAP.items():
            args.append(arg)
            args.append(encode(self, kwargs[key]))
        device.DevSerSetParameter(args)
        self._device = device

        # the following parameters are not supported by tango serial,
        # but can be used in bliss.

        if "xonxoff" in kwargs and kwargs["xonxoff"]:
            raise RuntimeError("Tango Serial Device Server does  not support xonxoff")

        if "rtscts" in kwargs and kwargs["rtscts"]:
            raise RuntimeError("Tango Serial Device Server does  not support rtscts")

    def close(self):
        self._device = None

    def _readline(self, eol):
        if not isinstance(eol, bytes):
            eol = eol.encode()
        lg = len(eol)

        if eol != self._last_eol:
            _, eol_encode = self.PAR_MAP[self.SL_NEWLINE]
            self._device.DevSerSetNewline(eol_encode(self, eol))
            self._last_eol = eol

        buff = b""
        while True:
            line = bytes(self._device.DevSerReadChar(self.SL_LINE)) or b""
            line = line if type(line) is bytes else line.encode()
            if line == b"":
                log_debug_data(self._cnt(), "Rx:", b"")
                return b""
            buff += line
            if buff[-lg:] == eol:
                log_debug_data(self._cnt(), "Rx:", buff)
                return buff[:-lg]

    def _raw_read(self, maxsize):
        if maxsize:
            buff = bytes(self._device.DevSerReadNBinData(maxsize)) or b""
            while len(buff) < maxsize:
                buff += bytes(self._device.DevSerReadNBinData(maxsize)) or b""
        else:
            buff = bytes(self._device.DevSerReadChar(self.SL_RAW)) or b""

        log_debug_data(self._cnt(), "Rx:", buff)
        return buff

    _read = _raw_read

    def _write(self, msg):
        log_debug_data(self._cnt(), "Tx:", msg)
        self._device.DevSerWriteChar(bytearray(msg))

    def flushInput(self):
        self._device.DevSerFlush(self.FLUSH_INPUT)


class Serial:
    LOCAL, RFC2217, SER2NET, TANGO = list(range(4))

    def __init__(
        self,
        port=None,
        baudrate=9600,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        timeout=5.0,
        xonxoff=False,
        rtscts=False,
        writeTimeout=None,
        dsrdtr=False,
        interCharTimeout=None,
        eol=b"\n",
    ):
        self._serial_kwargs = {
            "port": port,
            "baudrate": baudrate,
            "bytesize": bytesize,
            "parity": parity,
            "stopbits": stopbits,
            "timeout": timeout,
            "xonxoff": xonxoff,
            "rtscts": rtscts,
            "writeTimeout": writeTimeout,
            "dsrdtr": dsrdtr,
            "interCharTimeout": interCharTimeout,
        }
        self._port = port

        if isinstance(eol, bytes):
            self._eol = eol
        else:
            self._eol = eol.encode()

        self._timeout = timeout
        self._raw_handler = None
        self._lock = lock.RLock()
        self._type_dict = {0: "LOCAL", 1: "RFC2217", 2: "SER2NET", 3: "TANGO"}
        global_map.register(self, parents_list=["comms"], tag=str(self))

    def __del__(self):
        self.close()

    def __str__(self):
        return f"{self.__class__.__name__}[{self._serial_kwargs['port']}]"

    @property
    def lock(self):
        return self._lock

    @_atomic
    def open(self):
        if self._raw_handler is None:
            serial_type = self._check_type()
            log_debug(self, "open - serial_type=%s" % serial_type)
            log_debug_data(self, "serial kwargs", self._serial_kwargs)
            if serial_type == self.RFC2217:
                self._raw_handler = RFC2217(self, **self._serial_kwargs)
            elif serial_type == self.SER2NET:
                ser2net_url = self._serial_kwargs["port"]
                rfc2217_url = ser2net_request_rfc2217_url(ser2net_url)
                kwargs = self._serial_kwargs.copy()
                kwargs["port"] = rfc2217_url
                self._raw_handler = SER2NET(self, **kwargs)
            elif serial_type == self.TANGO:
                self._raw_handler = TangoSerial(self, **self._serial_kwargs)
            else:  # LOCAL
                self._raw_handler = LocalSerial(self, **self._serial_kwargs)
            global_map.register(
                self,
                parents_list=["comms"],
                children_list=[self._raw_handler],
                tag=str(self),
            )

    @_atomic
    def close(self):
        if self._raw_handler:
            self._raw_handler.close()
            self._raw_handler = None
            log_debug(self, "close")

    @try_open
    def raw_read(self, maxsize=None, timeout=None):
        local_timeout = timeout or self._timeout
        msg = self._raw_handler.raw_read(maxsize, local_timeout)
        log_debug_data(self, "raw_read", msg)
        return msg

    def read(self, size=1, timeout=None):
        with self._lock:
            return self._read(size, timeout)

    @try_open
    def _read(self, size=1, timeout=None):
        local_timeout = timeout or self._timeout
        msg = self._raw_handler.read(size, local_timeout)
        log_debug_data(self, "read", msg)
        if len(msg) != size:
            raise SerialError(
                "read timeout on serial (%s)" % self._serial_kwargs.get(self._port, "")
            )
        return msg

    def readline(self, eol=None, timeout=None):
        with self._lock:
            return self._readline(eol, timeout)

    @try_open
    def _readline(self, eol=None, timeout=None):
        local_eol = eol or self._eol
        local_timeout = timeout or self._timeout
        msg = self._raw_handler.readline(local_eol, local_timeout)
        log_debug_data(self, "readline", msg)
        return msg

    def write(self, msg, timeout=None):
        if isinstance(msg, str):
            raise TypeError("a bytes-like object is required, not 'str'")
        with self._lock:
            return self._write(msg, timeout)

    @try_open
    def _write(self, msg, timeout=None):
        local_timeout = timeout or self._timeout
        log_debug_data(self, "write", msg)
        return self._raw_handler.write(msg, local_timeout)

    @try_open
    def write_read(self, msg, write_synchro=None, size=1, timeout=None):
        if isinstance(msg, str):
            raise TypeError("a bytes-like object is required, not 'str'")
        with self._lock:
            try:
                self._write(msg, timeout)
                if write_synchro:
                    write_synchro.notify()
                ans = self._read(size, timeout)
            except BaseException:
                self.flush()
                raise
            return ans

    @try_open
    def write_readline(self, msg, write_synchro=None, eol=None, timeout=None):
        if isinstance(msg, str):
            raise TypeError("a bytes-like object is required, not 'str'")
        with self._lock:
            try:
                self._write(msg, timeout)
                if write_synchro:
                    write_synchro.notify()
                ans = self._readline(eol, timeout)
            except BaseException:
                self.flush()
                raise
            return ans

    @try_open
    def write_readlines(
        self, msg, nb_lines, write_synchro=None, eol=None, timeout=None
    ):
        if isinstance(msg, str):
            raise TypeError("a bytes-like object is required, not 'str'")
        with self._lock:
            try:
                self._write(msg, timeout)
                if write_synchro:
                    write_synchro.notify()

                str_list = []
                for ii in range(nb_lines):
                    str_list.append(self._readline(eol=eol, timeout=timeout))
            except BaseException:
                self.flush()
                raise
            return str_list

    @try_open
    def flush(self):
        log_debug(self, "flush")
        self._raw_handler.flushInput()

    def _check_type(self):
        port = self._serial_kwargs.get("port", "")
        port_lower = port.lower()
        if port_lower.startswith("rfc2217://"):
            return self.RFC2217
        elif port_lower.startswith("ser2net://"):
            return self.SER2NET
        elif port_lower.startswith("tango://"):
            return self.TANGO
        else:
            return self.LOCAL

    def __info__(self):
        serial_type = self._type_dict[self._check_type()]

        info_str = (
            f"SERIAL type={serial_type} url={self._port} \n"
            f"       timeout(s)={self._timeout} eol={self._eol!a}\n"
        )

        return info_str
