# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) 2015-2023 Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

"""\
Symetrie hexapod

YAML_ configuration example:

.. code-block:: yaml

    plugin: emotion
    class: SHexapod
    version: ssh_gpascii
    ssh_command:
      hostname: id99hexa1
      user: root
      password: deltatau
    axes:
      - name: h1tx
        role: tx
        unit: mm
      - name: h1ty
        role: ty
        unit: mm
      - name: h1tz
        role: tz
        unit: mm
      - name: h1rx
        role: rx
        unit: deg
      - name: h1ry
        role: ry
        unit: deg
      - name: h1rz
        role: rz
        unit: deg

"""
import numpy
import gevent
from bliss.comm import ssh_command
from .shexapod import BaseHexapod, Pose, BaseHexapodError


class HexapodError(BaseHexapodError):
    pass


class HexapodProtocolSSHgpascii(BaseHexapod):
    """Protocol for Symetrie hexapod connected via SSHgpaascii"""

    DEFAULT_CMD = "/opt/ppmac/gpascii/gpascii -2"
    DEFAULT_USER = "root"
    DEFAULT_PASSWORD = "deltatau"

    ACTION_STATES = (
        "None",
        "Stop",
        "ControlOn",
        "ControlOff",
        "Home",
        "HomeVirtual",
        "MovePTP",
        "MoveSpecificPos",
        "MoveSequence",
        "MoveJog",
        "Handwheel",
        "Maintenance",
    )

    VALIDATION_ERRORS = (
        (0, "Factory workspace limits"),
        (1, "Machine workspace limits"),
        (2, "User workspace limits"),
        (3, "Actuator limits"),
        (4, "Joints limits"),
        (5, "Due to backlash compensation"),
    )

    class Status:
        """Flags of hexapod general status"""

        ERROR_FLAG = 1 << 0
        INITIALIZED_FLAG = 1 << 1
        CONTROL_FLAG = 1 << 2
        IN_POSITION_FLAG = 1 << 3
        MOTION_TASK_FLAG = 1 << 4
        HOME_TASK_FLAG = 1 << 5
        HOME_COMPLETE_FLAG = 1 << 6

        def __init__(self, raw_status):
            self._status = raw_status

        @property
        def moving(self) -> int:
            """moving during motion or homing task?"""
            return self._status & (self.MOTION_TASK_FLAG | self.HOME_TASK_FLAG)

        @property
        def homing(self) -> int:
            """homing?"""
            return self._status & self.HOME_TASK_FLAG

        @property
        def control(self) -> int:
            """
            This means closed loop activated
            """
            return self._status & self.CONTROL_FLAG

        @property
        def error(self) -> int:
            """error flag"""
            return self._status & self.ERROR_FLAG

        @property
        def homing_done(self) -> int:
            """homing completed?"""
            return self._status & self.HOME_COMPLETE_FLAG

        @property
        def in_position(self) -> int:
            """in position?"""
            return self._status & self.IN_POSITION_FLAG

        @property
        def initialized(self) -> int:
            """
            True once the controller startup is terminated. Start-up takes about 2 minutes
            """
            return self._status & self.INITIALIZED_FLAG

        def __info__(self) -> str:
            """string containing all relevant status flags"""
            rstr = "Hexapod Status:\n\n"
            rstr += "ERROR\n" if self.error else ""
            rstr += (
                "System initialized\n"
                if self.initialized
                else "System NOT initialized\n"
            )
            rstr += "Moving\n" if self.moving else "Not Moving\n"
            rstr += "Homing\n" if self.homing else ""
            rstr += "Homing Done\n" if self.homing_done else "Homing NOT DONE\n"
            rstr += "In closed loop\n" if self.control else "Open loop\n"
            return rstr

    class AxisState:
        """
        Convert status bits into text messages
        """

        # bit, message if True, message if False
        FLAGS = [
            (0, "ERROR", "(no error)"),
            (1, "Control on", "Control Off"),
            (2, "In position", "NOT in position"),
            (3, "Motion task running", "No motion task running"),
            (4, "Home task running", "No home task running"),
            (5, "Homing completed", "Homing NOT completed"),
            (6, "Phase found", "Phase NOT found"),
            (7, "Brake ON", "Brake off"),
            (8, "Hardware home input ON", "Hardware home input OFF"),
            (9, "Negative limit switch ACTIVE", "Negative limit switch not active"),
            (10, "Positive limit switch ACTIVE", "Positive limit switch not active"),
            (11, "Software limit REACHED", "No software limit reached"),
            (12, "Following ERROR", "No following error"),
            (13, "Drive FAULT", "No drive fault"),
            (14, "Encoder ERROR", "No encoder error"),
        ]

        ERROR_FLAG = 1 << 0
        CONTROL_ON_FLAG = 1 << 1
        IN_POSITION_FLAG = 1 << 2
        MOTION_TASK_RUNNING_FLAG = 1 << 3
        HOME_TASK_RUNNING_FLAG = 1 << 4
        HOME_COMPLETE_FLAG = 1 << 5
        PHASE_FOUND_FLAG = 1 << 6
        BRAKE_ON_FLAG = 1 << 7
        HOME_HW_INPUT_FLAG = 1 << 8
        LIMIT_NEG_FLAG = 1 << 9
        LIMIT_POS_FLAG = 1 << 10
        LIMIT_SW_FLAG = 1 << 11
        FOLLOWING_ERROR_FLAG = 1 << 12
        DRIVE_FAULT_FLAG = 1 << 13
        ENCODER_ERROR_FLAG = 1 << 14

        def __init__(self, raw_status: int):
            """init"""
            self._status = raw_status

        def axis_state(self, bit: int, true_msg: str, false_msg: str) -> str:
            """return message describing True or False state"""
            return true_msg if self._status & (1 << bit) else false_msg

        @property
        def status(self) -> str:
            """return text string describing all status flags"""
            return "".join(f"    {self.axis_state(*i)}\n" for i in self.FLAGS)

    class WaitTimeout(RuntimeError):
        """timeout error"""

        pass

    def __init__(self, config):
        """init"""
        super().__init__(config)
        ssh_config = config.get("ssh_command", dict())
        try:
            hostname = ssh_config["hostname"]
        except KeyError:
            raise RuntimeError("**hostname** should be part of the config")

        user = ssh_config.get("user", self.DEFAULT_USER)
        password = ssh_config.get("password", self.DEFAULT_PASSWORD)
        self.comm = ssh_command.SshCommand(
            hostname,
            user,
            password,
            "/opt/ppmac/gpascii/gpascii -2",
            eol="\x06\n",
            connection_cbk=self._cbk,
        )

    def _controller_id(self) -> dict:
        """Read the controller ID.
        Returns:
           (dict): Controller ID
        """
        with self.comm.lock:
            self.comm.write_readline(b"c_cmd=C_VERSION\r\n")
            self._wait_cmd_0("Getting controller version")
            reply = self.comm.write_readline(b"c_par(0),11,1\r\n")
        data = reply.split(b"\n")
        print(len(data))
        return {
            "Controller software ID": int(data[0]),
            "Controller software version": tuple(int(i) for i in data[1:5]),
            "API software version": tuple(int(i) for i in data[5:9]),
            "System ID": int(data[9]),
            "System number": int(data[10]),
            "System configuration version": data[11].decode("ascii"),
        }

    @property
    def controller_id(self) -> str:
        """Read the controller ID.
        Returns:
           (str): controller ID information
        """
        id_format = {
            "Controller software ID": "{0:d}",
            "Controller software version": "{0[0]}.{0[1]}.{0[2]}.{0[3]}",
            "API software version": "{0[0]}.{0[1]}.{0[2]}.{0[3]}",
            "System ID": "{0}",
            "System number": "{0}",
            "System configuration version": "{0}",
        }
        id_dict = self._controller_id()
        txt = ""
        for key, format_str in id_format.items():
            try:
                msg = format_str.format(id_dict[key])
                # print(f"{key:>29s}: {msg}")
                txt += f"{key:>29s}: {msg}\n"
            except KeyError:
                txt += f"{key}: *unknown*\n"
        return txt

    def _full_system_status(self) -> dict:
        """Read all controller status variables
        Returns:
           (dict): status variables
        """
        with self.comm.lock:
            reply = self.comm.write_readline(b"s_hexa,50,1\r\n")
        data = reply.split(b"\n")
        return {
            "Hexapod status": int(data[0]),
            "Action status": int(data[1]),
            "User position": [float(i) for i in data[2:8]],
            "Machine position": [float(i) for i in data[8:14]],
            "Axis status": [int(i) for i in data[14:20]],
            "Axis position": [float(i) for i in data[20:26]],
            "digital i/o": [int(i) for i in data[26:34]],
            "analog i/o": [float(i) for i in data[34:42]],
            "Cycle": int(data[42]),
            "Index": int(data[43]),
            "Error number": int(data[44]),
            "Field bus": int(data[45]),
            "Heartbeat": int(data[46]),
            "Reserved": [int(i) for i in data[47:50]],
        }

    def get_metadata(self):
        """read metadata of hexapod
        Returns:
           (dict): status variables
        """
        status = self._full_system_status()

        metadata_keys = [
            "Hexapod status",
            "Action status",
            "User position",
            "Machine position",
            "Axis status",
            "Axis position",
            "Error number",
        ]
        metadata = {key: status[key] for key in metadata_keys}
        origins = self.get_origin()
        metadata["object_cs"] = tuple(origins["object_cs"])
        metadata["user_cs"] = tuple(origins["user_cs"])

        return metadata

    @property
    def full_system_status(self) -> str:
        """Read all controller status variables
        Returns:
           (str): status variables
        """
        status_format = {
            "Hexapod status": "{:04x}",
            "Action status": "{:04x}",
            "User position": "tx={0[0]:8.4f}, ty={0[1]:8.4f}, tz={0[2]:8.4f}, rx={0[3]:8.4f}, ry={0[4]:8.4f}, rz={0[5]:8.4f}",
            "Machine position": "tx={0[0]:8.4f}, ty={0[1]:8.4f}, tz={0[2]:8.4f}, rx={0[3]:8.4f}, ry={0[4]:8.4f}, rz={0[5]:8.4f}",
            "Axis status": "{0[0]:04x} {0[1]:04x} {0[2]:04x} {0[3]:04x} {0[4]:04x} {0[5]:04x}",
            "Axis position": "{0[0]:8.4f}, {0[1]:8.4f}, {0[2]:8.4f}, {0[3]:8.4f}, {0[4]:8.4f}, {0[5]:8.4f}",
            "digital i/o": "{0[0]} {0[1]} {0[2]} {0[3]}   {0[4]} {0[5]} {0[6]} {0[7]}",
            "analog i/o": "{0[0]} {0[1]} {0[2]} {0[3]} {0[4]} {0[5]} {0[6]} {0[7]}",
            "Cycle": "{0}",
            "Index": "{0}",
            "Error number": "{0}",
            "Field bus": "{0}",
            "Heartbeat": "{0}",
            "Reserved": "{0[0]} {0[1]} {0[2]}",
        }

        status_dict = self._full_system_status()
        txt = ""
        for key, format_str in status_format.items():
            try:
                msg = format_str.format(status_dict[key])
                # print(f"{key:>20s}: {msg}")
                txt += f"{key:>20s}: {msg}\n"
            except KeyError:
                txt += f"{key}: *unknown*\n"

        origin = self.get_origin()
        for (name, pose) in origin.items():
            pos_txt = f"tx={pose.tx:8.4f}, ty={pose.ty:8.4f}, tz={pose.tz:8.4f}, "
            pos_txt += f"rx={pose.rx:8.4f}, ry={pose.ry:8.4f}, rz={pose.rz:8.4}"
            txt += f"{name:>20s}: {pos_txt}\n"

        return txt

    def _action_state(self) -> int:
        """Read action state from controller
        Returns:
           (int): action state
        """
        with self.comm.lock:
            reply = self.comm.write_readline(b"s_action\r\n")
        return int(reply)

    @property
    def action_state(self) -> str:
        """Read action state from controller
        Returns:
           (str): action state
        """
        state = self._action_state()
        return self.ACTION_STATES[state]

    def _user_and_object_cs(self) -> dict:
        """Read user and object coordinate system origins from controller
        Returns:
           (dict): dictionary of origins
        """
        with self.comm.lock:
            self.comm.write_readlines(b"c_cfg=0\r\nc_cmd=C_CFG_CS\r\n", 2)
            # wait c_cmd == 0
            self._wait_cmd_0("Getting user and object reference")
            reply = self.comm.write_readline(b"c_par(0),12,1\r\n")
        data = reply.split(b"\n")
        user_cs = Pose(*map(float, data[:6]))
        object_cs = Pose(*map(float, data[6 : 6 + 6]))
        return dict(user_cs=user_cs, object_cs=object_cs)

    def get_origin(self):
        """Read user and object coordinate system origins from controller
        Returns:
           (dict): dictionary of origins
        """
        return self._user_and_object_cs()

    @property
    def object_pose(self):
        """read position in object coordinate system"""
        with self.comm.lock:
            reply = self.comm.write_readline(b"s_uto_tx,6,1\r\n")
        data = numpy.fromstring(reply.decode(), sep="\n")
        # data[3:6] = numpy.rad2deg(data[3:6])
        return Pose(*data)

    @property
    def platform_pose(self):
        """read position in platform coordinate system"""
        with self.comm.lock:
            reply = self.comm.write_readline(b"s_mtp_tx,6,1\r\n")
        data = numpy.fromstring(reply.decode(), sep="\n")
        # data[3:6] = numpy.rad2deg(data[3:6])
        return Pose(*data)

    @property
    def factory_limits(self):
        return self._get_limits(0)

    @property
    def machine_limits(self):
        return self._get_limits(1)

    @property
    def user_limits(self):
        return self._get_limits(2)

    def _get_limits(self, lim):
        with self.comm.lock:
            cmd = f"c_cfg=0\r\nc_par(0)={lim}\r\nc_cmd=C_CFG_LIMIT\r\n"
            reply = self.comm.write_readlines(cmd.encode(), 3)
            self._wait_cmd_0("Getting limits")
            reply = self.comm.write_readline(b"c_par(0),13,1\r\n")
        data = numpy.fromstring(reply.decode(), sep="\n")
        low_pose = Pose(*data[1:7])
        high_pose = Pose(*data[7:13])
        return dict(low_limits=low_pose, high_limits=high_pose)

    def _axis_status(self) -> tuple:
        """Read axis status variables
        Returns:
           (tuple): Axis status variables
        """
        with self.comm.lock:
            reply = self.comm.write_readline(b"s_ax_1,6,1\r\n")
        return tuple(int(i) for i in reply.split())

    def axis_status(self) -> str:
        """Read axis status variables
        Returns:
           (str): Axis status
        """
        status = self._axis_status()
        txt = "Axis status:\n"
        for i in range(6):
            txt += f"--- Axis {i+1}:\n{self.AxisState(status[i]).status}\n"
        return txt

    @property
    def axis_state(self) -> str:
        """Read axis status variables
        Returns:
           (str): Axis status
        """
        return self.axis_status()

    def _axis_positions(self) -> tuple:
        """Read axis positions
        Returns:
           (tuple): Axis positions
        """
        with self.comm.lock:
            reply = self.comm.write_readline(b"s_pos_ax_1,6,1\r\n")
        return tuple(float(i) for i in reply.split())

    @property
    def axis_positions(self) -> str:
        """Read axis positions
        Returns:
           (str): Axis positions
        """
        positions = self._axis_positions()
        txt = "Axis positions:\n"
        for i in range(6):
            txt += f"   Axis {i+1}: {positions[i]:8.4f}\n"
        return txt

    def _system_status(self) -> int:
        """Read system status variable (short)
        Returns:
           (int): Hexapod system status
        """
        with self.comm.lock:
            reply = self.comm.write_readline(b"s_hexa\r\n")
        return int(reply)

    @property
    def system_status(self):
        return self.Status(self._system_status())

    @property
    def tspeed(self):
        speed = self._get_speed()
        return speed["vt"]

    @property
    def rspeed(self):
        speed = self._get_speed()
        return speed["vr"]

    def set_origin(self, user_origin, object_origin):
        """
        c_cfg=1
        c_par(0)=txu c_par(1)= tyu c_par(2)= tzu c_par(3)= rxu c_par(4)= ryu c_par(5)= rzu
        c_par(6)=txo c_par(7)= tyo c_par(8)= tzo c_par(9)= rxo c_par(10)= ryo c_par(11)= rzo
        c_cmd=C_CFG_CS
        """
        par_cmd = []
        par_index = 0
        for pos in user_origin + object_origin:
            par_cmd.append(f"c_par({par_index})={pos}")
            par_index += 1
        if par_index != 12:
            raise HexapodError("user_origin and object_origin must contains 6 values")

        cmd_string = b"c_cfg=1\r\n"
        par_string = " ".join(par_cmd)
        cmd_string += par_string.encode() + b"\r\n"
        cmd_string += b"c_cmd=C_CFG_CS\r\n"
        with self.comm.lock:
            self.comm.write_readlines(cmd_string, 3)

    def dump(self, **kwargs):
        """Desposit a full confession (nobody expects the Spanish Inquisition)"""
        return self.full_system_status

    def __info__(self):
        """display info on hexapod"""
        return self.full_system_status

    def _cfg_home(self):
        """Return home task options
        Returns:
           (bool): Home auto: automatic homing enabled
           (bool): Home virtual: Virtual homing enabled
           (int): Home type
        """
        with self.comm.lock:
            self.comm.write_readlines(b"c_cfg=0\r\nc_cmd=C_CFG_HOME\r\n", 2)
            # wait c_cmd == 0
            self._wait_cmd_0("Getting home options")
            reply = self.comm.write_readline(b"c_par(0),3,1\r\n")
        data = reply.split(b"\n")
        return bool(data[0]), bool(data[1]), int(data[2])

    @property
    def cfg_home(self):
        """Return home task options
        Returns:
           (str): Home type options
        """
        home_auto, home_virtual, home_type = self._cfg_home()
        txt = "Home auto: " + ("enabled" if home_auto else "disabled")
        txt += "\nHome virtual: " + ("enabled" if home_virtual else "disabled")
        txt += f"\nConfigured home type: {home_type}\n"
        return txt

    def homing(self):
        """
        start the homing procedure
        """
        with self.comm.lock:
            self.comm.write_readline(b"c_cmd=C_HOME\r\n")

    def _homing(self, async_=False):
        """
        homing procedure
        """
        action = self._action_state()
        if action != 0:
            # some other action running, cannot home
            print(f"Warning: action running: {self.ACTION_STATES[action]}")
            # should we return/raise error here?

        with self.comm.lock:
            self.comm.write_readline(b"c_cmd=C_HOME\r\n")
        if async_:
            return

        gevent.sleep(0.2)
        if self._action_state() == 4:
            # homing now
            print("Hexapod is homing")
        for delay in range(60):
            state = self._action_state()
            if state == 0:
                # done. Note that we just count cycles, not measure time
                print(f"Homing finished after {delay} seconds")
                return
            if state == 4:
                # still homing
                pass
            else:
                # unexpected state
                print(f"Unexpected state {self.ACTION_STATES[state]}")
                break
            gevent.sleep(1)
        # time out
        print(f"Hexapod status after 60 seconds: {self.ACTION_STATES[state]}")

    def _stop(self):
        """stop current action"""
        with self.comm.lock:
            self.comm.write_readline(b"c_cmd=C_STOP\r\n")

    def _reset(self):
        """soft reset state register"""
        with self.comm.lock:
            self.comm.write_readline(b"c_cmd=C_CLEARERROR\r\n")

    def connect(self):
        """connect to controller"""
        self.comm.connect()
        # should we check if this actually worked?

    def _validate_move(self, pose):
        """
        c_par(0)=vm
        c_par(1)=movetype
        c_par(2)=tx c_par(3)=ty c_par(4)=tz c_par(5)=rx c_par(6)=ry c_par(7)=rz
        c_cmd=C_VALID_PTP

        vm = validation mode (only 1 implemented)
        movetype 0 = absolute
                 1 = object relative
                 2 = user relative
        """
        parameters = []
        for i, value in enumerate([1, 0] + list(pose)):
            parameters.append(f"c_par({i})={value}")
        parameters.append("c_cmd=C_VALID_PTP\r\n")
        cmd = " ".join(parameters)
        with self.comm.lock:
            self.comm.write_readline(cmd.encode())
            self._wait_cmd_0("Validating motion")
            ans = self.comm.write_readline(b"c_par(0)\r\n")
            ans = int(ans)
        if ans < 0:
            raise HexapodError("Move validation failed")
        if ans > 0:
            txt = [
                "Move not allowed",
            ]
            for (value, desc) in self.VALIDATION_ERRORS:
                if ans & (1 << value):
                    txt.append(desc)
            err = ", ".join(txt)
            raise HexapodError(err)

    def _move(self, pose, async_=False):
        """
        c_par(0)=movetype
        c_par(1)=tx c_par(2)=ty c_par(3)=tz c_par(4)=rx c_par(5)=ry c_par(6)=rz
        c_cmd=C_MOVE_PTP

        movetype 0 = absolute
                 1 = object relative
                 2 = user relative
        """
        self._validate_move(pose)

        parameters = []
        for i, value in enumerate([0] + list(pose)):
            parameters.append(f"c_par({i})={value}")
        parameters.append("c_cmd=C_MOVE_PTP\r\n")
        cmd = " ".join(parameters)
        with self.comm.lock:
            self.comm.write_readline(cmd.encode())
            self._wait_moving("Wait motion starts")

    def _cbk(self, ssh_cmd):
        """
        This callback is called on every connection.
        Remove the Banner i.e:**STDIN Open for ASCII Input\n**
        set echo7
        """
        transaction = ssh_cmd.new_transaction()
        ssh_cmd._readline(transaction, eol=b"\n")
        ssh_cmd.write_readline(b"echo7\r\n")

    def _get_speed(self):
        """
        c_cfg=0
        c_cmd=C_CFG_SPEED
        then c_par(0),6,1
        """
        with self.comm.lock:
            self.comm.write_readlines(b"c_cfg=0\r\nc_cmd=C_CFG_SPEED\r\n", 2)
            # wait c_cmd == 0
            self._wait_cmd_0("Getting Speed values")
            reply = self.comm.write_readline(b"c_par(0),6,1\r\n")
        return {
            k: float(v)
            for k, v in zip(
                ("vt", "vr", "vt_min", "vr_min", "vt_max", "vr_max"), reply.split(b"\n")
            )
        }

    def _wait_moving(self, timeout_msg):
        with gevent.Timeout(3.0, self.WaitTimeout(timeout_msg)):
            wait_moving = 0
            while not wait_moving:
                gevent.sleep(10e-3)
                status = self.system_status
                wait_moving = status.moving

    def _wait_cmd_0(self, timeout_msg):
        with gevent.Timeout(3.0, self.WaitTimeout(timeout_msg)):
            wait_return = 1
            while wait_return:
                gevent.sleep(20e-3)
                wait_return = int(self.comm.write_readline(b"c_cmd\r\n"))
