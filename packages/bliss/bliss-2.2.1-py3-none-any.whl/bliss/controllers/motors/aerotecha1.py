import weakref
import gevent
import automation1 as a1

from bliss.controllers.motor import Controller
from bliss.common.axis import AxisState
from bliss.common.switch import Switch as BaseSwitch
from bliss.common.encoder import Encoder as BaseEncoder
from bliss.common.encoder import lazy_init

from bliss.common.utils import object_method
from bliss.common.logtools import log_debug


def discover_aerotech_axes(host):
    ctrl = a1.Controller.connect(host=host)
    if not ctrl.is_running:
        ctrl.start()
    print("          name    speed      acc   stroke unit   resolution")
    print("    ---------- -------- -------- -------- ---- ------------")
    for axis in ctrl.runtime.parameters.axes:
        chan = axis.axis_index
        name = axis.identification.axisname.value
        unit = axis.units.unitsname.value
        speed = axis.motion.defaultaxisspeed.value
        acc = axis.motion.defaultaxisramprate.value
        stroke = axis.motion.maxjogdistance.value
        resolution = axis.units.countsperunit.value
        print(
            f"{chan:2d}: {name:10s} {speed:8.2f} {acc:8.2f} {stroke:8.2f} {unit:4s} {resolution:12.3f}"
        )
    ctrl.disconnect()


class AerotechA1(Controller):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        config = self.config.config_dict
        self.__ipaddr = config.get("ipaddress", None)
        if self.__ipaddr is None:
            raise ValueError("Need to specify ipaddress in AertotechA1 config")
        self.controller = None

    def _create_subitem_from_config(
        self, name, cfg, parent_key, item_class, item_obj=None
    ):
        if parent_key == "switches":
            switch = item_class(name, self, cfg)
            self._switches[name] = switch
            return switch
        else:
            return super()._create_subitem_from_config(
                name, cfg, parent_key, item_class, item_obj
            )

    def initialize(self):
        self._aero_axis = {}
        self._aero_speed = {}
        self._aero_acc = {}
        self._aero_enc = {}

        self._aero_state = AxisState()
        self._aero_state.create_state("HOMEDONE", "Homing done")

        self._is_moving = {}
        self.__move_task = None

        self.controller = a1.Controller.connect(host=self.__ipaddr)

    def close(self):
        if self.controller is not None:
            self.controller.disconnect()

    def initialize_hardware(self):
        self.controller.start()
        self._commands.fault_and_error.acknowledgeall()

    def initialize_axis(self, axis):
        log_debug(self, "initialize_axis %s", axis.name)
        if axis.name not in self._aero_axis.keys():
            aero_name = axis.config.get("aero_name", str, "")
            # --- check aero name not already configured
            if aero_name in self._aero_axis.values():
                others = [
                    name
                    for name in self._aero_axis
                    if self._aero_axis[name] == aero_name
                ]
                raise ValueError(
                    "Aero Axis [%s] already defined for [%s]"
                    % (aero_name, ",".join(others))
                )
            # --- check aero name is known to controller
            self._check_valid_aero_name(aero_name)

            # --- mapping bliss axis name <> controller axis name
            self._aero_axis[axis.name] = aero_name

    def _check_valid_aero_name(self, name):
        try:
            self._parameters.axes[name]
        except a1.ControllerException:
            raise ValueError("Aero axis name [%s] does not exist on controller" % name)

    def _axis_to_aero(self, axis):
        aero_axis = self._aero_axis.get(axis.name, None)
        if aero_axis is None:
            raise ValueError("Aerotech axis [%s] not initialised" % axis.name)
        return aero_axis

    def initialize_hardware_axis(self, axis):
        log_debug(self, "initialize_hardware_axis", axis.name)
        self.set_on(axis)

    def initialize_encoder(self, encoder):
        if encoder.name not in self._aero_enc.keys():
            aero_name = encoder.config.get("aero_name", str, None)
            if aero_name is None:
                raise ValueError(
                    "Missing aero_name key in %s encoder config" % encoder.name
                )
            self._check_valid_aero_name(aero_name)
            self._aero_enc[encoder.name] = aero_name

            encoder.init_output()

    def _enc_to_aero(self, encoder):
        aero_enc = self._aero_enc.get(encoder.name, None)
        if aero_enc is None:
            raise ValueError("Aerotech encoder [%s] not initialised" % encoder.name)
        return aero_enc

    @property
    def _commands(self):
        return self.controller.runtime.commands

    @property
    def _status(self):
        return self.controller.runtime.status

    @property
    def _parameters(self):
        return self.controller.runtime.parameters

    def __info__(self):
        serial = self.controller.serial_number
        version = a1.version_gen.__version__
        info = "\nAEROTECH AUTOMATION1 :\n"
        info += f"     IP address    = {self.__ipaddr}\n"
        info += f"     Serial number = {serial}\n"
        info += f"     MDK version   = {version}\n"
        return info

    def clear_error(self, axis):
        name = self._axis_to_aero(axis)
        self._commands.fault_and_error.faultacknowledge(name)

    def set_on(self, axis):
        self.clear_error(axis)
        name = self._axis_to_aero(axis)
        self._commands.motion.enable(name)

    def set_off(self, axis):
        name = self._axis_to_aero(axis)
        self._commands.motion.disable(name)

    def set_velocity(self, axis, new_vel):
        self._aero_speed[axis.name] = new_vel / abs(axis.steps_per_unit)

    def read_velocity(self, axis):
        return self._aero_speed[axis.name] * abs(axis.steps_per_unit)

    def set_acceleration(self, axis, new_acc):
        name = self._axis_to_aero(axis)
        acc = new_acc / abs(axis.steps_per_unit)
        self._commands.motion_setup.setupaxisrampvalue(
            name, a1.RampMode.Rate, acc, a1.RampMode.Rate, acc
        )
        self._aero_acc[axis.name] = acc

    def read_acceleration(self, axis):
        return self._aero_acc[axis.name] * abs(axis.steps_per_unit)

    def read_status(self, axis):
        name = self._axis_to_aero(axis)
        items = a1.StatusItemConfiguration()
        items.axis.add(a1.AxisStatusItem.AxisFault, name)
        items.axis.add(a1.AxisStatusItem.AxisStatus, name)
        items.axis.add(a1.AxisStatusItem.DriveStatus, name)
        result = self._status.get_status_items(items)
        fault = result.axis.get(a1.AxisStatusItem.AxisFault, name).value
        axis_status = result.axis.get(a1.AxisStatusItem.AxisStatus, name).value
        drive_status = result.axis.get(a1.AxisStatusItem.DriveStatus, name).value

        return (int(fault), int(axis_status), int(drive_status))

    def state(self, axis):
        (aero_fault, aero_axis, aero_drive) = self.read_status(axis)

        clockwise = axis.config.get("direction", "clockwise") == "clockwise"
        state = self._aero_state.new()
        if aero_fault & a1.AxisFault.CwEndOfTravelLimitFault:
            state.set("LIMPOS" if clockwise else "LIMNEG")
        if aero_fault & a1.AxisFault.CcwEndOfTravelLimitFault:
            state.set("LIMNEG" if clockwise else "LIMPOS")
        if aero_fault > 0:
            state.set("FAULT")

        if aero_axis & a1.AxisStatus.Homed:
            state.set("HOMEDONE")

        if aero_drive & a1.DriveStatus.Enabled:
            # In the SDK it says:
            # Jogging = 1 << 8: The axis is performing asynchronous motion (MoveIncremental(), MoveAbsolute(), MoveFreerun()).
            if (
                aero_drive & a1.DriveStatus.MoveActive
                or aero_axis & a1.AxisStatus.Jogging
            ):
                state.set("MOVING")
            else:
                state.set("READY")
        else:
            state.set("OFF")

        if not state.MOVING:
            self._is_moving[axis.name] = False

        if aero_fault:
            self.clear_error(axis)

        return state

    def start_all(self, *motion_list):
        names = list()
        pos = list()
        speeds = list()
        for motion in motion_list:
            axis = motion.axis
            names.append(self._axis_to_aero(axis))
            pos.append(motion.target_pos / axis.steps_per_unit)
            speeds.append(self._aero_speed[axis.name])

        self._commands.motion.moveabsolute(names, pos, speeds)
        for motion in motion_list:
            self._is_moving[motion.axis.name] = True

    def stop_all(self, *motion_list):
        names = list()
        for motion in motion_list:
            axis = motion.axis
            names.append(self._axis_to_aero(axis))
        self._commands.motion.abort(names)

    def stop(self, axis):
        name = self._axis_to_aero(axis)
        self._commands.motion.abort(name)

    def start_jog(self, axis, velocity, direction):
        name = self._axis_to_aero(axis)
        jog_vel = direction * velocity / abs(axis.steps_per_unit)
        self._commands.motion.movefreerun(name, jog_vel)

    def stop_jog(self, axis):
        name = self._axis_to_aero(axis)
        self._commands.motion.movefreerunstop(name)

    def read_position(self, axis):
        name = self._axis_to_aero(axis)
        items = a1.StatusItemConfiguration()
        items.axis.add(a1.AxisStatusItem.PositionCommand, name)
        items.axis.add(a1.AxisStatusItem.PositionFeedback, name)
        result = self._status.get_status_items(items)
        if not self._is_moving.get(axis.name, False):
            position = result.axis.get(a1.AxisStatusItem.PositionCommand, name).value
        else:
            position = result.axis.get(a1.AxisStatusItem.PositionFeedback, name).value
        return position

    def read_encoder(self, encoder):
        name = self._enc_to_aero(encoder)
        items = a1.StatusItemConfiguration()
        items.axis.add(a1.AxisStatusItem.PositionFeedback, name)
        result = self._status.get_status_items(items)
        position = result.axis.get(a1.AxisStatusItem.PositionFeedback, name).value
        return position * encoder.steps_per_unit

    def home_search(self, axis, switch):
        # direction may be set using
        # runtime.parameters.axes["X"].hometype
        # to be checked
        name = self._axis_to_aero(axis)
        self._commands.motion.homeasync(name)

    def home_state(self, axis):
        name = self._axis_to_aero(axis)
        items = a1.StatusItemConfiguration()
        items.axis.add(a1.AxisStatusItem.AxisStatus, name)
        result = self._status.get_status_items(items)
        axis_status = int(result.axis.get(a1.AxisStatusItem.AxisStatus, name).value)

        state = self._aero_state.new()
        if axis_status & a1.AxisStatus.Homing:
            state.set("MOVING")
            return state
        else:
            return self.state(axis)

    def get_axis_info(self, axis):
        name = self._axis_to_aero(axis)
        info = "AEROTECH AXIS :\n"
        info += f"     controller axis name : {name}\n"
        info += f"     use {axis.name}.dump_status() to get a detailed axis status\n"
        return info

    @object_method(types_info=("None", "str"))
    def get_info(self, axis):
        (axis_fault, axis_status, drive_status) = self.read_status(axis)
        info = f"\nAXIS STATUS : {axis_status:08x}"
        for item in a1.AxisStatus:
            value = bool(axis_status & item.value)
            info += f"\n{item.name:>30s} {value}"
        info += f"\n\nAXIS FAULT : {axis_fault:08x}"
        for item in a1.AxisFault:
            value = bool(axis_fault & item.value)
            info += f"\n{item.name:>30s} {value}"
        info += f"\n\nDRIVE STATUS : {drive_status:08x}"
        for item in a1.DriveStatus:
            value = bool(drive_status & item.value)
            info += f"\n{item.name:>30s} {value}"
        return info

    @object_method(types_info=("None", "None"))
    def dump_status(self, axis):
        info = self.get_info(axis)
        print(info)

    def get_status_item(self, axis, *names):
        items = list()
        if not len(names):
            for item in a1.AxisStatusItem:
                items.append(item)
        else:
            for name in names:
                for item in a1.AxisStatusItem:
                    if item.name == name:
                        items.append(item)
        aero_name = self._axis_to_aero(axis)
        request = a1.StatusItemConfiguration()
        for item in items:
            request.axis.add(item, aero_name)
        result = self._status.get_status_items(request)
        reply = dict()
        for item in items:
            reply[item.name] = result.axis.get(item, aero_name).value
        return reply

    # --- aerotech specific commands

    def _get_axis_parameter_value(self, aero_name, group_name, parameter_name):
        param_group = getattr(self._parameters.axes[aero_name], group_name)
        param_item = getattr(param_group, parameter_name)
        return param_item.value

    def _set_axis_parameter_value(self, aero_name, group_name, parameter_name, value):
        param_group = getattr(self._parameters.axes[aero_name], group_name)
        param_item = getattr(param_group, parameter_name)
        param_item.value = value

    def get_encoder_parameter(self, encoder, group, name):
        aero_name = self._enc_to_aero(encoder)
        return self._get_axis_parameter_value(aero_name, group, name)

    def set_encoder_parameter(self, encoder, group, name, value):
        aero_name = self._enc_to_aero(encoder)
        self._set_axis_parameter_value(aero_name, group, name, value)

    def get_axis_parameter(self, axis, group, name):
        aero_name = self._axis_to_aero(axis)
        return self._get_axis_parameter_value(aero_name, group, name)

    def set_axis_parameter(self, axis, group, name, value):
        aero_name = self._axis_to_aero(axis)
        self._set_axis_parameter_value(aero_name, group, name, value)

    def enable_drive_encoder_output(self, encoder):
        """Enable encoder output on the auxiliary encoder output of the axis drive"""
        name = self._enc_to_aero(encoder)
        self._commands.device.driveencoderoutputoff(
            name, a1.EncoderOutputChannel.AuxiliaryEncoder
        )
        self._commands.device.driveencoderoutputconfigureinput(
            name,
            a1.EncoderOutputChannel.AuxiliaryEncoder,
            a1.EncoderInputChannel.PrimaryEncoder,
        )
        self._commands.device.driveencoderoutputconfiguredivider(
            name, a1.EncoderOutputChannel.AuxiliaryEncoder, encoder.output_divider
        )
        self._set_axis_parameter_value(
            name,
            "feedback",
            "primaryemulatedquadraturedivider",
            encoder.internal_divider,
        )
        self._commands.device.driveencoderoutputon(
            name,
            a1.EncoderOutputChannel.AuxiliaryEncoder,
            a1.EncoderOutputMode.Default,
        )

    def disable_drive_encoder_output(self, encoder):
        name = self._enc_to_aero(encoder)
        self._commands.device.driveencoderoutputoff(
            name, a1.EncoderOutputChannel.AuxiliaryEncoder
        )

    def enable_switch_encoder_output(self, encoder):
        """Enable encoder output on the high speed encoder output of the controller"""
        name = self._enc_to_aero(encoder)
        self._commands.device.driveencoderoutputoff(
            name, a1.EncoderOutputChannel.HighSpeedOutputs
        )
        self._commands.device.driveencoderoutputconfigureinput(
            name,
            a1.EncoderOutputChannel.HighSpeedOutputs,
            a1.EncoderInputChannel.PrimaryEncoder,
        )
        self._commands.device.driveencoderoutputconfiguredivider(
            name, a1.EncoderOutputChannel.HighSpeedOutputs, encoder.output_divider
        )
        self._commands.device.driveencoderoutputon(
            name,
            a1.EncoderOutputChannel.HighSpeedOutputs,
            a1.EncoderOutputMode.Default,
        )

    def disable_switch_encoder_output(self, encoder):
        name = self._enc_to_aero(encoder)
        self._commands.device.driveencoderoutputoff(
            name, a1.EncoderOutputChannel.HighSpeedOutputs
        )

    def digital_output_get(self, axis, output_num):
        name = self._axis_to_aero(axis)
        self._commands.io.digitaloutputget(name, output_num)

    def digital_output_set(self, axis, output_num, value):
        name = self._axis_to_aero(axis)
        self._commands.io.digitaloutputset(name, output_num, value)

    def home_axes(self, *axes):
        names = [self._axis_to_aero(axis) for axis in axes]
        self._commands.motion.home(names)

    def wait_for_inposition(self, *axes):
        names = [self._axis_to_aero(axis) for axis in axes]
        self._commands.motion.waitforinposition(names)

    def enable_axes(self, *axes):
        names = [self._axis_to_aero(axis) for axis in axes]
        self._commands.motion.enable(names)

    def disable_axes(self, *axes):
        names = [self._axis_to_aero(axis) for axis in axes]
        self._commands.motion.disable(names)


class Encoder(BaseEncoder):
    def __init__(self, name, controller, motor_controller, config):
        super().__init__(name, controller, motor_controller, config)
        self.mode = "SINGLE"
        self._internal_divider = int(config.get("internal_divider", 1))
        self._output_divider = int(config.get("output_divider", 1))
        self._output_encoder = bool(config.get("output_encoder", False))
        self._raw_steps_per_unit = float(config.get("steps_per_unit", 1.0))

    def init_output(self):
        if self._output_encoder:
            self.controller.enable_drive_encoder_output(self)

    @property
    @lazy_init
    def steps_per_unit(self):
        return self._raw_steps_per_unit / self._internal_divider / self._output_divider

    @property
    def raw_steps_per_unit(self):
        return self.steps_per_unit

    @property
    def aerotech_resolution(self):
        return self.controller.get_encoder_parameter(self, "units", "countsperunit")

    @property
    def unit(self):
        if self.axis is not None:
            return self.axis.unit
        else:
            return self._unit

    @property
    def internal_divider(self):
        return self._internal_divider

    @internal_divider.setter
    def internal_divider(self, value):
        self._internal_divider = int(value)
        self.init_output()

    @property
    def output_divider(self):
        return self._output_divider

    @output_divider.setter
    def output_divider(self, value):
        self._output_divider = int(value)
        self.init_output()

    @property
    def output_encoder(self):
        return self._output_encoder

    @output_encoder.setter
    def output_encoder(self, onoff):
        self._output_encoder = bool(onoff)
        if self._output_encoder:
            self.controller.enable_drive_encoder_output(self)
        else:
            self.controller.disable_drive_encoder_output(self)


class Switch(BaseSwitch):
    def __init__(self, name, controller, config):
        BaseSwitch.__init__(self, name, config)
        self.__controller = weakref.proxy(controller)
        self.__axes = weakref.WeakValueDictionary()
        self.__current = "DISABLED"

    def _init(self):
        axes = self.config.get("axes", [])
        if not len(axes):
            axes = [
                axis
                for axis in self.__controller._axes.items()
                if axis.encoder is not None
            ]
        else:
            for axis in axes:
                if axis.encoder is None:
                    raise ValueError(
                        "AeroteachA1 Switch : axis [%s] has no encoder configured",
                        axis.name,
                    )

        self.__axes.update({axis.name.upper(): axis for axis in axes})

    def _states_list(self):
        return list(self.__axes.keys()) + ["DISABLED"]

    def _get(self):
        return self.__current

    def _set(self, state):
        if state == "DISABLED":
            if self.__current_state != "DISABLED":
                axis = self.__axes[self.__current]
                self.__controller.disable_switch_encoder_output(axis.encoder)
                self.__current = state
        else:
            axis = self.__axes.get(state)
            if state is None:
                raise ValueError(
                    "AeroteachA1 Switch : state [%s] does not exist", axis.name
                )

            self.__controller.enable_switch_encoder_output(axis.encoder)
            self.__current = state


class AerotechA1Program(object):
    def __init__(self, controller, progname, progdata, progtask=1):
        if isinstance(controller, AerotechA1):
            self.controller = controller.controller
        elif isinstance(controller, a1.Controller):
            self.controller = controller
        else:
            raise ValueError("AerotechA1Progran wrong controller object type")
        self.progdata = progdata
        self.progname = progname
        self.progtask = progtask
        self.stop()

    def __info__(self):
        info = f"Program name  : {self.progname}\n"
        info += f"Source file   : {self.source_filename}\n"
        info += f"Compiled file : {self.compiled_filename}\n"
        info += f"Task number   : {self.progtask}\n"
        info += f"Task state    : {self.status}\n"
        return info

    @property
    def task(self):
        return self.controller.runtime.tasks[self.progtask]

    @property
    def state(self):
        return self.task.status.task_state

    @property
    def source_filename(self):
        fname = self.task.status.aeroscript_source_file_name
        if not len(fname):
            fname = "UNDEFINED"
        return fname

    @property
    def compiled_filename(self):
        fname = self.task.status.compiled_aeroscript_source_file_name
        if not len(fname):
            fname = "UNDEFINED"
        return fname

    @property
    def status(self):
        state = self.state
        for item in a1.TaskState:
            if state == item.value:
                return item.name
        return "UNKNOWN"

    @property
    def filename(self):
        return f"{self.progname}.ascript"

    def upload_program(self):
        self.controller.files.write_text(self.filename, self.progdata)

    def download_program(self):
        return self.controller.files.read_text(self.filename)

    def prepare(self):
        self.upload_program()
        self.task.program.load(self.filename)
        if self.state != a1.TaskState.ProgramReady:
            raise RuntimeError(f"AerotechA1Progran failed to load {self.progname}")

    def start(self):
        self.task.program.start()

    def stop(self):
        self.task.program.stop()

    def is_running(self):
        state = self.state
        if state == a1.TaskState.Error:
            errtxt = self.task.status.error_message
            raise RuntimeError(f" AerotechA1Progran error on {self.progname}: {errtxt}")
        if state == a1.TaskState.ProgramRunning:
            return True
        return False


def aerotech_test_program(progname, progdata, *motors, polling_time=0.1):
    if not len(motors):
        raise ValueError("Need to specify at least one motor")
    ctrl = motors[0].controller
    encs = [mot.encoder for mot in motors]
    if None in encs:
        raise ValueError("Motors should have an encoder")

    prog = AerotechA1Program(ctrl, progname, progdata)
    print("Prepare program")
    prog.prepare()
    print(prog.__info__())

    try:
        print("Start program")
        prog.start()
        while prog.is_running():
            encvals = [f"{enc.name} = {enc.raw_read:10.6f}" for enc in encs]
            print(f"status = {prog.status}", *encvals)
            gevent.sleep(polling_time)
        print(f"status = {prog.status}")
    finally:
        print("Stop program")
        prog.stop()
        for mot in motors:
            mot.sync_hard()
