# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

"""Helper about string formatting"""

from __future__ import annotations
from collections.abc import Callable
from typing import NamedTuple

import weakref
from silx.gui import qt


class InvalidatableSignal(qt.QObject):
    """Manage a signal which can be invalidated instead of been triggered all
    the time.
    """

    triggered = qt.Signal()

    def __init__(self, parent: qt.QObject | None = None):
        super(InvalidatableSignal, self).__init__(parent=parent)
        self.__invalidated = False

    def trigger(self):
        """Trigger the signal"""
        self.__invalidated = False
        self.triggered.emit()

    def triggerIf(self, condition=None):
        """Trigger the signal only if this `condition` is True.

        Else this object is invalidated.
        """
        if condition:
            self.trigger()
        else:
            self.__invalidated = True

    def invalidate(self):
        """Invalidate this object.

        Calling `validate` will execute the trigger.
        """
        self.__invalidated = True

    def validate(self):
        """Trigger the signal, only if this object was invalidated."""
        if self.__invalidated:
            self.trigger()


class Event(NamedTuple):
    callback: Callable
    args: tuple[object, ...]
    kwargs: dict[str, object]
    callbackId: object = None

    def emit(self):
        self.callback(*self.args, **self.kwargs)


class EventAggregator(qt.QObject):
    """Allow to stack events and to trig them time to time"""

    eventAdded = qt.Signal()

    def __init__(self, parent: qt.QObject | None = None):
        super(EventAggregator, self).__init__(parent=parent)
        self.__eventStack: list[Event] = []
        self.__callbacks: weakref.WeakKeyDictionary[
            Callable, Callable
        ] = weakref.WeakKeyDictionary()

    def clear(self):
        """Clean up all the current events.

        This events will not be received.
        """
        self.__eventStack = []

    def empty(self):
        """Returns true if there is no stored events."""
        return len(self.__eventStack) == 0

    def callbackTo(self, callback, callbackId=None):
        """Create a callback for events which have to be emitted to this
        `callback`

        Returns a callable which have to be used to receive the event
        """
        internalCallback = self.__callbacks.get(callback, None)
        if internalCallback is None:

            def func(*args, **kwargs):
                self.__eventStack.append(Event(callback, args, kwargs, callbackId))
                self.eventAdded.emit()

            internalCallback = func
            self.__callbacks[callback] = internalCallback

        return internalCallback

    def flush(self):
        """Flush all the stored event to the targetted callbacks."""
        eventStack, self.__eventStack = self.reduce(self.__eventStack)
        for e in eventStack:
            e.emit()

    def reduce(self, eventStack: list) -> tuple[list, list]:
        """This method can be implemented to reduce the amount of event in the
        stack before emitting them.

        Returns the events to process now, and the events to process next time.
        """
        return eventStack, []
