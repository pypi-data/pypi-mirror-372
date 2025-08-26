# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

"""
IcePAP shutter.
Basic configuration:
    name: fastshutter
    axis_name: mot_name            #axis name
    external_control: $wago_switch #external control reference (not mandatory)
    closed_position: 1             # the closed position (in user position)
    opened_position: 2             # the opened position (in user position)
"""

from __future__ import annotations
import weakref
import math
from tabulate import tabulate

from bliss.config.beacon_object import BeaconObject
from bliss.controllers.shutters.shutter import AxisWithExtTriggerShutter
from bliss.common.shutter import BaseShutterState
from bliss.common.standard import info
from bliss.common.axis import Axis
from bliss.shell.getval import getval_idx_list, getval_float
from bliss.controllers.shutters.shutter import ShutterMode
from bliss.shell.standard import print_html


class Shutter(AxisWithExtTriggerShutter):
    """
    Icepap Shutter class.
    """

    _auto_power = False

    @property
    def axis(self):
        if self.mode == self.CONFIGURATION:
            return self._axis
        else:
            raise RuntimeError(
                "Shutter %s is not in configuration mode, "
                " please switch to that mode before asking "
                " the reference axis" % self.name
            )

    closed_position = BeaconObject.property_setting("closed_position")

    @closed_position.setter
    def closed_position(self, position):
        if self._is_initialized and self.mode != self.CONFIGURATION:
            raise RuntimeError(
                "Shutter %s: can set the closed position, "
                "not in Configuration mode" % self.name
            )

    opened_position = BeaconObject.property_setting("opened_position")

    @opened_position.setter
    def opened_position(self, position):
        if self._is_initialized and self.mode != self.CONFIGURATION:
            raise RuntimeError(
                "Shutter %s: can set the opened position, "
                "not in Configuration mode" % self.name
            )

    def __init__(self, name, controller, config):
        AxisWithExtTriggerShutter.__init__(self, name, config)
        self.__controller = weakref.proxy(controller)
        self._axis: Axis | None = None

    def _init(self):
        axis_name = self.config.get("axis_name")
        if axis_name is not None:
            self._axis = self.__controller.get_axis(axis_name)
            self._axis.position  # real init
        else:
            raise RuntimeError("Shutter %s has no axis_name configured" % self.name)

        self._auto_power = self.config.get("auto_power", False)

    def _set_mode(self, mode):
        """
        Overload AxisWithExtTriggerShutter abstract method.
        """
        self._axis.activate_tracking(False)

        if mode == self.EXTERNAL:
            ext_ctrl = self.external_control
            if ext_ctrl is not None:
                ext_ctrl.set("CLOSED")

            closed_position = self.closed_position
            if closed_position is None:
                raise RuntimeError(
                    "Shutter %s hasn't been configured, "
                    "missing closed_position" % self.name
                )
            opened_position = self.settings.get(
                "opened_position", self.config.get("opened_position")
            )
            if opened_position is None:
                raise RuntimeError(
                    "Shutter %s hasn't been configured, "
                    "missing opened_position" % self.name
                )
            self._load_position(closed_position, opened_position)

            # Let the power always on in external mode as it cannot be activated
            # by external signal.
            if self._auto_power:
                self._axis.on()

            self._axis.activate_tracking(True)
        else:
            # Switch power off in automatic or configuration mode.
            if self._auto_power:
                self._axis.off()

    def _load_position(self, closed_position, opened_position):
        """
        Update positions in Icepap controller and in settings.

        No check of current icepap positions ???
        """
        self._axis.set_tracking_positions(
            [closed_position, opened_position], cyclic=True
        )
        self.settings.update(
            {"closed_position": closed_position, "opened_position": opened_position}
        )

    def _opening_time(self):
        return self._move_time()

    def _closing_time(self):
        return self._move_time()

    def _move_time(self):
        """
        Calculation of opening or closing movement duration.
        Return moving time *in seconds*.
        """
        acctime = self._axis.acctime  # second
        velocity = self._axis.velocity  # user_unit / second
        acceleration_distance = velocity * acctime  # user_unit
        total_distance = abs(self.opened_position - self.closed_position)  # user_unit
        if acceleration_distance > total_distance:
            return 2 * math.sqrt(total_distance / self._axis.acceleration)
        else:
            t1 = (total_distance - acceleration_distance) / velocity
            return t1 + 2 * acctime

    def _measure_open_close_time(self):
        """
        Oveload method of `AxisWithExtTriggerShutter` class.
        Return: (opening, closing) time in seconds.
        """
        tmove = self._move_time()
        return tmove, tmove

    def _open(self):
        """
        Overload AxisWithExtTriggerShutter abstract method.
        """
        open_pos = self.opened_position
        if open_pos is None:
            raise RuntimeError(
                "Shutter %s hasn't been configured, "
                "missing opened_position" % self.name
            )

        if self._auto_power:
            self._axis.on()

        self._axis.move(open_pos)

        if self._auto_power:
            self._axis.off()

    def _close(self):
        """
        Overload AxisWithExtTriggerShutter abstract method.
        """
        closed_pos = self.closed_position
        if closed_pos is None:
            raise RuntimeError(
                "Shutter %s hasn't been configured, "
                "missing closed_position" % self.name
            )

        self._axis.move(closed_pos)

    def _state(self):
        """
        Overload AxisWithExtTriggerShutter abstract method.
        """
        axis = self._axis
        assert axis is not None
        curr_pos = axis.position
        if curr_pos == self.closed_position:
            return BaseShutterState.CLOSED
        elif curr_pos == self.opened_position:
            return BaseShutterState.OPEN
        else:
            if axis.state.MOVING:
                return BaseShutterState.MOVING
            return BaseShutterState.UNKNOWN

    def get_info(self):
        _otime_ms = int(self.opening_time() * 100000) / 100
        tables = [
            ("State:", f"{self.state.name}"),
            ("Mode:", f"{self.mode.name}"),
            ("open position:", f"{self.opened_position}"),
            ("closed position:", f"{self.closed_position}"),
            ("steps_per_unit:", f"{self._axis.steps_per_unit}"),
            ("current position:", f"{self._axis.position} uu"),
            ("velocity:", f"{self._axis.velocity} uu/s"),
            ("acceleration:", f"{self._axis.acceleration} uu/s/s"),
            ("acctime:", f"{self._axis.acctime * 1000} ms"),
            ("opening time:", f"{_otime_ms} ms  (calculated)"),
        ]
        info_str = f"Shutter: {self.name}  (axis: {self._axis.name})\n"
        info_str += tabulate(tables)
        if self.external_control:
            info_str += f"\nExternal Control: {self.external_control.name}\n"
            info_str += info(self.external_control)

        return info_str

    def __info__(self):
        """
        On-line info about shutter.
        """
        info_str = self.get_info()
        info_str += f"\nUse {self.name}.tune() to configure parameters of the shutter's motor ({self._axis.name}).\n"
        return info_str

    def tune(self):
        """
        Interactive menu to tune the shutter motor parameters.
        * print info
        * switch to CONFIGURATION mode
        * ask for parameters
        """
        modes_list = [
            ShutterMode.CONFIGURATION,
            ShutterMode.MANUAL,
            ShutterMode.EXTERNAL,
        ]

        choise_list = modes_list.copy()
        choise_list.remove(self.mode)
        choise_list.append("exit menu")

        old_mode = self.mode

        if old_mode == ShutterMode.CONFIGURATION:
            print("hummm... already in CONFIGURATION mode ???")

        print("")
        # Use print_html() to circumvent display bug.
        print_html(self.get_info())
        print("")

        _ans = getval_idx_list(choise_list, "Switch to mode:", default=3)

        new_mode = _ans[1]
        if new_mode in modes_list:
            print("ok, shutter switches to :", new_mode)
            self.mode = new_mode

        if new_mode == ShutterMode.CONFIGURATION:
            _opos = getval_float("open position (uu)", default=self.opened_position)
            _cpos = getval_float("close position (uu)", default=self.closed_position)
            _vel = getval_float("velocity (uu/s)", default=self._axis.velocity)
            _acctime = getval_float(
                "acceleration time (ms)", default=self._axis.acctime * 1000
            )

            if _opos != self.opened_position:
                self.opened_position = _opos

            if _cpos != self.closed_position:
                self.closed_position = _cpos

            # Set velocity first, before acctime because
            # icepap controller change acceleration on velocity change.
            if _vel != self._axis.velocity:
                self._axis.velocity = _vel

            if _acctime != self._axis.acctime:
                self._axis.acctime = _acctime / 1000

            if old_mode in [ShutterMode.MANUAL, ShutterMode.EXTERNAL]:
                print("revert shutter mode to:", old_mode)
                self.mode = old_mode
            else:
                print(
                    "You must manually switch back to external mode to validate changes."
                )

        print("")
        # Use print_html() to circumvent display bug.
        print_html(self.get_info())
        print("")
