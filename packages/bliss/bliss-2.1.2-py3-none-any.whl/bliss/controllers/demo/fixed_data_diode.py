import os
import numpy
from bliss.physics import units
from bliss.common.counter import SoftCounter, SamplingMode
from bliss.common.protocols import CounterContainer
from bliss.controllers.counter import counter_namespace
from bliss.common.utils import autocomplete_property
from bliss.common.axis import Axis


class FixedDataDiode(CounterContainer):
    """Controller with a diode emitting an fixed 1D signal read from a file."""

    def __init__(self, name, config):
        self._name = name

        axis = config["axis"]
        if not isinstance(axis, Axis):
            raise RuntimeError(f"'axis' field is not an Axis (found {type(axis)})")
        self.axis = axis

        filename = config.get("data_filename")
        if filename:
            data = self._load_data(filename)
        else:
            data = numpy.array(config["data"])
        x, self._y = data.T

        axis_unit = self.axis.unit or "eV"
        if axis_unit != "eV":
            x = (x * units.ur("eV")).to(axis_unit).magnitude
        self._x = x

        self.counter = SoftCounter(
            self, self._read_signal, name=self._name, mode=SamplingMode.SINGLE
        )

    def _load_data(self, filename):
        """Load the filename as a numpy array"""
        filename = os.path.expandvars(filename)
        if not os.path.isfile(filename):
            raise RuntimeError(f"Cannot find file {filename}")
        return numpy.loadtxt(filename)

    @autocomplete_property
    def counters(self):
        return counter_namespace([self.counter])

    def _read_signal(self):
        return numpy.interp(
            self.axis.dial, self._x, self._y, left=self._y[0], right=self._y[-1]
        )
