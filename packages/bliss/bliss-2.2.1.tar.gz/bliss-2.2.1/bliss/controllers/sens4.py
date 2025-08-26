# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

"""
BLISS counter_controller for Sens4 VPM-5 SmartPirani vacuum gauge.
"""

import time

from bliss import global_map
from bliss.comm.util import get_comm
from bliss.common.counter import SamplingCounter, SamplingMode
from bliss.common.logtools import log_debug
from bliss.common.protocols import CounterContainer, counter_namespace
from bliss.common.utils import autocomplete_property
from bliss.controllers.counter import SamplingCounterController


UNITS_P = "MBAR", "PASCAL", "TORR"
UNITS_T = "CELSIUS", "FAHRENHEIT", "KELVIN"


class Hardware:
    TIME_BEFORE_QUERY = 0.5

    def __init__(self, comm):
        self.comm = comm
        self.model = self.query("MD")
        self.pressure_unit = self.query("U", command_par="P").lower()
        self.temperature_unit = self.query("U", command_par="T").lower()
        self.last_temperature = None
        self.last_pressure = None

        global_map.register(
            self,
            children_list=[self.comm],
        )

    def _write(self, sensor=254, command="MD", command_par=None, value=None):
        # sensors answer when addressed via 254
        cmd = f"@{sensor}{command}"
        cmd += "?" if value is None else "!"
        if command_par is not None:
            cmd += str(command_par)
        if value is not None:
            if command_par is not None:
                cmd = cmd + ","
            cmd = cmd + str(value)
        cmd = cmd + "\\"
        return self.comm.write(cmd.encode("ascii"), timeout=self.TIME_BEFORE_QUERY)

    def _readline(self, cast=None):
        data = self.comm.readline(eol="\\", timeout=self.TIME_BEFORE_QUERY)
        ans = data.decode("ascii")
        if ans == "":
            return ""
        # remove @253ACK
        idx = ans.find("ACK") + 3
        value = ans[idx:]
        # remove termination
        value = value[:-1]
        if cast is not None:
            value = cast(value)
        return value

    def _write_readline(
        self, sensor=254, command="MD", command_par=None, value=None, cast=None
    ):
        # sensors answer when addressed via 254
        cmd = f"@{sensor}{command}"
        cmd += "?" if value is None else "!"
        if command_par is not None:
            cmd += str(command_par)
        if value is not None:
            if command_par is not None:
                cmd = cmd + ","
            cmd = cmd + str(value)
        cmd = cmd + "\\"

        data = self.comm.write_readline(
            cmd.encode("ascii"), eol="\\", timeout=self.TIME_BEFORE_QUERY
        )

        ans = data.decode("ascii")
        if ans == "":
            return ""
        # remove @253ACK
        idx = ans.find("ACK") + 3
        value = ans[idx:]
        if cast is not None:
            value = cast(value)
        return value

    def query(self, command="MD", command_par=None, cast=None):
        return self._write_readline(command=command, command_par=command_par, cast=cast)

    def set(self, command=None, command_par=None, value=None):
        if value is not None:
            self._write(
                command=command,
                command_par=command_par,
                value=value,
            )
            time.sleep(self.TIME_BEFORE_QUERY)
        return self.query(command=command, command_par=command_par)

    def set_pressure_unit(self, value):
        if value.upper() not in UNITS_P:
            raise ValueError(f"Pressure unit must be one of {UNITS_P}")
        self.set(command="U", command_par="P", value=value.upper())
        self.pressure_unit = self.query("U", command_par="P").lower()

    def set_temperature_unit(self, value):
        if value.upper() not in UNITS_T:
            raise ValueError(f"Temperature unit must be one of {UNITS_T}")
        self.set(command="U", command_par="T", value=value.upper())
        self.temperature_unit = self.query("U", command_par="T").lower()

    def read_pressure(self):
        pressure = self.query("P", cast=float)
        self.last_pressure = pressure
        return pressure

    def read_pirani_pressure(self):
        return self.query("P", command_par="MP", cast=float)

    def read_diaphragm_pressure(self):
        return self.query("P", command_par="PZ", cast=float)

    def read_temperature(self):
        temperature = self.query("T", cast=float)
        self.last_temperature = temperature
        return temperature


class Sens4Counter(SamplingCounter):
    """
    Sens4 Counter (with additional "role")
    """

    def __init__(self, name, controller, unit, role):
        self.role = role

        super().__init__(
            name=name, controller=controller, mode=SamplingMode.LAST, unit=unit
        )


class Sens4SamplingCounterController(SamplingCounterController):
    def __init__(self, name, hw):
        super().__init__(name, register_counters=True)
        self._hw = hw

    def read(self, counter):
        if "pressure" == counter.role:
            return self._hw.read_pressure()
        elif "pirani" == counter.role:
            return self._hw.read_pirani_pressure()
        elif "diaphragm" == counter.role:
            return self._hw.read_diaphragm_pressure()
        elif "temperature" == counter.role:
            return self._hw.read_temperature()
        else:
            assert "Invalid counter role"


class Sens4(CounterContainer):
    def __init__(self, config):
        """
        Sens4 Controller
        """

        self._config = config
        self._name = config["name"]

        log_debug(self, f"Initialize Sens4 {self._name}")

        self._model = None
        self._pressure_unit = None
        self._temperature_unit = None
        self._hw: Hardware | None = None

        global_map.register(self, parents_list=["controllers", "counters"])

        self._try_connect()

    def _try_connect(self):
        try:
            self._hw = Hardware(get_comm(self._config))

            # Construct counter counter_controller
            self.counter_controller = Sens4SamplingCounterController(
                self._name, self._hw
            )

            # Construct counters
            self.counter_controller.create_counter(
                Sens4Counter, "Pressure", unit=self.pressure_unit, role="pressure"
            )
            self.counter_controller.create_counter(
                Sens4Counter, "PiraniPressure", unit=self.pressure_unit, role="pirani"
            )
            self.counter_controller.create_counter(
                Sens4Counter,
                "DiaphragmPressure",
                unit=self.pressure_unit,
                role="diaphragm",
            )
            self.counter_controller.create_counter(
                Sens4Counter,
                "Temperature",
                unit=self.temperature_unit,
                role="temperature",
            )

            global_map.register(self._hw, parents_list=[self])

        except Exception:
            log_debug(self, "Sens4 " + self.name + " is OFFLINE")
            self._hw = None

    def hw(self) -> Hardware:
        if self._hw:
            return self._hw

        self._try_connect()
        return self._hw

    @property
    def name(self):
        return self._name

    @property
    def state(self) -> str:
        return "OFFLINE" if self._hw is None else "ONLINE"

    @autocomplete_property
    def counters(self):
        return self.counter_controller.counters

    @property
    def counter_groups(self):
        groups = dict()
        groups["default"] = self.counter_controller.counters
        return counter_namespace(groups)

    @property
    def model(self):
        if self._model is None:
            self._model = self.hw().model
        return self._model

    @property
    def pressure_unit(self):
        if self._pressure_unit is None:
            self._pressure_unit = self.hw().pressure_unit
        return self._pressure_unit

    @property
    def temperature_unit(self):
        if self._temperature_unit is None:
            self._temperature_unit = self.hw().temperature_unit
        return self._temperature_unit

    def __info__(self):
        lines = []
        lines.append(f"=== Sens4: {self.name} ===")
        if self.hw():
            pressure = self.hw().read_pressure()
            temperature = self.hw().read_temperature()
            lines.append(f"model: {self.model}")
            lines.append(f"  P = {pressure} {self.pressure_unit}")
            lines.append(f"  T = {temperature} {self.temperature_unit}")
        else:
            lines.append("state: OFFLINE")

        return "\n".join(lines)
