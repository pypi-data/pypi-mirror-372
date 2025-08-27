# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

""" BaseShutter, BaseShutterState """

from contextlib import contextmanager
from enum import Enum, unique


@unique
class BaseShutterState(Enum):
    """Base states"""

    UNKNOWN = "Unknown state"
    OPEN = "Open"
    CLOSED = "Closed"
    MOVING = "Moving"
    FAULT = "Fault state"

    # Used by Tango
    DISABLE = "Hutch not searched"
    # Used by Tango
    STANDBY = "Wait for permission"
    # Used by Tango
    RUNNING = "Automatic opening"


class BaseShutter:
    """Define a simple shutter"""

    # Properties
    @property
    def name(self):
        """A unique name"""
        raise NotImplementedError

    @property
    def config(self):
        """Config of shutter"""
        raise NotImplementedError

    @property
    def state(self):
        """Verbose message of the shutter state"""
        raise NotImplementedError

    @property
    def state_string(self):
        """Transfer state to a string"""
        return self.state.value

    @property
    def is_open(self):
        """Check if the device is open"""
        return self.state == BaseShutterState.OPEN

    @property
    def is_closed(self):
        """Check if the device is closed"""
        return self.state == BaseShutterState.CLOSED

    # Methods
    def open(self, timeout=None):
        """Method that opens the shutter"""
        raise NotImplementedError

    def close(self, timeout=None):
        """Method that closes the shutter"""
        raise NotImplementedError

    def __info__(self):
        return f"{self.name}: {self.state_string}"

    def __enter__(self):
        self.open()

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    @property
    @contextmanager
    def closed_context(self):
        """Context manager that ensures shutter is closed within the context.

        This is the opposite as 'normal' shutter function.

        The `close` method is only called if the shutter is not already closed.
        And the `open` state is restored only if the shutter was initially open.
        """
        was_open = self.is_open
        try:
            if not self.is_closed:
                self.close()
            yield
        finally:
            if was_open:
                self.open()

    @property
    @contextmanager
    def open_context(self):
        """Context manager that ensures shutter is open within the context.

        This is an advanced 'normal' shutter function.

        The `open` method is only called if the shutter is not already open.
        And the `closed` state is restored only if the shutter was initially closed.
        """
        was_closed = self.is_closed
        try:
            if not self.is_open:
                self.open()
            yield
        finally:
            if was_closed:
                self.closed()
